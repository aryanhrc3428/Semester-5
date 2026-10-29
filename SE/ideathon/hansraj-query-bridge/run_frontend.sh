#!/usr/bin/env bash
# Starts the web app on http://localhost:3000 (development mode).
set -e
cd "$(dirname "$0")/frontend"
[ -d node_modules ] || npm install --no-audit --no-fund
exec npm run dev
