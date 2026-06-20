# Docker PyCharm Isolation R0

This is a first-revision Docker/X11 wrapper for running a tarball-based PyCharm
installation in an isolated Linux container while keeping project files,
PyCharm state, and plugins persistent on the host.

## Related project notes

- `../README.md` for project-wide requirements, backlog, and the current state
  and next step recorded at the end of the file.
- `debugging.md` for the handoff from the debugging session that made the
  current image work.
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

By default, persistent data lands in:

- `~/.local/share/pycharm-docker/state`
- `~/.local/share/pycharm-docker/plugins`

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

## Debugging handoff

The detailed handoff lives in `debugging.md`. It records the problems seen while
bringing the MVP to a working state:

- Top priority: Markdown preview can render blank and make the PyCharm GUI
  unresponsive, with captured Mesa/DRI/OpenGL/Skiko context creation errors in
  `debugging.md`.
- Docker build networking required opt-in host networking on the user's laptop.
- The default launcher mode now connects the IDE container to the host Docker
  daemon; validate `docker info` from inside the launched IDE container. Also
  validate explicit `--docker-in-docker` mode if isolated Docker state is needed.
- JetBrains/Skiko failed until Mesa/OpenGL runtime libraries supplied
  `libGL.so.1`.
- Container runtime warnings included missing `XDG_RUNTIME_DIR` and accessibility
  bus warnings.
- A JetBrains duplicate-feature error appeared in the Full Line / ML completion
  path and should be checked in IDE logs if AI chat behaves strangely.
