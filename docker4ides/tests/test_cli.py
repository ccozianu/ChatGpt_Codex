from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from docker4ides import cli


def test_top_level_help_returns_success(capsys) -> None:
    result = cli.main(["--help"])

    assert result == 0
    assert "run pycharm" in capsys.readouterr().out


def test_run_pycharm_delegates_to_current_script() -> None:
    with patch.object(cli.subprocess, "run") as run:
        run.return_value.returncode = 0

        result = cli.main(["run", "pycharm", "--project", "/tmp/example"])

    assert result == 0
    command = run.call_args.args[0]
    assert command[0].endswith("docker4pycharm/run-pycharm-container.sh")
    assert command[1:] == ["--project", "/tmp/example"]


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
