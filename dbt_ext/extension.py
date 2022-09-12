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
        self.dbt_type = os.getenv("DBT_TYPE", "postgres")

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
        dbt_transform_dir = Path(os.environ["MELTANO_PROJECT_ROOT"]) / "transform"
        if not dbt_transform_dir.exists():
            log.info("creating dbt transform directory", path=dbt_transform_dir)
            dbt_transform_dir.mkdir(parents=True, exist_ok=True)

        for entry in ir_files("files_dbt_ext.bundle.transform").iterdir():
            if entry.name == "__pycache__":
                continue
            log.debug(f"deploying {entry.name}", entry=entry, dst=dbt_transform_dir)
            if entry.is_file():
                shutil.copy(entry, dbt_transform_dir / entry.name)
            else:
                shutil.copytree(
                    entry, dbt_transform_dir / entry.name, dirs_exist_ok=True
                )

        profiles_dir = dbt_transform_dir / "profiles"
        if not profiles_dir.exists():
            log.info("creating dbt profiles directory", path=profiles_dir)
            profiles_dir.mkdir(parents=True, exist_ok=True)

        for entry in ir_files("files_dbt_ext.profiles").iterdir():
            if entry.name == self.dbt_type and entry.is_dir():
                log.debug(
                    f"deploying {entry.name} profile", entry=entry, dst=profiles_dir
                )
                shutil.copytree(entry, profiles_dir / entry.name, dirs_exist_ok=True)
                break
        else:
            log.error(f"dbt type {self.dbt_type} had no matching profile.")

        log.info(
            "dbt initialized",
            dbt_type=self.dbt_type,
            dbt_transform_dir=dbt_transform_dir,
            profiles_dir=profiles_dir,
        )
