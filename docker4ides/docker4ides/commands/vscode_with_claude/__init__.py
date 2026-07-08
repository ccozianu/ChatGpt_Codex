"""VS Code plus Claude configuration command group."""

from __future__ import annotations

from docker4ides.commands.base import BaseGroup


class VscodeWithClaudeCommand(BaseGroup):
    name = "vscode_with_claude"
    help = "Build and run the VS Code plus Claude configuration."
    subcommand_package = "docker4ides.commands.vscode_with_claude"


COMMAND = VscodeWithClaudeCommand

