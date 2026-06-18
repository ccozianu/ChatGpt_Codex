#!/usr/bin/env bash
set -euo pipefail

: "${PROJECT_PATH:=/project}"
: "${HOME:=/ide-state/home}"

mkdir -p \
  "$HOME" \
  "$HOME/.ssh" \
  /ide-state/config \
  /ide-state/system \
  /ide-state/log \
  /ide-plugins
chmod 700 "$HOME/.ssh" 2>/dev/null || true

IDEA_PROPERTIES=/tmp/pycharm-docker.idea.properties
cat > "$IDEA_PROPERTIES" <<EOF_PROPS
idea.config.path=/ide-state/config
idea.system.path=/ide-state/system
idea.plugins.path=/ide-plugins
idea.log.path=/ide-state/log
EOF_PROPS
export PYCHARM_PROPERTIES="$IDEA_PROPERTIES"

# Keep GitHub SSH first-use state inside the isolated IDE home, not in the host home.
if [ ! -f "$HOME/.ssh/config" ]; then
  cat > "$HOME/.ssh/config" <<'EOF_SSH'
Host github.com
  StrictHostKeyChecking accept-new
  UserKnownHostsFile ~/.ssh/known_hosts
EOF_SSH
  chmod 600 "$HOME/.ssh/config" 2>/dev/null || true
fi

# Optional HTTPS GitHub credential path. The wrapper mounts the token as a file
# rather than exposing it as a long-lived Docker environment variable.
if [ -n "${GITHUB_TOKEN_FILE:-}" ] && [ -r "${GITHUB_TOKEN_FILE}" ]; then
  ASKPASS=/tmp/git-askpass-github.sh
  cat > "$ASKPASS" <<'EOF_ASKPASS'
#!/usr/bin/env sh
case "$1" in
  *Username*|*username*) printf '%s\n' "${GITHUB_USER:-x-access-token}" ;;
  *Password*|*password*) cat "${GITHUB_TOKEN_FILE}" ;;
  *) printf '\n' ;;
esac
EOF_ASKPASS
  chmod 700 "$ASKPASS"
  export GIT_ASKPASS="$ASKPASS"
  export GIT_TERMINAL_PROMPT=0
fi

if [ "$#" -eq 0 ]; then
  set -- /opt/pycharm/bin/pycharm.sh "$PROJECT_PATH"
fi

exec "$@"
