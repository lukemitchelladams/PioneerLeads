#!/bin/bash
# SessionStart hook for Brown Bison cloud sessions.
# Sync mode on purpose: guarantees tooling is ready before the agent starts.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

# PDF text extraction + Playwright (browsers pre-installed at /opt/pw-browsers); idempotent
for mod in pypdf playwright; do
  if ! python3 -c "import $mod" 2>/dev/null; then
    python3 -m pip install --quiet --disable-pip-version-check "$mod" >/dev/null 2>&1 || true
  fi
done

echo "== Brown Bison workspace =="
echo "Read memory/MEMORY.md before doing anything."
echo
sed -n '1,40p' memory/MEMORY.md 2>/dev/null || true
