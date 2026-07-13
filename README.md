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
- `docker4ides pycharm build` now uses a Python-owned `python-on-whales` /
  Docker buildx backend plus
  packaged PyCharm runtime assets under `docker4ides/`, instead of delegating
  image construction to `docker4pycharm/build-image.sh`.
- The accepted end-user CLI model is
  `docker4ides CONFIGURATION ACTION [options]`; noun-first paths such as
  `docker4ides run pycharm` are intentionally unsupported.
- `codium_with_claude` is the active next proof-point configuration. It is a
  distinct VSCodium plus Claude Code environment; the earlier
  `vscode_with_claude` placeholder remains separate.

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

Recent implementation fix:

- `docker4ides` PEX artifacts now package the legacy PyCharm helper assets
  needed by delegated `pycharm build`, `pycharm check-runtime`, and
  `bootstrap project` commands, so those commands no longer require a sibling
  source checkout at runtime.

Recent manual validation:

- On 2026-07-10, the user confirmed the rebuilt PEX path successfully built a
  new `codex-debug-v012` PyCharm image from the PEX command line and launched
  this environment successfully. Treat the PEX-packaged `pycharm build` fix as
  manually validated.
- On 2026-07-12, the user confirmed the Python-owned,
  `python-on-whales`-backed PyCharm image builder was built and launched
  successfully on the host. Its outstanding host-level validation is complete.

Current proof-point implementation:

- On 2026-07-12, implementation started for the user-selected
  `codium_with_claude` configuration. It composes an Ubuntu 24.04 image with
  VSCodium, Claude Code CLI, Python 3.12, and the current Node.js/npm release
  channels, plus an X11 launcher with explicit project and state mounts.
- This target intentionally does not reuse the registered
  `vscode_with_claude` stub. A local host-network build produced
  `codium-with-claude:latest` and container checks confirmed VSCodium
  1.126.04524, Python 3.12.3, Node.js 26.5.0, npm 12.0.1, and Claude Code
  2.1.207. GUI/X11 launch validation remains outstanding.
- A build-verified Vite, React, and TypeScript five-in-a-row project now lives
  under `docker4ides/tests/resources/sample_projects/` as a realistic manual
  IDE workload and a future end-to-end-test fixture.
- `codium_with_claude build` accepts `--ide-archive` for a local VSCodium tar
  archive, avoiding the VSCodium apt repository when that option is used.
- The Codium image development baseline now includes `xterm` for direct X11
  validation and `strace` for diagnosing silent process exits. A rebuilt image
  and host GUI launch still need manual validation.
- `codium_with_claude run --debug-shell` provides interactive Bash through the
  normal entrypoint with the same mounts and X11 environment for host-level
  diagnosis.
- Host debugging confirmed X11 with `xterm`, then traced the silent VSCodium
  exit to Chromium sandbox startup: Docker denies the user-namespace path and
  the archive-installed `/opt/codium/chrome-sandbox` has mode `0755` instead
  of the required root-owned `4755`. The active bug record is
  `docker4ides/implementation-notes/bugs/2026-07-13-vscodium-sandbox-silent-exit.md`.

Current architectural direction:

- On 2026-07-11, the user made Python-native, reusable image building the
  current priority. The supported `docker4ides` image-build path must stop
  delegating to or copying build implementation from `docker4pycharm`. The
  active Python package should own build planning and execution, with
  composable inputs for base images, IDEs, and AI-agent options.
- On 2026-07-12, the user selected a Docker CLI-backed Python backend for the
  active image-build path. `docker4ides` should use `python-on-whales` to drive
  local Docker buildx while keeping image planning, configuration composition,
  and CLI behavior in repository-owned Python code.
- `docker4pycharm/` remains useful as historical reference material, but it is
  not the implementation source for the target Python image-build path.

Current validation workflow:

- `docker4ides` uses Nox as the main developer validation entry point. Nox
  reuses its managed virtual environments by default for faster iteration.
  Use `cd docker4ides && python -m nox -s tests` for Python compile checks plus
  pytest, and `cd docker4ides && python -m nox -s build` for the full local
  gate: Python compile checks, shell syntax checks, pytest, CLI smoke tests,
  PEX build, and PEX smoke tests.
- When a clean slate is required, run
  `cd docker4ides && python -m nox --no-reuse-existing-virtualenvs -s build`.
  Removing `docker4ides/.nox/` before the command is also acceptable when
  deliberately discarding cached Nox environments.
- Prefer adding automated Nox-covered checks over relying on one-off manual
  smoke tests. Manual validation is still useful for host Docker/image/IDE
  behavior that cannot yet be exercised in repository automation.

Current task:

1. Add a real static typecheck gate for the `docker4ides` Python
   source tree. A recent minor issue in
   `docker4ides/docker4ides/configurations/pycharm/_image_build.py` should
   have been caught before runtime by `mypy`, `pyright`, or an equivalent
   checker, but the repository currently has no such gate. Define the chosen
   checker, add it to the contributor/dev workflow, wire it into Nox, and make
   sure source and PEX-affecting Python paths are covered.
   Requirements: `docker4ides/REQUIREMENTS.md` R-FRAMEWORK-001,
   R-PYTHON-MVP-003.
   This task is explicitly delayed at the user's request while the VSCodium
   proof point is implemented. Verification: add the typecheck command/session, run it cleanly on the
   current tree, and include it in `cd docker4ides && python -m nox -s build`
   or document an explicit short-term reason not to.

2. Finish and validate `codium_with_claude` as a distinct VSCodium plus Claude
   Code proof point. Confirm the image provides Python 3.12, current Node.js
   and npm, and Claude Code; then build and launch it on the host against a
   project. Keep its project, X11, persistent state, credentials, and network
   exposure explicit.
   Requirements: `docker4ides/REQUIREMENTS.md` R-IMAGE-BUILD-001,
   R-PYTHON-MVP-003, R-FRAMEWORK-001, R-SCOPE-001.
   Verification: run `cd docker4ides && python -m nox -s build`; manually run
   `docker4ides codium_with_claude build`, verify tool versions in the image,
   and run `docker4ides codium_with_claude run --project ...` on an X11 host.
   First fix and validate the root-owned `4755` VSCodium sandbox helper for the
   local-archive image path without making `--no-sandbox`, broad capabilities,
   or a relaxed seccomp profile part of the supported launcher.

Next task:

1. Complete host validation and any fixes for `codium_with_claude`, then return
   to the delayed static typecheck gate and shared IDE-configuration protocol.

Standing rule:

1. Keep any isolation relaxation explicit and documented.
   Requirements: `docker4ides/REQUIREMENTS.md` R-SCOPE-001, R-DOCKER-001 and
   root R-PRODUCT-002.
   Reopen if: a change adds host access, credentials, networking, devices, or
   filesystem mounts without matching documentation.
