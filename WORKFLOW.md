# Human / Agent Iteration Workflow

This project treats markdown files in the repository as the durable memory for
human/agent work. Conversation is useful for speed, but project state must
survive model changes, IDE restarts, and future sessions.

## Core Loop

1. Start each session by reading the repository brief and its final handoff
   section.
2. Read `REQUIREMENTS.md` for the requirement overview when changing behavior,
   validation scope, or priorities, then open the relevant detailed files under
   `docs/requirements/` as needed.
3. Work from the active task list, not from stale conversation memory.
4. Keep each cycle narrow enough that the user can validate the result.
5. When the user validates something manually, update the handoff so the same
   task is not picked up again.
6. When an issue disappears or is deferred, remove it from the active task list
   and preserve the symptoms, logs, and reasoning in the completed-task archive.
7. Commit coherent units of work when asked, or at natural save points when the
   user wants the session state preserved.

## Turn-Level Choreography

Use each meaningful work cycle as a small contract between the human and the
agent.

1. Frame the slice.
   - The human states the goal, constraint, or uncertainty.
   - The agent restates the target outcome, relevant assumptions, and the next
     narrow slice it intends to execute.
2. Define closure before deep work.
   - State what "done for this slice" means.
   - State what evidence will count: test output, diff review, manual
     validation, or a documented decision.
3. Execute one narrow slice.
   - Prefer one coherent change over multiple partially finished ideas.
   - If the work uncovers a larger issue, record it and either finish the
     current slice or stop at a clear checkpoint.
4. Report with evidence.
   - Lead with the result.
   - Include only the evidence the human needs to evaluate the slice.
   - Separate "done", "not done", and "needs human input".
5. Decide the next branch explicitly.
   - Continue to the next slice.
   - Ask the human to validate or choose.
   - Stop and update the handoff because the session reached a useful checkpoint.

The goal is steady throughput, not long uninterrupted agent runs with vague
status.

## Slice Sizing Rules

Prefer slices that fit one of these shapes:

- one code path plus its direct tests;
- one documentation or workflow improvement plus the matching handoff update;
- one bug reproduction or diagnosis write-up;
- one manual-validation request with exact commands and expected observations;
- one decision that removes ambiguity for later implementation work.

Avoid slices that mix several of these unless the work is trivial. If a task is
too large to validate in one pass, split it before implementation.

## Human Input Contract

The human should provide, when relevant:

- the current priority or outcome to optimize for;
- risk tolerance, especially for host access, credentials, and security
  tradeoffs;
- manual validation results that only the human can observe;
- tie-break decisions when several defensible approaches remain.

The agent should ask for human input only when it materially changes the work
or when external validation is required. Otherwise, make the smallest reasonable
assumption, state it, and continue.

## Agent Reporting Contract

For each meaningful slice, the agent should report in this order:

1. Outcome.
2. Evidence.
3. Remaining gap or risk.
4. Recommended next slice.

Keep reports concise. The user should not need to reconstruct the state from a
long chronology.

## Decision And Escalation Rules

Escalate to the human when:

- a choice changes scope, architecture, or security posture materially;
- repository evidence is insufficient and several plausible interpretations
  remain;
- external state must change outside the agent's authority;
- the next slice would otherwise become speculative or broad.

Do not escalate merely because implementation is tedious or because several
small, compatible actions are possible.

## Checkpoint Triggers

Create or refresh durable state when any of these happen:

- a stage or subtask reaches a real closure point;
- manual validation changes project state;
- a new bug, decision, or requirement appears;
- the session ends with unfinished but resumable work;
- the active next step changes.

If the user and agent are moving quickly, prefer more frequent small handoff
updates over one large retrospective rewrite.

## Markdown Roles

Use markdown files with distinct responsibilities:

- `README.md`: project brief, current state, and the active next task list.
  The final section is the handoff point.
- `REQUIREMENTS.md`: implementation-agnostic requirement overview and index for
  project-level goals and concrete requirements.
- `docs/requirements/`: one markdown file per root requirement, with
  frontmatter metadata and canonical detailed requirement text.
- Subproject requirement overviews, such as `docker4ides/REQUIREMENTS.md`:
  implementation-specific requirement scope, status framing, and links to the
  canonical detailed requirement records for that subproject.
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
- Subproject implementation notes: strategy, decisions, retired issues,
  validation details, debugging history, and tradeoffs specific to one
  implementation path.

## Subproject Roles

Top-level documentation must keep the repository split clear:

- `docker4ides/` is the active Python CLI/framework subproject. New framework
  behavior, configuration protocol work, packaging, and tests should normally
  be implemented there.
- `docker4pycharm/` is the historical/reference PyCharm shell subproject. It
  remains useful as an operational baseline and comparison target, but current
  docs should not present it as the active development path unless the work is
  explicitly about preserving or validating the reference implementation.

When editing user-facing docs, avoid mixing these roles. Historical notes may
describe old commands, but current instructions should point users to
`docker4ides/` and the configuration-first CLI when describing active
development.

## Requirements Register

Use root `REQUIREMENTS.md` as the project-level overview and index for
requirements that should remain true across implementations. Use
`docs/requirements/` for the canonical detailed record of each root
requirement. Use subproject requirements files for implementation-specific
behavior, validation scope, and traceability.

The active task list says what to do next; the relevant requirements register
says why the task exists, how important it is, and how implementation and
validation map back to project intent.

Each root requirement record under `docs/requirements/` should have:

- A stable ID such as `R-CONC-001`.
- A short title.
- A type split: high-level goal or concrete requirement.
- A clear statement.
- Priority: `MVP`, `current stabilization`, or `later`.
- Status: `proposed`, `accepted`, `implemented`, `repo-validated`,
  `manually validated`, `deferred`, or `rejected`.
- Frontmatter metadata that stays easy to maintain in source control.
- Validation references or evaluation signals appropriate to the item type.
- Related tasks, bug records, decisions, or completed-task records.

Goals are evaluated by judgment and accumulated evidence. Concrete requirements
must be testable in principle, even if some verification is manual.

When a task, bug, or implementation note materially implements, validates,
changes, defers, rejects, or reinterprets a requirement, add a `Requirements:`
line with the relevant IDs. If no requirement exists yet, either add a proposed
requirement first or explicitly note that the work is exploratory.

Do not turn requirements files into a second active backlog. Requirements
should remain stable enough to help future sessions understand intent. The
active tasks in `README.md` remain the source of truth for immediate next work.

## User-Level Documentation Protocol

When changing behavior that an end user can observe or invoke, update the
user-level documentation in the same change as the code and requirement update.
Examples include command names, command order, options, defaults, generated
artifacts, setup steps, validation expectations, IDE configuration names, or
host-exposure behavior.

Use this documentation split:

- `REQUIREMENTS.md` records the requirement overview and links to the
  canonical detailed requirement files.
- Target user docs such as `docker4ides/README.md` describe how the user does
  it: installation path, command path, common examples, validation expectations,
  and current limitations.
- The root `README.md` final section records current state, recent changes, and
  next work for future agents.
- Implementation notes record design rationale, rejected alternatives, and
  evidence that would distract from user instructions.

For every user-visible change, check:

1. Is there an accepted or proposed requirement for the behavior?
2. Does the relevant user-level README show the supported command path and
   defaults?
3. Are unsupported or intentionally removed paths absent from current user docs?
4. If host exposure, credentials, devices, Docker access, or persistent state
   changed, is the isolation impact documented beside the option/default?
5. Does the handoff mention any manual validation still required?

Do not rely on historical notes as user documentation. Historical sections may
keep old command names when they describe what happened at that time, but
current user docs must show only the supported interface.

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

In practical terms:

- the human chooses the hill to climb;
- the agent chooses the next safe foothold;
- both should expect each slice to end in evidence or an explicit blocker.

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

When using a Dockerized IDE environment created by this project on another
repository, the same process should live inside that repository, not only
inside this DockerForIDEIsolation repo.

An environment may include a reusable bootstrap template at a documented path,
for example:

```text
/usr/local/share/docker4ide/vibe-coding-process.md
```

In the mounted project, ask the agent:

```text
Bootstrap the vibe-coding process documentation from
/usr/local/share/docker4ide/vibe-coding-process.md into this project.
Create or update AGENTS.md, README.md, REQUIREMENTS.md, docs/requirements/, and
implementation-notes/ as appropriate. Preserve existing project docs and adapt
the process to this repository.
```

At minimum, add or update these files in the target project:

```text
AGENTS.md
README.md
REQUIREMENTS.md
docs/requirements/
implementation-notes/
implementation-notes/bugs/
implementation-notes/completed-tasks/
```

The target project's `README.md` should end with a current-state and next-step
section. The target project's `REQUIREMENTS.md` should give an overview and
index of accepted requirements with stable IDs, while the canonical detailed
records live under `docs/requirements/`. The target project's `AGENTS.md`
should instruct agents to read the brief first, then any target-specific
handoff notes. Retired debugging details or important decisions should go under
that project's `implementation-notes/` folder. Active bug evidence should go
under `implementation-notes/bugs/`. Closed task records should go under
`implementation-notes/completed-tasks/`.

The Docker image and launcher provide the working environment. The mounted
project provides the source of truth for the work.
