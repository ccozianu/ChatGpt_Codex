"""Command line entry point for Docker4IDEs.

The initial refactoring slice keeps the validated shell implementation as the
source of behavior and exposes it through a stable Python command tree. Shared
runtime logic can move behind these commands incrementally.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence


PROJECT_NAME = "docker4ides"


class CliError(Exception):
    """User-facing command error."""


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Docker4IDEs CLI."""

    args = list(sys.argv[1:] if argv is None else argv)
    try:
        return dispatch(args)
    except CliError as exc:
        print(f"{PROJECT_NAME}: {exc}", file=sys.stderr)
        return 2


def dispatch(args: Sequence[str]) -> int:
    if not args or args[0] in {"-h", "--help", "help"}:
        print_top_level_help()
        return 0

    command = args[0]
    rest = list(args[1:])

    if command == "run":
        return dispatch_run(rest)
    if command == "build":
        return dispatch_build(rest)
    if command == "check":
        return dispatch_check(rest)
    if command in {"bootstrap", "bootstrap-project"}:
        return dispatch_bootstrap(rest)

    raise CliError(f"unknown command: {command}")


def dispatch_run(args: Sequence[str]) -> int:
    if not args or args[0] in {"-h", "--help", "help"}:
        print_run_help()
        return 0

    target = args[0]
    rest = list(args[1:])
    if target == "pycharm":
        return run_script("docker4pycharm/run-pycharm-container.sh", rest)

    raise CliError(f"unknown run target: {target}")


def dispatch_build(args: Sequence[str]) -> int:
    if not args or args[0] in {"-h", "--help", "help"}:
        print_build_help()
        return 0

    target = args[0]
    rest = list(args[1:])
    if target == "pycharm":
        return run_script("docker4pycharm/build-image.sh", rest)

    raise CliError(f"unknown build target: {target}")


def dispatch_check(args: Sequence[str]) -> int:
    if not args or args[0] in {"-h", "--help", "help"}:
        print_check_help()
        return 0

    scope = args[0]
    rest = list(args[1:])
    if scope != "runtime":
        raise CliError(f"unknown check scope: {scope}")

    if not rest or rest[0] in {"-h", "--help", "help"}:
        print_check_runtime_help()
        return 0

    target = rest[0]
    target_args = rest[1:]
    if target == "pycharm":
        return run_script("docker4pycharm/check-runtime-deps.sh", target_args)

    raise CliError(f"unknown runtime check target: {target}")


def dispatch_bootstrap(args: Sequence[str]) -> int:
    if args and args[0] == "project":
        args = args[1:]
    if args and args[0] in {"help"}:
        args = ["--help", *args[1:]]
    return run_script("docker4pycharm/bootstrap-project.sh", list(args))


def run_script(relative_path: str, args: Sequence[str]) -> int:
    script = repo_root() / relative_path
    if not script.exists():
        raise CliError(f"compatibility script is missing: {script}")
    if not os.access(script, os.X_OK):
        raise CliError(f"compatibility script is not executable: {script}")

    completed = subprocess.run([str(script), *args], check=False)
    return completed.returncode


def repo_root() -> Path:
    override = os.environ.get("DOCKER4IDES_REPO_ROOT")
    if override:
        return Path(override).expanduser().resolve()

    return Path(__file__).resolve().parents[2]


def print_top_level_help() -> None:
    print(
        """Usage:
  docker4ides <command> [target] [options]
  python -m docker4ides <command> [target] [options]

Commands:
  run pycharm [options]              Launch PyCharm through the current compatibility wrapper
  build pycharm [options]            Build the PyCharm image through the current compatibility wrapper
  check runtime pycharm [options]    Run the PyCharm runtime dependency check
  bootstrap project [options]        Seed human/agent workflow files in a project

Run a leaf command with --help to see the underlying compatibility script options."""
    )


def print_run_help() -> None:
    print(
        """Usage:
  docker4ides run <target> [options]

Targets:
  pycharm    Launch the current Dockerized PyCharm profile.

Example:
  docker4ides run pycharm --project /path/to/project --ssh-agent"""
    )


def print_build_help() -> None:
    print(
        """Usage:
  docker4ides build <target> [options]

Targets:
  pycharm    Build the current Dockerized PyCharm image.

Example:
  docker4ides build pycharm --pycharm /path/to/pycharm.tar.gz"""
    )


def print_check_help() -> None:
    print(
        """Usage:
  docker4ides check <scope> <target> [options]

Scopes:
  runtime    Run runtime dependency checks."""
    )


def print_check_runtime_help() -> None:
    print(
        """Usage:
  docker4ides check runtime <target> [options]

Targets:
  pycharm    Run the current PyCharm runtime dependency check."""
    )
