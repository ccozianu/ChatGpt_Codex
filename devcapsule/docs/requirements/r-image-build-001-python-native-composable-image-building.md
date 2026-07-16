---
id: R-IMAGE-BUILD-001
title: Python-Native Composable Image Building
type: requirement
kind: concrete-requirement
status: accepted
priority: current stabilization
source_of_truth: repo
verification:
  - tests
  - manual
external_refs: []
---

# R-IMAGE-BUILD-001: Python-Native Composable Image Building

## Statement

Supported DevCapsule image builds must be planned and executed by the active
Python package without depending on the historical `docker4pycharm` build
implementation.

## Implementation

- Current delegated `pycharm build` behavior is transitional and should be
  replaced
- The shared build protocol should migrate PyCharm first
- Both editable-source and PEX invocation paths must remain supported

## Verification

- Add focused tests for build-plan composition, input validation, generated
  recipe/context, and Docker command construction
- Confirm source-install and PEX `pycharm build` work without invoking legacy
  build helpers
- Run `python -m nox -s build`
- Manually build and launch a PyCharm image through the PEX artifact on the
  host

## Related

- `R-PYTHON-MVP-002`
- `R-PYTHON-MVP-003`
- `R-FRAMEWORK-001`
- `R-SCOPE-001`
- `devcapsule/implementation-notes/completed-tasks/2026-07-13-vscodium-sandbox-and-foreground-launch.md`
