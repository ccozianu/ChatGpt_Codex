"""Command line entry point for Docker4IDEs."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Annotated, Sequence

import click
import typer

from docker4ides.pycharm import (
    DockerMode,
    IdeConfigMode,
    PycharmRunError,
    PycharmRunOptions,
    run_pycharm,
)


PROJECT_NAME = "docker4ides"
FORWARD_CONTEXT = {
    "allow_extra_args": True,
    "ignore_unknown_options": True,
    "help_option_names": [],
}


class CliError(Exception):
    """User-facing command error."""


app = typer.Typer(no_args_is_help=True, help="Profile-driven Docker launch tooling for isolated IDEs.")
run_app = typer.Typer(no_args_is_help=True, help="Run an IDE profile.")
build_app = typer.Typer(no_args_is_help=True, help="Build an IDE image.")
check_app = typer.Typer(no_args_is_help=True, help="Run environment checks.")
check_runtime_app = typer.Typer(no_args_is_help=True, help="Run runtime dependency checks.")
bootstrap_app = typer.Typer(no_args_is_help=True, help="Bootstrap project workflow files.")

app.add_typer(run_app, name="run")
app.add_typer(build_app, name="build")
app.add_typer(check_app, name="check")
check_app.add_typer(check_runtime_app, name="runtime")
app.add_typer(bootstrap_app, name="bootstrap")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Docker4IDEs CLI."""

    args = list(sys.argv[1:] if argv is None else argv)
    try:
        app(args=args, prog_name=PROJECT_NAME, standalone_mode=False)
    except typer.Exit as exc:
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
    return 0


@run_app.command("pycharm")
def run_pycharm_command(
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Host project directory to open. Defaults to the current directory."),
    ] = Path("."),
    profile: Annotated[
        str | None,
        typer.Option(
            "--profile",
            help="Named PyCharm state profile under ~/.config/docker-pycharm-NAME.",
        ),
    ] = None,
    image: Annotated[str | None, typer.Option("--image", help="Docker image to run.")] = None,
    name: Annotated[str | None, typer.Option("--name", help="Container name.")] = None,
    global_settings: Annotated[
        Path | None,
        typer.Option("--global-settings", "--state", help="Shared IDE config/home root."),
    ] = None,
    project_state: Annotated[
        Path | None,
        typer.Option("--project-state", help="Per-project IDE cache/log/workspace root."),
    ] = None,
    project_state_root: Annotated[
        Path | None,
        typer.Option(
            "--project-state-root",
            help="Root for mirrored per-project state paths. Example: /work/.state mirrors /work/project to /work/.state/project.",
        ),
    ] = None,
    config_mode: Annotated[
        IdeConfigMode | None,
        typer.Option(
            "--config-mode",
            case_sensitive=False,
            help="PyCharm config path mode: shared, project, or custom.",
        ),
    ] = None,
    ide_config: Annotated[
        Path | None,
        typer.Option("--ide-config", help="PyCharm config dir. Implies --config-mode custom."),
    ] = None,
    project_config: Annotated[
        bool,
        typer.Option("--project-config", help="Compatibility shorthand for --config-mode project."),
    ] = False,
    shared_config: Annotated[
        bool,
        typer.Option("--shared-config", help="Compatibility shorthand for --config-mode shared."),
    ] = False,
    project_mount: Annotated[
        str | None,
        typer.Option("--project-mount", help="In-container project path."),
    ] = None,
    plugins: Annotated[Path | None, typer.Option("--plugins", help="Persistent PyCharm plugins dir.")] = None,
    ssh_agent: Annotated[bool, typer.Option("--ssh-agent", help="Forward host SSH agent socket.")] = False,
    git_user_name: Annotated[str | None, typer.Option("--git-user-name", help="Git user.name inside IDE.")] = None,
    git_user_email: Annotated[str | None, typer.Option("--git-user-email", help="Git user.email inside IDE.")] = None,
    git_identity_from_host: Annotated[
        bool,
        typer.Option("--git-identity-from-host", help="Require host Git identity import."),
    ] = False,
    no_git_identity_from_host: Annotated[
        bool,
        typer.Option("--no-git-identity-from-host", help="Disable host Git identity import."),
    ] = False,
    git_token_file: Annotated[
        Path | None,
        typer.Option("--git-token-file", "--github-token-file", help="HTTPS Git token file."),
    ] = None,
    git_token_env: Annotated[
        str | None,
        typer.Option("--git-token-env", "--github-token-env", help="Environment variable containing HTTPS Git token."),
    ] = None,
    git_token_user: Annotated[
        str | None,
        typer.Option("--git-token-user", "--github-user", help="Username for HTTPS Git askpass."),
    ] = None,
    git_token_host: Annotated[
        str | None,
        typer.Option("--git-token-host", help="Comma/space-separated hosts allowed to receive the token."),
    ] = None,
    docker: Annotated[
        bool,
        typer.Option("--docker", "--host-docker", help="Connect to the host Docker daemon."),
    ] = False,
    docker_socket: Annotated[
        Path | None,
        typer.Option("--docker-socket", help="Host Docker socket for --docker."),
    ] = None,
    docker_in_docker: Annotated[
        bool,
        typer.Option("--docker-in-docker", "--dind", help="Start an isolated inner Docker daemon."),
    ] = False,
    no_docker: Annotated[bool, typer.Option("--no-docker", help="Disable Docker access.")] = False,
    debug_native: Annotated[
        bool,
        typer.Option("--debug-native", help="Add ptrace/seccomp permissions for native debugging."),
    ] = False,
    dev_sudo: Annotated[
        bool,
        typer.Option("--dev-sudo", "--sudo", help="Enable passwordless sudo for the IDE user."),
    ] = False,
    writable_root: Annotated[
        bool,
        typer.Option("--writable-root", help="Do not run with a read-only root filesystem."),
    ] = False,
    ignore_config_lock: Annotated[
        bool,
        typer.Option("--ignore-config-lock", help="Skip preflight for an existing PyCharm config .lock."),
    ] = False,
    docker_arg: Annotated[
        list[str] | None,
        typer.Option("--docker-arg", help="Append one raw docker-run argument; repeat for advanced cases."),
    ] = None,
) -> None:
    """Launch PyCharm through the translated Python launcher."""

    options = PycharmRunOptions(
        project=project,
        profile=profile,
        image=image,
        name=name,
        global_settings=global_settings,
        project_state=project_state,
        project_state_root=project_state_root,
        config_mode=resolve_config_mode(config_mode, ide_config, project_config, shared_config),
        ide_config=ide_config,
        project_mount=project_mount,
        plugins=plugins,
        use_ssh_agent=ssh_agent,
        git_user_name=git_user_name,
        git_user_email=git_user_email,
        git_identity_from_host=resolve_git_identity_mode(git_identity_from_host, no_git_identity_from_host),
        git_token_file=git_token_file,
        git_token_env=git_token_env,
        git_token_username=git_token_user,
        git_token_hosts=git_token_host,
        docker_mode=resolve_docker_mode(docker, docker_in_docker, no_docker),
        host_docker_socket=docker_socket,
        debug_native=debug_native,
        writable_root=writable_root,
        enable_sudo=dev_sudo,
        ignore_config_lock=ignore_config_lock,
        extra_docker_args=list(docker_arg or []),
    )
    try:
        raise typer.Exit(run_pycharm(options))
    except PycharmRunError as exc:
        raise click.ClickException(str(exc)) from exc


@build_app.command("pycharm", context_settings=FORWARD_CONTEXT)
def build_pycharm_command(ctx: typer.Context) -> None:
    """Build the current Dockerized PyCharm image through the compatibility script."""

    raise typer.Exit(run_script("docker4pycharm/build-image.sh", list(ctx.args)))


@check_runtime_app.command("pycharm", context_settings=FORWARD_CONTEXT)
def check_runtime_pycharm_command(ctx: typer.Context) -> None:
    """Run the current PyCharm runtime dependency check."""

    raise typer.Exit(run_script("docker4pycharm/check-runtime-deps.sh", list(ctx.args)))


@bootstrap_app.command("project", context_settings=FORWARD_CONTEXT)
def bootstrap_project_command(ctx: typer.Context) -> None:
    """Seed human/agent workflow files in a project."""

    raise typer.Exit(run_script("docker4pycharm/bootstrap-project.sh", list(ctx.args)))


@app.command("bootstrap-project", context_settings=FORWARD_CONTEXT, hidden=True)
def bootstrap_project_alias_command(ctx: typer.Context) -> None:
    """Compatibility alias for ``bootstrap project``."""

    raise typer.Exit(run_script("docker4pycharm/bootstrap-project.sh", list(ctx.args)))


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
    if ide_config is not None and (config_mode in {IdeConfigMode.shared, IdeConfigMode.project} or any(requested_shorthands)):
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
