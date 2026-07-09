# DockerForIDEIsolation

This repository explores a practical way to make development environments
reproducible, resumable, and explicit about host boundaries for both humans and
AI coding agents.

The long-term goal is a family of batteries-included development environments
that combine:

1. A real IDE or agentic editor for the target development domain.
2. The tools an AI coding agent needs to make progress inside that environment.
3. Persistent project memory: requirements, decisions, bugs, validation notes,
   and the current next step stored in the repository.
4. Reproducibility, portability, and clear host-exposure boundaries.

The development process used in this repository is part of the product idea.
Projects opened through these Dockerized IDE environments should be able to
carry the same kind of human/agent workflow documents, requirements register,
handoff notes, and implementation evidence if the user chooses that mode.

## Repository Shape

The root of the repository should stay implementation-agnostic. It should
explain the product goal, durable human/agent workflow, active handoff, and
documentation map without requiring the reader to distinguish old shell details
from current Python implementation details.

- `docker4ides/` is the active Python CLI/framework subproject. New framework
  code, current user-facing command behavior, packaging, tests, and
  configuration protocol work belong there.
- `docker4pycharm/` is the historical PyCharm shell implementation and
  reference baseline. It preserves the first working Dockerized PyCharm MVP,
  including the old root project brief and implementation notes.
- `docs/` contains implementation-agnostic product and positioning material.
- Root markdown files define project-level process, requirements, agent
  instructions, and the documentation index.

The current public command model for the active implementation is
configuration-first:

```text
docker4ides CONFIGURATION ACTION [options]
```

Examples:

```text
docker4ides pycharm run ...
docker4ides pycharm build ...
```

## Product Principles

- The selected project should be the primary mounted host filesystem surface.
- IDE state, plugins, runtime credentials, Docker access, devices, networking,
  and other host exposure should be explicit and documented.
- AI agents should have enough tools and durable context to work effectively
  without broad ambient access to the host.
- Project memory should live in versioned files, not only in chat history.
- Historical implementation notes are useful, but current user documentation
  should show only the supported interface.

## Documentation Map

Start with:

- `index.md` for the complete markdown documentation map.
- `AGENTS.md` for instructions future agents must follow before changing this
  repository.
- `WORKFLOW.md` for the human/agent iteration protocol.
- `REQUIREMENTS.md` for implementation-agnostic product and workflow
  requirements.
- `docker4ides/REQUIREMENTS.md` for active Python implementation requirements
  and traceability.
- `docker4ides/README.md` for active Python CLI usage.
- `docker4pycharm/README.md` for the historical PyCharm shell reference.

## Current State And Next Step

This section is the project handoff point. Future agents should update it when
completing a stage, changing the project state materially, or ending a session.

Current stage: `docker4pycharm` v0/MVP checkpoint complete; `docker4ides`
Python MVP is the active post-MVP refactoring stage.

Current status:

- `docker4pycharm/` preserves the original working PyCharm shell/Docker
  prototype, including historical design context now stored in
  `docker4pycharm/historical-root-README.md`.
- `docker4ides/` contains the active Python package, configuration-first CLI,
  distribution path, tests, and the PyCharm configuration package.
- The accepted end-user CLI model is
  `docker4ides CONFIGURATION ACTION [options]`; noun-first paths such as
  `docker4ides run pycharm` are intentionally unsupported.
- `vscode_with_claude` is the intended next proof-point configuration after
  the PyCharm run-path hardening work.

Recent documentation cleanup:

- Implementation-specific future refactoring history moved to
  `docker4pycharm/FUTURE_AGENT_REFACTORING_BRIEF.md`.
- PyCharm AI plugin setup moved to `docker4pycharm/user.md`.
- The Click command parsing brief moved to
  `docker4ides/implementation-notes/click_based_cli_parsing_brief.md`.
- Detailed Python/PyCharm implementation requirements moved to
  `docker4ides/REQUIREMENTS.md`.
- Root `README.md`, root markdown files, and top-level `docs/` are now meant to
  stay implementation-agnostic.

Current task:

1. Continue Python V1 hardening on the configuration-first command surface.
   Audit `docker4ides pycharm run` parity against the historical shell
   launcher, add focused tests for missing run-planning or Docker-argument
   behavior, verify the Python implementation no longer depends on
   `docker4pycharm` bootstrap crutches for supported run behavior, and keep
   cleanup within the accepted V1 scope.
   Requirements: `docker4ides/REQUIREMENTS.md` R-PYTHON-MVP-003,
   R-FRAMEWORK-001, R-SCOPE-001.
   Verification: run `cd docker4ides && python -m nox -s build`; review
   generated Docker arguments and docs together for changed mount, credential,
   device, or Docker access behavior.

Next task:

1. Define the small shared Python protocol for IDE configurations based on the
   documented end-user model, then make PyCharm and VS Code plus Claude conform
   to it before implementing VS Code plus Claude behavior.

Standing rule:

1. Keep any isolation relaxation explicit and documented.
   Requirements: `docker4ides/REQUIREMENTS.md` R-SCOPE-001, R-DOCKER-001 and
   root R-PRODUCT-002.
   Reopen if: a change adds host access, credentials, networking, devices, or
   filesystem mounts without matching documentation.
