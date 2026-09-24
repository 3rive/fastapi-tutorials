#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if ! python3 -m venv /tmp/venv-check 2>/dev/null; then
  if command -v apt-get >/dev/null 2>&1; then
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3.12-venv
  fi
  rm -rf /tmp/venv-check
fi
rm -rf /tmp/venv-check

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

# shellcheck source=/dev/null
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [[ -f entitlements-mfe/package.json ]]; then
  (cd entitlements-mfe && npm install)
fi
