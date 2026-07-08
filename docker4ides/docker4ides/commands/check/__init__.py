"""Check command group."""

from __future__ import annotations

from docker4ides.commands.base import BaseGroup


class CheckCommand(BaseGroup):
    name = "check"
    help = "Compatibility path for environment checks."
    subcommand_package = "docker4ides.commands.check"
    hidden = True


COMMAND = CheckCommand
