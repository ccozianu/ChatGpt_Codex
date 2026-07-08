"""PyCharm configuration command support."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click

from docker4ides.compat import run_script
from docker4ides.pycharm import (
    DockerMode,
    IdeConfigMode,
    PycharmRunError,
    PycharmRunOptions,
    run_pycharm,
)


RUN_PARAMS = [
    click.Option(
        ["--project", "-p"],
        type=click.Path(path_type=Path),
        default=Path("."),
        help="Host project directory to open. Defaults to the current directory.",
    ),
    click.Option(["--profile"], help="Named PyCharm state profile under ~/.config/docker-pycharm-NAME."),
    click.Option(["--image"], help="Docker image to run."),
    click.Option(["--name"], help="Container name."),
    click.Option(
        ["--global-settings", "--state"],
        type=click.Path(path_type=Path),
        help="Shared IDE config/home root.",
    ),
    click.Option(
        ["--project-state"],
        type=click.Path(path_type=Path),
        help="Per-project IDE cache/log/workspace root.",
    ),
    click.Option(
        ["--project-state-root"],
        type=click.Path(path_type=Path),
        help=(
            "Root for mirrored per-project state paths. "
            "Example: /work/.state mirrors /work/project to /work/.state/project."
        ),
    ),
    click.Option(
        ["--config-mode"],
        type=click.Choice(["shared", "project", "custom"], case_sensitive=False),
        help="PyCharm config path mode: shared, project, or custom.",
    ),
    click.Option(
        ["--ide-config"],
        type=click.Path(path_type=Path),
        help="PyCharm config dir. Implies --config-mode custom.",
    ),
    click.Option(
        ["--project-config"],
        is_flag=True,
        help="Compatibility shorthand for --config-mode project.",
    ),
    click.Option(
        ["--shared-config"],
        is_flag=True,
        help="Compatibility shorthand for --config-mode shared.",
    ),
    click.Option(["--project-mount"], help="In-container project path."),
    click.Option(
        ["--plugins"],
        type=click.Path(path_type=Path),
        help="Persistent PyCharm plugins dir.",
    ),
    click.Option(["--ssh-agent"], is_flag=True, help="Forward host SSH agent socket."),
    click.Option(["--git-user-name"], help="Git user.name inside IDE."),
    click.Option(["--git-user-email"], help="Git user.email inside IDE."),
    click.Option(["--git-identity-from-host"], is_flag=True, help="Require host Git identity import."),
    click.Option(["--no-git-identity-from-host"], is_flag=True, help="Disable host Git identity import."),
    click.Option(
        ["--git-token-file", "--github-token-file"],
        type=click.Path(path_type=Path),
        help="HTTPS Git token file.",
    ),
    click.Option(
        ["--git-token-env", "--github-token-env"],
        help="Environment variable containing HTTPS Git token.",
    ),
    click.Option(["--git-token-user", "--github-user"], help="Username for HTTPS Git askpass."),
    click.Option(["--git-token-host"], help="Comma/space-separated hosts allowed to receive the token."),
    click.Option(["--docker", "--host-docker"], is_flag=True, help="Connect to the host Docker daemon."),
    click.Option(
        ["--docker-socket"],
        type=click.Path(path_type=Path),
        help="Host Docker socket for --docker.",
    ),
    click.Option(
        ["--docker-in-docker", "--dind"],
        is_flag=True,
        help="Start an isolated inner Docker daemon.",
    ),
    click.Option(["--no-docker"], is_flag=True, help="Disable Docker access."),
    click.Option(
        ["--debug-native"],
        is_flag=True,
        help="Add ptrace/seccomp permissions for native debugging.",
    ),
    click.Option(
        ["--dev-sudo", "--sudo"],
        is_flag=True,
        help="Enable passwordless sudo for the IDE user.",
    ),
    click.Option(
        ["--writable-root"],
        is_flag=True,
        help="Do not run with a read-only root filesystem.",
    ),
    click.Option(
        ["--ignore-config-lock"],
        is_flag=True,
        help="Skip preflight for an existing PyCharm config .lock.",
    ),
    click.Option(
        ["--docker-arg"],
        multiple=True,
        help="Append one raw docker-run argument; repeat for advanced cases.",
    ),
]


FORWARD_CONTEXT = {
    "allow_extra_args": True,
    "ignore_unknown_options": True,
    "help_option_names": [],
}


def run_from_cli_options(**kwargs: Any) -> int:
    """Run PyCharm from Click-parsed options."""

    options = PycharmRunOptions(
        project=kwargs["project"],
        profile=kwargs["profile"],
        image=kwargs["image"],
        name=kwargs["name"],
        global_settings=kwargs["global_settings"],
        project_state=kwargs["project_state"],
        project_state_root=kwargs["project_state_root"],
        config_mode=resolve_config_mode(
            as_ide_config_mode(kwargs["config_mode"]),
            kwargs["ide_config"],
            kwargs["project_config"],
            kwargs["shared_config"],
        ),
        ide_config=kwargs["ide_config"],
        project_mount=kwargs["project_mount"],
        plugins=kwargs["plugins"],
        use_ssh_agent=kwargs["ssh_agent"],
        git_user_name=kwargs["git_user_name"],
        git_user_email=kwargs["git_user_email"],
        git_identity_from_host=resolve_git_identity_mode(
            kwargs["git_identity_from_host"],
            kwargs["no_git_identity_from_host"],
        ),
        git_token_file=kwargs["git_token_file"],
        git_token_env=kwargs["git_token_env"],
        git_token_username=kwargs["git_token_user"],
        git_token_hosts=kwargs["git_token_host"],
        docker_mode=resolve_docker_mode(kwargs["docker"], kwargs["docker_in_docker"], kwargs["no_docker"]),
        host_docker_socket=kwargs["docker_socket"],
        debug_native=kwargs["debug_native"],
        writable_root=kwargs["writable_root"],
        enable_sudo=kwargs["dev_sudo"],
        ignore_config_lock=kwargs["ignore_config_lock"],
        extra_docker_args=list(kwargs["docker_arg"] or []),
    )
    try:
        return run_pycharm(options)
    except PycharmRunError as exc:
        raise click.ClickException(str(exc)) from exc


def build_image(args: list[str]) -> int:
    """Build the PyCharm image through the current compatibility script."""

    return run_script("docker4pycharm/build-image.sh", args)


def check_runtime(args: list[str]) -> int:
    """Run the PyCharm runtime dependency check compatibility script."""

    return run_script("docker4pycharm/check-runtime-deps.sh", args)


def as_ide_config_mode(value: str | None) -> IdeConfigMode | None:
    if value is None:
        return None
    return IdeConfigMode(value.lower())


def resolve_config_mode(
    config_mode: IdeConfigMode | None,
    ide_config: Path | None,
    project_config: bool,
    shared_config: bool,
) -> IdeConfigMode | None:
    requested_shorthands = [project_config, shared_config]
    if sum(1 for requested in requested_shorthands if requested) > 1:
        raise click.BadParameter("choose only one of --project-config or --shared-config")
    if config_mode is not None and any(requested_shorthands):
        raise click.BadParameter("do not combine --config-mode with --project-config or --shared-config")
    conflicting_config_mode = config_mode in {IdeConfigMode.shared, IdeConfigMode.project}
    if ide_config is not None and (conflicting_config_mode or any(requested_shorthands)):
        raise click.BadParameter("--ide-config can only be used with --config-mode custom")
    if project_config:
        return IdeConfigMode.project
    if shared_config:
        return IdeConfigMode.shared
    if config_mode is not None:
        return config_mode
    if ide_config is not None:
        return IdeConfigMode.custom
    return None


def resolve_git_identity_mode(from_host: bool, no_from_host: bool) -> str | None:
    if from_host and no_from_host:
        raise click.BadParameter("choose only one of --git-identity-from-host or --no-git-identity-from-host")
    if from_host:
        return "1"
    if no_from_host:
        return "0"
    return None


def resolve_docker_mode(docker: bool, docker_in_docker: bool, no_docker: bool) -> DockerMode | None:
    requested_modes = [docker, docker_in_docker, no_docker]
    if sum(1 for requested in requested_modes if requested) > 1:
        raise click.BadParameter("choose only one Docker mode flag")
    if docker:
        return DockerMode.host
    if docker_in_docker:
        return DockerMode.dind
    if no_docker:
        return DockerMode.none
    return None

