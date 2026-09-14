#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

DATA_DIR="${MONGODB_DATA_DIR:-/tmp/fastapi-tutorials-mongo}"
PORT="${MONGODB_PORT:-27017}"
PID_FILE="${DATA_DIR}/mongod.pid"
LOG_FILE="${DATA_DIR}/mongod.log"

mkdir -p "${DATA_DIR}"

if [[ -f "${PID_FILE}" ]] && kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
  echo "MongoDB already running (pid $(cat "${PID_FILE}")) on port ${PORT}"
  exit 0
fi

if command -v mongod >/dev/null 2>&1; then
  mongod --dbpath "${DATA_DIR}" --port "${PORT}" --bind_ip 127.0.0.1 \
    --logpath "${LOG_FILE}" --fork --pidfilepath "${PID_FILE}"
  echo "MongoDB started on mongodb://127.0.0.1:${PORT}"
  exit 0
fi

DOCKER=(docker)
if ! docker info >/dev/null 2>&1; then
  if sudo docker info >/dev/null 2>&1; then
    DOCKER=(sudo docker)
  else
    echo "Install MongoDB (mongodb-org) or Docker to run a local database."
    exit 1
  fi
fi

"${DOCKER[@]}" compose up -d mongodb

echo "Waiting for MongoDB to become healthy..."
for _ in $(seq 1 60); do
  if "${DOCKER[@]}" compose exec -T mongodb mongosh --quiet --eval "db.adminCommand('ping').ok" 2>/dev/null | grep -q 1; then
    echo "MongoDB is ready on localhost:${PORT}"
    exit 0
  fi
  sleep 1
done

echo "MongoDB did not become ready in time."
exit 1
