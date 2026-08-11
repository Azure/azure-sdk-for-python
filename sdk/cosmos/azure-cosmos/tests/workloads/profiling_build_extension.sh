#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# RESPONSIBILITY: compile the Rust extension that Python will actually import,
# and prove which file that is.
#
# maturin compiles the PyO3 binding plus the Cosmos driver source into
# azure.cosmos._rust and installs it into the ACTIVE Python environment. It
# does not download anything: it builds whatever commits are checked out (see
# profiling_update_source.sh).
#
# WHY THE TWO CARGO SETTINGS: a release build normally discards the function
# names and line numbers stored alongside compiled code. Without them, Linux
# perf can only show numeric addresses like 0x7f2a91c4, so a Rust frame in a
# CPU profile cannot be attributed to any function. Keeping them costs nothing
# at run time and is what makes lines like this readable:
#
#   tokio-runtime-w  _rust.abi3.so  [.] azure_cosmos_driver::gateway::send
#
# WHY THE IMPORT CHECK: 'COSMOS_BACKEND=rust' only states an intention. If the
# extension failed to build or an older copy shadows it on sys.path, Python
# keeps working and the run still looks Rust-configured. Printing the resolved
# __file__ and its timestamp is what turns that into a fact.
#
# The counter check matters for the same reason: operation_count(),
# attempt_count() and retry_count() are what the next document uses to prove a
# real read entered Rust. An extension without them cannot support that proof.
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
RUST_REPO="$(profiling_rust_repo "${PY_REPO}")"
export AZURE_COSMOS_BUILD_PYTHON_COMMIT
export AZURE_COSMOS_BUILD_RUST_DRIVER_COMMIT
AZURE_COSMOS_BUILD_PYTHON_COMMIT="$(git -C "${PY_REPO}" rev-parse HEAD)" || exit 2
AZURE_COSMOS_BUILD_RUST_DRIVER_COMMIT="$(git -C "${RUST_REPO}" rev-parse HEAD)" || exit 2

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

if ! maturin develop --release; then
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
counters = ("operation_count", "attempt_count", "retry_count")
missing = [name for name in counters if not hasattr(_rust, name)]
for name in counters:
    print(f"    {name:<16}: {'present' if hasattr(_rust, name) else 'MISSING'}")

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
