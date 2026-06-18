# DockerForIDEIsolation

This repository is a continuation point for the Docker/PyCharm isolation work bootstrapped from a ChatGPT design session. It is intended to be read by both a human developer and a future AI development agent working inside PyCharm.

The first concrete build target is `docker4pycharm`, a Docker/X11 configuration for running PyCharm in a Linux container while keeping PyCharm user state and plugins persistent outside the image and while exposing only an explicitly selected project directory to the IDE.

## Conversation summary

The user requested a Docker environment whose main goal is to run PyCharm in isolation without degrading the expected IDE experience. The environment should allow future installation of AI-related PyCharm plugins, including ChatGPT/Codex and possibly Claude-related tooling in later revisions. The environment is expected to run from a normal Linux developer workstation under X11, launched from `xterm` or a similar terminal. The assumed host baseline is a common Linux distribution newer than Ubuntu 22.04, with systemd newer than 249.x if systemd functionality is ever needed.

The key requirements were:

- Run PyCharm isolated in Docker, but preserve normal IDE features as much as practical.
- Start the environment with a simple command, either `docker start ...` or a suitably parameterized Bash/Python launcher.
- Keep PyCharm configuration and plugins outside the Docker image so user settings and installed plugins persist across runs.
- Map one project directory into the container and launch PyCharm directly against that project.
- Do not mount arbitrary host directories into the container. Other than the project directory, the IDE state directory, and the plugins directory, avoid exposing host directories to PyCharm.
- Include the usual Linux development/debugging tools inside the image: `ssh`, `git`, `netcat`, `nslookup`, `strace`, and other bread-and-butter development utilities.
- Support GitHub fetch/push workflows without baking credentials into the image. The first revision supports SSH agent forwarding and an optional HTTPS token mounted as a temporary secret file.
- Accept PyCharm either as a `.tar.gz` distribution or as an already-unpacked folder supplied to the image build script.

The first implementation generated the following files, which should live under `docker4pycharm/` in this repository:

```text
docker4pycharm/
  Dockerfile
  build-image.sh
  run-pycharm-container.sh
  entrypoint.sh
  README.md
```

This root `README.md` is intentionally broader than `docker4pycharm/README.md`. It records the design rationale and project continuation notes so a future development agent does not lose context.

## Important design decision: `docker run` wrapper instead of pure `docker start`

The user mentioned `docker start ...` as an acceptable target. The first implementation uses a launcher script around `docker run` instead.

Reason: project path, X11 authorization file, SSH agent socket, optional GitHub token, user/group mapping, and temporary runtime files are all per-invocation inputs. These are naturally container-creation options, not restart options. A pre-created container started with `docker start` would make these inputs awkward or stale.

The wrapper still gives the user a stable start command:

```bash
./docker4pycharm/run-pycharm-container.sh --project /path/to/project --ssh-agent
```

A future revision may add a convenience top-level command such as `./run-ide pycharm --project ...`, but it should preserve the per-run mount and credential model.

## Current architecture

### Image

The image is built from `ubuntu:24.04`. The supplied PyCharm distribution is normalized into the Docker build context as `pycharm/` and copied into:

```text
/opt/pycharm
```

The image symlinks PyCharm to:

```text
/usr/local/bin/pycharm
```

The default entrypoint is:

```text
/usr/bin/tini -- /usr/local/bin/entrypoint.sh
```

### Runtime mounts

The launcher mounts only the required host resources by default:

```text
/project       -> selected host project directory, read/write
/ide-state     -> persistent PyCharm state root, read/write
/ide-plugins   -> persistent PyCharm plugins root, read/write
/tmp/.X11-unix -> host X11 socket directory, read-only
/tmp/.docker.xauth -> temporary generated Xauthority file, read-only
/etc/passwd    -> temporary generated passwd file, read-only
/etc/group     -> temporary generated group file, read-only
```

Optional mounts:

```text
/run/host-ssh-agent.sock      -> host SSH agent socket, only with --ssh-agent
/run/secrets/github-token     -> temporary GitHub HTTPS token file, only with --github-token-file or --github-token-env
```

The default persistent host locations are:

```text
~/.local/share/pycharm-docker/state
~/.local/share/pycharm-docker/plugins
```

These can be overridden with:

```bash
--state /some/state/dir
--plugins /some/plugins/dir
```

### PyCharm state redirection

The container entrypoint creates an `idea.properties` file at runtime and sets `PYCHARM_PROPERTIES` so PyCharm uses externalized state paths:

```properties
idea.config.path=/ide-state/config
idea.system.path=/ide-state/system
idea.plugins.path=/ide-plugins
idea.log.path=/ide-state/log
```

The container also sets:

```text
HOME=/ide-state/home
XDG_CONFIG_HOME=/ide-state/home/.config
XDG_CACHE_HOME=/ide-state/home/.cache
XDG_DATA_HOME=/ide-state/home/.local/share
```

This gives PyCharm, Git, SSH, shell tools, and plugins a writable home-like location without mounting the host home directory.

### PyCharm launch behavior

PyCharm is launched with the selected project mounted as `/project` and passed as the command-line argument:

```bash
/opt/pycharm/bin/pycharm.sh /project
```

This should open PyCharm directly on the mapped project directory.

### GUI model

Revision 0 uses X11 forwarding through the host X socket:

```text
/tmp/.X11-unix
```

The launcher creates a temporary Xauthority file using `xauth nlist` and `xauth nmerge`, then mounts it into the container as `/tmp/.docker.xauth`.

If PyCharm cannot connect to the display because no Xauthority cookie was copied, the wrapper warns that the user may need to allow the local user explicitly, for example:

```bash
xhost +SI:localuser:$(id -un)
```

This is a pragmatic development-workstation choice, not a perfect GUI security boundary. Future revisions may evaluate `xpra`, VNC, Waypipe, a nested X server, or a dedicated untrusted X session.

### Security posture

The first launcher aims for a constrained default profile:

- `--read-only` root filesystem by default.
- Writable `tmpfs` mounts for `/tmp`, `/run`, and `/var/tmp`.
- `--cap-drop ALL` by default.
- `--security-opt no-new-privileges`.
- Private IPC namespace.
- PID limit.
- No host `$HOME` mount.
- No host `~/.ssh` mount.
- No Docker socket mount.
- No system package-cache or language-environment mounts from the host.

The project directory is mounted read/write because normal IDE operation requires editing project files. PyCharm settings, caches, plugins, logs, SSH known-hosts, and any IDE-local home files are stored under `/ide-state` or `/ide-plugins`.

### Native-debugging exception

Native debugging and some `strace` workflows require extra privileges. The launcher supports:

```bash
./docker4pycharm/run-pycharm-container.sh --project /repo --debug-native
```

This adds:

```text
--cap-add SYS_PTRACE
--security-opt seccomp=unconfined
```

Use this only when needed for native debugging, non-child process tracing, or similar development work.

### GitHub credential model

The first implementation avoids mounting host `~/.ssh` or embedding credentials in the image.

Preferred SSH workflow:

```bash
ssh-add -l
./docker4pycharm/run-pycharm-container.sh --project /repo --ssh-agent
```

The container gets only the forwarded SSH agent socket. SSH known-hosts are stored in `/ide-state/home/.ssh/known_hosts`, not on the host home directory.

Optional HTTPS token workflow:

```bash
export GITHUB_TOKEN=ghp_...
./docker4pycharm/run-pycharm-container.sh \
  --project /repo \
  --github-token-env GITHUB_TOKEN
```

The wrapper writes the environment variable value to a temporary file, mounts that file read-only at `/run/secrets/github-token`, and configures `GIT_ASKPASS` inside the container. This avoids persisting the token in the Docker image and avoids placing it directly in a long-lived Docker environment variable.

A token file can also be supplied directly:

```bash
./docker4pycharm/run-pycharm-container.sh \
  --project /repo \
  --github-token-file /path/to/token-file
```

## Installed tool baseline

Revision 0 installs common development and debugging utilities including:

```text
ca-certificates curl wget git openssh-client gnupg2 xauth
build-essential make cmake pkg-config gcc g++ gdb lldb
python3 python3-pip python3-venv python3-dev
netcat-openbsd dnsutils iproute2 iputils-ping traceroute
procps psmisc lsof strace tcpdump socat telnet whois
jq ripgrep fd-find fzf tree less vim-tiny nano
tini
```

It also installs X11/GTK/font libraries needed by JetBrains IDEs:

```text
libx11-6 libxext6 libxrender1 libxtst6 libxi6 libxrandr2 libxss1 libxkbfile1
libgtk-3-0 libnss3 libnspr4 libasound2t64 libfontconfig1 libfreetype6
libdbus-1-3 xdg-utils fonts-dejavu fonts-liberation
```

## Build and run quickstart

From the repository root:

```bash
cd docker4pycharm

./build-image.sh \
  --pycharm /path/to/pycharm-professional-or-community.tar.gz
```

Or with an unpacked PyCharm directory:

```bash
cd docker4pycharm

./build-image.sh \
  --pycharm /path/to/unpacked/pycharm
```

Run PyCharm on a project:

```bash
./docker4pycharm/run-pycharm-container.sh \
  --project /path/to/project \
  --ssh-agent
```

Use a custom image name:

```bash
./docker4pycharm/build-image.sh \
  --pycharm /path/to/pycharm.tar.gz \
  --image docker4pycharm:dev

./docker4pycharm/run-pycharm-container.sh \
  --image docker4pycharm:dev \
  --project /path/to/project \
  --ssh-agent
```

## AI plugin direction

The near-term ChatGPT/Codex integration path for PyCharm is documented separately in `user.md`.

As of the documentation checked on 2026-06-18, the recommended path is:

1. Use PyCharm/JetBrains IDE version 2025.3 or newer for Codex in JetBrains AI Chat.
2. Install or update the JetBrains AI Assistant plugin.
3. Open the JetBrains AI Chat/widget.
4. Authenticate using the user’s ChatGPT account.
5. Select Codex from the agent picker in AI Chat.

This is preferable to installing a random third-party “ChatGPT” plugin, because the JetBrains/OpenAI-supported path integrates Codex into JetBrains AI Chat and supports ChatGPT account sign-in.

Potential container-specific issue: account login flows may open a browser or localhost callback. Because PyCharm is running inside Docker, the login flow should be tested early. If browser handoff fails, likely mitigation paths include:

- Use the “copy URL” or manual sign-in option if the plugin offers one.
- Temporarily pass through a host browser via `xdg-open` bridging in a future launcher revision.
- Use an OpenAI API key or JetBrains AI subscription authentication path if ChatGPT-account OAuth proves awkward inside the container.
- Consider a launcher option for host networking only during sign-in, if strictly necessary and documented.

Do not add such relaxations silently. Treat them as explicit, auditable options.

## Future development backlog

Suggested next work items:

1. Move the current generated files into `docker4pycharm/` and keep this root README as the project-level context.
2. Add a top-level wrapper, for example `./run-ide pycharm --project ...`, that delegates to `docker4pycharm/run-pycharm-container.sh`.
3. Add automated shell linting and smoke tests for the launcher scripts.
4. Add a minimal X11 smoke test command such as `xeyes` or `xclock` in a diagnostic mode, if an appropriate package is installed.
5. Add a `--project-readonly` mode for code review or browsing use cases.
6. Add a `--network none` mode for high-isolation sessions, plus documented exceptions for Git/AI plugin workflows.
7. Add a separate `--login-relaxed` or similar mode only if AI plugin OAuth requires additional browser/network handling.
8. Consider rootless Docker or Podman compatibility.
9. Consider Wayland-native and `xpra`/VNC alternatives to direct X11 socket sharing.
10. Consider a per-project state namespace so different projects can have separate IDE caches and plugin sets when desired.
11. Add a mechanism for passing additional trusted CA certificates or corporate proxy settings without mounting host-wide directories.
12. Add clear documentation for Claude-related plugins in a later revision, after verifying the current recommended PyCharm integration path.

## Guidance for future AI development agents

When continuing this project inside the bootstrapped IDE:

- Preserve the core isolation principle: do not mount host directories beyond the explicitly selected project, IDE state, IDE plugins, and narrowly scoped runtime/credential resources.
- Prefer explicit launcher options over broad default access.
- Do not mount the host Docker socket by default.
- Do not mount host `~/.ssh`; use SSH agent forwarding or explicit secret files.
- Do not persist API keys or OAuth tokens into the image.
- Treat AI plugin authentication as a first-class integration test.
- Make security relaxations opt-in, visible in command-line flags, and documented.
- Keep `docker4pycharm/README.md` focused on that subproject’s operational usage.
- Keep this root `README.md` focused on project-wide context, design rationale, and future direction.

## Reference links checked during bootstrap

These links were used to validate the current PyCharm/OpenAI/JetBrains assumptions. Re-check them before making future authentication or plugin recommendations, because IDE plugin behavior and subscription rules can change.

- OpenAI Codex IDE extension documentation: https://developers.openai.com/codex/ide
- JetBrains blog: Codex is integrated into JetBrains IDEs: https://blog.jetbrains.com/ai/2026/01/codex-in-jetbrains-ides/
- JetBrains AI Assistant installation guide: https://www.jetbrains.com/help/ai-assistant/installation-guide-ai-assistant.html
- JetBrains AI Assistant Marketplace page: https://plugins.jetbrains.com/plugin/22282-jetbrains-ai-assistant
