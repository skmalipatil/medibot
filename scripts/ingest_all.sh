#!/usr/bin/env bash
# medibot — ingest every collection into Qdrant.
#
# Usage:
#   ./scripts/ingest_all.sh
#
# Assumes:
#   * Qdrant is running   (docker compose up -d)
#   * .env is filled      (cp .env.example .env)
#   * data/mediassist_data/<collection>/ folders exist

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ ! -f .env ]; then
  echo "ERROR: .env not found. Run: cp .env.example .env  (then add your Gemini key)"
  exit 1
fi

echo "==> Checking Qdrant..."
QDRANT_URL="$(grep -E '^QDRANT_URL=' .env | cut -d= -f2- || true)"
QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"
curl -fsS "${QDRANT_URL}/healthz" > /dev/null || {
  echo "ERROR: Qdrant not reachable at ${QDRANT_URL}. Run: docker compose up -d"
  exit 1
}

echo "==> Running ingestion for all collections..."
python -m backend.ingest --all

echo "==> Done."
