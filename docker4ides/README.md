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

```bash
python3.12 -m venv .venv-dev
. .venv-dev/bin/activate
python -m pip install --upgrade pip
python -m pip install -r docker4ides/dev-requirements.txt
python -m pip install -e ./docker4ides --no-deps

python -m pytest docker4ides
```

Run the full local build gate:

```bash
cd docker4ides
python -m nox -s build
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
```

The archive contains the Python CLI and runtime dependencies. Commands that
delegate to sibling `docker4pycharm/` shell scripts still require a source
checkout.

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
