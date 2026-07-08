from __future__ import annotations

from pathlib import Path

import nox


nox.options.sessions = ["build"]
nox.options.default_venv_backend = "venv"

PROJECT_ROOT = Path(__file__).parent
REPO_ROOT = PROJECT_ROOT.parent
PEX_PATH = PROJECT_ROOT / "dist" / "docker4ides.pex"


def install_locked(session: nox.Session) -> None:
    session.install("-r", str(PROJECT_ROOT / "dev-requirements.txt"))
    session.install("-e", str(PROJECT_ROOT), "--no-deps")


def check_python_syntax(session: nox.Session) -> None:
    session.run("python", "-m", "compileall", "-q", str(PROJECT_ROOT / "docker4ides"))


def check_shell_syntax(session: nox.Session) -> None:
    scripts = [
        *sorted((REPO_ROOT / "docker4pycharm").glob("*.sh")),
        *sorted((PROJECT_ROOT / "scripts").glob("*.sh")),
    ]
    for script in scripts:
        session.run("bash", "-n", str(script), external=True)


def run_tests(session: nox.Session) -> None:
    session.run("python", "-m", "pytest", str(PROJECT_ROOT))


def run_smoke(session: nox.Session) -> None:
    session.run("python", "-m", "docker4ides", "--help")
    session.run("python", "-m", "docker4ides", "pycharm", "run", "--help")
    session.run("python", "-m", "docker4ides", "vscode_with_claude", "--help")
    session.run(str(REPO_ROOT / "docker4pycharm" / "run-pycharm-container.sh"), "--help", external=True)


def build_pex(session: nox.Session) -> None:
    session.run(
        str(PROJECT_ROOT / "scripts" / "build-pex.sh"),
        env={"PYTHON": "python"},
        external=True,
    )


def smoke_pex(session: nox.Session) -> None:
    session.run("python", str(PEX_PATH), "--help")
    session.run("python", str(PEX_PATH), "pycharm", "run", "--help")
    session.run("python", str(PEX_PATH), "vscode_with_claude", "--help")


@nox.session(python="3.12")
def syntax(session: nox.Session) -> None:
    install_locked(session)
    check_python_syntax(session)
    check_shell_syntax(session)


@nox.session(python="3.12")
def tests(session: nox.Session) -> None:
    install_locked(session)
    check_python_syntax(session)
    run_tests(session)


@nox.session(python="3.12")
def smoke(session: nox.Session) -> None:
    install_locked(session)
    run_smoke(session)


@nox.session(python="3.12")
def pex(session: nox.Session) -> None:
    install_locked(session)
    check_shell_syntax(session)
    build_pex(session)
    smoke_pex(session)


@nox.session(python="3.12")
def build(session: nox.Session) -> None:
    install_locked(session)
    check_python_syntax(session)
    check_shell_syntax(session)
    run_tests(session)
    run_smoke(session)
    build_pex(session)
    smoke_pex(session)
