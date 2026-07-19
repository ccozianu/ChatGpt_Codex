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
- PyCharm must remain the default answer for the capability set
  {python, python-ide, gemini}. The existing `devcapsule pycharm run` path must
  remain functional during an explicit deprecation and migration window.
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

### Option C: Capability-first declaration with a curated image matrix

Users declare capabilities. A curated set of capability combinations resolves
directly to complete, prebuilt images. Combinations outside the matrix fail
with an honest message and a request path, rather than being composed on
demand.

Cost: not every combination works on day one, and the matrix is maintained by
hand. Users who want an uncurated combination wait for us. Each supported
platform needs its own tested image digest.

## Decision

Adopt **Option C**.

Review checkpoint, 2026-07-19: the human and agent have settled sections 1
through 3 below for the working specification. Sections 4 through 9 remain to
be reviewed in the next session. The decision record remains `proposed` until
that review is complete and the human adopts the finished record.

### 1. Portable project declaration and developer-owned runtime realization

Configuration is a hierarchical key-value tree. Ordinary values are resolved
by applying four layers in increasing order of precedence:

1. workstation configuration, which supplies this developer's defaults for
   every project on the workstation;
2. committed project-global `devcapsule.toml`, which supplies portable values
   for every checkout and workstation instantiating the project;
3. uncommitted project-local configuration owned by this developer on this
   workstation; and
4. run-once command-line values, which are intentionally not persisted.

The last specified ordinary value wins. Policy constraints are not ordinary
values: applicable constraints combine restrictively and a higher-precedence
value cannot silently bypass them.

The committed `devcapsule.toml` is hand-authored repository content. It
declares portable capabilities, project identity, container-internal settings,
and safe values:

```toml
[capabilities]
need = ["python", "python-ide", "docker-cli", "gemini"]

[project]
name = "DevCapsule"
slug = "devcapsule"
creator = "https://github.com/ccozianu"
mount = "/workspace/project"

[host.docker.mode.recommended]
value = "host-socket"
justification = "Required to run peer DevCapsule instances during the full test suite."
enables = ["full-test-suite"]
```

Committed repository content is untrusted for purposes of workstation access.
It must not activate host Docker socket access, host networking, credential or
agent-state mounts, arbitrary host-path mounts, devices, privileged mode,
Linux capabilities, or similar host exposure. It may constrain such exposure
or recommend a value, but a recommendation is not a configured value and does
not participate directly in overlay precedence. Security-sensitive access is
activated only by developer-owned project-local configuration or an explicit
run-once choice. With neither, the safe value applies. If the requested action
cannot work safely, DevCapsule stops and explains the missing authorization
instead of silently relaxing isolation.

Each security-sensitive recommendation contains a proposed `value`, a
project-authored `justification`, and the functionality it `enables`.
DevCapsule presents that text alongside a DevCapsule-authored explanation of
the security effect; repository text must not define its own risk description.
An unresolved interactive recommendation offers at least: deny for this run,
allow for this run, persistently allow for this checkout, and persistently deny
for this checkout. Denial is the default. Noninteractive execution never
prompts or grants access: it uses an existing developer-owned decision or
fails with an actionable instruction. A changed recommendation never mutates
an earlier adoption silently, and workstation policy may prohibit a
recommended value.

The workstation configuration root is
`$XDG_CONFIG_HOME/devcapsule/`. If `XDG_CONFIG_HOME` is unset or empty, it is
`~/.config/devcapsule/`; non-XDG platforms use their platform-appropriate user
configuration directory. `devcapsule config path` prints the actual resolved
file. Workstation-wide values live in `config.toml` beneath that root.

A project has a portable, self-asserted identity formed by a `creator` URI and
a `slug`. A creator may be an HTTPS profile URL or a `mailto:` URI; a plain
email entered during bootstrap is normalized to `mailto:`. DevCapsule warns
that both values will be committed and may become public. The pair is useful
for organization and local collision detection but is neither authenticated
ownership nor a grant of trust. Federated identity, ownership transfer, forks,
mirrors, and cross-workstation verification are deferred beyond this
local-first specification.

Project-local configuration lives under:

```text
$XDG_CONFIG_HOME/devcapsule/projects/<url-encoded-creator>/<url-encoded-slug>/
```

DevCapsule defines one canonical URI normalization and percent-encoding so an
identity maps deterministically. The common one-checkout case uses a single,
plain TOML file:

```text
devcapsule.toml
```

That file records a human-readable checkout name, its workstation-observed
canonical path, and its local values. When the same project identity gains a
second checkout, additional records use:

```text
checkouts/<checkout-name>.toml
```

The first record is not moved or renamed. Checkout names are workstation-owned
labels, and each record repeats its decoded creator, slug, checkout name, and
canonical path so it remains understandable and salvageable with an ordinary
text editor. DevCapsule verifies the observed path before applying the record.
A fresh clone, fork, or second checkout cannot inherit another checkout's
security approvals merely by copying or claiming the same committed project
identity. Removing a checkout does not promote another automatically.

Personal IDE state and credentials also remain developer-owned and outside the
committed declaration and image. This includes IDE settings and extensions,
Git identity and credential material, agent login state, token values, and the
host paths of personal state roots. The project may describe an integration it
needs, but it cannot supply credentials, assume a developer's host paths, or
authorize their exposure.

IDE application state is durable and project-scoped by default. DevCapsule
persists the IDE's own configuration, home, and extension or plugin state in a
developer-owned project state directory and mounts it again for later sessions.
This allows values entered through IDE settings, including secrets stored by
the IDE or a plugin, to survive container replacement without teaching
DevCapsule plugin-specific storage formats or copying secret values into TOML.
Disposable caches and logs remain separable from this durable state.

DevCapsule also provides a persistent project-runtime state mount by default,
replacing the need to repeat `--project-state` on each launch. It is scoped to
the local checkout and kept outside the source tree. It holds rebuildable but
expensive state such as IDE indexes and system data, logs, downloaded Python
and npm packages, and other language-tool or build caches. Runtime components
map their conventional cache locations into named locations beneath this
mount—for example through `XDG_CACHE_HOME`, `PIP_CACHE_DIR`, and the npm cache
setting—rather than assuming that every tool follows XDG paths automatically.
Deleting project-runtime state may make the next launch or build slower but
must not delete source, IDE preferences, or credentials.

Durable IDE state, project-runtime state, and the project source are therefore
three distinct mounts with different lifecycles and trust implications. Their
host paths are selected by convention from the observed project and checkout;
ordinary use does not require command-line path options. A developer-owned
configuration value may relocate them when workstation storage layout requires
it.

A developer may instead opt a project into a workstation-global state profile
for a particular IDE implementation. This shares that IDE's settings and
stored credentials with every checkout explicitly assigned to the profile, so
it is never selected by committed project configuration or by default. Because
durable IDE state may contain credentials, a new checkout must separately
authorize mounting either the project-scoped state or a global IDE profile; a
copied project identity alone is insufficient. The exact XDG data and state
paths and the command used to select a global profile remain CLI specification
work.

Resolution separately produces `devcapsule.lock`, generated and committed,
which pins the matrix version, target platform, exact component versions,
registry reference, and complete image digest. The lock is resolution output,
not a fifth general-purpose configuration overlay. `run` uses the locked
digest; it does not silently re-resolve.

### 2. A capability is an abstract requirement; the lock holds concrete components

`python-ide` is a requirement. `vscodium@1.126.04524` is a component. Users
declare requirements; the resolver selects components and writes them to the
lock. Project types (`python-lib`, `fastapi`) are input-time templates that
expand to capabilities when `devcapsule init` or `devcapsule project new`
writes the manifest. A manifest stores the expanded capability list, not both
a type and a second potentially conflicting list. This collapses the
announcement's second noun into the first while keeping the friendly
project-creation vocabulary.

### 3. Capability sets are named by intent; configuration-first run is deprecated

Named sets take intent names (`python-lib`, `fastapi`). Naming a set after its
implementation bakes in a lie the first time the implementation changes.

The abstract capability set {python, python-ide, gemini} resolves to the
curated PyCharm image by default in the initial matrix. The selected concrete
IDE is recorded in `devcapsule.lock` and may change only through an explicit
lock update. A project that genuinely depends on one implementation may add an
implementation constraint to resolution, but ordinary users declare intent
and do not select an IDE product in the run command. The exact constraint
spelling remains schema work.

The primary launch form is `devcapsule run`, normally invoked from within the
project. DevCapsule discovers `devcapsule.toml`, identifies the local checkout,
loads the configuration layers and durable-state conventions from section 1,
and runs the image digest selected by the lock. An explicit project path may be
accepted when launching from elsewhere.

Configuration-first launch forms such as `devcapsule pycharm run` are
deprecated. They remain temporarily as migration shims with an actionable
warning, but they are not the enduring implementation-pinning interface and
may be removed after the compatibility window. Image build and maintainer
workflows are separate from the normal project launch grammar and will be
specified independently.

Routine launch state does not remain a collection of product-specific flags.
Image selection comes from the lock; project and checkout identity select
state paths by convention; IDE configuration and plugins persist in the IDE
state mount; project caches persist in the project-runtime state mount; and
Git identity, credentials, Docker access, debugging privileges, sudo,
networking relaxations, and other workstation choices come from
developer-owned configuration and the recommendation flow. Alternate launch
modes such as a diagnostic shell should be actions rather than IDE-specific
flags. Command-line values remain for inspection, explicit project selection,
and conspicuous run-once exceptions; the exact generic override spelling is
part of the remaining grammar review.

### 4. Two IDE capabilities resolve to one interactive surface

Requesting `python-ide` and `javascript-ide` means "one interactive IDE surface
that understands both," not two editor processes. The matrix selects one
complete image whose single interactive-surface component provides both
capabilities; if no such image is curated, resolution fails and lists the
nearest supported sets that were considered.

Exactly one component in a resolved image may provide the interactive surface
and own the normal container foreground lifecycle. Agent CLIs, terminals, and
debug shells are tools or alternate launch modes, not additional interactive
surface providers. This needs no supervisor and no second IDE process because
the collapse happens during resolution rather than at runtime.

### 5. The matrix resolves complete images, not layers

The resolution matrix maps a normalized capability set plus target platform
directly to one complete, tested image digest. It does not return a set of
layers, run a dependency solver, or compose a new image locally. How DevCapsule
builds those curated images and reuses Docker layer cache is an implementation
decision outside this record. That build machinery may use ordered inputs, but
it is not part of the end-user resolution contract.

### 6. Lock lifecycle and failure behavior

`devcapsule lock` normalizes the declared capability set, selects an exact
supported matrix entry for the current or explicitly requested platform, and
writes the lock. The lock records at least:

- a lock-format version and resolution-matrix version;
- the normalized requested capabilities and selected components;
- the target operating system and architecture;
- the immutable registry reference and complete image digest.

`devcapsule run` requires a lock consistent with the manifest and current
platform. A missing or stale lock produces an actionable instruction to run
`devcapsule lock`; it never changes the selected image implicitly. An
unavailable digest is a pull or registry error, not permission to select a
different image. Lock regeneration is explicit, and the generated format must
be deterministic so ordinary branch merges can distinguish a real resolution
change from serialization noise.

An unsupported capability set fails before build or run. The error reports the
normalized request, target platform, nearest curated sets, and the documented
request path. V1 does not fall back to local composition.

### 7. Capability requirements and host permissions are distinct

Capabilities describe what is present inside the capsule. Host declarations
describe what the running capsule may access. For example, `docker-cli` means
the client binary is installed; `host.docker-daemon = "host-socket"` grants
access to the host daemon. Neither implies the other. Capability names must not
encode ambient host privileges.

The committed declaration may state that host integration is useful or needed,
but it cannot authorize that integration. Persistent authorization belongs to
the developer-owned configuration for the observed checkout. One-off CLI
overrides remain available for diagnosis and exceptional local work, but they
must be explicit, apply only to that invocation, print the effective relaxation
before launch, and never modify the manifest or lock. Security-relaxing
overrides may require interactive confirmation; automation must use a separate
explicit acknowledgement option. The later CLI specification must classify
which changes are relaxations and preserve noninteractive failure by default.

### 8. Devcontainer Features are not the project capability format

DevCapsule does not adopt devcontainer Features as the top-level capability
declaration or resolution format. Features specify installable implementation
units and lifecycle behavior, while DevCapsule capabilities are abstract
project requirements resolved only through a curated complete-image matrix.
Making Features the public format would expose the composition model rejected
for V1 and would blur the boundary between declaring intent and executing
third-party installation code.

This rejection does not forbid a curated image builder from consuming selected
Features internally, nor a later import or compatibility tool. Either would
require its own trust, pinning, ordering, and redistribution policy; it would
not change the `devcapsule.toml` capability model decided here.

### 9. Grammar

```text
devcapsule init --need python --need python-ide --need docker-cli # writes manifest
devcapsule lock                                                   # writes lock
devcapsule run                                                    # uses locked digest
devcapsule run --docker-daemon host-socket                        # one-run relaxation
devcapsule pycharm run                                            # pinned compatibility form
devcapsule project new my-lib --type python-lib                   # expands a template
devcapsule project adopt .                                        # path defaults to .
```

The exact spelling of security-override acknowledgement and personal-state
selection remains specification work, but the behavioral constraints above are
part of this decision.

## Rationale

**Declaration is cheap; composition is a research project.** Curated capability
sets backed by complete prebuilt images deliver most of the compelling story
for a small fraction of the work. Arbitrary composition is a small fraction of
the story for most of the work. Option C ships the part users feel and defers
the part that is invisible when it works. When someone requests an uncurated
combination, maintainers can add and validate a new complete matrix entry
without promising that the client can compose it.

**The declaration makes the standing rule mechanical.** A project can explain
why it recommends an integration, while only developer-owned configuration can
authorize the corresponding host exposure. The choice and its security effect
remain visible at adoption and launch instead of being implied by repository
content. This converts "keep any isolation relaxation explicit and documented"
from a rule people must remember into a property of the format and command
behavior.

**It attacks the cause of the parity bug.** A shared manifest and runtime
planner make common behavior data-driven and testable in one place. PyCharm and
Codium may still need thin adapters for IDE-specific entrypoints, sandboxing,
and validation, but those adapters no longer own copies of the shared host and
state policy. The parity work is therefore a down payment on this decision when
it extracts the common planner instead of copying flags.

**The lock is what makes "seconds" true.** A pinned image digest is a pull, not
a build. This makes Docker Hub publication load-bearing rather than launch
housekeeping.

Option A was rejected because the parity bug already demonstrates its failure
at N=2. Option B was rejected on scope, not on merit: it may become justified
later, but arriving there before V1 means never shipping V1.

## Consequences

What becomes true:

- Shared runtime policy and resolution become data, with thin IDE-specific
  build and launch adapters where behavior genuinely differs.
- Project recommendations are committed and reviewable, while actual host
  exposure authorization remains developer-owned and checkout-specific.
- Project type stops being stored as a second source of truth and becomes an
  input-time template for capabilities.
- Personal state and credentials are explicitly outside the committed project
  declaration and lock.
- `devcapsule pycharm run` keeps working and continues to mean PyCharm during
  its explicit deprecation and migration window.

What becomes harder:

- The curated matrix is hand-maintained, and uncurated combinations fail. That
  failure must be honest and actionable, listing what was tried and how to
  request an addition. A vague failure here poisons the whole model.
- Each supported platform requires a tested complete image and digest.
- `devcapsule.lock` needs a deterministic format, explicit update behavior,
  and useful merge-conflict handling.
- Docker Hub publication becomes a prerequisite rather than a nice-to-have, so
  the existing namespace task is now on the critical path.
- One-off isolation relaxations remain possible but must be conspicuous and
  cannot silently rewrite committed policy.

What is accepted as lost:

- Arbitrary composition on day one. Users asking for combinations we have not
  curated get a clear "not yet," not magic.
- Devcontainer Features are not the project-facing capability format for V1.

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
- A later decision may consider curated internal use or import compatibility
  for devcontainer Features. Their use as DevCapsule's top-level capability
  format is rejected by this record.

## Reopen If

- Requests for uncurated capability combinations become the dominant support
  load. That is the signal that the matrix has stopped scaling and the composer
  from Option B is worth building.
- The resolver acquires version solving. At that point this is a package
  manager and deserves its own decision record rather than growing quietly
  inside a CLI.
- Prebuilt image pull time stops being meaningfully faster than a local build,
  which would remove the main justification for the curated matrix.
- Real projects need more than one simultaneously running interactive IDE
  surface often enough that the single-surface model becomes an obstacle.
- Project policy and personal state cannot remain cleanly separated without
  making normal setup materially harder.
