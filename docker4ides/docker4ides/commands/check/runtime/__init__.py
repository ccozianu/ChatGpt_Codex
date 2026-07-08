"""Runtime check command group."""

from __future__ import annotations

from docker4ides.commands.base import BaseGroup


class RuntimeCommand(BaseGroup):
    name = "runtime"
    help = "Run runtime dependency checks."
    subcommand_package = "docker4ides.commands.check.runtime"


COMMAND = RuntimeCommand

