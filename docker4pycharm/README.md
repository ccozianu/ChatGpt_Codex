# Docker PyCharm Isolation R0

This is a first-revision Docker/X11 wrapper for running a tarball-based PyCharm
installation in an isolated Linux container while keeping project files,
PyCharm settings, per-project IDE state, and plugins persistent on the host.

## Related project notes

- `../README.md` for project-wide requirements, backlog, and the current state
  and next step recorded at the end of the file.
- `../WORKFLOW.md` for the human/agent iteration process used by this project
  and reusable target projects.
- `debugging.md` for the handoff from the debugging session that made the
  current image work.
- `implementation-notes/using-v0-for-real-python-projects.md` for applying the
  current image to an ordinary Python project.
- `../user.md` for the human-facing PyCharm AI plugin setup guide.

## Build

Bootstrap or update the host image from the host Docker daemon:

```bash
./build-image.sh --pycharm /path/to/pycharm-professional-2026.1.tar.gz
# or
./build-image.sh --pycharm /path/to/unpacked/pycharm
```

After rebuilding with the current Dockerfile and launching through the default
runtime path, the IDE-side agent gets the Docker CLI connected to the host
Docker daemon through the host Docker socket. Docker commands run inside
PyCharm/Codex operate on host Docker images, containers, networks, and volumes.
The image also includes `shellcheck` for launcher-script linting.

The image carries the reusable human/agent process bootstrap template at:

```text
/usr/local/share/docker4ide/vibe-coding-process.md
```

Use it when opening an ordinary project that does not yet have local
`AGENTS.md`, README handoff, or `implementation-notes/` process docs.

If the normal Docker build network cannot reach Ubuntu package repositories on
the host, opt into host networking for the build:

```bash
./build-image.sh --network host --pycharm /path/to/pycharm-professional-2026.1.tar.gz
# or
DOCKER_BUILD_NETWORK=host ./build-image.sh --pycharm /path/to/pycharm-professional-2026.1.tar.gz
```

## Run

By default, Docker commands inside PyCharm/Codex connect to the host Docker
daemon through `/run/host-docker.sock`:

```bash
./run-pycharm-container.sh --project /path/to/project --ssh-agent
```

This default is convenient for local development, but it is not a strong
sandbox boundary: tools inside the IDE can control the host Docker daemon.

Use true Docker-in-Docker only when you explicitly want separate Docker state
inside the PyCharm container:

```bash
./run-pycharm-container.sh --project /path/to/project --ssh-agent --docker-in-docker
# or
./run-pycharm-container.sh --project /path/to/project --ssh-agent --dind
```

When DinD is enabled, the launcher prints a large stderr warning and starts the
outer IDE container with `--privileged`, a writable root filesystem, and an
inner `dockerd`. Disable Docker entirely for a higher-isolation session with:

```bash
./run-pycharm-container.sh --project /path/to/project --ssh-agent --no-docker
# or
DOCKER_MODE=none ./run-pycharm-container.sh --project /path/to/project --ssh-agent
```

The inner daemon is started without bridge/iptables management because the outer
PyCharm container uses host networking. For inner image builds that need network
access, pass `--network host` to `build-image.sh`.

## Mesa / OpenGL runtime

The image installs Mesa/OpenGL runtime packages required by JetBrains Skiko:

```text
libgl1 libglx-mesa0 libgl1-mesa-dri mesa-utils
```

The launcher and entrypoint default PyCharm to Mesa software GL through:

```text
LIBGL_ALWAYS_SOFTWARE=1
MESA_LOADER_DRIVER_OVERRIDE=llvmpipe
LIBGL_DRI3_DISABLE=1
```

This is intentional. The default isolation model does not mount host
`/dev/dri` render devices, so Mesa's hardware GLX path can log:

```text
MESA: error: Failed to query drm device.
glx: failed to create dri3 screen
failed to load driver: iris
```

Those lines mean Mesa tried the host GPU/DRI path and fell back. They are
different from the earlier blocking `libGL.so.1: cannot open shared object
file` failure, which meant required libraries were missing from the image.

Override the software GL defaults only for targeted rendering tests:

```bash
PYCHARM_LIBGL_ALWAYS_SOFTWARE=0 \
PYCHARM_MESA_LOADER_DRIVER_OVERRIDE= \
PYCHARM_LIBGL_DRI3_DISABLE=0 \
./run-pycharm-container.sh --project /path/to/project
```

Do not mount host `/dev/dri` or other GPU devices as a quiet default; make that
an explicit documented launcher option if the project later decides hardware GL
is worth the extra host exposure.

NVIDIA GPU passthrough is intentionally deferred. The likely future use case is
not IDE rendering, but Python ML development where CUDA-capable NVIDIA hardware
is useful inside the selected project environment. Add that later as an
explicit documented profile or launcher option, not as part of the default
software-GL path.

By default, persistent data lands in:

- `~/.local/share/pycharm-docker/state` for shared IDE configuration and the isolated IDE home
- `~/.local/share/pycharm-docker/project-state/<project-id>` for per-project caches, logs, and volatile workspace state
- `~/.local/share/pycharm-docker/plugins` for shared user-installed plugins

The launcher mounts the selected host project at a per-project container path
like `/workspace/<project-id>` instead of always using `/project`. This is
intentional: JetBrains IDEs record project/recent-workspace state by path, and
different host projects should not all look like the same in-container project.

Useful storage options:

```bash
./run-pycharm-container.sh \
  --project /path/to/project \
  --global-settings ~/.local/share/pycharm-docker/state \
  --plugins ~/.local/share/pycharm-docker/plugins
```

`--global-settings` should be shared when you want the same PyCharm appearance,
keymaps, plugin settings, AI login state, Git SSH known-hosts, and other
IDE-local home files across projects. `--state` is kept as a legacy alias for
`--global-settings`.

Use `--project-state` only when you want to override the automatically generated
per-project state directory:

```bash
./run-pycharm-container.sh \
  --project /path/to/project \
  --project-state ~/.local/share/pycharm-docker/project-state/my-project
```

Use `--project-mount` only when a project or tool truly needs a fixed
in-container path:

```bash
./run-pycharm-container.sh \
  --project /path/to/project \
  --project-mount /workspace/my-project
```

Avoid reusing the same `--project-state` or `--project-mount` for unrelated
projects; doing so can make PyCharm restore stale project-window state.

## GitHub credential options

SSH agent forwarding:

```bash
ssh-add -l
./run-pycharm-container.sh --project /path/to/project --ssh-agent
```

HTTPS token via environment variable without storing the token in Docker inspect:

```bash
export GITHUB_TOKEN=ghp_...
./run-pycharm-container.sh --project /path/to/project --github-token-env GITHUB_TOKEN
```

Native debugging or aggressive strace use:

```bash
./run-pycharm-container.sh --project /path/to/project --debug-native
```

## Runtime verification

Inside a launched PyCharm container, run:

```bash
docker4ide-check-runtime-deps
```

When running from this repository before rebuilding the image, the same helper
is available as:

```bash
./docker4pycharm/check-runtime-deps.sh
```

The helper checks the IDE runtime's Skiko native `libGL` dependency resolution,
`XDG_RUNTIME_DIR`, writable IDE paths, and the GLX renderer path. The expected
renderer under the default isolation model is Mesa `llvmpipe`.

## Debugging handoff

The detailed handoff lives in `debugging.md`. It records the problems seen while
bringing the MVP to a working state:

- Historical note: Markdown preview previously rendered blank and could make
  the PyCharm GUI unresponsive, but this is no longer reproduced in the current
  iterations. The old symptoms and log signatures are preserved in
  `implementation-notes/completed-tasks/2026-06-20-markdown-preview-skiko-opengl-hang-retired.md`.
- Docker build networking required opt-in host networking on the user's laptop.
- The default launcher mode now connects the IDE container to the host Docker
  daemon. Explicit `--docker-in-docker` mode is available if isolated Docker
  state is needed.
- JetBrains/Skiko failed until Mesa/OpenGL runtime libraries supplied
  `libGL.so.1`.
- Mesa is intentionally defaulted to software GL/`llvmpipe` so the container
  does not need host `/dev/dri` access.
- Container runtime warnings included missing `XDG_RUNTIME_DIR` and accessibility
  bus warnings.
- A JetBrains duplicate-feature error appeared in the Full Line / ML completion
  path and should be checked in IDE logs if AI chat behaves strangely.
