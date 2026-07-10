# Docker4IDEs Python CLI

`docker4ides` is the Python command layer for the post-MVP refactor. It uses
Click for the public command tree and option parsing, with class-backed built-in
commands discovered from `docker4ides.commands`. The primary command shape is
configuration-first, for example `docker4ides pycharm run`. The `commands`
package is deliberately a thin CLI adapter; IDE-specific knowledge belongs in
configuration packages such as `docker4ides.configurations.pycharm`. The
PyCharm run path is being translated from the validated
`docker4pycharm/run-pycharm-container.sh` Bash launcher into maintainable Python
runtime planning and Docker invocation code.

## User Setup

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ./docker4ides

python -m docker4ides --help
```

## Development Setup

Nox is the preferred developer cycle. By default this repository reuses Nox's
managed virtual environments between runs, so repeated commands avoid starting
from a completely fresh venv unless explicitly requested.

Run these commands from a Python environment where Nox is installed.

```bash
cd docker4ides

python -m nox -s tests   # Python compile checks plus pytest
python -m nox -s syntax  # Python compile checks plus shell syntax checks
python -m nox -s smoke   # source CLI and shell-wrapper help smoke tests
python -m nox -s pex     # build the PEX artifact and smoke-test it
python -m nox -s build   # full local gate
```

The `tests` session is the Nox way to run pytest for this project. It installs
the locked contributor dependencies into the managed Nox venv, installs
`docker4ides` editable with `--no-deps`, runs Python compile checks, then runs
`python -m pytest docker4ides`.

The `build` session is the default Nox session, so these are equivalent:

```bash
cd docker4ides
python -m nox
python -m nox -s build
```

Run a clean-slate build when dependency or environment reuse could hide a
problem:

```bash
cd docker4ides
python -m nox --no-reuse-existing-virtualenvs -s build
```

If you want to discard all cached Nox environments before a clean build:

```bash
cd docker4ides
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

python -m pytest docker4ides
```

The Nox build session installs the locked contributor dependencies, installs
`docker4ides` editable with `--no-deps`, compiles Python files, checks shell
script syntax, runs tests, smoke-tests the Python CLI and shell wrapper help,
builds the PEX artifact, and smoke-tests the PEX CLI.

`pyproject.toml` is the source of truth for Python runtime and development
dependencies. The pinned `requirements.txt` and `dev-requirements.txt` files
are reproducibility artifacts. Contributors should use the locked setup above;
the direct `python -m pip install -e "./docker4ides[dev]"` path remains useful
for quick local checks when exact dependency reproducibility is not needed.

Regenerate lock files after editing dependencies in `pyproject.toml`:

```bash
cd docker4ides
python -m piptools compile --strip-extras pyproject.toml --output-file requirements.txt
python -m piptools compile --strip-extras --extra dev pyproject.toml --output-file dev-requirements.txt
```

## End-User Artifact

Build a single-file PEX archive from a contributor environment:

```bash
cd docker4ides
scripts/build-pex.sh
```

For normal development, prefer the project build gate:

```bash
python -m nox -s pex
```

If the contributor environment is not activated, point the script at it:

```bash
PYTHON=/path/to/venv/bin/python docker4ides/scripts/build-pex.sh
```

Run the artifact with Python 3.12+:

```bash
python3.12 docker4ides/dist/docker4ides.pex --help
python3.12 docker4ides/dist/docker4ides.pex pycharm run --help
python3.12 docker4ides/dist/docker4ides.pex pycharm build --help
```

The archive contains the Python CLI, runtime dependencies, and the legacy
PyCharm build/runtime helper assets still needed by the current delegated
`pycharm build`, `pycharm check-runtime`, and `bootstrap project` commands.

The PEX build embeds `/tmp/docker4ides-pex-root` as its default runtime
extraction/cache root so it does not depend on IDE project-state cache
directories being writable. If the launch environment explicitly sets
`PEX_ROOT`, that value still controls PEX before Docker4IDEs starts; point it
at a writable directory or unset it if PEX warns about an unwritable cache.

## Commands

Docker4IDEs uses a configuration-first command model:

```text
docker4ides CONFIGURATION ACTION [options]
```

`CONFIGURATION` names an IDE-plus-agent environment. `pycharm` is the current
implemented configuration. `vscode_with_claude` is registered as the next V1
proof point, but its image and launcher are not implemented yet.

End users should be able to:

- discover available configurations with `docker4ides --help`;
- build or update a configuration image when that configuration supports
  `build`;
- run a configuration against a selected project with `run`;
- pass configuration-specific options without exposing unrelated host state;
- use the same command shape from source installs and from the PEX artifact.

```bash
python -m docker4ides --help
docker4ides pycharm run --project /path/to/project
docker4ides pycharm run
docker4ides pycharm run --project /path/to/project --config-mode project
docker4ides pycharm run --profile codex --project-state-root /path/to/workspace/.state
docker4ides pycharm build --pycharm /path/to/pycharm.tar.gz
docker4ides pycharm check-runtime
docker4ides vscode_with_claude --help
docker4ides bootstrap project --project /path/to/project
```

`pycharm run` defaults `--project` to the current directory. Use `--profile
NAME` to group shared PyCharm settings and plugins under
`~/.config/docker-pycharm-NAME/`, and `--project-state-root DIR` to mirror
per-project state under a separate state tree.

Unsupported command shapes such as `docker4ides run pycharm`,
`docker4ides build pycharm`, and `docker4ides bootstrap-project` are
intentionally not part of the Python CLI.
