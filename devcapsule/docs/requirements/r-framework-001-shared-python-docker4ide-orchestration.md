---
id: R-FRAMEWORK-001
title: Shared Python Docker4IDE Orchestration
type: requirement
kind: high-level-goal
status: implemented
priority: current stabilization
source_of_truth: repo
verification:
  - repo-inspection
  - tests
external_refs: []
---

# R-FRAMEWORK-001: Shared Python Docker4IDE Orchestration

## Statement

The post-MVP implementation should refactor one-off IDE launcher logic into a
shared Python `docker4ides` framework with reusable runtime orchestration,
profile loading, IDE-family adapters, and thin compatibility wrappers.

## Implementation

- `docker4ides/pyproject.toml`
- `docker4ides/docker4ides/cli.py`
- `docker4ides/docker4ides/__main__.py`
- `docker4ides/docker4ides/configurations/pycharm/`
- `docker4ides/noxfile.py`
- `docker4ides/docker4ides/commands/`
- `docker4ides/tests/test_cli.py`
- `docker4ides/docker4ides/project.py`
- `docker4ides/tests/test_project.py`

## Verification Or Evaluation

- 2026-07-03 initial editable-install and pytest validation passed
- 2026-07-05 translated Python `pycharm run` path replaced Bash forwarding
- 2026-07-05 Click/Typer command-tree migration validated
- 2026-07-07 ergonomics and packaging-contract slices validated
- 2026-07-08 Nox build orchestration and class-backed Click discovery
  validated

## Related

- `docker4pycharm/FUTURE_AGENT_REFACTORING_BRIEF.md`
- root `README.md`
