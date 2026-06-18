#!/usr/bin/env bash
set -euo pipefail

IMAGE="${IMAGE:-pycharm-isolated:latest}"
NAME="pycharm-isolated-$(id -un)-$(date +%s)"
PROJECT=""
STATE_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/pycharm-docker/state"
PLUGIN_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/pycharm-docker/plugins"
USE_SSH_AGENT=0
GITHUB_TOKEN_FILE=""
GITHUB_TOKEN_ENV=""
GITHUB_USER="x-access-token"
DEBUG_NATIVE=0
WRITABLE_ROOT=0
EXTRA_DOCKER_ARGS=()

usage() {
  cat <<'USAGE'
Usage:
  ./run-pycharm-container.sh --project /path/to/project [options]

Options:
  --image IMAGE                 Docker image to run. Default: pycharm-isolated:latest
  --name NAME                   Container name. Default: unique name with timestamp
  --state DIR                   Persistent IDE state root. Default: ~/.local/share/pycharm-docker/state
  --plugins DIR                 Persistent PyCharm plugins dir. Default: ~/.local/share/pycharm-docker/plugins
  --ssh-agent                   Forward host SSH agent socket into the container
  --github-token-file FILE      Mount an HTTPS GitHub token file for Git askpass
  --github-token-env ENVVAR     Read token from host ENVVAR, place it in a temporary mounted file
  --github-user USER            Username for HTTPS GitHub askpass. Default: x-access-token
  --debug-native                Add ptrace/seccomp permissions for native debugging/strace of non-child processes
  --writable-root               Do not run the container with a read-only root filesystem
  --docker-arg ARG              Append one raw docker-run argument; repeat for advanced cases
  -h, --help                    Show this help
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --project) PROJECT="${2:?missing value for --project}"; shift 2 ;;
    --image) IMAGE="${2:?missing value for --image}"; shift 2 ;;
    --name) NAME="${2:?missing value for --name}"; shift 2 ;;
    --state) STATE_DIR="${2:?missing value for --state}"; shift 2 ;;
    --plugins) PLUGIN_DIR="${2:?missing value for --plugins}"; shift 2 ;;
    --ssh-agent) USE_SSH_AGENT=1; shift ;;
    --github-token-file) GITHUB_TOKEN_FILE="${2:?missing value for --github-token-file}"; shift 2 ;;
    --github-token-env) GITHUB_TOKEN_ENV="${2:?missing value for --github-token-env}"; shift 2 ;;
    --github-user) GITHUB_USER="${2:?missing value for --github-user}"; shift 2 ;;
    --debug-native) DEBUG_NATIVE=1; shift ;;
    --writable-root) WRITABLE_ROOT=1; shift ;;
    --docker-arg) EXTRA_DOCKER_ARGS+=("${2:?missing value for --docker-arg}"); shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$PROJECT" ]; then
  echo "Missing --project" >&2
  usage >&2
  exit 2
fi
if [ -z "${DISPLAY:-}" ]; then
  echo "DISPLAY is not set; this X11 launcher needs an active X session." >&2
  exit 1
fi

PROJECT="$(readlink -f "$PROJECT")"
STATE_DIR="$(mkdir -p "$STATE_DIR" && readlink -f "$STATE_DIR")"
PLUGIN_DIR="$(mkdir -p "$PLUGIN_DIR" && readlink -f "$PLUGIN_DIR")"

if [ ! -d "$PROJECT" ]; then
  echo "Project directory does not exist: $PROJECT" >&2
  exit 1
fi

RUNTIME_PARENT="${XDG_RUNTIME_DIR:-/tmp}"
XAUTH_FILE="$(mktemp "$RUNTIME_PARENT/pycharm-docker-xauth.XXXXXX")"
PASSWD_FILE="$(mktemp "$RUNTIME_PARENT/pycharm-docker-passwd.XXXXXX")"
GROUP_FILE="$(mktemp "$RUNTIME_PARENT/pycharm-docker-group.XXXXXX")"
TOKEN_TMP=""
cleanup() {
  rm -f "$XAUTH_FILE" "$PASSWD_FILE" "$GROUP_FILE"
  [ -z "$TOKEN_TMP" ] || rm -f "$TOKEN_TMP"
}
trap cleanup EXIT

if command -v xauth >/dev/null 2>&1; then
  # Docker/X11 compatibility trick: convert the family field to FamilyWild.
  xauth nlist "$DISPLAY" 2>/dev/null | sed -e 's/^..../ffff/' | xauth -f "$XAUTH_FILE" nmerge - 2>/dev/null || true
fi
chmod 600 "$XAUTH_FILE"
if [ ! -s "$XAUTH_FILE" ]; then
  echo "Warning: no Xauthority cookie was copied. If PyCharm cannot open, run: xhost +SI:localuser:$(id -un)" >&2
fi

cat > "$PASSWD_FILE" <<EOF_PASSWD
root:x:0:0:root:/root:/bin/bash
$(id -un):x:$(id -u):$(id -g):PyCharm Docker User:/ide-state/home:/bin/bash
EOF_PASSWD
cat > "$GROUP_FILE" <<EOF_GROUP
root:x:0:
$(id -gn):x:$(id -g):
EOF_GROUP
chmod 644 "$PASSWD_FILE" "$GROUP_FILE"

DOCKER_ARGS=(
  --rm
  -i
  --name "$NAME"
  --network=host
  --user "$(id -u):$(id -g)"
  --workdir /project
  --env DISPLAY
  --env XAUTHORITY=/tmp/.docker.xauth
  --env PROJECT_PATH=/project
  --env HOME=/ide-state/home
  --env CODEX_HOME=/ide-state/home/.codex
  --env QT_X11_NO_MITSHM=1
  --env _JAVA_AWT_WM_NONREPARENTING=1
  --env GITHUB_USER="$GITHUB_USER"
  --mount "type=bind,src=$PROJECT,dst=/project"
  --mount "type=bind,src=$STATE_DIR,dst=/ide-state"
  --mount "type=bind,src=$PLUGIN_DIR,dst=/ide-plugins"
  --mount "type=bind,src=/tmp/.X11-unix,dst=/tmp/.X11-unix,ro"
  --mount "type=bind,src=$XAUTH_FILE,dst=/tmp/.docker.xauth,ro"
  --mount "type=bind,src=$PASSWD_FILE,dst=/etc/passwd,ro"
  --mount "type=bind,src=$GROUP_FILE,dst=/etc/group,ro"
  --tmpfs /tmp:rw,exec,nosuid,nodev,size=2g
  --tmpfs /run:rw,nosuid,nodev,size=128m
  --tmpfs /var/tmp:rw,exec,nosuid,nodev,size=1g
  --cap-drop ALL
  --security-opt no-new-privileges
  --ipc private
  --pids-limit 4096
)

if [ "$WRITABLE_ROOT" -eq 0 ]; then
  DOCKER_ARGS+=(--read-only)
fi

if [ "$DEBUG_NATIVE" -eq 1 ]; then
  DOCKER_ARGS+=(--cap-add SYS_PTRACE --security-opt seccomp=unconfined)
fi

if [ "$USE_SSH_AGENT" -eq 1 ]; then
  if [ -z "${SSH_AUTH_SOCK:-}" ] || [ ! -S "${SSH_AUTH_SOCK:-}" ]; then
    echo "--ssh-agent was requested, but SSH_AUTH_SOCK is not a socket." >&2
    exit 1
  fi
  DOCKER_ARGS+=(
    --mount "type=bind,src=$SSH_AUTH_SOCK,dst=/run/host-ssh-agent.sock"
    --env SSH_AUTH_SOCK=/run/host-ssh-agent.sock
  )
fi

if [ -n "$GITHUB_TOKEN_ENV" ]; then
  if [ -z "${!GITHUB_TOKEN_ENV:-}" ]; then
    echo "--github-token-env $GITHUB_TOKEN_ENV was requested, but that variable is empty or unset." >&2
    exit 1
  fi
  TOKEN_TMP="$(mktemp "$RUNTIME_PARENT/pycharm-docker-gh-token.XXXXXX")"
  printf '%s' "${!GITHUB_TOKEN_ENV}" > "$TOKEN_TMP"
  chmod 600 "$TOKEN_TMP"
  GITHUB_TOKEN_FILE="$TOKEN_TMP"
fi

if [ -n "$GITHUB_TOKEN_FILE" ]; then
  GITHUB_TOKEN_FILE="$(readlink -f "$GITHUB_TOKEN_FILE")"
  if [ ! -r "$GITHUB_TOKEN_FILE" ]; then
    echo "GitHub token file is not readable: $GITHUB_TOKEN_FILE" >&2
    exit 1
  fi
  DOCKER_ARGS+=(
    --mount "type=bind,src=$GITHUB_TOKEN_FILE,dst=/run/secrets/github-token,ro"
    --env GITHUB_TOKEN_FILE=/run/secrets/github-token
  )
fi

DOCKER_ARGS+=("${EXTRA_DOCKER_ARGS[@]}")

exec docker run "${DOCKER_ARGS[@]}" "$IMAGE" /opt/pycharm/bin/pycharm.sh /project
