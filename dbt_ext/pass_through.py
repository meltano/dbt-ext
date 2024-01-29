"""Passthrough shim for dbt extension."""

import sys

import structlog
from meltano.edk.logging import pass_through_logging_config

from dbt_ext.extension import dbt


def pass_through_cli() -> None:
    """Pass through CLI entry point."""
    pass_through_logging_config()
    ext = dbt()
    ext.pass_through_invoker(
        structlog.getLogger("dbt_invoker"), *sys.argv[1:] if len(sys.argv) > 1 else []
    )
