"""Docker launcher for VSCodium plus Claude Code."""

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from docker4ides.compat import CliError

DEFAULT_IMAGE = "codium-with-claude:latest"


@dataclass(frozen=True)
class CodiumRunOptions:
    project: Path
    image: str = DEFAULT_IMAGE
    name: str | None = None
    state: Path | None = None
    project_state: Path | None = None
    debug_shell: bool = False
    extra_docker_args: tuple[str, ...] = ()


def build_codium_run_command(options: CodiumRunOptions, env: Mapping[str, str] | None = None) -> list[str]:
    env = os.environ if env is None else env
    project = options.project.expanduser().resolve()
    if not project.is_dir():
        raise CliError(f"Project directory does not exist: {project}")
    display = env.get("DISPLAY")
    if not display:
        raise CliError("DISPLAY is not set; VSCodium currently requires a host X11 display")
    home = Path(env.get("HOME", str(Path.home()))).expanduser()
    state = (options.state or home / ".config" / "docker4ides" / "codium-with-claude").resolve()
    project_state = (options.project_state or project / ".docker4ides" / "codium-state").resolve()
    state.mkdir(parents=True, exist_ok=True)
    project_state.mkdir(parents=True, exist_ok=True)
    name = options.name or f"codium-with-claude-{os.getuid()}-{int(time.time())}"
    container_command = (
        ["bash"]
        if options.debug_shell
        else [
            "codium",
            "--user-data-dir=/ide-global-settings/codium/user-data",
            "--extensions-dir=/ide-global-settings/codium/extensions",
            "/workspace/project",
        ]
    )
    interactive_args = ["--interactive", "--tty"] if options.debug_shell else []
    return [
        "docker",
        "run",
        "--rm",
        *interactive_args,
        "--name",
        name,
        "--env",
        f"DISPLAY={display}",
        "--env",
        f"HOST_UID={os.getuid()}",
        "--env",
        f"HOST_GID={os.getgid()}",
        "--volume",
        f"{project}:/workspace/project",
        "--volume",
        f"{state}:/ide-global-settings",
        "--volume",
        f"{project_state}:/ide-project-state",
        "--volume",
        "/tmp/.X11-unix:/tmp/.X11-unix:ro",
        *options.extra_docker_args,
        options.image,
        *container_command,
    ]


def run_codium(options: CodiumRunOptions, env: Mapping[str, str] | None = None) -> int:
    return subprocess.run(build_codium_run_command(options, env), check=False).returncode
