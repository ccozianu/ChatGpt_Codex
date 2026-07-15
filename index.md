# Documentation Index

Status: maintained index of repository markdown documentation.

When adding, deleting, or renaming any `.md` file, update this index in the
same change.

## Start Here

- [Project brief and handoff](README.md)
- [Documentation index](index.md)
- [Agent instructions](AGENTS.md)
- [Requirements overview and index](REQUIREMENTS.md)
- [Human / agent workflow](WORKFLOW.md)

## Root Requirement Records

- [R-PRODUCT-001 Batteries-Included IDE Environments](docs/requirements/r-product-001-batteries-included-ide-environments.md)
- [R-PRODUCT-002 Explicit Host Boundaries](docs/requirements/r-product-002-explicit-host-boundaries.md)
- [R-PRODUCT-003 Durable Human/Agent Project Memory](docs/requirements/r-product-003-durable-human-agent-project-memory.md)
- [R-PRODUCT-004 Reusable Human/Agent Workflow](docs/requirements/r-product-004-reusable-human-agent-workflow.md)
- [R-PRODUCT-005 Incremental Human/Agent Execution Loop](docs/requirements/r-product-005-incremental-human-agent-execution-loop.md)
- [R-DOCS-001 Root Documentation Stays Implementation-Agnostic](docs/requirements/r-docs-001-root-documentation-stays-implementation-agnostic.md)
- [R-DOCS-002 Current User Docs Show Current Interfaces](docs/requirements/r-docs-002-current-user-docs-show-current-interfaces.md)

## Active Docker4IDEs Development

- [Docker4IDEs Python CLI](docker4ides/README.md)
- [Docker4IDEs implementation requirements overview](docker4ides/REQUIREMENTS.md)
- [R-ENV-001 Dockerized PyCharm Runtime](docker4ides/docs/requirements/r-env-001-dockerized-pycharm-runtime.md)
- [R-STATE-001 Persistent IDE State And Plugins](docker4ides/docs/requirements/r-state-001-persistent-ide-state-and-plugins.md)
- [R-SETTINGS-001 Per-IDE Settings Profile Seed](docker4ides/docs/requirements/r-settings-001-per-ide-settings-profile-seed.md)
- [R-SCOPE-001 Explicit Host Filesystem Exposure](docker4ides/docs/requirements/r-scope-001-explicit-host-filesystem-exposure.md)
- [R-DEV-001 Useful Development Tooling Baseline](docker4ides/docs/requirements/r-dev-001-useful-development-tooling-baseline.md)
- [R-GIT-001 Git Identity And Credentials Without Host Credential Mounts](docker4ides/docs/requirements/r-git-001-git-identity-and-credentials-without-host-credential-mounts.md)
- [R-DOCKER-001 Explicit Docker Capability Profiles](docker4ides/docs/requirements/r-docker-001-explicit-docker-capability-profiles.md)
- [R-PROJECT-001 Per-Project IDE Runtime State](docker4ides/docs/requirements/r-project-001-per-project-ide-runtime-state.md)
- [R-CONC-001 Concurrent Project Sessions](docker4ides/docs/requirements/r-conc-001-concurrent-project-sessions.md)
- [R-PROC-001 Durable Human/Agent Project Memory](docker4ides/docs/requirements/r-proc-001-durable-human-agent-project-memory.md)
- [R-DOCS-001 Generated Documentation Index](docker4ides/docs/requirements/r-docs-001-generated-documentation-index.md)
- [R-DOCS-002 User-Level Documentation Coevolves With User-Visible Behavior](docker4ides/docs/requirements/r-docs-002-user-level-documentation-coevolves-with-user-visible-behavior.md)
- [R-IDE-CONFIG-001 Configuration-First End-User CLI Model](docker4ides/docs/requirements/r-ide-config-001-configuration-first-end-user-cli-model.md)
- [R-PYTHON-MVP-001 Source Checkout Install And Run](docker4ides/docs/requirements/r-python-mvp-001-source-checkout-install-and-run.md)
- [R-PYTHON-MVP-002 Single-File Python CLI Artifact](docker4ides/docs/requirements/r-python-mvp-002-single-file-python-cli-artifact.md)
- [R-PYTHON-MVP-003 Python MVP Feature Scope](docker4ides/docs/requirements/r-python-mvp-003-python-mvp-feature-scope.md)
- [R-IMAGE-BUILD-001 Python-Native Composable Image Building](docker4ides/docs/requirements/r-image-build-001-python-native-composable-image-building.md)
- [R-FRAMEWORK-001 Shared Python Docker4IDE Orchestration](docker4ides/docs/requirements/r-framework-001-shared-python-docker4ide-orchestration.md)
- [Click-based CLI parsing brief](docker4ides/implementation-notes/click_based_cli_parsing_brief.md)
- [PyCharm image vibe-coding bootstrap template](docker4ides/docker4ides/assets/pycharm/image-assets/vibe-coding-process.md)
- [TypeScript five-in-a-row sample project](docker4ides/tests/resources/sample_projects/typescript_tictactoe_5inrow/README.md)

## Product And Positioning

- [Draft pitch: batteries included, boundaries explicit](docs/draft-pitch.md)
- [LinkedIn announcement draft](docs/linkedin-announcement.md)
- [Working backwards press release](docs/working-backwards-press-release.md)

## Docker4PyCharm Historical Reference

- [Docker PyCharm isolation README](docker4pycharm/README.md)
- [Historical root project brief](docker4pycharm/historical-root-README.md)
- [Post-MVP refactoring strategy](docker4pycharm/FUTURE_AGENT_REFACTORING_BRIEF.md)
- [PyCharm AI plugin and ChatGPT subscription setup](docker4pycharm/user.md)
- [Debugging notes](docker4pycharm/debugging.md)
- [Vibe-coding process bootstrap template](docker4pycharm/image-assets/vibe-coding-process.md)

## Implementation Notes And Decisions

- [Per-project IDE state split](docker4pycharm/implementation-notes/2026-06-21-per-project-ide-state-split.md)
- [Git identity and remote credential transport](docker4pycharm/implementation-notes/2026-06-22-git-identity-and-credentials.md)
- [Default JetBrains GL to Mesa software rendering](docker4pycharm/implementation-notes/2026-06-22-mesa-software-gl-default.md)
- [Development sudo profile](docker4pycharm/implementation-notes/2026-06-24-development-sudo-profile.md)
- [Python project UX defaults](docker4pycharm/implementation-notes/2026-06-24-python-project-ux-defaults.md)
- [Docker-in-Docker implementation choice](docker4pycharm/implementation-notes/docker-in-docker-immplementation-choice.md)
- [Docker in containerized development environments TLDR](docker4pycharm/implementation-notes/docker_in_devcontainer_tldr.md)
- [Using PyCharm v0 for real Python projects](docker4pycharm/implementation-notes/using-v0-for-real-python-projects.md)

## Bugs

- [Codium run lacks shared developer runtime options](docker4ides/implementation-notes/bugs/2026-07-13-codium-run-option-parity.md)
- [Bug template](docker4pycharm/implementation-notes/bugs/_template.md)
- [Concurrent projects sharing global settings lock](docker4pycharm/implementation-notes/bugs/2026-06-24-concurrent-projects-shared-global-settings-lock.md)

## Completed, Retired, And Deferred Tasks

- [VSCodium sandbox and foreground launch](docker4ides/implementation-notes/completed-tasks/2026-07-13-vscodium-sandbox-and-foreground-launch.md)
- [Completed task archive README](docker4pycharm/implementation-notes/completed-tasks/README.md)
- [Bootstrap process template V004 validation](docker4pycharm/implementation-notes/completed-tasks/2026-06-20-bootstrap-process-template-v004-validation.md)
- [Default host Docker passthrough validation retired](docker4pycharm/implementation-notes/completed-tasks/2026-06-20-default-host-docker-passthrough-validation-retired.md)
- [Explicit Docker-in-Docker validation](docker4pycharm/implementation-notes/completed-tasks/2026-06-20-explicit-docker-in-docker-validation.md)
- [Markdown preview Skiko/OpenGL hang retired](docker4pycharm/implementation-notes/completed-tasks/2026-06-20-markdown-preview-skiko-opengl-hang-retired.md)
- [Mesa/Skiko Markdown preview validation](docker4pycharm/implementation-notes/completed-tasks/2026-06-22-mesa-skiko-markdown-validation.md)
- [Development sudo account validation failure](docker4pycharm/implementation-notes/completed-tasks/2026-06-28-dev-sudo-account-validation.md)
- [Git remote credential manual validation deferred](docker4pycharm/implementation-notes/completed-tasks/2026-06-28-git-remote-validation-deferred.md)
- [Local Git identity edge-case validation](docker4pycharm/implementation-notes/completed-tasks/2026-06-30-local-git-identity-edge-validation.md)
- [PyCharm v0 MVP checkpoint](docker4pycharm/implementation-notes/completed-tasks/2026-06-30-pycharm-v0-mvp-checkpoint.md)
