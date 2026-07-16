---
id: D-0001
title: Capability-First CLI Model
status: proposed
date-proposed: 2026-07-16
date-decided:
decided-by:
requirements:
  - R-IDE-CONFIG-001
  - R-FRAMEWORK-001
  - R-IMAGE-BUILD-001
  - R-PRODUCT-001
  - R-PRODUCT-002
supersedes:
superseded-by:
---

# D-0001: Capability-First CLI Model

## Context

DevCapsule currently asks users to pick a product configuration by name:

```text
devcapsule CONFIGURATION ACTION [options]
```

This is the accepted model recorded in R-IDE-CONFIG-001 (status:
`implemented`). Two configurations exist: `pycharm` and `codium_with_claude`.

Three pressures make that model hard to carry into V1.

**Configurations are code, and code drifts.** Each configuration is a
hand-written Python class owning its own image spec and launcher. With exactly
two of them, they have already diverged far enough to need a bug record:
`devcapsule/implementation-notes/bugs/2026-07-13-codium-run-option-parity.md`.
Codium is missing Git transport, Docker modes, native debugging, sudo, and
writable-root controls that PyCharm has. That divergence is not an oversight to
be patched; it is the predictable behavior of a design where every
IDE-times-toolchain-times-agent combination is a separate hand-written artifact.

**The declared value proposition is not implemented.** `docs/v1-announcement.md`
promises that "the project can declare the IDE surface, runtime profile, state
layout, allowed host resources, and the current project memory in version
controlled files." Only project memory is actually declared today. The other
four live as roughly thirty command-line flags whose correct combination
survives in a developer's shell history. That is the same failure the
announcement's own Problem section indicts: "half-remembered setup steps, and
undocumented assumptions." The flags are the new stale notes.

**Users do not want our products; they want their tools present.** Nobody wants
a Dockerized PyCharm. They want Python, an IDE that understands it, and Docker
to be there when they open the repository. Configuration-first makes the user
translate their need into our catalog. That translation is our job.

Additionally, the announcement commits to project types (`python-cli`,
`python-lib`, `fastapi`, `java-lib`, `quarkus-rest`) via `devcapsule new
--type`. That introduces a second noun competing with configuration, and a bare
verb that already violates R-IDE-CONFIG-001's stated grammar.

Constraints this decision must respect:

- Reproducibility is the core product promise, so whatever is declared must be
  pinnable to exact versions.
- The `pycharm` configuration must remain functional and supported as the
  default answer for the capability set {python, python-ide, gemini}.
- Gemini CLI is the default agent capability because it can be redistributed
  inside DevCapsule images.
- Docker images are linear layer stacks, not sets. Composition is not union.
- Root documentation stays implementation-agnostic (R-DOCS-001).

## Options Considered

### Option A: Keep the configuration-first model

Users continue selecting `pycharm` or `codium_with_claude` by name. New
combinations become new hand-written configurations.

Cost: every combination is code. The parity bug is the evidence that this does
not survive two configurations, let alone the five project types V1 has already
promised publicly. The announcement's declarative claim stays false, so either
the product or the announcement has to give.

### Option B: Capability-first with a full composition engine

Users declare arbitrary capabilities; a resolver composes any combination on
demand and builds the image.

Cost: this is a dependency resolver with version solving, ordering, and
conflict detection — a package manager. Docker's linear layer model means
arbitrary union has no cheap implementation: multi-stage `COPY` works only for
relocatable trees (like the existing `/opt/node/node-{version}`) and breaks on
apt dependency graphs, `/etc` mutation, and system users. Building this before
V1, with two configurations and unfinished parity, is a multi-year detour.
Resolvers are where package managers go to die.

### Option C: Capability-first declaration with a curated resolution matrix

Users declare capabilities. A curated set of capability combinations resolves
to named, prebuilt images. Combinations outside the matrix fail with an honest
message and a request path, rather than being composed on demand.

Cost: not every combination works on day one, and the matrix is maintained by
hand. Users who want an uncurated combination wait for us.

## Decision

Adopt **Option C**.

### 1. Two files, two jobs

A repository declares what it needs in `devcapsule.toml`, hand-authored and
committed:

```toml
[capabilities]
need = ["python", "python-ide", "docker", "gemini"]

[project]
type = "python-lib"
mount = "/workspace/project"

[host]                      # every exposure, in one reviewable block
docker = "none"
network = "bridge"
sudo = false
writable-root = false
debug-native = false

[host.git]
identity-from-host = true
token-env = "GITHUB_TOKEN"
token-hosts = ["github.com"]

[agent]
autonomy = "full"           # see D-0002
```

Resolution produces `devcapsule.lock`, generated and committed, which pins
exact component versions and the resolved image digest.

This is the two-layer model every package manager converges on, and it is how
this decision satisfies two requirements that otherwise conflict: the
declaration is abstract enough to be ergonomic and portable, and the lock is
concrete enough to be reproducible.

### 2. A capability is an abstract requirement; the lock holds concrete components

`python-ide` is a requirement. `vscodium@1.126.04524` is a component. Users
declare requirements; the resolver selects components and writes them to the
lock. Project types (`python-lib`, `fastapi`) are named aliases over capability
sets — friendly abstractions, not a competing taxonomy. This collapses the
announcement's second noun into the first.

### 3. Capability sets are named by intent; `pycharm` survives as an alias

Named sets take intent names (`python-lib`, `fastapi`). Naming a set after its
implementation bakes in a lie the first time the implementation changes.

`pycharm` is retained as a supported compatibility alias resolving to
{python, python-ide, gemini}, and `devcapsule pycharm run` keeps working
unchanged. R-IDE-CONFIG-001's grammar is not abolished; it becomes the explicit
form. When `devcapsule.toml` is present it supplies the configuration, so bare
`devcapsule run` is consistent with the model rather than a violation of it —
the noun still comes first, it just comes from the file instead of argv.

### 4. Two IDE capabilities resolve to one IDE

Requesting `python-ide` and `javascript-ide` means "an IDE that understands
both," not two editors. The resolver selects a single component satisfying both
requirements; if none exists in the matrix, resolution fails and lists what was
tried.

Exactly one resolved component may declare `provides-entrypoint`. This needs no
supervisor and no second foreground process, because the collapse happens
during resolution rather than at runtime.

### 5. Resolution order is canonical

Every capsule builds as an ordered chain: `base → language runtimes → tooling →
agent CLI → IDE`. Popular *prefixes* get prebuilt, so `python+docker+pycharm`
and `python+gemini+antigravity` share a cached `base→python` prefix. Ordered
prefixes are the implementable version of the set-union intuition.

### 6. Grammar

```text
devcapsule init --need python --need python-ide --need docker   # writes devcapsule.toml
devcapsule lock                                                 # resolve; write devcapsule.lock
devcapsule run                                                  # the file supplies the noun
devcapsule run --docker host                                    # one-off override, not persisted
devcapsule pycharm run                                          # explicit form; still supported
devcapsule project new my-lib --type python-lib                 # `project` is a peer noun
devcapsule project adopt .                                      # path positional, defaults to .
```

## Rationale

**Declaration is cheap; composition is a research project.** Named capability
sets with prebuilt images deliver most of the compelling story for a small
fraction of the work. Arbitrary composition is a small fraction of the story
for most of the work. Option C ships the part users feel and defers the part
that is invisible when it works. When someone requests an uncurated
combination, we add it to the matrix and rebuild overnight — unglamorous,
invisible to the user, and it buys a year.

**The declaration makes the standing rule mechanical.** The `[host]` block puts
every isolation relaxation on one reviewable surface. `sudo = true` becomes a
line in a pull request diff that a human reviews. That converts "keep any
isolation relaxation explicit and documented" from a rule people must remember
into a property of the format. It is also a sharper claim than the
announcement currently makes: host boundaries get code-reviewed, which no
devcontainer competitor can say.

**It dissolves the parity bug instead of fixing it twice.** Once configurations
are data rather than code, there is one generic builder and one generic
launcher. PyCharm and Codium stop being two hand-written things that drift.
The parity work is then a down payment on this decision rather than throwaway
effort — provided it is executed as "extract the generic launcher," not "copy
PyCharm's flags into Codium."

**The lock is what makes "seconds" true.** A pinned image digest is a pull, not
a build. This makes Docker Hub publication load-bearing rather than launch
housekeeping.

Option A was rejected because the parity bug already demonstrates its failure
at N=2. Option B was rejected on scope, not on merit: it is probably where this
ends up, but arriving there before V1 means never shipping V1.

## Consequences

What becomes true:

- Configurations become data. One generic builder, one generic launcher.
- Host exposure is declared, diffable, and reviewable in one block.
- Project type stops being a second noun and becomes an alias over capabilities.
- `devcapsule pycharm run` keeps working; existing users are not broken.

What becomes harder:

- The curated matrix is hand-maintained, and uncurated combinations fail. That
  failure must be honest and actionable, listing what was tried and how to
  request an addition. A vague failure here poisons the whole model.
- `devcapsule.lock` needs a format, a resolver, and merge-conflict behavior.
- Docker Hub publication becomes a prerequisite rather than a nice-to-have, so
  the existing namespace task is now on the critical path.

What is accepted as lost:

- Arbitrary composition on day one. Users asking for combinations we have not
  curated get a clear "not yet," not magic.

Cleanups this decision forces, each currently a public-API wart:

- `--profile` is overloaded: it means "named state directory" in the CLI while
  the announcement uses "runtime profile" and "capability profile" for host
  exposure. Three concepts, one word. Rename before launch.
- `--docker` / `--docker-in-docker` / `--no-docker` are an enum modeled as
  three booleans with a runtime conflict check, even though `DockerMode`
  already exists internally. Same for the Git identity pair. Expose the enum.
- `codium_with_claude` is the only underscored command in a kebab-case CLI.
- `--plugins` is PyCharm vocabulary that does not survive contact with Codium
  extensions; `--git-token-host` is singular but takes a list.

Open questions deliberately left to sibling decisions:

- **D-0002**: agent autonomy inside the capsule, and the portable declaration
  of it across agent runtimes.
- **D-0003**: Gemini CLI as the default agent capability, recording the
  redistribution rationale that currently exists only in chat history.
- **D-0004**: whether devcontainer Features become the capability format for
  the tooling layer. This is the format question, orthogonal to this record's
  model question, and it carries real strategic weight: adopting an existing
  spec buys an ecosystem on day one and changes "more than just a devcontainer"
  from a competitive claim into a compatibility story.

## Reopen If

- Requests for uncurated capability combinations become the dominant support
  load. That is the signal that the matrix has stopped scaling and the composer
  from Option B is worth building.
- The resolver acquires version solving. At that point this is a package
  manager and deserves its own decision record rather than growing quietly
  inside a CLI.
- Prebuilt image pull time stops being meaningfully faster than a local build,
  which would remove the main justification for the curated matrix.
