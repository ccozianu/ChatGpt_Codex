# Docker4IDEs Python CLI

`docker4ides` is the Python command layer for the post-MVP refactor. The first
slice is a compatibility facade over the current validated `docker4pycharm`
shell scripts; shared launcher planning and profile loading will move into this
package incrementally.

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
docker4ides build pycharm --pycharm /path/to/pycharm.tar.gz
docker4ides check runtime pycharm
docker4ides bootstrap project --project /path/to/project
```

Run tests:

```bash
python -m pytest
```
