from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import patch

from docker4ides import cli, compat
from docker4ides.configurations.vscode_with_claude import VscodeWithClaudeConfiguration


def test_top_level_help_returns_success(capsys) -> None:
    result = cli.main(["--help"])

    assert result == 0
    output = capsys.readouterr().out
    assert "pycharm" in output
    assert "vscode_with_claude" in output


def test_run_pycharm_uses_translated_python_launcher(tmp_path: Path) -> None:
    project = tmp_path / "example"
    project.mkdir()
    data_home = tmp_path / "data"

    with (
        patch("docker4ides.configurations.pycharm._launcher.shutil.which", return_value=None),
        patch("docker4ides.configurations.pycharm._launcher.subprocess.run") as run,
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

        result = cli.main(["pycharm", "run", "--project", str(project), "--no-docker"])

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
        patch("docker4ides.configurations.pycharm._launcher.shutil.which", return_value=None),
        patch("docker4ides.configurations.pycharm._launcher.subprocess.run") as run,
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

        result = cli.main(["pycharm", "run", "--no-docker"])

    assert result == 0
    command = run.call_args.args[0]
    assert any(arg.startswith(f"type=bind,src={project.resolve()},dst=") for arg in command)


def test_run_pycharm_rejects_conflicting_config_mode_options(tmp_path: Path) -> None:
    project = tmp_path / "example"
    project.mkdir()

    result = cli.main(
        [
            "pycharm",
            "run",
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
            "pycharm",
            "run",
            "--project",
            str(project),
            "--project-config",
            "--shared-config",
        ]
    )

    assert result == 2


def test_build_pycharm_delegates_to_current_script() -> None:
    with patch.object(compat.subprocess, "run") as run:
        run.return_value.returncode = 0

        result = cli.main(["pycharm", "build", "--pycharm", "/tmp/pycharm.tar.gz"])

    assert result == 0
    command = run.call_args.args[0]
    assert command[0].endswith("docker4pycharm/build-image.sh")
    assert command[1:] == ["--pycharm", "/tmp/pycharm.tar.gz"]


def test_build_pycharm_falls_back_to_packaged_assets(tmp_path: Path) -> None:
    missing_repo = tmp_path / "missing-repo"

    def run_compat_script(command: list[str], check: bool) -> subprocess.CompletedProcess[str]:
        script = Path(command[0])
        asset_root = script.parent

        assert check is False
        assert script.name == "build-image.sh"
        assert script.exists()
        assert os.access(script, os.X_OK)
        assert (asset_root / "Dockerfile").exists()
        assert (asset_root / "entrypoint.sh").exists()
        assert (asset_root / "bootstrap-project.sh").exists()
        assert (asset_root / "check-runtime-deps.sh").exists()
        assert (asset_root / "image-assets" / "vibe-coding-process.md").exists()

        return subprocess.CompletedProcess(command, 0)

    with (
        patch.dict(os.environ, {"DOCKER4IDES_REPO_ROOT": str(missing_repo)}),
        patch.object(compat.subprocess, "run", side_effect=run_compat_script),
    ):
        result = cli.main(["pycharm", "build", "--pycharm", "/tmp/pycharm.tar.gz"])

    assert result == 0


def test_runtime_check_pycharm_delegates_to_current_script() -> None:
    with patch.object(compat.subprocess, "run") as run:
        run.return_value.returncode = 0

        result = cli.main(["pycharm", "check-runtime"])

    assert result == 0
    command = run.call_args.args[0]
    assert command[0].endswith("docker4pycharm/check-runtime-deps.sh")
    assert command[1:] == []


def test_bootstrap_project_delegates_to_current_script() -> None:
    with patch.object(compat.subprocess, "run") as run:
        run.return_value.returncode = 0

        result = cli.main(["bootstrap", "project", "--project", "/tmp/example"])

    assert result == 0
    command = run.call_args.args[0]
    assert command[0].endswith("docker4pycharm/bootstrap-project.sh")
    assert command[1:] == ["--project", "/tmp/example"]


def test_repo_root_can_be_overridden(tmp_path: Path) -> None:
    with patch.dict(os.environ, {"DOCKER4IDES_REPO_ROOT": str(tmp_path)}):
        assert cli.repo_root() == tmp_path.resolve()


def test_top_level_commands_are_discovered() -> None:
    commands = cli.cli.list_commands(None)

    assert "bootstrap" in commands
    assert "pycharm" in commands
    assert "vscode_with_claude" in commands
    assert "bootstrap-project" not in commands
    assert "run" not in commands
    assert "build" not in commands
    assert "check" not in commands


def test_noun_first_pycharm_command_order_is_not_supported() -> None:
    assert cli.main(["run", "pycharm"]) == 2
    assert cli.main(["build", "pycharm"]) == 2
    assert cli.main(["check", "runtime", "pycharm"]) == 2


def test_bootstrap_project_alias_is_not_supported() -> None:
    assert cli.main(["bootstrap-project", "--project", "/tmp/example"]) == 2


def test_vscode_with_claude_configuration_is_registered(capsys) -> None:
    result = cli.main(["vscode_with_claude", "--help"])

    assert result == 0
    output = capsys.readouterr().out
    assert "run" in output
    assert "build" in output


def test_vscode_with_claude_configuration_identity() -> None:
    config = VscodeWithClaudeConfiguration()

    assert config.name == "vscode_with_claude"
    assert config.ide == "vscode"
    assert config.agent == "claude"
    assert not config.implemented


def test_vscode_with_claude_run_fails_explicitly(capsys) -> None:
    result = cli.main(["vscode_with_claude", "run"])

    assert result == 1
    assert "not implemented yet" in capsys.readouterr().err


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
