# DevCapsule Python CLI

`devcapsule` is the Python command layer for the post-MVP refactor. It uses
Click for the public command tree and option parsing, with class-backed built-in
commands discovered from `devcapsule.commands`. The primary command shape is
configuration-first, for example `devcapsule pycharm run`. The `commands`
package is deliberately a thin CLI adapter; IDE-specific knowledge belongs in
configuration packages such as `devcapsule.configurations.pycharm`. The
PyCharm run path is being translated from the validated
`docker4pycharm/run-pycharm-container.sh` Bash launcher into maintainable Python
runtime planning and Docker invocation code.

Read [devcapsule/REQUIREMENTS.md](REQUIREMENTS.md) first for the subproject
requirement overview. The canonical detailed records for those requirements live
under `devcapsule/docs/requirements/`.

## User Setup

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ./devcapsule

python -m devcapsule --help
```

## Development Setup

Nox is the preferred developer cycle. By default this repository reuses Nox's
managed virtual environments between runs, so repeated commands avoid starting
from a completely fresh venv unless explicitly requested.

Run these commands from a Python environment where Nox is installed.

```bash
cd devcapsule

python -m nox -s tests   # Python compile checks plus pytest
python -m nox -s syntax  # Python compile checks plus shell syntax checks
python -m nox -s typecheck  # mypy for package, tests, and noxfile.py
python -m nox -s smoke   # source CLI and shell-wrapper help smoke tests
python -m nox -s pex     # build the PEX artifact and smoke-test it
python -m nox -s build   # full local gate
```

The `tests` session is the Nox way to run pytest for this project. It installs
the locked contributor dependencies into the managed Nox venv, installs
`devcapsule` editable with `--no-deps`, runs Python compile checks, then runs
`python -m pytest devcapsule`.

The `typecheck` session runs `mypy` across the `devcapsule` Python package,
tests, and `noxfile.py`.

The `build` session is the default Nox session, so these are equivalent:

```bash
cd devcapsule
python -m nox
python -m nox -s build
```

Run a clean-slate build when dependency or environment reuse could hide a
problem:

```bash
cd devcapsule
python -m nox --no-reuse-existing-virtualenvs -s build
```

If you want to discard all cached Nox environments before a clean build:

```bash
cd devcapsule
rm -rf .nox
python -m nox -s build
```

The manual virtualenv workflow is still supported when directly inspecting a
developer environment:

```bash
python3.12 -m venv .venv-dev
. .venv-dev/bin/activate
python -m pip install --upgrade pip
python -m pip install -r dev-requirements.txt
python -m pip install -e . --no-deps

python -m pytest devcapsule
```

The Nox build session installs the locked contributor dependencies, installs
`devcapsule` editable with `--no-deps`, compiles Python files, checks shell
script syntax, runs `mypy`, runs tests, smoke-tests the Python CLI and shell
wrapper help, builds the PEX artifact, and smoke-tests the PEX CLI.

`pyproject.toml` is the source of truth for Python runtime and development
dependencies. The pinned `requirements.txt` and `dev-requirements.txt` files
are reproducibility artifacts. Contributors should use the locked setup above;
the direct `python -m pip install -e "./devcapsule[dev]"` path remains useful
for quick local checks when exact dependency reproducibility is not needed.

Regenerate lock files after editing dependencies in `pyproject.toml`:

```bash
cd devcapsule
python -m piptools compile --strip-extras pyproject.toml --output-file requirements.txt
python -m piptools compile --strip-extras --extra dev pyproject.toml --output-file dev-requirements.txt
```

## End-User Artifact

Build a single-file PEX archive from a contributor environment:

```bash
cd devcapsule
scripts/build-pex.sh
```

For normal development, prefer the project build gate:

```bash
python -m nox -s pex
```

If the contributor environment is not activated, point the script at it:

```bash
PYTHON=/path/to/venv/bin/python devcapsule/scripts/build-pex.sh
```

Run the artifact with Python 3.12+:

```bash
python3.12 devcapsule/dist/devcapsule.pex --help
python3.12 devcapsule/dist/devcapsule.pex pycharm run --help
python3.12 devcapsule/dist/devcapsule.pex pycharm build --help
```

The archive contains the Python CLI, runtime dependencies, and the legacy
PyCharm build/runtime helper assets still needed by the current delegated
`pycharm build`, `pycharm check-runtime`, and `bootstrap project` commands.

The PEX build embeds `/tmp/devcapsule-pex-root` as its default runtime
extraction/cache root so it does not depend on IDE project-state cache
directories being writable. If the launch environment explicitly sets
`PEX_ROOT`, that value still controls PEX before DevCapsule starts; point it
at a writable directory or unset it if PEX warns about an unwritable cache.

## Commands

DevCapsule uses a configuration-first command model:

```text
devcapsule CONFIGURATION ACTION [options]
```

`CONFIGURATION` names an IDE-plus-agent environment. `pycharm` and
`codium_with_claude` are implemented configurations. The active public-default
image builds bundle pinned Node.js/npm plus the Gemini CLI as command-line
tooling. `codium_with_claude` is VSCodium plus that CLI/tooling baseline and
is distinct from the registered,
unimplemented `vscode_with_claude` placeholder.

End users should be able to:

- discover available configurations with `devcapsule --help`;
- build or update a configuration image when that configuration supports
  `build`;
- run a configuration against a selected project with `run`;
- pass configuration-specific options without exposing unrelated host state;
- use the same command shape from source installs and from the PEX artifact.

```bash
python -m devcapsule --help
devcapsule pycharm run --project /path/to/project
devcapsule pycharm run
devcapsule pycharm run --project /path/to/project --config-mode project
devcapsule pycharm run --profile codex --project-state-root /path/to/workspace/.state
devcapsule pycharm build --pycharm /path/to/pycharm.tar.gz
devcapsule pycharm check-runtime
devcapsule vscode_with_claude --help
devcapsule codium_with_claude build
devcapsule codium_with_claude build --ide-archive /path/to/VSCodium-linux-x64.tar.gz
devcapsule codium_with_claude run --project /path/to/project
devcapsule codium_with_claude run --project /path/to/project --profile codex
devcapsule codium_with_claude run --project /path/to/project --project-state-root /path/to/workspace/.state
devcapsule codium_with_claude run --project /path/to/project --project-mount /workspace/project
devcapsule codium_with_claude run --project /path/to/project --debug-shell
devcapsule codium_with_claude run --project /path/to/project --network host
devcapsule bootstrap project --project /path/to/project
```

`pycharm build` and `codium_with_claude build` use Ubuntu 24.04 and install
Python plus a pinned Node.js archive under `/opt/node/node-{version}`, expose
that runtime through `/opt/node/current` and `/usr/local/bin`, and install a
pinned Gemini CLI version with that bundled npm. The Codium image also installs
VSCodium plus `xterm` for basic X11 validation and `strace` for process-level
diagnostics. Update the pinned versions in source when intentionally advancing
the public-default tooling baseline. Use
`--image`, `--base-image`,
`--network`, and repeatable `--extra-apt-package` options to customize a build.
Pass `--ide-archive PATH` to install VSCodium from a local `.tar.gz` (or other
tar format recognized by Python) containing an executable `bin/codium`. In
that mode the build does not configure or contact the VSCodium apt repository;
the archive is installed under `/opt/codium`. The pinned Node.js archive and
Gemini CLI are still fetched during the image build from their configured
upstream sources.

`codium_with_claude run` currently targets Linux X11. It mounts the selected
project at `/workspace/project` by default, a persistent VSCodium/Claude home
(by default `~/.config/devcapsule/codium-with-claude`) at
`/ide-global-settings`, a project-local state directory (by default
`.devcapsule/codium-state`) at `/ide-project-state`, and the host X11 socket
read-only. `--profile NAME` moves the shared global state under
`~/.config/devcapsule-codium-with-claude-NAME/state`. `--project-state-root
DIR` mirrors per-project state outside the source tree, and `--project-mount`
overrides the in-container project path explicitly. It passes `DISPLAY` and
uses ordinary Docker bridge networking so VSCodium and Claude Code can reach
their services. It does not mount the Docker socket, SSH agent, host home,
devices, or other credentials by default. Claude authentication written under
its container home persists in the explicit global state directory. Gemini CLI
state is also bind-mounted directly from the host by default: the host
`~/.gemini` directory is exposed as `~/.gemini` inside the container so
existing Gemini authentication, settings, and trusted-folder state can be
reused across DevCapsule launches. Set `DEVCAPSULE_GEMINI_STATE_DIR` to point
at a different host directory when needed.
Use `--debug-shell` to run interactive Bash through the normal image
entrypoint with the same project, state, and X11 mounts instead of starting
VSCodium.
Use `--network MODE` to select an explicit Docker network mode for either the
normal IDE or `--debug-shell` path. The default remains Docker bridge
networking. `--network host` is useful for host-bound development services and
debugging, but shares the host network namespace and therefore weakens network
isolation.
Normal launches execute VSCodium's Electron binary directly so it remains the
foreground container process. They do not use the `bin/codium` CLI wrapper,
which detaches the GUI and exits before the IDE session ends.

The local-archive build path restores root ownership and mode `4755` on
VSCodium's Chromium sandbox helper after safe archive extraction strips the
setuid bit. This path and foreground launching were manually validated on
2026-07-13. Do not adopt `--no-sandbox` as a normal workaround. The evidence
and validation record are documented in
`implementation-notes/completed-tasks/2026-07-13-vscodium-sandbox-and-foreground-launch.md`.

Known parity gap: `codium_with_claude run` now shares `--profile`,
`--project-state-root`, and `--project-mount` with the common runtime-layout
model, but it still lacks many of the Git credential, Docker capability,
debugging, sudo, and additional filesystem options available from
`pycharm run`. The intended shared versus IDE-specific behavior is tracked in
`implementation-notes/bugs/2026-07-13-codium-run-option-parity.md`.

`pycharm run` defaults `--project` to the current directory. Use `--profile
NAME` to group shared PyCharm settings and plugins under
`~/.config/docker-pycharm-NAME/`, and `--project-state-root DIR` to mirror
per-project state under a separate state tree. Gemini CLI state is
bind-mounted into the container at `~/.gemini` from the host `~/.gemini` by
default; override that host source path with `DEVCAPSULE_GEMINI_STATE_DIR`
when needed.

Unsupported command shapes such as `devcapsule run pycharm`,
`devcapsule build pycharm`, and `devcapsule bootstrap-project` are
intentionally not part of the Python CLI.
