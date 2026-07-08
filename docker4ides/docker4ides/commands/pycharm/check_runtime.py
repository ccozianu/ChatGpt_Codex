"""PyCharm configuration runtime check command."""

from __future__ import annotations

from docker4ides.commands.base import BaseCommand
from docker4ides.configurations.pycharm import FORWARD_CONTEXT, check_runtime


class PycharmCheckRuntimeCommand(BaseCommand):
    name = "check-runtime"
    help = "Run the current PyCharm runtime dependency check."
    context_settings = FORWARD_CONTEXT
    pass_context = True

    def run(self) -> int:
        return check_runtime(list(self.ctx.args))


COMMAND = PycharmCheckRuntimeCommand

