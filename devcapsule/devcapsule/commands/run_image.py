"""Expert local-image launcher for the PyCharm dogfood migration."""

from __future__ import annotations

from pathlib import Path

import click

from devcapsule.commands.base import BaseCommand
from devcapsule.configurations.pycharm import DockerMode, PycharmRunOptions, run_pycharm


class RunImageCommand(BaseCommand):
    """Run a local image through the first V1 persistence adapter."""

    image: str
    project: Path
    project_mount: str | None
    home: Path | None
    global_settings: Path | None
    plugins: Path | None
    project_state: Path | None
    docker_daemon: str
    development_sudo: bool
    container_name: str | None

    name = "run-image"
    help = (
        "Run a local PyCharm-compatible image without project lock resolution. "
        "This is the expert dogfood and image-construction path."
    )
    params = [
        click.Argument(["image"]),
        click.Option(
            ["--project", "-p"],
            type=click.Path(path_type=Path),
            default=Path("."),
            show_default=True,
        ),
        click.Option(
            ["--project-mount"],
            help="Absolute in-container project path; preserve the old path when adopting existing IDE state.",
        ),
        click.Option(["--home"], type=click.Path(path_type=Path)),
        click.Option(
            ["--global-settings"],
            type=click.Path(path_type=Path),
            help="Legacy root whose home/ and config/ directories are adopted in place.",
        ),
        click.Option(["--plugins"], type=click.Path(path_type=Path)),
        click.Option(
            ["--project-state"],
            type=click.Path(path_type=Path),
            help="Legacy root whose system/, log/, and home/.cache/ directories are adopted in place.",
        ),
        click.Option(
            ["--docker-daemon"],
            type=click.Choice(["none", "host-socket"]),
            default="none",
            show_default=True,
        ),
        click.Option(
            ["--development-sudo"],
            is_flag=True,
            help="Enable the existing explicit development-sudo profile for this run.",
        ),
        click.Option(["--name", "container_name"]),
    ]

    def run(self) -> int:
        docker_mode = DockerMode.host if self.docker_daemon == "host-socket" else DockerMode.none
        return run_pycharm(
            PycharmRunOptions(
                project=self.project,
                project_mount=self.project_mount,
                image=self.image,
                name=self.container_name,
                persistent_home=self.home,
                global_settings=self.global_settings,
                project_state=self.project_state,
                plugins=self.plugins,
                docker_mode=docker_mode,
                enable_sudo=self.development_sudo,
                extra_docker_args=["--pull=never"],
            )
        )


COMMAND = RunImageCommand
