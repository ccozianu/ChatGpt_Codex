from __future__ import annotations

from pathlib import Path

from docker4ides.pycharm import DockerMode, IdeConfigMode, PycharmRunOptions, build_run_config


def base_env(tmp_path: Path) -> dict[str, str]:
    return {
        "DISPLAY": ":1",
        "HOME": str(tmp_path / "home"),
        "XDG_DATA_HOME": str(tmp_path / "data"),
        "PYCHARM_GIT_IDENTITY_FROM_HOST": "0",
    }


def test_ide_config_option_implies_custom_config_mode(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    custom_config = tmp_path / "custom-config"

    config = build_run_config(
        PycharmRunOptions(
            project=project,
            ide_config=custom_config,
            docker_mode=DockerMode.none,
        ),
        base_env(tmp_path),
    )

    assert config.ide_config_mode == "custom"
    assert config.ide_config == custom_config.resolve()


def test_explicit_shared_config_mode_ignores_env_ide_config_dir(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    env = base_env(tmp_path)
    env["PYCHARM_IDE_CONFIG_DIR"] = str(tmp_path / "env-config")

    config = build_run_config(
        PycharmRunOptions(
            project=project,
            config_mode=IdeConfigMode.shared,
            docker_mode=DockerMode.none,
        ),
        env,
    )

    assert config.ide_config_mode == "shared"
    assert config.ide_config == (tmp_path / "data" / "pycharm-docker" / "state" / "config").resolve()


def test_env_ide_config_dir_implies_custom_when_mode_is_unset(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    env = base_env(tmp_path)
    env["PYCHARM_IDE_CONFIG_DIR"] = str(tmp_path / "env-config")

    config = build_run_config(PycharmRunOptions(project=project, docker_mode=DockerMode.none), env)

    assert config.ide_config_mode == "custom"
    assert config.ide_config == (tmp_path / "env-config").resolve()
