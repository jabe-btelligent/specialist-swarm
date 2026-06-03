#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

HOST="${HOST:-127.0.0.1}"
PORT="${1:-${PORT:-8000}}"
ADDRESS="http://${HOST}:${PORT}/"

echo "Starting AAPL stock-ranking live demo server..."
echo "Open: ${ADDRESS}"
echo

uv run python demo_server.py --host "${HOST}" --port "${PORT}"
