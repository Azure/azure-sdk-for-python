#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# RESPONSIBILITY: compile the Rust extension that Python will actually import,
# and prove which file that is.
#
# Cargo fetches/resolves the locked driver dependency; maturin builds the binding
# and installs it in the active Python environment. Debug information is retained
# for native symbol lookup. Keep this exact binary with the capture.
#
# Importing checks which extension is loaded. It does not prove a read used it,
# and embedded commit labels alone are not source-to-binary attestation.
#
# The private counters supply binding-entry and recorded diagnostic evidence.
# They do not by themselves prove that a read reached the service backend.
#
# Usage:
#   ./profiling_build_extension.sh
# ---------------------------------------------------------------------------
set -uo pipefail
cd "$(dirname "$0")"

source ./profiling_common.sh
profiling_load_env || exit 2

PKG_ROOT="$(cd ../.. && pwd)"          # .../sdk/cosmos/azure-cosmos
PY_REPO="$(profiling_python_repo)" || exit 2
export AZURE_COSMOS_BUILD_PYTHON_COMMIT
export AZURE_COSMOS_BUILD_RUST_DRIVER_COMMIT
AZURE_COSMOS_BUILD_PYTHON_COMMIT="$(git -C "${PY_REPO}" rev-parse HEAD)" || exit 2
# Cargo resolves the pinned dependency, not the sibling checkout's HEAD.
cargo fetch --locked --manifest-path "${PKG_ROOT}/Cargo.toml" || exit 2
AZURE_COSMOS_BUILD_RUST_DRIVER_COMMIT="$(python3 ./perf_build_details.py driver-commit)" || exit 2

command -v maturin >/dev/null 2>&1 || {
  echo "ERROR: maturin is not installed in the perfdrill environment." >&2
  echo "       python3 -m pip install maturin" >&2
  exit 2
}

echo "=== Building the Rust extension with symbols kept ==="
echo "    python env : ${VIRTUAL_ENV:-none}"
echo "    package    : ${PKG_ROOT}"

cd "${PKG_ROOT}" || exit 1
export CARGO_PROFILE_RELEASE_DEBUG=1      # keep debug info in the release build
export CARGO_PROFILE_RELEASE_STRIP=false  # and do not strip it afterwards

if ! maturin develop --release --locked; then
  echo "ERROR: maturin develop --release failed. The extension was not replaced," >&2
  echo "       so any import below may still be an older build." >&2
  exit 1
fi

echo
echo "=== Confirming which extension Python imports ==="
python3 - <<'PY'
import datetime
import os
import sys

try:
    from azure.cosmos import _rust
except Exception as exc:
    print(f"FAIL: cannot import azure.cosmos._rust: {exc}")
    sys.exit(1)

path = getattr(_rust, "__file__", None) or "unknown"
print(f"    extension path : {path}")
print(f"    Python commit  : {getattr(_rust, '__python_commit__', 'unknown')}")
print(f"    Rust commit    : {getattr(_rust, '__rust_driver_commit__', 'unknown')}")
if os.path.exists(path):
    built = datetime.datetime.fromtimestamp(
        os.path.getmtime(path), datetime.timezone.utc
    )
    print(f"    built (UTC)    : {built:%Y-%m-%dT%H:%M:%SZ}")

# These three back the path proof in 03-path-proof-and-baseline.md.
counters = ("_debug_operation_count", "_debug_attempt_count", "_debug_retry_count")
missing = [name for name in counters if not callable(getattr(_rust, name, None))]
for name in counters:
    print(f"    {name:<24}: {'MISSING' if name in missing else 'present'}")

if missing:
    print(f"FAIL: extension lacks {', '.join(missing)}; the path proof cannot run.")
    sys.exit(1)
print("OK: extension imports and exposes the operation counters.")
PY
rc=$?

if [[ ${rc} -ne 0 ]]; then
  echo "!! Build produced an extension that cannot support the path proof." >&2
  exit 1
fi
profiling_verify_extension_build || exit 1

echo "=== Extension ready ==="
exit 0
