"""PyCharm configuration command group."""

from __future__ import annotations

from docker4ides.commands.base import BaseGroup


class PycharmCommand(BaseGroup):
    name = "pycharm"
    help = "Build and run the PyCharm IDE configuration."
    subcommand_package = "docker4ides.commands.pycharm"


COMMAND = PycharmCommand

