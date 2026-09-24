#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "${ROOT}/data"
echo "SQLite data directory ready at ${ROOT}/data"
