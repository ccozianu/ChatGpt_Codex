"""VS Code plus Claude configuration command support."""

from __future__ import annotations

from dataclasses import dataclass

import click


ALIAS = "vscode_with_claude"


@dataclass(frozen=True)
class VscodeWithClaudeConfiguration:
    alias: str = ALIAS
    ide: str = "vscode"
    agent: str = "claude"
    implemented: bool = False


def describe_configuration() -> VscodeWithClaudeConfiguration:
    """Return the V1 proof-point configuration identity."""

    return VscodeWithClaudeConfiguration()


def not_implemented(command: str) -> int:
    """Fail explicitly for commands whose implementation is still pending."""

    raise click.ClickException(
        f"{ALIAS} {command} is registered as the next configuration module, "
        "but its Docker image and launcher are not implemented yet."
    )

