"""Top-level bootstrap-project compatibility alias."""

from __future__ import annotations

from docker4ides.commands.base import BaseCommand
from docker4ides.compat import run_script


FORWARD_CONTEXT = {
    "allow_extra_args": True,
    "ignore_unknown_options": True,
    "help_option_names": [],
}


class BootstrapProjectAliasCommand(BaseCommand):
    name = "bootstrap-project"
    help = "Compatibility alias for bootstrap project."
    context_settings = FORWARD_CONTEXT
    hidden = True
    pass_context = True

    def run(self) -> int:
        return run_script("docker4pycharm/bootstrap-project.sh", list(self.ctx.args))


COMMAND = BootstrapProjectAliasCommand
