from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import patch

from docker4ides import cli


def test_top_level_help_returns_success(capsys) -> None:
    result = cli.main(["--help"])

    assert result == 0
    output = capsys.readouterr().out
    assert "run" in output
    assert "build" in output


def test_run_pycharm_uses_translated_python_launcher(tmp_path: Path) -> None:
    project = tmp_path / "example"
    project.mkdir()
    data_home = tmp_path / "data"

    with (
        patch("docker4ides.pycharm.shutil.which", return_value=None),
        patch("docker4ides.pycharm.subprocess.run") as run,
        patch.dict(
            os.environ,
            {
                "DISPLAY": ":1",
                "XDG_DATA_HOME": str(data_home),
                "PYCHARM_GIT_IDENTITY_FROM_HOST": "0",
            },
            clear=False,
        ),
    ):
        run.return_value.returncode = 0

        result = cli.main(["run", "pycharm", "--project", str(project), "--no-docker"])

    assert result == 0
    command = run.call_args.args[0]
    assert command[:2] == ["docker", "run"]
    assert "docker4pycharm/run-pycharm-container.sh" not in command[0]
    assert any(arg.startswith(f"type=bind,src={project.resolve()},dst=") for arg in command)
    assert "--cap-drop" in command
    assert "--read-only" in command


def test_run_pycharm_defaults_project_to_current_directory(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "current-project"
    project.mkdir()
    monkeypatch.chdir(project)

    with (
        patch("docker4ides.pycharm.shutil.which", return_value=None),
        patch("docker4ides.pycharm.subprocess.run") as run,
        patch.dict(
            os.environ,
            {
                "DISPLAY": ":1",
                "XDG_DATA_HOME": str(tmp_path / "data"),
                "PYCHARM_GIT_IDENTITY_FROM_HOST": "0",
            },
            clear=False,
        ),
    ):
        run.return_value.returncode = 0

        result = cli.main(["run", "pycharm", "--no-docker"])

    assert result == 0
    command = run.call_args.args[0]
    assert any(arg.startswith(f"type=bind,src={project.resolve()},dst=") for arg in command)


def test_run_pycharm_rejects_conflicting_config_mode_options(tmp_path: Path) -> None:
    project = tmp_path / "example"
    project.mkdir()

    result = cli.main(
        [
            "run",
            "pycharm",
            "--project",
            str(project),
            "--config-mode",
            "shared",
            "--ide-config",
            str(tmp_path / "custom-config"),
        ]
    )

    assert result == 2


def test_run_pycharm_rejects_multiple_config_shorthands(tmp_path: Path) -> None:
    project = tmp_path / "example"
    project.mkdir()

    result = cli.main(
        [
            "run",
            "pycharm",
            "--project",
            str(project),
            "--project-config",
            "--shared-config",
        ]
    )

    assert result == 2


def test_build_pycharm_delegates_to_current_script() -> None:
    with patch.object(cli.subprocess, "run") as run:
        run.return_value.returncode = 0

        result = cli.main(["build", "pycharm", "--pycharm", "/tmp/pycharm.tar.gz"])

    assert result == 0
    command = run.call_args.args[0]
    assert command[0].endswith("docker4pycharm/build-image.sh")
    assert command[1:] == ["--pycharm", "/tmp/pycharm.tar.gz"]


def test_runtime_check_pycharm_delegates_to_current_script() -> None:
    with patch.object(cli.subprocess, "run") as run:
        run.return_value.returncode = 0

        result = cli.main(["check", "runtime", "pycharm"])

    assert result == 0
    command = run.call_args.args[0]
    assert command[0].endswith("docker4pycharm/check-runtime-deps.sh")
    assert command[1:] == []


def test_bootstrap_project_delegates_to_current_script() -> None:
    with patch.object(cli.subprocess, "run") as run:
        run.return_value.returncode = 0

        result = cli.main(["bootstrap", "project", "--project", "/tmp/example"])

    assert result == 0
    command = run.call_args.args[0]
    assert command[0].endswith("docker4pycharm/bootstrap-project.sh")
    assert command[1:] == ["--project", "/tmp/example"]


def test_repo_root_can_be_overridden(tmp_path: Path) -> None:
    with patch.dict(os.environ, {"DOCKER4IDES_REPO_ROOT": str(tmp_path)}):
        assert cli.repo_root() == tmp_path.resolve()


def test_build_pex_script_is_available() -> None:
    script = Path(__file__).resolve().parents[1] / "scripts" / "build-pex.sh"

    assert script.exists()
    assert os.access(script, os.X_OK)

    completed = subprocess.run(
        [str(script), "--help"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 0
    assert "dist/docker4ides.pex" in completed.stdout
