#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/build-pex.sh [--output dist/devcapsule.pex]

Build a single-file DevCapsule PEX archive from the local package and the
pinned runtime dependency lock file.

Environment:
  PYTHON                 Python executable used to run PEX. Default: python
  DOCKER4IDES_PEX_SHEBANG  Shebang embedded in the archive.
                           Default: /usr/bin/env python3.12
  DOCKER4IDES_RUNTIME_PEX_ROOT
                         Runtime extraction/cache root embedded in the archive.
                         Default: /tmp/devcapsule-pex-root
USAGE
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd "${script_dir}/.." && pwd)"
output="${project_dir}/dist/devcapsule.pex"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output)
      if [[ $# -lt 2 ]]; then
        echo "scripts/build-pex.sh: --output requires a path" >&2
        exit 2
      fi
      output="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "scripts/build-pex.sh: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

python_bin="${PYTHON:-python}"
pex_shebang="${DOCKER4IDES_PEX_SHEBANG:-/usr/bin/env python3.12}"
runtime_pex_root="${DOCKER4IDES_RUNTIME_PEX_ROOT:-/tmp/devcapsule-pex-root}"

if ! "${python_bin}" -c "import pex" >/dev/null 2>&1; then
  cat >&2 <<EOF
scripts/build-pex.sh: PEX is not installed for ${python_bin}.

Set up contributor dependencies first, or point PYTHON at that environment:
  python -m pip install -r devcapsule/dev-requirements.txt
  python -m pip install -e ./devcapsule --no-deps
  PYTHON=/path/to/venv/bin/python devcapsule/scripts/build-pex.sh
EOF
  exit 1
fi

mkdir -p "$(dirname "${output}")"

cd "${project_dir}"
rm -rf build devcapsule.egg-info
exec "${python_bin}" -m pex \
  -r requirements.txt \
  . \
  -c devcapsule \
  --python-shebang "${pex_shebang}" \
  --runtime-pex-root "${runtime_pex_root}" \
  -o "${output}"
