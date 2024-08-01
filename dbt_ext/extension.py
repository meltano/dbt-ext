"""Meltano dbt extension."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import structlog
from meltano.edk import models
from meltano.edk.extension import ExtensionBase
from meltano.edk.process import Invoker, log_subprocess_error
from meltano.edk.types import ExecArg

from . import dbt_files

try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources

log = structlog.get_logger()


class MissingProfileTypeError(Exception):
    """Missing profile type error."""

    pass


class dbt(ExtensionBase):
    """Extension implementing the ExtensionBase interface."""

    def __init__(self) -> None:
        """Initialize the extension.

        Raises:
            MissingProfileTypeError: If the profile type is not set.
        """
        self.dbt_bin = "dbt"
        self.dbt_ext_type = os.getenv("DBT_EXT_TYPE", None)
        if not self.dbt_ext_type:
            raise MissingProfileTypeError("DBT_EXT_TYPE must be set")
        self.dbt_project_dir = Path(os.getenv("DBT_PROJECT_DIR", "transform"))
        self.dbt_profiles_dir = Path(
            os.getenv("DBT_PROFILES_DIR", self.dbt_project_dir / "profiles")
        )
        self.dbt_invoker = Invoker(self.dbt_bin, cwd=self.dbt_project_dir)
        self.skip_pre_invoke = (
            os.getenv("DBT_EXT_SKIP_PRE_INVOKE", "false").lower() == "true"
        )

    def pre_invoke(self, invoke_name: str | None, *invoke_args: ExecArg) -> None:
        """Pre-invoke hook.

        Runs `dbt deps` to ensure dependencies are up-to-date on every invocation.

        Args:
            invoke_name: The name of the command that will eventually be invoked.
            invoke_args: The arguments that will be passed to the command.
        """
        if self.skip_pre_invoke:
            log.debug("skipping pre-invoke as DBT_EXT_SKIP_PRE_INVOKE is set")
            return

        if invoke_name in ["deps", "clean"]:
            log.debug("skipping pre-invoke as command being invoked is deps or clean")
            return

        try:
            log.info("Extension executing `dbt clean`...")
            self.dbt_invoker.run_and_log("clean")
        except subprocess.CalledProcessError as err:
            log_subprocess_error(
                "dbt clean", err, "pre invoke step of `dbt clean` failed"
            )
            sys.exit(err.returncode)

        try:
            log.info("Extension executing `dbt deps`...")
            self.dbt_invoker.run_and_log("deps")
        except subprocess.CalledProcessError as err:
            log_subprocess_error(
                "dbt deps", err, "pre invoke step of `dbt deps` failed"
            )
            sys.exit(err.returncode)

    def invoke(self, command_name: str | None, *command_args: ExecArg) -> None:
        """Invoke the underlying cli, that is being wrapped by this extension.

        Args:
            command_name: The name of the command to invoke.
            command_args: The arguments to pass to the command.
        """
        try:
            command_msg = command_name if command_name else self.dbt_bin
            if len(command_args) > 0:
                command_msg += f" {command_args[0]}"
            log.info(f"Extension executing `{command_msg}`...")
            self.dbt_invoker.run_and_log(command_name, *command_args)
        except subprocess.CalledProcessError as err:
            log_subprocess_error(f"dbt {command_name}", err, "dbt invocation failed")
            sys.exit(err.returncode)

    def describe(self) -> models.Describe:
        """Describe the extension.

        Returns:
            The extension description
        """
        # TODO: could we auto-generate all or portions of this from typer instead?
        return models.Describe(
            commands=[
                models.ExtensionCommand(
                    name="dbt_extension", description="extension commands"
                ),
                models.InvokerCommand(
                    name="dbt_invoker", description="pass through invoker"
                ),
            ]
        )

    def initialize(self, force: bool = False) -> None:
        """Initialize the extension.

        Args:
            force: Whether to force initialization.
        """
        if not self.dbt_project_dir.exists():
            log.info("creating dbt project directory", path=self.dbt_project_dir)
            self.dbt_project_dir.mkdir(parents=True, exist_ok=True)

        files_dir = resources.files(dbt_files)

        for entry in files_dir.joinpath("bundle", "transform").iterdir():
            if entry.name == "__pycache__":
                continue
            log.debug(f"deploying {entry.name}", entry=entry, dst=self.dbt_project_dir)
            if entry.is_file():
                shutil.copy(entry, self.dbt_project_dir / entry.name)
            else:
                shutil.copytree(
                    entry, self.dbt_project_dir / entry.name, dirs_exist_ok=True
                )

        if not self.dbt_profiles_dir.exists():
            log.info("creating dbt profiles directory", path=self.dbt_profiles_dir)
            self.dbt_profiles_dir.mkdir(parents=True, exist_ok=True)

        for entry in files_dir.joinpath("profiles").iterdir():
            if entry.name == self.dbt_ext_type and entry.is_dir():
                log.debug(
                    f"deploying {entry.name} profile",
                    entry=entry,
                    dst=self.dbt_profiles_dir,
                )
                shutil.copytree(entry, self.dbt_profiles_dir, dirs_exist_ok=True)
                break
        else:
            log.error(f"dbt type {self.dbt_ext_type} had no matching profile.")

        log.info(
            "dbt initialized",
            dbt_ext_type=self.dbt_ext_type,
            dbt_project_dir=self.dbt_project_dir,
            dbt_profiles_dir=self.dbt_profiles_dir,
        )
