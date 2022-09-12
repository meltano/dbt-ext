"""Meltano dbt extension."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import structlog
from meltano.edk import models
from meltano.edk.extension import ExtensionBase
from meltano.edk.process import Invoker, log_subprocess_error

try:
    from importlib.resources import files as ir_files
except ImportError:
    from importlib_resources import files as ir_files

log = structlog.get_logger()


class dbt(ExtensionBase):
    """Extension implementing the ExtensionBase interface."""

    def __init__(self) -> None:
        """Initialize the extension."""
        self.dbt_bin = "dbt"  # verify this is the correct name
        self.dbt_invoker = Invoker(self.dbt_bin)
        self.dbt_type = os.getenv("DBT_EXT_TYPE", None)
        if not self.dbt_type:
            raise Exception("DBT_EXT_TYPE must be set")
        self.dbt_project_dir = Path(os.getenv("DBT_EXT_PROJECT_DIR", "transform"))
        self.dbt_profiles_dir = Path(os.getenv("DBT_EXT_PROFILES_DIR", None))

    def invoke(self, command_name: str | None, *command_args: Any) -> None:
        """Invoke the underlying cli, that is being wrapped by this extension.

        Args:
            command_name: The name of the command to invoke.
            command_args: The arguments to pass to the command.
        """
        try:
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

        for entry in ir_files("files_dbt_ext.bundle.transform").iterdir():
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

        for entry in ir_files("files_dbt_ext.profiles").iterdir():
            if entry.name == self.dbt_type and entry.is_dir():
                log.debug(
                    f"deploying {entry.name} profile", entry=entry, dst=self.dbt_profiles_dir
                )
                shutil.copytree(entry, self.dbt_profiles_dir, dirs_exist_ok=True)
                break
        else:
            log.error(f"dbt type {self.dbt_type} had no matching profile.")

        log.info(
            "dbt initialized",
            dbt_type=self.dbt_type,
            dbt_project_dir=self.dbt_project_dir,
            dbt_profiles_dir=self.dbt_profiles_dir,
        )
