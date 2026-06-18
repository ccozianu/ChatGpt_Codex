# Docker PyCharm Isolation R0

This is a first-revision Docker/X11 wrapper for running a tarball-based PyCharm
installation in an isolated Linux container while keeping project files,
PyCharm state, and plugins persistent on the host.

## Build

```bash
./build-image.sh --pycharm /path/to/pycharm-professional-2026.1.tar.gz
# or
./build-image.sh --pycharm /path/to/unpacked/pycharm
```

## Run

```bash
./run-pycharm-container.sh --project /path/to/project --ssh-agent
```

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
