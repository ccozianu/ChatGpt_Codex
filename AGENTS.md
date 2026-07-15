# Agent Instructions

Before starting work in this repository, read the project brief at:

```text
README.md
```

Pay special attention to the final section of `README.md`, which records the current stage, current state, and planned next step. Then read any target-specific or handoff documents referenced there.

After reading the required documents, acknowledge to the user that you
understand what the project is about, including the requirements and
specification described in the brief.

Treat `REQUIREMENTS.md` as the overview/index for root requirements. Read the
specific detailed files under `docs/requirements/` only as needed for the task
you are working on.

If the brief defines a planned next step, state that next step to the user before proceeding.

If the brief does not define a planned next step, remind the user through the agent or IDE plugin to help choose the next step to work on.

At an appropriate moment, such as when completing a stage, changing the project state materially, or ending a session, do your best to update the final section of `README.md` so the next agent/model pair can resume from the then-current state.

The repository-level documentation index lives at:

```text
index.md
```

Whenever you add a new `.md` file, delete an existing `.md` file, or rename or
move a `.md` file, update `index.md` in the same change so it continues to list
all markdown documentation using relative links grouped by category.
