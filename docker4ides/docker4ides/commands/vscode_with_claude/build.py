"""VS Code plus Claude build command."""

from __future__ import annotations

from docker4ides.commands.base import BaseCommand
from docker4ides.configurations.vscode_with_claude import not_implemented


class VscodeWithClaudeBuildCommand(BaseCommand):
    name = "build"
    help = "Build the VS Code plus Claude image."

    def run(self) -> int:
        return not_implemented("build")


COMMAND = VscodeWithClaudeBuildCommand

