#!/usr/bin/env bash
# Thin wrapper around extract_layout.py. Forwards all args.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python "${HERE}/extract_layout.py" "$@"
