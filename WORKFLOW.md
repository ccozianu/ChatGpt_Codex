# Human / Agent Iteration Workflow

This project treats markdown files in the repository as the durable memory for
human/agent work. Conversation is useful for speed, but project state must
survive model changes, IDE restarts, and future sessions.

## Core Loop

1. Start each session by reading the repository brief and its final handoff
   section.
2. Read the requirements register when changing behavior, validation scope, or
   priorities.
3. Work from the active task list, not from stale conversation memory.
4. Keep each cycle narrow enough that the user can validate the result.
5. When the user validates something manually, update the handoff so the same
   task is not picked up again.
6. When an issue disappears or is deferred, remove it from the active task list
   and preserve the symptoms, logs, and reasoning in the completed-task archive.
7. Commit coherent units of work when asked, or at natural save points when the
   user wants the session state preserved.

## Markdown Roles

Use markdown files with distinct responsibilities:

- `README.md`: project brief, requirements, current state, and the active next
  task list. The final section is the handoff point.
- `REQUIREMENTS.md`: the canonical requirements register. It gives stable IDs
  to requirements and records priority, status, implementation references,
  validation references, and related tasks or bugs.
- `AGENTS.md`: instructions every future agent should read before touching the
  repository.
- `implementation-notes/`: decisions, retired issues, validation details,
  debugging history, tradeoffs, and other context that should not clutter the
  active task list.
- `implementation-notes/bugs/`: one file per active or recently investigated
  bug, with symptoms, reproduction, evidence, hypotheses, verification target,
  and close criteria.
- `implementation-notes/completed-tasks/`: one file per completed, retired,
  manually validated, or no-longer-reproduced task. This is the retrospective
  archive.
- Target-specific docs such as `docker4pycharm/README.md`: operational usage
  for one subproject or runtime target.
- Larger future-direction docs such as `FUTURE_AGENT_REFACTORING_BRIEF.md`:
  strategy that is important but not part of the immediate active task list.

## Requirements Register

Use `REQUIREMENTS.md` to manage high-level and intermediate requirements. The
active task list says what to do next; the requirements register says why the
task exists, how important it is, and how implementation and validation map
back to project intent.

Each requirement should have:

- A stable ID such as `R-CONC-001`.
- A short title.
- A clear statement.
- Priority: `MVP`, `current stabilization`, or `later`.
- Status: `proposed`, `accepted`, `implemented`, `repo-validated`,
  `manually validated`, `deferred`, or `rejected`.
- Implementation references.
- Validation references.
- Related tasks, bug records, decisions, or completed-task records.

When a task, bug, or implementation note materially implements, validates,
changes, defers, rejects, or reinterprets a requirement, add a `Requirements:`
line with the relevant IDs. If no requirement exists yet, either add a proposed
requirement first or explicitly note that the work is exploratory.

Do not turn `REQUIREMENTS.md` into a second active backlog. Requirements should
remain stable enough to help future sessions understand intent. The active
tasks in `README.md` remain the source of truth for immediate next work.

## Active Task Format

Each active task should include enough closure detail that the next agent knows
when to remove it from the list:

```markdown
1. Task title.
   Requirements: R-...
   Done means: ...
   Verification: ...
   Reopen if: ...
```

Use a lighter form only for very small tasks. The important rule is that the
done condition and verification path should be explicit before work starts.

## Active Tasks Versus Historical Context

The active task list should contain only work that the next session should
actually consider doing.

## Bug Intake

Use `implementation-notes/bugs/` when a bug needs durable evidence before it is
fixed, retired, or converted into a completed task. Name files like:

```text
implementation-notes/bugs/YYYY-MM-DD-short-title.md
```

Each bug file should capture:

- Requirements, if the bug affects known requirements.
- Symptom.
- Environment: image, launcher command, project path or mount, host
  assumptions, and relevant versions.
- Reproduction: manual steps are acceptable when automation is not practical.
- Expected and actual behavior.
- Evidence: logs, stack traces, screenshots, commands, and timestamps.
- Current hypothesis, with uncertainty.
- Verification target: automated test, script/check, or manual validation.
- Fix notes and close criteria.

Do not include secrets. Keep detailed bug evidence in the bug file. The root
README active task list should only contain the next action, such as
investigating the bug, validating a fix, or adding a regression check.

When a task is completed, validated, no longer reproduced, or intentionally
retired:

1. Remove it from the active list.
2. Add a dated status note near the current-state section if future agents need
   to know why it disappeared.
3. Move detailed evidence into `implementation-notes/completed-tasks/`.
4. State when the task should be reopened, for example "only if a later image or
   launcher change regresses this path."

This keeps the next-session question "what should we do next?" unambiguous.

## Completed Task Archive

Use one markdown file per closed task:

```text
implementation-notes/completed-tasks/YYYY-MM-DD-short-task-name.md
```

Recommended structure:

```markdown
# Completed Task: ...

Date: ...

Status: completed | retired | manually validated | no longer reproduced

## Original Task

...

## Requirements

R-...

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
```

This folder is not a second active backlog. It is the evidence trail for
retrospective, debugging, and future comparison.

## Human And Agent Responsibilities

The human owns product direction, risk tolerance, code-quality judgment,
overall project-quality acceptance, manual validation in the GUI, and external
operations the container cannot perform, such as pushing without Git
credentials.

The agent owns repository inspection, implementation, documentation updates,
status hygiene, tests or static checks that can run in the current environment,
and commits when requested.

When the human reports a manual validation result, treat it as authoritative
project state and update markdown accordingly.

## Session Close Checklist

At the end of a meaningful session, update the handoff with:

```text
Changed:
- ...

Requirements:
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

Keep this concise. The goal is to make the next session start cleanly.

## Decision Notes

For decisions that may be revisited, use a small note under
`implementation-notes/`:

```markdown
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
```

## External State Register

Some state cannot or should not live in Git: credentials, GUI logins, local
image tags, manually built images, host firewall behavior, or services running
outside the container. Record these facts without secrets in the current-state
section or an implementation note.

## Git Hygiene

Before editing or committing:

1. Check `git status --short --untracked-files=all`.
2. Keep unrelated user or IDE changes out of commits unless they are clearly
   part of the requested save point.
3. Use one commit message that describes the saved state, not every small
   conversational step.
4. If pushing is blocked by missing user credentials, commit locally and let the
   human push externally.

## Applying This To Other Projects

When using the Dockerized PyCharm environment on a normal Python repository, the
same process should live inside that repository, not only inside this
DockerForIDEIsolation repo.

The PyCharm image should include a reusable bootstrap template at:

```text
/usr/local/share/docker4ide/vibe-coding-process.md
```

In the mounted project, ask the agent:

```text
Bootstrap the vibe-coding process documentation from
/usr/local/share/docker4ide/vibe-coding-process.md into this project.
Create or update AGENTS.md, README.md, REQUIREMENTS.md, and
implementation-notes/ as appropriate. Preserve existing project docs and adapt
the process to this repository.
```

At minimum, add or update these files in the target project:

```text
AGENTS.md
README.md
REQUIREMENTS.md
implementation-notes/
implementation-notes/bugs/
implementation-notes/completed-tasks/
```

The target project's `README.md` should end with a current-state and next-step
section. The target project's `REQUIREMENTS.md` should record accepted
requirements with stable IDs and map them to active tasks, bugs,
implementation, and validation evidence. The target project's `AGENTS.md`
should instruct agents to read the brief first, then any target-specific
handoff notes. Retired debugging details or important decisions should go under
that project's `implementation-notes/` folder. Active bug evidence should go
under `implementation-notes/bugs/`. Closed task records should go under
`implementation-notes/completed-tasks/`.

The Docker image and launcher provide the working environment. The mounted
project provides the source of truth for the work.
