"""Passthrough shim for dbt extension."""
import sys

import structlog

from dbt_ext.extension import dbt
from meltano.edk.logging import pass_through_logging_config


def pass_through_cli() -> None:
    """Pass through CLI entry point."""
    pass_through_logging_config()
    ext = dbt()
    ext.pass_through_invoker(
        structlog.getLogger("dbt_invoker"),
        *sys.argv[1:] if len(sys.argv) > 1 else []
    )
