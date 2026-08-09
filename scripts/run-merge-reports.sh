#!/usr/bin/env bash
# ==============================================================================
# merge-reports.py wrapper — this is a shell pass-through
# The actual Python script is merge-reports.py in the same directory.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/merge-reports.py" "$@"
