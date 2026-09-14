#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"${ROOT}/scripts/install-mongodb.sh"
"${ROOT}/scripts/start-mongodb.sh"
