#!/usr/bin/env bash
# Thin wrapper around create_and_test.py. Forwards all args.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python "${HERE}/create_and_test.py" "$@"
