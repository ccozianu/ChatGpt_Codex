"""PyCharm configuration build command."""

from __future__ import annotations

from docker4ides.commands.base import BaseCommand
from docker4ides.configurations.pycharm import FORWARD_CONTEXT, build_image


class PycharmBuildCommand(BaseCommand):
    name = "build"
    help = "Build the current Dockerized PyCharm image through the compatibility script."
    context_settings = FORWARD_CONTEXT
    pass_context = True

    def run(self) -> int:
        return build_image(list(self.ctx.args))


COMMAND = PycharmBuildCommand

