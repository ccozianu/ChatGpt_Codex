#!/usr/bin/env bash
set -euo pipefail

IMAGE="${IMAGE:-pycharm-isolated:latest}"
NAME="pycharm-isolated-$(id -un)-$(date +%s)"
PROJECT=""
BASE_DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/pycharm-docker"
GLOBAL_SETTINGS_DIR="${PYCHARM_GLOBAL_SETTINGS_DIR:-$BASE_DATA_DIR/state}"
PROJECT_STATE_DIR="${PYCHARM_PROJECT_STATE_DIR:-}"
PLUGIN_DIR="${PYCHARM_PLUGIN_DIR:-$BASE_DATA_DIR/plugins}"
PROJECT_MOUNT="${PYCHARM_PROJECT_MOUNT:-}"
USE_SSH_AGENT=0
GITHUB_TOKEN_FILE=""
GITHUB_TOKEN_ENV=""
GITHUB_USER="x-access-token"
DEBUG_NATIVE=0
WRITABLE_ROOT=0
DOCKER_MODE="${DOCKER_MODE:-}"
HOST_DOCKER_SOCKET="${HOST_DOCKER_SOCKET:-/var/run/docker.sock}"
HOST_DOCKER_GID=""
EXTRA_DOCKER_ARGS=()
PYCHARM_LIBGL_ALWAYS_SOFTWARE="${PYCHARM_LIBGL_ALWAYS_SOFTWARE-${LIBGL_ALWAYS_SOFTWARE-1}}"
PYCHARM_MESA_LOADER_DRIVER_OVERRIDE="${PYCHARM_MESA_LOADER_DRIVER_OVERRIDE-${MESA_LOADER_DRIVER_OVERRIDE-llvmpipe}}"
PYCHARM_LIBGL_DRI3_DISABLE="${PYCHARM_LIBGL_DRI3_DISABLE-${LIBGL_DRI3_DISABLE-1}}"

sanitize_name() {
  local value="$1"

  value="$(printf '%s' "$value" | tr -c '[:alnum:]._-' '-')"
  while [[ "$value" == -* ]]; do
    value="${value#-}"
  done
  while [[ "$value" == *- ]]; do
    value="${value%-}"
  done

  if [ -z "$value" ]; then
    value="project"
  fi

  printf '%s' "$value"
}

project_namespace() {
  local path="$1"
  local base safe_base hash

  base="$(basename "$path")"
  safe_base="$(sanitize_name "$base")"
  if command -v sha256sum >/dev/null 2>&1; then
    hash="$(printf '%s' "$path" | sha256sum)"
    hash="${hash%% *}"
    hash="${hash:0:12}"
  else
    hash="$(printf '%s' "$path" | cksum)"
    hash="${hash%% *}"
  fi

  printf '%s-%s' "$hash" "$safe_base"
}

if [ -z "${DOCKER_MODE:-}" ]; then
  if [ -n "${DOCKER_IN_DOCKER:-}" ]; then
    case "$DOCKER_IN_DOCKER" in
      1|true|TRUE|yes|YES|on|ON) DOCKER_MODE="dind" ;;
      0|false|FALSE|no|NO|off|OFF) DOCKER_MODE="none" ;;
      *) echo "DOCKER_IN_DOCKER must be 1/0, true/false, yes/no, or on/off." >&2; exit 2 ;;
    esac
  else
    DOCKER_MODE="host"
  fi
fi

usage() {
  cat <<'USAGE'
Usage:
  ./run-pycharm-container.sh --project /path/to/project [options]

Options:
  --image IMAGE                 Docker image to run. Default: pycharm-isolated:latest
  --name NAME                   Container name. Default: unique name with timestamp
  --global-settings DIR         Shared IDE config/home root. Default: ~/.local/share/pycharm-docker/state
  --state DIR                   Legacy alias for --global-settings
  --project-state DIR           Per-project IDE cache/log/workspace root. Default: auto under ~/.local/share/pycharm-docker/project-state
  --project-mount PATH          In-container project path. Default: /workspace/<project-id>
  --plugins DIR                 Persistent PyCharm plugins dir. Default: ~/.local/share/pycharm-docker/plugins
  --ssh-agent                   Forward host SSH agent socket into the container
  --github-token-file FILE      Mount an HTTPS GitHub token file for Git askpass
  --github-token-env ENVVAR     Read token from host ENVVAR, place it in a temporary mounted file
  --github-user USER            Username for HTTPS GitHub askpass. Default: x-access-token
  --docker, --host-docker       Connect to the host Docker daemon through /var/run/docker.sock. Default
  --docker-socket SOCKET        Host Docker socket for --docker. Default: /var/run/docker.sock
  --docker-in-docker, --dind    Start an isolated inner Docker daemon. Requires --privileged
  --no-docker                   Disable Docker access and use the stricter container profile
  --debug-native                Add ptrace/seccomp permissions for native debugging/strace of non-child processes
  --writable-root               Do not run the container with a read-only root filesystem
  --docker-arg ARG              Append one raw docker-run argument; repeat for advanced cases
  -h, --help                    Show this help

Mesa/OpenGL defaults:
  The launcher defaults JetBrains/Skiko GL to Mesa llvmpipe software rendering
  so X11 runs without mounting host /dev/dri devices. Override with
  PYCHARM_LIBGL_ALWAYS_SOFTWARE, PYCHARM_MESA_LOADER_DRIVER_OVERRIDE, or
  PYCHARM_LIBGL_DRI3_DISABLE when testing another rendering path.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --project) PROJECT="${2:?missing value for --project}"; shift 2 ;;
    --image) IMAGE="${2:?missing value for --image}"; shift 2 ;;
    --name) NAME="${2:?missing value for --name}"; shift 2 ;;
    --global-settings) GLOBAL_SETTINGS_DIR="${2:?missing value for --global-settings}"; shift 2 ;;
    --state) GLOBAL_SETTINGS_DIR="${2:?missing value for --state}"; shift 2 ;;
    --project-state) PROJECT_STATE_DIR="${2:?missing value for --project-state}"; shift 2 ;;
    --project-mount) PROJECT_MOUNT="${2:?missing value for --project-mount}"; shift 2 ;;
    --plugins) PLUGIN_DIR="${2:?missing value for --plugins}"; shift 2 ;;
    --ssh-agent) USE_SSH_AGENT=1; shift ;;
    --github-token-file) GITHUB_TOKEN_FILE="${2:?missing value for --github-token-file}"; shift 2 ;;
    --github-token-env) GITHUB_TOKEN_ENV="${2:?missing value for --github-token-env}"; shift 2 ;;
    --github-user) GITHUB_USER="${2:?missing value for --github-user}"; shift 2 ;;
    --docker|--host-docker) DOCKER_MODE=host; shift ;;
    --docker-socket) HOST_DOCKER_SOCKET="${2:?missing value for --docker-socket}"; shift 2 ;;
    --docker-in-docker|--dind) DOCKER_MODE=dind; shift ;;
    --no-docker) DOCKER_MODE=none; shift ;;
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
case "$DOCKER_MODE" in
  host|HOST|docker|DOCKER|socket|SOCKET) DOCKER_MODE=host ;;
  dind|DIND|docker-in-docker|DOCKER-IN-DOCKER) DOCKER_MODE=dind ;;
  none|NONE|off|OFF|no|NO|false|FALSE|0) DOCKER_MODE=none ;;
  *) echo "DOCKER_MODE must be host, dind, or none." >&2; exit 2 ;;
esac

PROJECT="$(readlink -f "$PROJECT")"
PROJECT_ID="$(project_namespace "$PROJECT")"
if [ -z "$PROJECT_STATE_DIR" ]; then
  PROJECT_STATE_DIR="$BASE_DATA_DIR/project-state/$PROJECT_ID"
fi
if [ -z "$PROJECT_MOUNT" ]; then
  PROJECT_MOUNT="/workspace/$PROJECT_ID"
fi
if [ "$PROJECT_MOUNT" != "/" ]; then
  PROJECT_MOUNT="${PROJECT_MOUNT%/}"
fi
case "$PROJECT_MOUNT" in
  /*) ;;
  *) echo "--project-mount must be an absolute in-container path." >&2; exit 2 ;;
esac
case "$PROJECT_MOUNT" in
  /|/dev|/dev/*|/etc|/etc/*|/home|/home/*|/ide-global-settings|/ide-global-settings/*|/ide-plugins|/ide-plugins/*|/ide-project-state|/ide-project-state/*|/opt|/opt/*|/proc|/proc/*|/run|/run/*|/sys|/sys/*|/tmp|/tmp/*|/usr|/usr/*|/var|/var/*)
    echo "--project-mount uses a reserved container path: $PROJECT_MOUNT" >&2
    exit 2
    ;;
esac
GLOBAL_SETTINGS_DIR="$(mkdir -p "$GLOBAL_SETTINGS_DIR" && readlink -f "$GLOBAL_SETTINGS_DIR")"
PROJECT_STATE_DIR="$(mkdir -p "$PROJECT_STATE_DIR" && readlink -f "$PROJECT_STATE_DIR")"
PLUGIN_DIR="$(mkdir -p "$PLUGIN_DIR" && readlink -f "$PLUGIN_DIR")"

if [ ! -d "$PROJECT" ]; then
  echo "Project directory does not exist: $PROJECT" >&2
  exit 1
fi

if [ "$DOCKER_MODE" = "host" ]; then
  if [ ! -S "$HOST_DOCKER_SOCKET" ]; then
    echo "Host Docker socket is not available: $HOST_DOCKER_SOCKET" >&2
    echo "Start Docker on the host, set HOST_DOCKER_SOCKET, or launch with --docker-in-docker / --no-docker." >&2
    exit 1
  fi
  HOST_DOCKER_SOCKET="$(readlink -f "$HOST_DOCKER_SOCKET")"
  HOST_DOCKER_GID="$(stat -c '%g' "$HOST_DOCKER_SOCKET")"
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
$(id -un):x:$(id -u):$(id -g):PyCharm Docker User:/ide-global-settings/home:/bin/bash
EOF_PASSWD
cat > "$GROUP_FILE" <<EOF_GROUP
root:x:0:
$(id -gn):x:$(id -g):
EOF_GROUP
if [ -n "$HOST_DOCKER_GID" ] && [ "$HOST_DOCKER_GID" != "$(id -g)" ]; then
  echo "host-docker:x:$HOST_DOCKER_GID:" >> "$GROUP_FILE"
fi
chmod 644 "$PASSWD_FILE" "$GROUP_FILE"

# Docker --mount values are intentionally comma-delimited single arguments.
# shellcheck disable=SC2054
DOCKER_ARGS=(
  --rm
  -i
  --name "$NAME"
  --network=host
  --workdir "$PROJECT_MOUNT"
  --env DISPLAY
  --env XAUTHORITY=/tmp/.docker.xauth
  --env PROJECT_PATH="$PROJECT_MOUNT"
  --env HOME=/ide-global-settings/home
  --env CODEX_HOME=/ide-global-settings/home/.codex
  --env XDG_CONFIG_HOME=/ide-global-settings/home/.config
  --env XDG_CACHE_HOME=/ide-project-state/home/.cache
  --env XDG_DATA_HOME=/ide-global-settings/home/.local/share
  --env IDE_GLOBAL_SETTINGS_PATH=/ide-global-settings
  --env IDE_PROJECT_STATE_PATH=/ide-project-state
  --env IDE_UID="$(id -u)"
  --env IDE_GID="$(id -g)"
  --env IDE_USER="$(id -un)"
  --env QT_X11_NO_MITSHM=1
  --env _JAVA_AWT_WM_NONREPARENTING=1
  --env LIBGL_ALWAYS_SOFTWARE="$PYCHARM_LIBGL_ALWAYS_SOFTWARE"
  --env MESA_LOADER_DRIVER_OVERRIDE="$PYCHARM_MESA_LOADER_DRIVER_OVERRIDE"
  --env LIBGL_DRI3_DISABLE="$PYCHARM_LIBGL_DRI3_DISABLE"
  --env GITHUB_USER="$GITHUB_USER"
  --mount "type=bind,src=$PROJECT,dst=$PROJECT_MOUNT"
  --mount "type=bind,src=$GLOBAL_SETTINGS_DIR,dst=/ide-global-settings"
  --mount "type=bind,src=$PROJECT_STATE_DIR,dst=/ide-project-state"
  --mount "type=bind,src=$PLUGIN_DIR,dst=/ide-plugins"
  --mount "type=bind,src=/tmp/.X11-unix,dst=/tmp/.X11-unix,ro"
  --mount "type=bind,src=$XAUTH_FILE,dst=/tmp/.docker.xauth,ro"
  --mount "type=bind,src=$PASSWD_FILE,dst=/etc/passwd,ro"
  --mount "type=bind,src=$GROUP_FILE,dst=/etc/group,ro"
  --tmpfs /tmp:rw,exec,nosuid,nodev,size=2g
  --tmpfs /run:rw,nosuid,nodev,size=128m
  --tmpfs /var/tmp:rw,exec,nosuid,nodev,size=1g
  --ipc private
  --pids-limit 4096
)

case "$DOCKER_MODE" in
  host)
    cat >&2 <<EOF_HOST_DOCKER
========================================================================
HOST DOCKER DAEMON IS CONNECTED TO THIS PYCHARM CONTAINER.

The launcher is mounting the host Docker socket:
  $HOST_DOCKER_SOCKET

Docker commands inside PyCharm/Codex operate on the host daemon. This is the
default local-development convenience mode, but it gives tools inside the IDE
broad control over host Docker images, containers, networks, and bind mounts.

For an isolated inner daemon, run:
  $0 --project "$PROJECT" --docker-in-docker

For a higher-isolation session with no Docker access, run:
  $0 --project "$PROJECT" --no-docker
========================================================================
EOF_HOST_DOCKER
    DOCKER_ARGS+=(
      --user "$(id -u):$(id -g)"
      --group-add "$HOST_DOCKER_GID"
      --env ENABLE_DIND=0
      --env DOCKER_HOST=unix:///run/host-docker.sock
      --mount "type=bind,src=$HOST_DOCKER_SOCKET,dst=/run/host-docker.sock"
      --cap-drop ALL
      --security-opt no-new-privileges
    )
    ;;
  dind)
  cat >&2 <<EOF_DIND
========================================================================
DOCKER-IN-DOCKER IS ENABLED FOR THIS PYCHARM CONTAINER.

The launcher is starting this IDE container with --privileged, a writable
root filesystem, and an inner Docker daemon. Use this when you want separate
Docker images, containers, and volumes inside the PyCharm environment.
The inner daemon does not manage bridge/iptables networking; use --network host
for inner builds that need network access.

To use the default host Docker daemon instead, run:
  $0 --project "$PROJECT" --docker

To turn Docker off for a higher-isolation session, run:
  $0 --project "$PROJECT" --no-docker
========================================================================
EOF_DIND
  DOCKER_ARGS+=(
    --privileged
    --env ENABLE_DIND=1
    --mount "type=volume,dst=/var/lib/docker"
  )
    ;;
  none)
  DOCKER_ARGS+=(
    --user "$(id -u):$(id -g)"
    --env ENABLE_DIND=0
    --cap-drop ALL
    --security-opt no-new-privileges
  )
    ;;
esac

if [ "$WRITABLE_ROOT" -eq 0 ] && [ "$DOCKER_MODE" != "dind" ]; then
  DOCKER_ARGS+=(--read-only)
fi

if [ "$DEBUG_NATIVE" -eq 1 ] && [ "$DOCKER_MODE" != "dind" ]; then
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

cat >&2 <<EOF_STORAGE
PyCharm storage:
  Shared global settings: $GLOBAL_SETTINGS_DIR
  Shared plugins:         $PLUGIN_DIR
  Per-project state:      $PROJECT_STATE_DIR
  Container project path: $PROJECT_MOUNT
EOF_STORAGE

exec docker run "${DOCKER_ARGS[@]}" "$IMAGE" /opt/pycharm/bin/pycharm.sh "$PROJECT_MOUNT"
