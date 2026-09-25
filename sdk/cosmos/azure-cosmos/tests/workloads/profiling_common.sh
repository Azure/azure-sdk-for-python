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
# Each Python-dependent step activates the selected environment. A missing
# interpreter is fatal rather than a warning.
#
# Build scripts activate Python only. Live profiling commands also load the
# complete ~/profiling_config.env, credentials from ~/perf_secrets.env, and
# functions from perf_common.sh. They never inherit sweep defaults.
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
  status="$(git -C "${dir}" status --porcelain --untracked-files=normal)" || {
    echo "ERROR: cannot inspect local changes in ${dir}." >&2
    return 2
  }
  [[ -n "${status}" ]]
}

profiling_python_repo() {
  git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel 2>/dev/null
}

# Compare embedded labels to the Python checkout and Cargo's resolved Git driver.
# The session check also compares the binary and local source fingerprints.
profiling_verify_extension_build() {
  local python_repo python_commit rust_commit
  python_repo="$(profiling_python_repo)" || {
    echo "ERROR: cannot locate the azure-sdk-for-python checkout." >&2
    return 2
  }
  python_commit="$(git -C "${python_repo}" rev-parse HEAD 2>/dev/null || echo unknown)"
  rust_commit="$(python3 "$(dirname "${BASH_SOURCE[0]}")/perf_build_details.py" driver-commit)" || return 2

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
    problems.append(f"Rust driver commit: extension={actual_rust}, Cargo dependency={expected_rust}")
if problems:
    print("ERROR: loaded _rust build labels disagree with the selected source:", file=sys.stderr)
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
  # Old session.env files exported RUN_ID; never inherit it from another experiment.
  local RUN_ID=""
  unset PROFILING_SESSION_ID ARTIFACTS PERF_PHASE
  session_dir="${session_dir%/}"
  session_env="${session_dir}/session.env"
  [[ -f "${session_env}" ]] || return 1

  # shellcheck disable=SC1090
  source "${session_env}" || return 1
  if [[ -n "${RUN_ID}" ]]; then
    if [[ -n "${PROFILING_SESSION_ID:-}" && "${PROFILING_SESSION_ID}" != "${RUN_ID}" ]]; then
      echo "ERROR: ${session_env} has conflicting PROFILING_SESSION_ID and historical RUN_ID." >&2
      return 1
    fi
    PROFILING_SESSION_ID="${RUN_ID}"
  fi
  [[ "${PROFILING_SESSION_ID:-}" =~ ^[0-9]{8}-[0-9]{9}$ ]] || {
    echo "ERROR: ${session_env} has an invalid PROFILING_SESSION_ID." >&2
    return 1
  }
  profiling_validate_phase "${PERF_PHASE:-}" || return 1
  canonical_dir="$(cd "${session_dir}" 2>/dev/null && pwd)" || return 1
  [[ "${ARTIFACTS:-}" == "${canonical_dir}" ]] || {
    echo "ERROR: ${session_env} points ARTIFACTS outside its session directory." >&2
    return 1
  }

  manifest="${ARTIFACTS}/manifest-${PROFILING_SESSION_ID}.json"
  [[ -f "${manifest}" ]] || {
    echo "ERROR: session ${session_dir} has no manifest." >&2
    return 1
  }
  python3 - "${manifest}" "${PROFILING_SESSION_ID}" "${PERF_PHASE}" \
    "${COSMOS_URI}" "${COSMOS_DATABASE}" "${COSMOS_CONTAINER}" <<'PY'
import json
import os
import sys
from perf_build_details import extension_details, source_digest

path, profiling_session_id, phase, uri, database, container = sys.argv[1:]
try:
    with open(path, encoding="utf-8") as handle:
        manifest = json.load(handle)
except Exception as exc:
    print(f"ERROR: cannot read session manifest {path}: {exc}", file=sys.stderr)
    raise SystemExit(1)

account = manifest.get("account") or {}
expected = {
    "stamp": (manifest.get("stamp"), profiling_session_id),
    "phase": (manifest.get("phase"), phase),
    "account.uri": (account.get("uri"), uri),
    "account.database": (account.get("database"), database),
    "account.container": (account.get("container"), container),
}
if "profiling_session_id" in manifest:
    expected["profiling_session_id"] = (manifest["profiling_session_id"], profiling_session_id)
bad = [f"{name}: manifest={actual!r}, expected={wanted!r}"
       for name, (actual, wanted) in expected.items() if actual != wanted]
configuration = manifest.get("configuration")
if configuration is not None and configuration.get("sha256") != os.environ.get("PROFILING_CONFIG_SHA256"):
    bad.append("~/profiling_config.env changed since profiling session creation; create a fresh profiling session")
build = manifest.get("build") or {}
if build.get("source_sha256") != source_digest():
    bad.append("SDK/binding/workload sources changed since session creation")
current = extension_details()
for name in ("rust_extension_sha256", "rust_extension_python_commit", "rust_extension_driver_commit"):
    if build.get(name) != current[name]:
        bad.append(f"{name}: loaded extension differs from the session manifest")
if bad:
    print("ERROR: session manifest does not match the active session/target:", file=sys.stderr)
    for problem in bad:
        print(f"       {problem}", file=sys.stderr)
    raise SystemExit(1)
PY
  [[ $? -eq 0 ]] || return 1
  profiling_verify_extension_build || return 1
  export PROFILING_SESSION_ID ARTIFACTS PERF_PHASE
}

profiling_activate_python() {
  if [[ ! -f ~/venvs/perfdrill/bin/activate ]]; then
    echo "ERROR: ~/venvs/perfdrill/bin/activate is missing." >&2
    return 2
  fi
  source ~/venvs/perfdrill/bin/activate || return 2
  if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    echo "ERROR: perfdrill activation did not set VIRTUAL_ENV." >&2
    return 2
  fi
}

profiling_load_config() {
  local config="$HOME/profiling_config.env" name
  local -a names=(
    COSMOS_URI COSMOS_DATABASE COSMOS_CONTAINER COSMOS_PARTITION_KEY
    COSMOS_MAX_ITEM_INDEX COSMOS_THROUGHPUT COSMOS_PREFERRED_LOCATIONS
    COSMOS_CLIENT_EXCLUDED_LOCATIONS COSMOS_REQUEST_EXCLUDED_LOCATIONS
    COSMOS_USE_MULTIPLE_WRITABLE_LOCATIONS
    RESULTS_COSMOS_URI RESULTS_COSMOS_DATABASE RESULTS_COSMOS_CONTAINER
    WORKLOAD_NUM_CLIENTS COSMOS_CONCURRENT_REQUESTS WORKLOAD_ARRIVAL_RATE
    WORKLOAD_MAX_INFLIGHT WORKLOAD_OPERATIONS COSMOS_REQUEST_TIMEOUT
    WORKLOAD_USE_SYNC WORKLOAD_USE_PROXY WORKLOAD_GC_FREEZE WORKLOAD_LOOP_LAG_MONITOR
    WORKLOAD_SKIP_CLOSE WORKLOAD_MIX WORKLOAD_DOC_PROFILE COSMOS_LOG_LEVEL
    COSMOS_ENABLE_DIAGNOSTICS_LOGGING PERF_ENABLED PERF_REPORT_INTERVAL
  )
  local -A inherited=()
  if [[ ! -f "$config" ]]; then
    echo "ERROR: ~/profiling_config.env is required. Copy profiling_config.env.example and fill in the target." >&2
    echo "       ~/perf_target.env and profiling_target.env are no longer loaded." >&2
    return 2
  fi
  for name in "${names[@]}"; do
    if [[ -v "$name" ]]; then inherited["$name"]="${!name}"; fi
    unset "$name"
  done
  source "$config" || { echo "ERROR: cannot load $config." >&2; return 2; }
  for name in "${names[@]}"; do
    if [[ ! -v "$name" ]]; then
      echo "ERROR: $config must explicitly set $name; profiling has no fallback defaults." >&2
      return 2
    fi
    if [[ -v "inherited[$name]" && "${inherited[$name]}" != "${!name}" ]]; then
      echo "ERROR: inherited $name conflicts with $config. Edit that file, then unset $name or use a fresh terminal." >&2
      return 2
    fi
    case "$name" in
      COSMOS_CLIENT_EXCLUDED_LOCATIONS|COSMOS_REQUEST_EXCLUDED_LOCATIONS|WORKLOAD_MIX) ;;
      *) [[ -n "${!name}" ]] || { echo "ERROR: $config has an empty $name." >&2; return 2; } ;;
    esac
    export "$name"
  done
  for name in WORKLOAD_NUM_CLIENTS COSMOS_CONCURRENT_REQUESTS COSMOS_THROUGHPUT \
      WORKLOAD_MAX_INFLIGHT PERF_REPORT_INTERVAL; do
    if [[ ! "${!name}" =~ ^[1-9][0-9]*$ ]]; then
      echo "ERROR: $name must be a positive integer in $config." >&2
      return 2
    fi
  done
  for name in COSMOS_MAX_ITEM_INDEX; do
    if [[ ! "${!name}" =~ ^(0|[1-9][0-9]*)$ ]]; then
      echo "ERROR: $name must be a nonnegative integer in $config." >&2
      return 2
    fi
  done
  for name in WORKLOAD_ARRIVAL_RATE COSMOS_REQUEST_TIMEOUT; do
    if [[ ! "${!name}" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
      echo "ERROR: $name must be a nonnegative number in $config." >&2
      return 2
    fi
  done
  if [[ "$COSMOS_PARTITION_KEY" != id && "$COSMOS_PARTITION_KEY" != pk ]]; then
    echo "ERROR: configure COSMOS_PARTITION_KEY=id or pk." >&2
    return 2
  fi
  for name in WORKLOAD_USE_SYNC WORKLOAD_USE_PROXY WORKLOAD_GC_FREEZE WORKLOAD_LOOP_LAG_MONITOR \
      WORKLOAD_SKIP_CLOSE COSMOS_ENABLE_DIAGNOSTICS_LOGGING COSMOS_USE_MULTIPLE_WRITABLE_LOCATIONS PERF_ENABLED; do
    if [[ "${!name}" != true && "${!name}" != false ]]; then
      echo "ERROR: $name must be true or false in $config." >&2
      return 2
    fi
  done
  for name in BASELINE_READ_RPS BASELINE_DATABASE BASELINE_CONTAINER BASELINE_OPERATIONS \
      PROFILING_PROOF_DATABASE PROFILING_PROOF_CONTAINER PROFILING_PROOF_PARTITION_KEY MEMRAY_ARRIVAL_RATE; do
    if [[ -v "$name" ]]; then
      echo "ERROR: $name is removed. Use ~/profiling_config.env and unset $name." >&2
      return 2
    fi
  done
  while IFS= read -r name; do
    echo "ERROR: $name is removed. Confirm the target with --confirm-target, not EXPECT_* settings." >&2
    return 2
  done < <(compgen -A variable EXPECT_)
  export PROFILING_CONFIG_PATH="$config"
  PROFILING_CONFIG_SHA256="$(python3 -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest())' "$config")" || return 2
  export PROFILING_CONFIG_SHA256
}

profiling_confirm_target() {
  if [[ $# -ne 4 || "$1" != --confirm-target ]]; then
    echo "ERROR: pass --confirm-target <account-endpoint> <database> <container> before contacting Cosmos." >&2
    return 2
  fi
  if [[ "${2%/}" != "${COSMOS_URI%/}" || "$3" != "$COSMOS_DATABASE" || "$4" != "$COSMOS_CONTAINER" ]]; then
    echo "ERROR: confirmed target differs from ~/profiling_config.env; no live target will be contacted." >&2
    return 2
  fi
}

profiling_require_read_workload() {
  if [[ "$WORKLOAD_OPERATIONS" != read || "$WORKLOAD_NUM_CLIENTS" != 1 ||
        "$COSMOS_CONCURRENT_REQUESTS" != 1 || "$WORKLOAD_USE_SYNC" != false ||
        "$WORKLOAD_USE_PROXY" != false || "$WORKLOAD_SKIP_CLOSE" != false ||
        "$PERF_ENABLED" != true || -n "$WORKLOAD_MIX" ]]; then
    echo "ERROR: configure one asynchronous read client, concurrency 1, reporting enabled, no proxy/mix/skipped close in ~/profiling_config.env." >&2
    return 2
  fi
  if ! [[ "$WORKLOAD_ARRIVAL_RATE" =~ ^[0-9]+([.][0-9]+)?$ ]] ||
     ! awk -v rate="$WORKLOAD_ARRIVAL_RATE" 'BEGIN { exit !(rate > 0) }'; then
    echo "ERROR: WORKLOAD_ARRIVAL_RATE must be positive for fixed-rate reads; edit ~/profiling_config.env." >&2
    return 2
  fi
}

profiling_load_env() {
  local here secrets_perm
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  profiling_activate_python || return 2

  # Load credentials first so they cannot replace validated experiment settings.
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

  if [[ -z "${COSMOS_KEY:-}" || -z "${RESULTS_COSMOS_KEY:-}" ]]; then
    echo "ERROR: ~/perf_secrets.env must supply COSMOS_KEY and RESULTS_COSMOS_KEY." >&2
    return 2
  fi
  export COSMOS_KEY RESULTS_COSMOS_KEY
  profiling_load_config || return 2
  source "${here}/perf_common.sh" || return 2
}
