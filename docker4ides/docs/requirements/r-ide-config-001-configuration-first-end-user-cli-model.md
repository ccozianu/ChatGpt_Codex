---
id: R-IDE-CONFIG-001
title: Configuration-First End-User CLI Model
type: requirement
kind: concrete-requirement
status: implemented
priority: current stabilization
source_of_truth: repo
verification:
  - tests
  - smoke-tests
external_refs: []
---

# R-IDE-CONFIG-001: Configuration-First End-User CLI Model

## Statement

End users should interact with Docker4IDEs through a configuration-first
command model:

```text
docker4ides CONFIGURATION ACTION [options]
```

Noun-first compatibility paths such as `docker4ides run pycharm` are
intentionally unsupported in the Python CLI.

## Implementation

- `docker4ides/README.md`
- `docker4ides/docker4ides/commands/`
- `docker4ides/docker4ides/configurations/`

## Verification

- `docker4ides/tests/test_cli.py`
- `nox -s build` smoke tests source and PEX help surfaces

## Related

- `R-PYTHON-MVP-001`
- `R-PYTHON-MVP-002`
- `R-PYTHON-MVP-003`
- `R-FRAMEWORK-001`
