"""Compatibility helpers for legacy shell-backed commands."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Sequence


class CliError(Exception):
    """User-facing command error."""


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
