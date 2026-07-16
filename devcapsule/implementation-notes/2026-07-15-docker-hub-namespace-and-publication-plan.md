# Docker Hub Namespace And Publication Plan

Date: 2026-07-15

Status: open V1 publication task

## Why This Note Exists

DevCapsule needs a documented path for publishing prebuilt Docker images for
users. This note records the current Docker Hub naming constraints, account
limits, and the concrete follow-up work needed before V1 image publication.

## Namespace Findings

- Docker Hub image names live under a Docker Hub namespace, which is either a
  user namespace or an organization namespace.
- The practical Docker Hub naming shape is:

```text
<docker-namespace>/<repository>:<tag>
```

- A domain-style namespace such as `mycodespace.ai/devcapsule` is not the
  expected Docker Hub repository naming model.
- The realistic namespace candidates to claim are more like:

```text
mycodespaceai/devcapsule
mycodespace/devcapsule
```

- Docker domain verification is useful for proving organizational control over
  `mycodespace.ai`, but it does not turn the Docker Hub namespace into a
  domain-style image path.

## Current Docker Hub Limit Findings

At the time of research, the Docker documentation indicates:

- authenticated Personal accounts get 200 pulls per 6 hours;
- Personal accounts get unlimited public repositories;
- Personal accounts get up to 1 private repository;
- Pro, Team, and Business accounts get unlimited pull rate and unlimited
  public/private repositories;
- Docker documents storage and transfer under fair-use language rather than a
  simple fixed free upload/storage quota on the main usage page.

Treat these limits as documentation-backed guidance that should be rechecked
immediately before public release.

## Recommended Publication Direction

For V1, prefer an organization-owned Docker Hub namespace rather than a
personal namespace.

Recommended target shape:

```text
mycodespaceai/devcapsule
```

Potential repository/tag examples:

```text
mycodespaceai/devcapsule:pycharm-latest
mycodespaceai/devcapsule:codium-latest
mycodespaceai/devcapsule:pycharm-v1
mycodespaceai/devcapsule:codium-v1
```

Whether PyCharm and Codium should share one repository with differentiated tags
or use separate repositories should be decided as part of the release process.

## Required V1 Follow-Up Work

1. Claim the chosen Docker Hub namespace, ideally as an organization.
2. Verify whether `mycodespace.ai` should also be added as a verified domain
   for the Docker organization/company account.
3. Choose the public repository naming scheme:
   - single repository with tags per IDE; or
   - separate repositories per IDE/runtime family.
4. Decide which Docker subscription tier is acceptable for projected pull
   volume and private/public needs.
5. Build release-ready images from the active `devcapsule` implementation.
6. Perform a real push/pull validation using the target namespace.
7. Document the end-user pull commands in current user docs.

## Minimal Push Flow To Reuse Later

```bash
docker login
docker tag devcapsule:latest mycodespaceai/devcapsule:latest
docker push mycodespaceai/devcapsule:latest
```

Adjust the repository and tag names once the final publication layout is
chosen.

## Open Questions

- Which Docker Hub namespace is actually available and preferable:
  `mycodespaceai`, `mycodespace`, or another close variant?
- Should V1 ship one repository with multiple image tags, or distinct
  repositories per environment?
- Is a Personal account sufficient for early testing, or should V1 start on an
  organization-backed paid plan immediately?
