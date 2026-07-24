# Bug: PyCharm Uses Host Networking Without Authorization

Date opened: 2026-07-23

Status: partially fixed in repository; manual validation and explicit
host-network selection remain open

Requirements: R-SCOPE-001, R-DOCKER-001, R-FRAMEWORK-001, root R-PRODUCT-002

## Symptom

Both `devcapsule pycharm run` and `devcapsule run-image` launch compatible
PyCharm images with Docker host networking even when the operator did not
request or persistently authorize that isolation relaxation.

## Evidence

The shared PyCharm launcher's `build_docker_args` function unconditionally
includes `--network=host`. Docker-daemon inspection of the running dogfood
container confirmed `NetworkMode=host` even though its `run-image` command did
not contain a network option.

## Expected Behavior

The safe default is Docker bridge networking. Host networking is available to
an operator who selects it explicitly on the command line or records it in
developer-owned checkout configuration. A committed project may recommend it
but cannot authorize it.

The expert `run-image` path should expose broad Docker-specific control. It
should make unusual or risky choices visible rather than maintaining a broad
forbidden-option list, while still applying restrictive workstation policy.

## Actual Behavior

Host networking is ambient and cannot be distinguished from an intentional
operator choice in the resulting Docker plan.

## Root Cause

The Python launcher retained the historical PyCharm prototype's unconditional
host-network setting while runtime authorization was being refactored.

## Fix Progress

On 2026-07-24 the unconditional `--network=host` argument was removed from the
shared PyCharm launcher. The capability-first end-to-end planning test now
asserts that the generated default Docker command does not contain host
networking. Normal `devcapsule run` accepts only bridge networking in this
first slice and directs expert exceptions to `run-image`.

The bug remains open because the shared explicit network option and
Docker-daemon inspection targets have not yet been implemented and validated.

## Proposed Fix Direction

- Remove the unconditional `--network=host` argument.
- Add a shared network-mode value whose safe default is `bridge`.
- Allow developer-owned checkout configuration and explicit command-line
  options to select `host`.
- Let committed configuration recommend, but not activate, host networking.
- Include the effective network mode in sanitized runtime-plan output.
- Preserve expert custom Docker arguments for `run-image`, subject only to
  structural plan validation and restrictive workstation policy.

## Verification Target

1. Automated: both PyCharm launch paths default to bridge networking.
2. Automated: explicit and checkout-owned host-network selections emit
   `--network=host`.
3. Automated: a committed recommendation alone does not enable host networking.
4. Manual: inspect a default and explicitly host-networked dogfood container.

## Close Criteria

Close when host networking is absent by default, remains available through an
explicit developer-owned choice, both launch paths share the behavior, and the
automated plus Docker-daemon inspection targets pass.
