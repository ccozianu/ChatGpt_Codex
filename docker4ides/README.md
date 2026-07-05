# Docker4IDEs Python CLI

`docker4ides` is the Python command layer for the post-MVP refactor. It uses
Typer/Click for the public command tree and option parsing. The `run pycharm`
path is being translated from the validated
`docker4pycharm/run-pycharm-container.sh` Bash launcher into maintainable Python
runtime planning and Docker invocation code. Compatibility wrappers remain for
commands that have not been translated yet.

## Development Setup

```bash
cd docker4ides
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r dev-requirements.txt -e .
```

Regenerate lock files after editing `.in` files:

```bash
python -m piptools compile --strip-extras requirements.in
python -m piptools compile --strip-extras dev-requirements.in
```

## Commands

```bash
python -m docker4ides --help
docker4ides run pycharm --project /path/to/project
docker4ides run pycharm --project /path/to/project --config-mode project
docker4ides build pycharm --pycharm /path/to/pycharm.tar.gz
docker4ides check runtime pycharm
docker4ides bootstrap project --project /path/to/project
```

Run tests:

```bash
python -m pytest
```
