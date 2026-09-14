#!/usr/bin/env bash
set -euo pipefail

if command -v mongod >/dev/null 2>&1; then
  exit 0
fi

if ! command -v apt-get >/dev/null 2>&1; then
  echo "MongoDB is not installed and apt-get is unavailable. Set MONGODB_URI to a remote cluster."
  exit 1
fi

sudo install -m 0755 -d /usr/share/keyrings
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc \
  | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" \
  | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list >/dev/null

sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq mongodb-org
