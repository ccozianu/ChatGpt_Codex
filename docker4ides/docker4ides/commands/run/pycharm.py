"""Legacy run pycharm command."""

from __future__ import annotations

from docker4ides.commands.base import BaseCommand
from docker4ides.configurations.pycharm import RUN_PARAMS, run_from_cli_options


class PycharmRunCommand(BaseCommand):
    name = "pycharm"
    help = "Compatibility path for pycharm run."
    params = RUN_PARAMS

    def run(self) -> int:
        return run_from_cli_options(**self.__dict__)


COMMAND = PycharmRunCommand
