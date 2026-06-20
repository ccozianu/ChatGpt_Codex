# Using PyCharm v0 For Real Python Projects

This note describes how to reuse the current human/agent workflow on an
ordinary Python project while continuing to stabilize the `docker4pycharm` v0
environment in parallel.

## Current Working Image

Use the current debug image as the practical starting point:

```bash
./docker4pycharm/run-pycharm-container.sh \
  --image pycharm-isolated:codex-debug-v003 \
  --project /path/to/python-project \
  --ssh-agent
```

The launcher defaults to host Docker daemon passthrough. Use
`--docker-in-docker` only when isolated Docker state is needed, and use
`--no-docker` when the Python project does not need Docker access.

## Two Parallel Tracks

Track 1 is this repository:

```text
DockerForIDEIsolation
  -> stabilize and document the PyCharm container environment
```

Track 2 is the mounted Python project:

```text
ordinary-python-project
  -> use the containerized PyCharm/Codex environment to do normal project work
```

Do not mix the two sources of truth. This repository documents and evolves the
IDE environment. The mounted Python project should contain its own project
brief, active task list, implementation notes, and commits.

## Bootstrap Docs In The Python Project

Images built from this Dockerfile revision carry a reusable process bootstrap
template at:

```text
/usr/local/share/docker4ide/vibe-coding-process.md
```

If an existing `pycharm-isolated:codex-debug-v003` tag was built before this
change, rebuild or retag a newer image before relying on that path.

For a new or existing Python project, ask the agent in that launched IDE
environment:

```text
Bootstrap the vibe-coding process documentation from
/usr/local/share/docker4ide/vibe-coding-process.md into this project.
Create or update AGENTS.md, README.md, and implementation-notes/ as appropriate.
Preserve existing project docs and adapt the process to this repository.
```

The agent should create or update:

```text
AGENTS.md
README.md
implementation-notes/
implementation-notes/completed-tasks/
```

The template is only a seed. After bootstrapping, the mounted Python project is
the source of truth for its own process, current state, and next tasks.

Recommended `AGENTS.md` behavior:

```text
Before starting work in this repository, read README.md.
Pay special attention to the final current-state and next-step section.
Then read any target-specific or handoff documents referenced there.
After reading the required documents, acknowledge the project purpose,
requirements, current state, and planned next step before proceeding.
When completing a stage, retiring a task, or ending a session, update the final
section of README.md so the next session can resume cleanly.
```

Recommended final `README.md` section shape:

```markdown
## Current State And Next Step

Current stage: ...

Current status: ...

Important decisions:

- ...

When resuming, read these files in order:

1. `README.md`
2. `implementation-notes/...`

Planned next items:

1. ...
   Done means: ...
   Verification: ...
   Reopen if: ...
2. ...
```

Use `implementation-notes/` for:

- Chosen architecture and rejected alternatives.
- Manual validation results.
- External constraints such as credentials, services, datasets, or deployment
  targets.
- Command transcripts or log signatures that are too detailed for the active
  README handoff.

Use `implementation-notes/completed-tasks/` for one file per task that was
completed, manually validated, retired, or no longer reproduced. Each file
should capture original task, done criteria, verification, environment
provenance, retrospective notes, and reopen conditions.

Use decision notes under `implementation-notes/` for choices that may be
revisited. Keep active tasks, completed tasks, and decisions separate: active
tasks answer what to do next, completed tasks record what happened and how it
was validated, and decisions explain why a path was chosen.

Record external state without secrets. Useful examples include local image tags,
manual GUI login state, host services, credential transport assumptions, and
pushes that must be performed by the user.

## First Real-Project Session

A good first session in a Python repo is:

1. Read the target project's current docs.
2. Inspect packaging and test setup, for example `pyproject.toml`,
   `requirements*.txt`, `tox.ini`, `noxfile.py`, `pytest.ini`, and CI config.
3. Run the cheapest available verification command.
4. Record the real project state and next useful task in the target
   `README.md`.
5. Start a narrow implementation task only after the active task list is clear.

## Practical Notes

- If the Python project needs GitHub access, prefer `--ssh-agent` or an explicit
  token secret. Do not mount host `~/.ssh`.
- If the project uses Docker for tests or services, the default host Docker
  passthrough gives convenient local behavior but broad host Docker control.
- If the project has sensitive files outside its repository root, do not mount
  those directories casually. Add explicit launcher support or documented
  secret handling instead.
- Keep commits scoped to the mounted Python project when working on that
  project, and scoped to DockerForIDEIsolation when working on the environment.
