# Vibe-Coding Process Bootstrap

This file is a reusable bootstrap template baked into the Dockerized IDE image.
It is not the target project's source of truth. Use it to create or update the
target project's own process documentation.

Expected image path:

```text
/usr/local/share/docker4ide/vibe-coding-process.md
```

## User Prompt

When starting work in a project that does not already have this process
documented, the user can ask:

```text
Bootstrap the vibe-coding process documentation from
/usr/local/share/docker4ide/vibe-coding-process.md into this project.
Create or update AGENTS.md, README.md, and implementation-notes/ as appropriate.
Preserve existing project docs and adapt the process to this repository.
```

## Agent Instructions

If you are the agent receiving that prompt:

1. Inspect the current repository before editing.
2. Preserve existing project documentation and conventions.
3. Create or update `AGENTS.md` so future agents read the project brief first.
4. Ensure `README.md` contains or links to the project purpose, requirements,
   current state, and active next task list.
5. Create `implementation-notes/` if the project does not already have a better
   equivalent.
6. Create `implementation-notes/completed-tasks/` for closed task records.
7. Add a short process note under `implementation-notes/` if useful, but do not
   duplicate large boilerplate into multiple places.
8. Keep active tasks separate from historical context.
9. Add explicit done criteria and verification notes for active tasks.
10. Run a cheap validation check if available.
11. Report exactly what changed and what remains uncommitted.

## Recommended AGENTS.md

Adapt this to the target project:

````markdown
# Agent Instructions

Before starting work in this repository, read the project brief at:

```text
README.md
```

Pay special attention to the final current-state and next-step section. Then
read any target-specific or handoff documents referenced there.

After reading the required documents, acknowledge that you understand the
project purpose, requirements, current state, and planned next step before
proceeding.

If the brief defines a planned next step, state that next step to the user
before proceeding.

If the brief does not define a planned next step, ask the user to choose the
next step to work on.

When completing a stage, retiring a task, changing project state materially, or
ending a session, update the final section of `README.md` so the next
agent/model pair can resume from the current state.
````

If the target project already has an `AGENTS.md`, merge these instructions
without deleting project-specific constraints.

## Recommended README.md Handoff Section

Add or adapt this near the end of `README.md`:

````markdown
## Current State And Next Step

This section is the project handoff point. Future agents should update it when
completing a stage, changing the project state materially, retiring a task, or
ending a session.

Current stage: ...

Current status: ...

Important decisions:

- ...

Retired or historical issues:

- ...

When resuming the project, read these files in order:

1. `README.md`
2. `implementation-notes/...`

Planned next items:

1. ...
   Done means: ...
   Verification: ...
   Reopen if: ...
2. ...
````

The active next-task list should contain only tasks the next agent should
actually consider doing.

## Recommended implementation-notes/ Use

Use `implementation-notes/` for details that matter but should not stay in the
active task list:

- Architecture decisions and rejected alternatives.
- Manual validation results.
- Retired bugs that may recur.
- Log signatures and command transcripts.
- External constraints such as credentials, services, datasets, deployment
  targets, or host setup.
- Risk and security notes.

Use `implementation-notes/completed-tasks/` for one file per task that was
completed, manually validated, retired, or no longer reproduced.

When a task is completed, manually validated, no longer reproduced, or
intentionally deferred:

1. Remove it from the active task list.
2. Add a dated status note if future agents need to know why it disappeared.
3. Preserve useful evidence in `implementation-notes/completed-tasks/`.
4. State when the task should be reopened.

Recommended completed-task file:

````markdown
# Completed Task: ...

Date: ...

Status: completed | retired | manually validated | no longer reproduced

## Original Task

...

## Done Means

...

## Verification

...

## Environment Provenance

- Image: ...
- Launcher mode: ...
- Project mount: ...
- Important host-side assumptions: ...

## Retrospective Notes

...

## Reopen If

...
````

## Session Close Checklist

At the end of a meaningful session, update the project handoff with:

```text
Changed:
- ...

Validated:
- ...

Not validated:
- ...

External state:
- ...

Uncommitted changes:
- ...

Next task:
- ...
```

Record external state without secrets. Useful examples include local image tags,
manual GUI login state, host services, credentials being available only through
an agent or secret file, and pushes that must be performed by the user.

## Decision Notes

For decisions that may be revisited, create a small note under
`implementation-notes/`:

````markdown
# Decision: ...

Date: ...

Context:
...

Options:
...

Decision:
...

Consequences:
...

Reopen if:
...
````

Keep active tasks, completed tasks, and decisions separate. Active tasks answer
"what should we do next?", completed tasks answer "what happened and how was it
validated?", and decisions answer "why did we choose this path?".

## First Pass In A Python Project

For a normal Python repository, a good first pass is:

1. Inspect `README.md`, `pyproject.toml`, `requirements*.txt`, `tox.ini`,
   `noxfile.py`, `pytest.ini`, and CI config if present.
2. Identify the cheapest reliable validation command.
3. Record the current state and next useful task in `README.md`.
4. Start implementation only after the active task list is clear.

## Git Hygiene

Before committing:

1. Run `git status --short --untracked-files=all`.
2. Keep unrelated user or IDE changes out of the commit.
3. Commit coherent units of work with a message that describes the saved state.
4. If pushing is blocked by missing user credentials, commit locally and let the
   user push externally.
