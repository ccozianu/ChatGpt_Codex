"""Bootstrap command group."""

from __future__ import annotations

from docker4ides.commands.base import BaseGroup


class BootstrapCommand(BaseGroup):
    name = "bootstrap"
    help = "Bootstrap project workflow files."
    subcommand_package = "docker4ides.commands.bootstrap"


COMMAND = BootstrapCommand
