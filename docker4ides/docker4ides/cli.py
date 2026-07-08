"""Command line entry point for Docker4IDEs."""

from __future__ import annotations

import sys
from typing import Sequence

import click

from docker4ides.commands.base import DiscoveredCommandGroup
from docker4ides.compat import CliError, repo_root


PROJECT_NAME = "docker4ides"


cli = DiscoveredCommandGroup(
    name=PROJECT_NAME,
    package_name="docker4ides.commands",
    help="Profile-driven Docker launch tooling for isolated IDEs.",
    no_args_is_help=True,
)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Docker4IDEs CLI."""

    args = list(sys.argv[1:] if argv is None else argv)
    try:
        result = cli.main(args=args, prog_name=PROJECT_NAME, standalone_mode=False)
    except click.exceptions.Exit as exc:
        return int(exc.exit_code or 0)
    except click.ClickException as exc:
        exc.show(file=sys.stderr)
        return int(exc.exit_code)
    except click.Abort:
        print(f"{PROJECT_NAME}: aborted", file=sys.stderr)
        return 1
    except CliError as exc:
        print(f"{PROJECT_NAME}: {exc}", file=sys.stderr)
        return 2
    return int(result or 0)
