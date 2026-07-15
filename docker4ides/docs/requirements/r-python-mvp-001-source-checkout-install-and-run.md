---
id: R-PYTHON-MVP-001
title: Source Checkout Install And Run
type: requirement
kind: concrete-requirement
status: repo-validated
priority: current stabilization
source_of_truth: repo
verification:
  - tests
  - smoke-tests
external_refs: []
---

# R-PYTHON-MVP-001: Source Checkout Install And Run

## Statement

A developer on a Linux workstation with Docker, X11, and Python 3.12+ must be
able to check out the repository, install `docker4ides` from source, and use
`python -m docker4ides` to launch PyCharm with the same core behavior currently
available through the historical shell launcher.

## Implementation

- `docker4ides/pyproject.toml`
- `docker4ides/requirements.txt`
- `docker4ides/dev-requirements.txt`
- `docker4ides/docker4ides/cli.py`
- `docker4ides/docker4ides/pycharm.py`
- `docker4ides/noxfile.py`
- `docker4ides/README.md`

## Verification

- 2026-07-07 fresh-venv repository-side validation passed
- 2026-07-08 `nox -s build` became the project build gate
- Additional host-workstation validation remains useful outside the current IDE
  container

## Related

- `R-FRAMEWORK-001`
