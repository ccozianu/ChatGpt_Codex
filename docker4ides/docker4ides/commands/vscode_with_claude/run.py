"""VS Code plus Claude run command."""

from __future__ import annotations

from docker4ides.commands.base import BaseCommand
from docker4ides.configurations.vscode_with_claude import not_implemented


class VscodeWithClaudeRunCommand(BaseCommand):
    name = "run"
    help = "Launch the VS Code plus Claude configuration."

    def run(self) -> int:
        return not_implemented("run")


COMMAND = VscodeWithClaudeRunCommand

