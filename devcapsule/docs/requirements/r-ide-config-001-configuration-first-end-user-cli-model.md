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

End users should interact with DevCapsule through a configuration-first
command model:

```text
devcapsule CONFIGURATION ACTION [options]
```

Noun-first compatibility paths such as `devcapsule run pycharm` are
intentionally unsupported in the Python CLI.

## Implementation

- `devcapsule/README.md`
- `devcapsule/devcapsule/commands/`
- `devcapsule/devcapsule/configurations/`

## Verification

- `devcapsule/tests/test_cli.py`
- `nox -s build` smoke tests source and PEX help surfaces

## Related

- `R-PYTHON-MVP-001`
- `R-PYTHON-MVP-002`
- `R-PYTHON-MVP-003`
- `R-FRAMEWORK-001`
