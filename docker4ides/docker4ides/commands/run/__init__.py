"""Run command group."""

from __future__ import annotations

from docker4ides.commands.base import BaseGroup


class RunCommand(BaseGroup):
    name = "run"
    help = "Compatibility path for IDE profile runs."
    subcommand_package = "docker4ides.commands.run"
    hidden = True


COMMAND = RunCommand
