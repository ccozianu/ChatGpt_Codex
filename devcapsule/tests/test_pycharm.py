from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import cast
from unittest.mock import patch

from devcapsule.configurations.pycharm import DockerMode, IdeConfigMode, PycharmRunOptions, build_run_config
from devcapsule.configurations.pycharm._launcher import (
    HostUser,
    PycharmRunConfig,
    TempRuntimeFiles,
    write_user_files,
)
from devcapsule.project import plan_project


def base_env(tmp_path: Path) -> dict[str, str]:
    return {
        "DISPLAY": ":1",
        "HOME": str(tmp_path / "home"),
        "XDG_DATA_HOME": str(tmp_path / "data"),
        "PYCHARM_GIT_IDENTITY_FROM_HOST": "0",
    }


def test_generated_passwd_home_matches_persistent_container_home(tmp_path: Path) -> None:
    files = TempRuntimeFiles(
        xauth_file=tmp_path / "xauth",
        passwd_file=tmp_path / "passwd",
        group_file=tmp_path / "group",
    )
    config = cast(PycharmRunConfig, SimpleNamespace(host_docker_gid=None, enable_sudo=False))

    with patch(
        "devcapsule.configurations.pycharm._launcher.current_host_user",
        return_value=HostUser(uid=1000, gid=1000, name="developer", group_name="developer"),
    ):
        write_user_files(config, files)

    assert "developer:x:1000:1000:PyCharm Docker User:/home/devcapsule:/bin/bash" in files.passwd_file.read_text()
    assert "/ide-global-settings/home" not in files.passwd_file.read_text()


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
    project_id = plan_project(project).project_id
    assert config.ide_config == (
        tmp_path / "data" / "devcapsule" / "projects" / "by-path" / project_id / "components" / "pycharm" / "config"
    ).resolve()


def test_env_ide_config_dir_implies_custom_when_mode_is_unset(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    env = base_env(tmp_path)
    env["PYCHARM_IDE_CONFIG_DIR"] = str(tmp_path / "env-config")

    config = build_run_config(PycharmRunOptions(project=project, docker_mode=DockerMode.none), env)

    assert config.ide_config_mode == "custom"
    assert config.ide_config == (tmp_path / "env-config").resolve()


def test_profile_sets_global_settings_and_plugins_defaults(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    env = base_env(tmp_path)
    env["XDG_CONFIG_HOME"] = str(tmp_path / "config")

    config = build_run_config(
        PycharmRunOptions(
            project=project,
            profile="codex",
            docker_mode=DockerMode.none,
        ),
        env,
    )

    profile_root = tmp_path / "config" / "docker-pycharm-codex"
    assert config.global_settings == (profile_root / "state").resolve()
    assert config.plugins == (profile_root / "plugins").resolve()


def test_project_state_root_mirrors_project_path_under_root_parent(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    project = workspace / "myProjects" / "example"
    project.mkdir(parents=True)

    config = build_run_config(
        PycharmRunOptions(
            project=project,
            project_state_root=workspace / ".state",
            docker_mode=DockerMode.none,
        ),
        base_env(tmp_path),
    )

    assert config.project_state == (workspace / ".state" / "myProjects" / "example").resolve()


def test_explicit_project_state_overrides_project_state_root(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    config = build_run_config(
        PycharmRunOptions(
            project=project,
            project_state=tmp_path / "explicit-state",
            project_state_root=tmp_path / ".state",
            docker_mode=DockerMode.none,
        ),
        base_env(tmp_path),
    )

    assert config.project_state == (tmp_path / "explicit-state").resolve()


def test_dogfood_legacy_roots_map_to_persistent_home_and_component_slots(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    global_settings = tmp_path / "docker-pycharm-codex" / "state"
    plugins = tmp_path / "docker-pycharm-codex" / "plugins"
    project_state = tmp_path / ".state" / "project"

    config = build_run_config(
        PycharmRunOptions(
            project=project,
            global_settings=global_settings,
            plugins=plugins,
            project_state=project_state,
            docker_mode=DockerMode.none,
        ),
        base_env(tmp_path),
    )

    assert config.persistent_home == (global_settings / "home").resolve()
    assert config.ide_config == (global_settings / "config").resolve()
    assert config.plugins == plugins.resolve()
    assert config.ide_system == (project_state / "system").resolve()
    assert config.ide_log == (project_state / "log").resolve()
    assert config.tool_cache == (project_state / "home" / ".cache").resolve()


def test_persistent_home_defaults_to_checkout_scoped_xdg_data(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    config = build_run_config(
        PycharmRunOptions(
            project=project,
            docker_mode=DockerMode.none,
        ),
        base_env(tmp_path),
    )

    project_id = plan_project(project).project_id
    assert config.persistent_home == (
        tmp_path / "data" / "devcapsule" / "projects" / "by-path" / project_id / "home"
    ).resolve()
