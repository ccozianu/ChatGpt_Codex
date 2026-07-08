"""Project bootstrap compatibility command."""

from __future__ import annotations

from docker4ides.commands.base import BaseCommand
from docker4ides.compat import run_script


FORWARD_CONTEXT = {
    "allow_extra_args": True,
    "ignore_unknown_options": True,
    "help_option_names": [],
}


class BootstrapProjectCommand(BaseCommand):
    name = "project"
    help = "Seed human/agent workflow files in a project."
    context_settings = FORWARD_CONTEXT
    pass_context = True

    def run(self) -> int:
        return run_script("docker4pycharm/bootstrap-project.sh", list(self.ctx.args))


COMMAND = BootstrapProjectCommand

