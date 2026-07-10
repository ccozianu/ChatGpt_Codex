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

## Repository Scope

The older MVP requirements in this register were proven first by the
`docker4pycharm/` shell implementation. That subproject is now the historical
PyCharm reference baseline.

Current active development happens in `docker4ides/`, the Python CLI and
framework subproject. New requirements that describe the active user interface,
configuration protocol, packaging, tests, or additional IDE-plus-agent targets
should normally point to `docker4ides/` implementation and documentation unless
they are explicitly about preserving or validating the historical
`docker4pycharm/` baseline.

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
Status: manually validated

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

### R-DOCS-002: User-Level Documentation Coevolves With User-Visible Behavior

Statement: Any change to user-visible behavior must update the relevant
user-level documentation in the same change. User-visible behavior includes CLI
command names/order, options, defaults, setup paths, generated artifacts,
configuration aliases, validation expectations, and any change to host
exposure, credential flow, Docker access, devices, persistent state, or
runtime isolation.

Priority: current stabilization
Status: implemented

Implementation:
- User-level documentation protocol in `WORKFLOW.md`
- Current Docker4IDEs user documentation in `docker4ides/README.md`
- Project handoff and current-state notes in `README.md`

Validation:
- Future behavior changes should review `REQUIREMENTS.md`, the relevant
  user-level README, and the root README handoff together before closing.
- The build gate validates examples only where they are represented as CLI
  smoke tests; broader user-doc accuracy still requires review.

Related:
- `R-PROC-001`
- `R-PYTHON-MVP-003`

### R-IDE-CONFIG-001: Configuration-First End-User CLI Model

Statement: End users should interact with Docker4IDEs through a
configuration-first command model:

```text
docker4ides CONFIGURATION ACTION [options]
```

The configuration alias names an IDE-plus-agent environment, such as
`pycharm` or `vscode_with_claude`. Each configuration should expose only the
actions it supports. The common expected actions are `run` to launch the
environment and `build` to build or update its image. A configuration may
expose additional actions, such as PyCharm's current `check-runtime`, when
the action is meaningful for that configuration. Noun-first compatibility
paths such as `docker4ides run pycharm` are intentionally unsupported in the
Python CLI.

Priority: current stabilization
Status: implemented

Implementation:
- Configuration-first command examples in `docker4ides/README.md`
- Command adapters under `docker4ides/docker4ides/commands/`
- Configuration interfaces under `docker4ides/docker4ides/configurations/`

Validation:
- `docker4ides/tests/test_cli.py` covers top-level command discovery,
  `pycharm run`, `pycharm build`, `pycharm check-runtime`, rejection of
  noun-first PyCharm command order, and rejection of the removed
  `bootstrap-project` alias.
- `nox -s build` smoke-tests `python -m docker4ides --help`,
  `python -m docker4ides pycharm run --help`, PEX `--help`, and PEX
  `pycharm run --help`.

Related:
- `R-PYTHON-MVP-001`
- `R-PYTHON-MVP-002`
- `R-PYTHON-MVP-003`
- `R-FRAMEWORK-001`

### R-PYTHON-MVP-001: Source Checkout Install And Run

Statement: A developer on a vanilla Linux workstation with Docker, X11, and
Python 3.12+ must be able to check out the repository, create a local Python
environment, install `docker4ides` from source with an editable package-native
install, and invoke `python -m docker4ides` to launch PyCharm with the same
core behavior currently available through `docker4pycharm/run-pycharm-container.sh`.

Priority: current stabilization
Status: repo-validated

Implementation:
- Package metadata and dependency declarations: `docker4ides/pyproject.toml`
- Pinned runtime and contributor lock artifacts:
  `docker4ides/requirements.txt`, `docker4ides/dev-requirements.txt`
- Python CLI command tree and PyCharm launcher:
  `docker4ides/docker4ides/cli.py`, `docker4ides/docker4ides/pycharm.py`
- Python build gate: `docker4ides/noxfile.py`
- Source-checkout setup documentation: `docker4ides/README.md`

Validation:
- Future validation should confirm the documented source-checkout flow on a
  host workstation outside the current Ubuntu 24.04 IDE container.
- Repository-side validation should use a fresh virtual environment and run
  `python -m pip install -e ./docker4ides`, `python -m docker4ides --help`,
  `python -m pip install -e "./docker4ides[dev]"`, and
  `python -m pytest docker4ides`.
- On 2026-07-07, repository-side validation passed in a fresh temporary venv
  with `python -m pip install -e ./docker4ides`, `python -m docker4ides
  --help`, `python -m pip install -e "./docker4ides[dev]"`, and
  `python -m pytest docker4ides`.
- On 2026-07-08, `nox -s build` became the `docker4ides` project Python build gate,
  covering locked dependency install, editable install with `--no-deps`,
  Python compilation, shell syntax checks, pytest, CLI smoke tests, PEX build,
  and PEX smoke tests.

Related:
- `R-FRAMEWORK-001`

### R-PYTHON-MVP-002: Single-File Python CLI Artifact

Statement: Python MVP should provide an end-user distribution path that does
not require users to create a virtual environment or understand editable
installs. A release build should produce a single executable Python archive,
for example a PEX file, that runs on supported Linux hosts with Python 3.12+
and exposes the same `docker4ides` CLI entry point.

Priority: current stabilization
Status: manually validated

Implementation:
- PEX build script: `docker4ides/scripts/build-pex.sh`
- PEX build dependency in contributor tooling: `docker4ides/pyproject.toml`,
  `docker4ides/dev-requirements.txt`
- Packaged legacy PyCharm helper assets:
  `docker4ides/docker4ides/assets/docker4pycharm/`
- Python build gate: `docker4ides/noxfile.py`
- End-user artifact documentation: `docker4ides/README.md`
- The generated artifact is intentionally ignored under `docker4ides/dist/`.

Validation:
- On 2026-07-07, repository-side validation passed in a fresh temporary venv
  using the locked contributor setup. It installed
  `docker4ides/dev-requirements.txt`, installed `docker4ides` editable with
  `--no-deps`, built `docker4ides/dist/docker4ides.pex` with
  `PYTHON=<tmp-venv>/bin/python docker4ides/scripts/build-pex.sh`, ran
  `python3.12 docker4ides/dist/docker4ides.pex --help`, ran
  `python3.12 docker4ides/dist/docker4ides.pex run pycharm --help`, and passed
  `python -m pytest docker4ides`.
- On 2026-07-08, `nox -s build` passed `docker4ides` project validation and included
  the PEX build plus PEX smoke checks as part of the build gate.
- On 2026-07-08, the user confirmed host smoke validation passed for the
  PyCharm run path through the PEX artifact on the Ubuntu 22.04 workstation.
- On 2026-07-10, `pycharm build` was fixed for PEX execution by packaging the
  legacy PyCharm build helper, Dockerfile, entrypoint, runtime-check,
  bootstrap helper, and process-template assets inside the `docker4ides`
  package. A regression test covers running the build command when the source
  repository root is unavailable.
- On 2026-07-10, the user confirmed host smoke validation passed for the PEX
  build path by building a new `codex-debu-v012` PyCharm image from the PEX
  command line and launching this environment successfully.

Related:
- `R-PYTHON-MVP-001`
- `R-FRAMEWORK-001`

### R-PYTHON-MVP-003: Python MVP Feature Scope

Statement: The project should refine and settle the feature list for V1
(`python_mvp`). The scope should distinguish must-have Python MVP behavior from
deferred post-MVP framework work, especially around CLI ergonomics, profile
files, host validation, PEX distribution, compatibility wrappers, acceptable
user documentation, and one additional IDE-plus-agent proof point that shows
the framework makes sense beyond PyCharm.

Priority: current stabilization
Status: accepted

Implementation:
- Accepted V1 (`python_mvp`) scope:
  - Keep `docker4pycharm/` shell scripts as the stable compatibility and
    reference surface for the current PyCharm MVP.
  - Keep `docker4ides pycharm run` as the Python-native day-to-day launcher
    for PyCharm, with parity for the current documented launch surface:
    project path/default project selection, project mount planning, shared /
    project / custom config modes, named profiles, project-state roots,
    plugins/global settings paths, host Docker, no-Docker, Docker-in-Docker,
    SSH-agent forwarding, Git identity import/override, HTTPS Git token
    transport, dev sudo, native-debug mode, writable-root behavior, config lock
    preflight, and advanced raw Docker arguments.
  - Ensure supported PyCharm run behavior in the Python codebase no longer
    depends on `docker4pycharm` bootstrap scripts or other compatibility
    crutches. The old shell implementation may remain as a user-facing
    compatibility wrapper and reference surface, but not as the implementation
    path for Python `pycharm run`.
  - Provide both contributor and end-user invocation paths: editable source
    install, pinned contributor setup, Nox build gate, and local PEX artifact.
  - Build and test at least one additional IDE-plus-agent combination:
    VS Code plus Claude. This should demonstrate that the framework works
    beyond the original PyCharm prototype and provide a concrete model for how
    future users can create their own IDE/agent configuration.
  - Provide acceptable user documentation for the functionality exposed in
    V1 / `python_mvp`, including the supported command path, setup path,
    validation expectations, and the VS Code plus Claude configuration model.
  - Make the `docker4ides` Python project itself embody a lightweight
    good-enough engineering process by current project standards. V1 should not
    add heavyweight release machinery, but should close obvious quality-gate
    gaps such as the current lack of test coverage reporting or gating.
  - Preserve the current explicit-host-exposure rule: any new mount, credential
    path, device, Docker mode, or isolation relaxation must be represented by a
    clear option/default, README text, and requirement or implementation note.
  - Keep tests focused on behavior that can regress without a GUI: option
    conflict handling, path/state planning, generated Docker arguments,
    temporary runtime-file behavior, packaging/build commands, and CLI smoke
    checks. GUI launch remains manually validated on the host when needed.
- Explicit V1 deferrals:
  - General YAML/JSON profile loading and product-profile validation beyond
    the model needed for the V1 VS Code plus Claude proof point.
  - IntelliJ, VSCodium, and broader IDE-family adapters beyond the V1 VS Code
    plus Claude proof point.
  - Extension/plugin installation workflows beyond persistent plugin state.
  - Translating `pycharm build`, `pycharm check-runtime`, and
    `bootstrap project` away from shell-script delegation.
  - Formal release automation, artifact signing, checksums, or publishing.
  - Alternative GUI transports such as Wayland, xpra, VNC, or nested X servers.
  - GPU/device profiles, including NVIDIA/CUDA-oriented passthrough.
  - GitHub SSH/HTTPS remote push validation that was explicitly deferred from
    the PyCharm v0 stabilization pass.
- Likely implementation order:
  1. Audit Python `pycharm run` against the shell launcher and current docs,
     then add focused tests for any missing run-planning or Docker-argument
     parity.
  2. Tighten end-user PEX/source-install documentation around the accepted V1
     command path and validation expectations.
  3. Build and test the V1 VS Code plus Claude proof point, keeping the result
     small enough to act as a model for future user-defined configurations.
  4. Close any small PyCharm parity gaps found by that audit without broadening
     host exposure.
  5. Add or tighten lightweight quality gates for the `docker4ides` Python
     project itself, including coverage reporting/gating unless explicitly
     deferred with rationale.
  6. Re-run `nox -s build`, host PEX PyCharm launch smoke, and the documented
     VS Code plus Claude validation path before calling V1 complete.

Validation:
- The accepted V1 feature list, explicit deferrals, done criteria, and likely
  implementation order are recorded in this requirement.
- The README handoff should identify the next implementation task from this
  accepted V1 scope.

Related:
- `R-PYTHON-MVP-001`
- `R-PYTHON-MVP-002`
- `R-FRAMEWORK-001`

### R-FRAMEWORK-001: Shared Python Docker4IDE Orchestration

Statement: The post-MVP implementation should refactor one-off IDE launcher
logic into a shared Python `docker4ides` framework with reusable runtime
orchestration, profile loading, IDE-family adapters, and thin compatibility
wrappers for existing target-specific commands. Existing target-specific
scripts under `docker4pycharm/` should remain accessible as the stable
compatibility/reference surface, while `python -m docker4ides` becomes the
ergonomic CLI for day-to-day invocation and framework development.

Priority: current stabilization
Status: implemented

Implementation:
- Initial Python project skeleton and command tree:
  `docker4ides/pyproject.toml`, `docker4ides/docker4ides/cli.py`,
  `docker4ides/docker4ides/__main__.py`
- Translated PyCharm run launcher:
  `docker4ides/docker4ides/configurations/pycharm/`
- Package metadata and pinned pip/pip-compile lock artifacts:
  `docker4ides/pyproject.toml`, `docker4ides/requirements.txt`,
  `docker4ides/dev-requirements.txt`
- Build orchestration: `docker4ides/noxfile.py`
- Class-backed Click CLI command tree and option parsing:
  `docker4ides/docker4ides/cli.py`,
  `docker4ides/docker4ides/commands/`, `docker4ides/pyproject.toml`,
  `docker4ides/requirements.txt`
- Initial command and translated run-path tests: `docker4ides/tests/test_cli.py`
- First launcher planning helper slice:
  `docker4ides/docker4ides/project.py`, `docker4ides/tests/test_project.py`
- Shared runtime orchestration, profile loading, and IDE-family adapters are
  not yet fully extracted from the current PyCharm shell scripts.

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
- On 2026-07-05, project namespace calculation, default project mount
  generation, and reserved project-mount validation were represented in Python
  and covered by tests matching the current shell launcher expectations.
- On 2026-07-05, the `docker4ides run pycharm` path was corrected from a Bash
  argument-forwarding facade into a translated Python launcher that parses the
  PyCharm run options, plans state/config/plugin/project mounts, creates the
  temporary runtime files, generates Docker run arguments, and invokes
  `docker run` directly.
- On 2026-07-05, the hand-rolled CLI dispatcher and internal PyCharm
  `argparse` parser were replaced with a Typer/Click command tree. PyCharm
  config selection now uses explicit `--config-mode shared|project|custom`
  semantics and rejects conflicting config options instead of preserving
  Bash-style order-sensitive overrides.
- On 2026-07-07, `docker4ides run pycharm` gained an ergonomics slice: the
  project defaults to the current directory, `--profile NAME` groups shared
  PyCharm settings/plugins under `~/.config/docker-pycharm-NAME/`, and
  `--project-state-root DIR` mirrors per-project state under a separate state
  tree while preserving explicit `--project-state` override behavior.
- On 2026-07-07, the Python packaging contract was moved to `pyproject.toml`:
  Python 3.12+ is required, runtime dependencies are package metadata,
  contributor dependencies are available through the `dev` extra, and the
  pinned lock files are regenerated from `pyproject.toml` instead of duplicated
  `.in` files.
- On 2026-07-08, Nox was added as the Python-native build orchestration layer.
  `nox -s build` is the local `docker4ides` project build gate while `pyproject.toml`
  remains package metadata and `dev-requirements.txt` remains the pinned
  contributor dependency lock.
- On 2026-07-08, the central Typer command registry was replaced with
  class-backed Click commands discovered from `docker4ides.commands`; optional
  external plugin entry points were intentionally deferred. Validation passed
  with `.venv/bin/python -m pytest`, CLI/help smoke checks, compatibility help
  forwarding checks, and `.venv/bin/python -m nox -s build`.

Related:
- `docker4pycharm/FUTURE_AGENT_REFACTORING_BRIEF.md`
- Planned next work item in `README.md`
