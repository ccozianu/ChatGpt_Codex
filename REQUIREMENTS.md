# Project Requirements

This root register records implementation-agnostic project requirements. It
does not replace implementation-specific registers or notes inside subprojects.

Use this file for requirements that should remain true whether the concrete
implementation is the historical PyCharm shell prototype, the active Python
`docker4ides` framework, or a later implementation.

Implementation-specific requirements currently live in:

- `docker4ides/REQUIREMENTS.md` for the active Python CLI/framework and the
  PyCharm baseline requirements it is preserving.
- `docker4pycharm/implementation-notes/` for the historical PyCharm shell
  prototype decisions, validations, bugs, and completed tasks.

## Status Values

- `proposed`: captured, but not yet accepted as a project requirement.
- `accepted`: accepted, but not yet implemented.
- `implemented`: supporting docs, process, or implementation exist, but
  validation is incomplete.
- `validated`: accepted by repository review, static checks, tests, or manual
  project-owner validation.
- `deferred`: accepted direction, but intentionally outside the current target.
- `rejected`: considered and intentionally not pursued.

## Current Requirements

### R-PRODUCT-001: Batteries-Included IDE Environments

Statement: The project should produce development environments that include the
IDE/editor surface, common development tools, persistent comfort state, and
agent-ready project context needed for useful work without repeated local setup.

Status: accepted

Validation:
- A concrete implementation must document what is included, what remains
  external, and how a user verifies the environment is ready.

### R-PRODUCT-002: Explicit Host Boundaries

Statement: Host exposure must be explicit. Project mounts, IDE state,
credentials, Docker access, devices, networking, and other host integrations
must be represented by documented options or defaults.

Status: accepted

Validation:
- Any implementation change that broadens host access must update the relevant
  user documentation and implementation requirements in the same change.

### R-PRODUCT-003: Durable Human/Agent Project Memory

Statement: Important requirements, decisions, bugs, validation notes, handoff
state, and next steps should live in repository files rather than only in chat
history or local memory.

Status: implemented

Validation:
- Root workflow docs define the project-memory protocol.
- Subproject docs should record implementation evidence close to the
  implementation that produced it.

### R-PRODUCT-004: Reusable Human/Agent Workflow

Statement: The human/agent development workflow used to build this repository
should itself be available to users of Dockerized environments created by this
project when they choose that mode.

Status: accepted

Validation:
- Environment implementations should provide or document a way to seed a target
  project with agent instructions, requirements, handoff notes, bug records,
  and implementation-note structure.

### R-DOCS-001: Root Documentation Stays Implementation-Agnostic

Statement: Root markdown files and top-level `docs/` should describe project
purpose, product positioning, workflow, and current handoff without embedding
implementation-specific shell/Python/Docker details that belong to a
subproject.

Status: implemented

Validation:
- `index.md` should route implementation-specific readers to the relevant
  subproject.
- When moving, adding, deleting, or renaming markdown files, update `index.md`
  in the same change.

### R-DOCS-002: Current User Docs Show Current Interfaces

Statement: Current user-facing documentation must show the supported interface
for the active implementation and must not require readers to infer whether an
old command shape or historical note still applies.

Status: accepted

Validation:
- Historical documents may keep old command names when describing old behavior,
  but active user docs should point to supported commands only.
