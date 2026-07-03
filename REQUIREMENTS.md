# Requirements Register

This file is the project-level source of truth for accepted requirements. It
does not replace the active task list in `README.md`; it gives tasks, bugs, and
implementation notes stable requirement IDs to reference.

Use this register to answer:

- Which requirements exist?
- Which requirements are in the current stabilization target?
- Which requirements are implemented, validated, deferred, or rejected?
- Which code, docs, bug records, or validation notes support each requirement?

## Status Values

- `proposed`: captured, but not yet accepted as a project requirement.
- `accepted`: accepted, but not yet implemented.
- `implemented`: code or docs exist, but validation is incomplete.
- `repo-validated`: static checks, smoke tests, or automated checks passed.
- `manually validated`: the user or agent validated behavior in the running
  product.
- `deferred`: accepted direction, but intentionally outside the current target.
- `rejected`: considered and intentionally not pursued.

## Priority Bands

- `MVP`: required for the first useful Dockerized PyCharm workflow.
- `current stabilization`: required before closing the current v0 stabilization
  pass.
- `later`: useful, but not required for the current target.

## Requirement Template

```markdown
### R-AREA-000: Short Name

Statement: ...

Priority: MVP | current stabilization | later
Status: proposed | accepted | implemented | repo-validated | manually validated | deferred | rejected

Implementation:
- ...

Validation:
- ...

Related:
- ...
```

Every active task, bug, or completed-task record should include a
`Requirements:` line when it materially implements, validates, changes, defers,
or reinterprets a requirement.

## Current Requirements

### R-ENV-001: Dockerized PyCharm Runtime

Statement: PyCharm must run inside a Docker container while preserving enough of
the normal IDE experience for real development work.

Priority: MVP
Status: manually validated

Implementation:
- `docker4pycharm/Dockerfile`
- `docker4pycharm/run-pycharm-container.sh`
- `docker4pycharm/entrypoint.sh`

Validation:
- Current-state notes in `README.md`
- `docker4pycharm/debugging.md`

Related:
- `docker4pycharm/README.md`

### R-STATE-001: Persistent IDE State And Plugins

Statement: PyCharm settings, IDE-local home state, and installed plugins must
persist outside the image across container runs and image rebuilds. Shared
state must be separated from lock-bearing or project-specific runtime state
when the IDE vendor requires that split.

Priority: MVP
Status: implemented

Implementation:
- `docker4pycharm/run-pycharm-container.sh`
- `docker4pycharm/entrypoint.sh`
- `docker4pycharm/README.md`

Validation:
- Manual validation still depends on the specific state path and launch mode
  being tested.
- Shared `idea.config.path` concurrency is explicitly not required because
  JetBrains locks that directory while an IDE process is running.

Related:
- `docker4pycharm/implementation-notes/2026-06-21-per-project-ide-state-split.md`
- `docker4pycharm/implementation-notes/bugs/2026-06-24-concurrent-projects-shared-global-settings-lock.md`

### R-SETTINGS-001: Per-IDE Settings Profile Seed

Statement: A user should eventually be able to maintain a global settings
profile per IDE or IDE family, such as Python/PyCharm, and use that profile to
seed the initial settings for a newly launched containerized IDE project
without sharing the same live lock-bearing config directory.

Priority: later
Status: deferred

Implementation:
- Not implemented.

Validation:
- Future validation should confirm that a new project can be initialized from a
  selected settings profile while preserving per-project runtime isolation.

Related:
- Future development backlog in `README.md`
- `R-STATE-001`
- `R-CONC-001`

### R-SCOPE-001: Explicit Host Filesystem Exposure

Statement: The IDE container must not mount arbitrary host directories. Host
filesystem exposure should be limited to the selected project, IDE state,
plugins, and narrowly scoped runtime or credential resources.

Priority: MVP
Status: implemented

Implementation:
- `docker4pycharm/run-pycharm-container.sh`
- `README.md`
- `docker4pycharm/README.md`

Validation:
- Review launcher Docker arguments and docs together when changing mounts.

Related:
- Planned stabilization item: keep any isolation relaxation explicit and
  documented.

### R-DEV-001: Useful Development Tooling Baseline

Statement: The image must include common Linux development and debugging tools
so IDE-side agents can make progress without repeatedly stopping for missing
basic dependencies. Tools that require local privilege escalation, such as
`sudo`, must be present in the image but enabled through an explicit development
profile rather than silently weakening the default launcher posture.

Priority: MVP
Status: manually validated

Implementation:
- `docker4pycharm/Dockerfile`
- `docker4pycharm/run-pycharm-container.sh`
- `docker4pycharm/check-runtime-deps.sh`

Validation:
- Repository-side syntax, lint, and runtime-helper checks recorded in
  `README.md`
- The rebuilt image development baseline was manually accepted by the user on
  2026-06-28, including the wrapper-only fix for `--dev-sudo` account
  validation.

Related:
- `docker4pycharm/implementation-notes/2026-06-24-python-project-ux-defaults.md`
- `docker4pycharm/implementation-notes/2026-06-24-development-sudo-profile.md`
- `docker4pycharm/implementation-notes/completed-tasks/2026-06-28-dev-sudo-account-validation.md`

### R-GIT-001: Git Identity And Credentials Without Host Credential Mounts

Statement: Git author identity and remote access must work without mounting
host `~/.gitconfig`, host `~/.ssh`, or host credential directories into the
container.

Priority: current stabilization
Status: manually validated

Implementation:
- `docker4pycharm/run-pycharm-container.sh`
- `docker4pycharm/entrypoint.sh`
- `docker4pycharm/README.md`

Validation:
- On 2026-06-28, the user confirmed default host global Git `user.name` and
  `user.email` values are passed correctly from the host Git config into the
  launched container.
- On 2026-06-28, the user confirmed explicit `--git-user-name` and
  `--git-user-email` command arguments work as expected, with commits showing
  the intended author in `git log`.
- On 2026-06-28, the user confirmed the default identity behavior with
  `git config --global --get user.name`, `git config --global --get
  user.email`, and a local test commit whose author is correct in `git log`.
- On 2026-06-28, the user deferred live GitHub SSH and HTTPS remote validation
  until after the post-MVP refactoring. This is not a v0/MVP blocker because
  the user can push from outside the isolated IDE environment.
- On 2026-06-30, the user confirmed the remaining local identity edge cases:
  `--no-git-identity-from-host` disables host identity import, and explicit
  `--git-identity-from-host` warns clearly when host identity values are
  missing.

Related:
- `docker4pycharm/implementation-notes/2026-06-22-git-identity-and-credentials.md`
- `docker4pycharm/implementation-notes/completed-tasks/2026-06-28-git-remote-validation-deferred.md`
- `docker4pycharm/implementation-notes/completed-tasks/2026-06-30-local-git-identity-edge-validation.md`

### R-DOCKER-001: Explicit Docker Capability Profiles

Statement: Docker capability inside the IDE must be deliberate and documented:
default host Docker socket passthrough for v0 productivity, explicit true
Docker-in-Docker when isolated Docker state is needed, and explicit no-Docker
mode for higher isolation.

Priority: MVP
Status: implemented

Implementation:
- `docker4pycharm/run-pycharm-container.sh`
- `docker4pycharm/README.md`
- `README.md`

Validation:
- `docker4pycharm/implementation-notes/completed-tasks/2026-06-20-explicit-docker-in-docker-validation.md`
- `docker4pycharm/implementation-notes/completed-tasks/2026-06-20-default-host-docker-passthrough-validation-retired.md`

Related:
- `docker4pycharm/implementation-notes/docker-in-docker-immplementation-choice.md`

### R-PROJECT-001: Per-Project IDE Runtime State

Statement: Volatile project workspace state, caches, logs, and default
container project mount paths must be namespaced per selected host project so
opening one project does not restore stale workspace state from another.

Priority: MVP
Status: manually validated

Implementation:
- `docker4pycharm/run-pycharm-container.sh`
- `docker4pycharm/entrypoint.sh`
- `docker4pycharm/README.md`

Validation:
- Manual validation update in `README.md`

Related:
- `docker4pycharm/implementation-notes/2026-06-21-per-project-ide-state-split.md`

### R-CONC-001: Concurrent Project Sessions

Statement: Users should be able to run separate projects concurrently when
practical. If IDEA-family config locking prevents shared `idea.config.path`
from supporting concurrent processes, the launcher must fail before Docker
startup with a clear diagnostic and provide a documented per-project config
workaround.

Priority: current stabilization
Status: repo-validated

Implementation:
- `docker4pycharm/run-pycharm-container.sh`
- `docker4pycharm/entrypoint.sh`
- `docker4pycharm/README.md`

Validation:
- Repository-side lock preflight and path-selection smoke tests recorded in
  `docker4pycharm/implementation-notes/bugs/2026-06-24-concurrent-projects-shared-global-settings-lock.md`
- The user accepted the shared-config concurrency behavior as a documented
  PyCharm/IDEA-family limitation on 2026-06-24. Full GUI validation of a second
  live project with `--project-config` remains useful, but is no longer a
  blocker for the current stabilization task.

Related:
- `docker4pycharm/implementation-notes/bugs/2026-06-24-concurrent-projects-shared-global-settings-lock.md`

### R-PROC-001: Durable Human/Agent Project Memory

Statement: Project requirements, active tasks, bug evidence, decisions,
validation status, and handoff state must live in repository files rather than
only in conversation history.

Priority: MVP
Status: implemented

Implementation:
- `WORKFLOW.md`
- `REQUIREMENTS.md`
- `AGENTS.md`
- `docker4pycharm/image-assets/vibe-coding-process.md`
- `docker4pycharm/bootstrap-project.sh`

Validation:
- Future sessions should verify that active tasks and bug records cite
  requirement IDs where applicable.

Related:
- Current process update on 2026-06-24

### R-DOCS-001: Generated Documentation Index

Statement: The repository should eventually generate `index.md` from structured
markdown frontmatter so the documentation map stays consistent as files are
added, deleted, renamed, moved, or recategorized.

Priority: later
Status: accepted

Implementation:
- Current manual index: `index.md`
- Current maintenance instruction: `AGENTS.md`
- Future implementation should add frontmatter conventions and a repository
  script or test that regenerates and verifies `index.md`.

Validation:
- Future validation should confirm every `.md` file has the required
  frontmatter fields and that generated `index.md` matches the committed file.

Related:
- Future development backlog in `README.md`
- `R-PROC-001`

### R-FRAMEWORK-001: Shared Python Docker4IDE Orchestration

Statement: The post-MVP implementation should refactor one-off IDE launcher
logic into a shared Python `docker4ides` framework with reusable runtime
orchestration, profile loading, IDE-family adapters, and thin compatibility
wrappers for existing target-specific commands.

Priority: later
Status: accepted

Implementation:
- Initial Python project skeleton and compatibility command tree:
  `docker4ides/pyproject.toml`, `docker4ides/docker4ides/cli.py`,
  `docker4ides/docker4ides/__main__.py`
- Initial pip/pip-compile dependency files:
  `docker4ides/requirements.in`, `docker4ides/requirements.txt`,
  `docker4ides/dev-requirements.in`, `docker4ides/dev-requirements.txt`
- Initial command delegation tests: `docker4ides/tests/test_cli.py`
- Shared runtime orchestration, profile loading, and IDE-family adapters are
  not yet extracted from the current PyCharm shell scripts.

Validation:
- On 2026-07-03, a temporary venv installed
  `docker4ides/dev-requirements.txt` and `docker4ides` editable, then passed
  `python -m pytest docker4ides`.
- On 2026-07-03, `python -m docker4ides --help`,
  `docker4ides run --help`, `python -m docker4ides run pycharm --help`, and
  `docker4ides build pycharm --help` were smoke checked.
- Future validation should confirm the Python CLI and the current
  `docker4pycharm/run-pycharm-container.sh` compatibility wrapper produce
  equivalent generated Docker behavior as runtime planning moves into Python.

Related:
- `FUTURE_AGENT_REFACTORING_BRIEF.md`
- Planned next work item in `README.md`
