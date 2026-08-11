#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# RESPONSIBILITY: shared setup for every profiling_*.sh script. Source it; do
# not run it.
#
# WHY THIS EXISTS: each profiling step runs as its own process, so an
# environment prepared by one of them disappears when it exits. A script that
# activates the perfdrill virtual environment cannot hand that activation to
# the next script. If each step does not load its own environment, later steps
# silently use the system python3 -- a different interpreter, without the built
# _rust extension and without py-spy or Memray -- and the checks they perform
# describe an environment that no measured run will ever use.
#
# Every helper therefore calls profiling_load_env at startup, and a missing
# piece is fatal rather than a warning: a step that "passes" against the wrong
# interpreter is worse than one that stops.
#
# Load order is fixed, and changing it breaks the settings:
#   1  ~/perf_secrets.env      account keys (not checked in)
#   2  ./profiling_target.env  account, data and load  (~/perf_target.env wins)
#   3  ./perf_env.sh           shared fallbacks; its "${VAR:-default}" forms
#                              must run LAST so profiling_target.env's values
#                              survive
#   4  ~/venvs/perfdrill       the interpreter holding the built extension
# ---------------------------------------------------------------------------

# A phase label reaches the filesystem as a directory name and the manifest as
# a JSON string value. Restricting it up front is cheaper than escaping it in
# both places: '..' or '/' would move the artifacts directory somewhere
# unintended, and a quote or newline would produce a manifest that no report
# can parse.
profiling_validate_phase() {
  local phase="$1"
  if [[ -z "${phase}" ]]; then
    echo "ERROR: the session phase must not be empty." >&2
    return 2
  fi
  if [[ ! "${phase}" =~ ^[A-Za-z0-9._-]+$ ]]; then
    echo "ERROR: invalid session phase '${phase}'." >&2
    echo "       Use only letters, digits, dot, underscore, hyphen." >&2
    return 2
  fi
  # Even within that character set, a name that is only dots would walk the path.
  if [[ "${phase}" =~ ^\.+$ ]]; then
    echo "ERROR: invalid session phase '${phase}'." >&2
    return 2
  fi
  return 0
}

# Reports whether a checkout has ANY local modification: unstaged, staged, or
# untracked. 'git diff --quiet' sees only the first of those, so a file that was
# added or staged would still be called clean, and the commit recorded in the
# manifest would not describe what was built.
profiling_repo_is_dirty() {
  local dir="$1" status
  status="$(git -C "${dir}" status --porcelain --untracked-files=normal 2>/dev/null)"
  [[ -n "${status}" ]]
}

profiling_python_repo() {
  git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel 2>/dev/null
}

profiling_rust_repo() {
  local python_repo="$1"
  printf '%s\n' "${AZURE_SDK_FOR_RUST_DIR:-${python_repo}/../azure-sdk-for-rust}"
}

# The extension carries the two commits supplied to Cargo when it was built.
# Comparing those attributes with both current checkouts closes the stale-build
# hole when source update and compilation are deliberately skipped together.
profiling_verify_extension_build() {
  local python_repo rust_repo python_commit rust_commit
  python_repo="$(profiling_python_repo)" || {
    echo "ERROR: cannot locate the azure-sdk-for-python checkout." >&2
    return 2
  }
  rust_repo="$(profiling_rust_repo "${python_repo}")"
  python_commit="$(git -C "${python_repo}" rev-parse HEAD 2>/dev/null || echo unknown)"
  rust_commit="$(git -C "${rust_repo}" rev-parse HEAD 2>/dev/null || echo unknown)"

  python3 - "${python_commit}" "${rust_commit}" <<'PY'
import sys

expected_python, expected_rust = sys.argv[1:]
try:
    from azure.cosmos import _rust
except Exception as exc:
    print(f"ERROR: cannot import azure.cosmos._rust: {exc}", file=sys.stderr)
    raise SystemExit(1)

actual_python = getattr(_rust, "__python_commit__", "unknown")
actual_rust = getattr(_rust, "__rust_driver_commit__", "unknown")
problems = []
if actual_python != expected_python:
    problems.append(f"Python commit: extension={actual_python}, checkout={expected_python}")
if actual_rust != expected_rust:
    problems.append(f"Rust driver commit: extension={actual_rust}, checkout={expected_rust}")
if problems:
    print("ERROR: loaded _rust was not built from the current checkouts:", file=sys.stderr)
    for problem in problems:
        print(f"       {problem}", file=sys.stderr)
    print("       Re-run profiling_build_extension.sh.", file=sys.stderr)
    raise SystemExit(1)

print(f"    extension Python commit    : {actual_python}")
print(f"    extension Rust commit      : {actual_rust}")
PY
}

# Load only a complete session and prove that its directory, variables,
# manifest, target, and currently imported extension all describe one run.
profiling_load_session() {
  local session_dir="$1" session_env manifest canonical_dir
  session_dir="${session_dir%/}"
  session_env="${session_dir}/session.env"
  [[ -f "${session_env}" ]] || return 1

  # shellcheck disable=SC1090
  source "${session_env}" || return 1
  [[ "${RUN_ID:-}" =~ ^[0-9]{8}-[0-9]{9}$ ]] || {
    echo "ERROR: ${session_env} has an invalid RUN_ID." >&2
    return 1
  }
  profiling_validate_phase "${PERF_PHASE:-}" || return 1
  canonical_dir="$(cd "${session_dir}" 2>/dev/null && pwd)" || return 1
  [[ "${ARTIFACTS:-}" == "${canonical_dir}" ]] || {
    echo "ERROR: ${session_env} points ARTIFACTS outside its session directory." >&2
    return 1
  }

  manifest="${ARTIFACTS}/manifest-${RUN_ID}.json"
  [[ -f "${manifest}" ]] || {
    echo "ERROR: session ${session_dir} has no manifest." >&2
    return 1
  }
  python3 - "${manifest}" "${RUN_ID}" "${PERF_PHASE}" \
    "${COSMOS_URI}" "${COSMOS_DATABASE}" "${COSMOS_CONTAINER}" <<'PY'
import json
import sys

path, run_id, phase, uri, database, container = sys.argv[1:]
try:
    with open(path, encoding="utf-8") as handle:
        manifest = json.load(handle)
except Exception as exc:
    print(f"ERROR: cannot read session manifest {path}: {exc}", file=sys.stderr)
    raise SystemExit(1)

account = manifest.get("account") or {}
expected = {
    "stamp": (manifest.get("stamp"), run_id),
    "phase": (manifest.get("phase"), phase),
    "account.uri": (account.get("uri"), uri),
    "account.database": (account.get("database"), database),
    "account.container": (account.get("container"), container),
}
bad = [f"{name}: manifest={actual!r}, expected={wanted!r}"
       for name, (actual, wanted) in expected.items() if actual != wanted]
if bad:
    print("ERROR: session manifest does not match the active session/target:", file=sys.stderr)
    for problem in bad:
        print(f"       {problem}", file=sys.stderr)
    raise SystemExit(1)
PY
  [[ $? -eq 0 ]] || return 1
  profiling_verify_extension_build
}

profiling_load_env() {
  local here secrets_perm
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  # 1. Credentials.
  if [[ ! -f ~/perf_secrets.env ]]; then
    echo "ERROR: ~/perf_secrets.env not found." >&2
    echo "       It holds COSMOS_KEY and is the one file deliberately not" >&2
    echo "       checked in. Create it, then: chmod 600 ~/perf_secrets.env" >&2
    return 2
  fi
  # A key readable by other accounts on this VM is a credential leak, so this
  # is enforced rather than merely documented.
  secrets_perm="$(stat -c '%a' ~/perf_secrets.env 2>/dev/null || echo unknown)"
  if [[ "${secrets_perm}" != "600" && "${secrets_perm}" != "400" ]]; then
    if [[ "${PROFILING_ALLOW_LOOSE_SECRETS:-0}" == "1" ]]; then
      echo "WARNING: ~/perf_secrets.env permission is ${secrets_perm}, not 600." >&2
    else
      echo "ERROR: ~/perf_secrets.env permission is ${secrets_perm}, not 600." >&2
      echo "       Other accounts on this VM may be able to read the key. Run:" >&2
      echo "           chmod 600 ~/perf_secrets.env" >&2
      echo "       Set PROFILING_ALLOW_LOOSE_SECRETS=1 only if this is intended." >&2
      return 2
    fi
  fi
  # shellcheck disable=SC1090
  source ~/perf_secrets.env || { echo "ERROR: ~/perf_secrets.env failed to load." >&2; return 2; }

  # 2. Target. The checked-in file defines the profiling account and data; an
  # operator copy in the home directory overrides it for a different account.
  if [[ -f ~/perf_target.env ]]; then
    # shellcheck disable=SC1090
    source ~/perf_target.env || { echo "ERROR: ~/perf_target.env failed to load." >&2; return 2; }
  elif [[ -f "${here}/profiling_target.env" ]]; then
    # shellcheck disable=SC1091
    source "${here}/profiling_target.env" || {
      echo "ERROR: ${here}/profiling_target.env failed to load." >&2
      return 2
    }
  else
    echo "ERROR: no profiling target found. Expected ${here}/profiling_target.env" >&2
    echo "       (checked in) or ~/perf_target.env (operator override)." >&2
    return 2
  fi

  # 3. Shared fallbacks and helper functions, last so profiling_target.env wins.
  # shellcheck disable=SC1091
  source "${here}/perf_env.sh" >/dev/null 2>&1 || {
    echo "ERROR: ${here}/perf_env.sh failed (usually a missing account key)." >&2
    return 2
  }

  # 4. The interpreter that holds the built extension and the capture tools.
  if [[ ! -f ~/venvs/perfdrill/bin/activate ]]; then
    echo "ERROR: the perfdrill Python environment is missing." >&2
    echo "       Expected ~/venvs/perfdrill/bin/activate" >&2
    echo "       Without it, later steps would silently use the system python3," >&2
    echo "       which does not have the built _rust extension or the profilers." >&2
    return 2
  fi
  # shellcheck disable=SC1090
  source ~/venvs/perfdrill/bin/activate || {
    echo "ERROR: could not activate the perfdrill environment." >&2
    return 2
  }
  if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    echo "ERROR: perfdrill activation did not take effect (VIRTUAL_ENV unset)." >&2
    return 2
  fi

  return 0
}
