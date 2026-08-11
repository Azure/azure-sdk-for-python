#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# RESPONSIBILITY: confirm the terminal is pointed at the profiling target, and
# that the capture tools exist -- before anything expensive or destructive runs.
#
# Two runs can only be compared if they used the same account, the same items,
# and the same load. Every one of those arrives as an environment variable, and
# a wrong value does not announce itself: the workload runs happily against the
# wrong container and produces numbers that look fine and mean nothing.
#
# WHY THE ENDPOINT IS COMPARED, NOT JUST PRINTED: database and container names
# are not unique across accounts. Another subscription can hold its own
# lat_probe_db/lat_probe_cont. Checking only those names would pass while
# measuring, and seeding, an entirely different account.
#
# The specific trap this catches: perf_env.sh supplies fallbacks for the scale
# and leak tests, not for profiling. It defaults COSMOS_DATABASE to scale_db and
# COSMOS_MAX_ITEM_INDEX to 10000. The profiling values come from
# ./profiling_target.env (or an operator copy at ~/perf_target.env), which must
# be sourced BEFORE perf_env.sh so its values win the "${VAR:-default}"
# fallbacks. Source them the other way round and the workload silently reads
# test-0 .. test-10000, of which only the first 1,001 exist -- roughly nine
# reads in ten would 404.
#
# Every expected value is overridable so this script can guard another target:
#   EXPECT_DATABASE=other_db ./profiling_check_target.sh
#
# Nothing here prints a secret; keys are only tested for presence.
#
# Usage:
#   ./profiling_check_target.sh
# ---------------------------------------------------------------------------
set -uo pipefail
cd "$(dirname "$0")"

source ./profiling_common.sh
profiling_load_env || exit 2

# Defaults describe the validated profiling target in profiling_target.env.
EXPECT_URI="${EXPECT_URI:-https://profiling.documents.azure.com:443/}"
EXPECT_DATABASE="${EXPECT_DATABASE:-lat_probe_db}"
EXPECT_CONTAINER="${EXPECT_CONTAINER:-lat_probe_cont}"
EXPECT_PARTITION_KEY="${EXPECT_PARTITION_KEY:-id}"
EXPECT_MAX_ITEM_INDEX="${EXPECT_MAX_ITEM_INDEX:-1000}"
EXPECT_THROUGHPUT="${EXPECT_THROUGHPUT:-400}"
EXPECT_PREFERRED_LOCATIONS="${EXPECT_PREFERRED_LOCATIONS:-West US 2}"
EXPECT_NUM_CLIENTS="${EXPECT_NUM_CLIENTS:-1}"
EXPECT_CONCURRENT_REQUESTS="${EXPECT_CONCURRENT_REQUESTS:-1}"
EXPECT_ARRIVAL_RATE="${EXPECT_ARRIVAL_RATE:-250}"
EXPECT_OPERATIONS="${EXPECT_OPERATIONS:-read}"
EXPECT_REQUEST_TIMEOUT="${EXPECT_REQUEST_TIMEOUT:-30}"
EXPECT_MAX_INFLIGHT="${EXPECT_MAX_INFLIGHT:-10000}"
EXPECT_USE_SYNC="${EXPECT_USE_SYNC:-false}"
EXPECT_GC_FREEZE="${EXPECT_GC_FREEZE:-false}"
EXPECT_LOOP_LAG_MONITOR="${EXPECT_LOOP_LAG_MONITOR:-true}"
EXPECT_USE_PROXY="${EXPECT_USE_PROXY:-false}"
EXPECT_LOG_LEVEL="${EXPECT_LOG_LEVEL:-WARNING}"
EXPECT_DIAGNOSTICS_LOGGING="${EXPECT_DIAGNOSTICS_LOGGING:-false}"
EXPECT_MULTIPLE_WRITABLE_LOCATIONS="${EXPECT_MULTIPLE_WRITABLE_LOCATIONS:-false}"
EXPECT_CLIENT_EXCLUDED_LOCATIONS="${EXPECT_CLIENT_EXCLUDED_LOCATIONS:-}"
EXPECT_REQUEST_EXCLUDED_LOCATIONS="${EXPECT_REQUEST_EXCLUDED_LOCATIONS:-}"
EXPECT_REPORT_INTERVAL="${EXPECT_REPORT_INTERVAL:-60}"
EXPECT_RESULTS_DATABASE="${EXPECT_RESULTS_DATABASE:-perfdb}"
EXPECT_RESULTS_CONTAINER="${EXPECT_RESULTS_CONTAINER:-perfresults-v2}"
# The results account defaults to the account under test (perf_env.sh), so the
# expectation follows the same rule unless overridden.
EXPECT_RESULTS_URI="${EXPECT_RESULTS_URI:-${EXPECT_URI}}"

failures=0

check_value() {
  local label="$1" actual="$2" expected="$3"
  if [[ "${actual}" == "${expected}" ]]; then
    printf '    %-30s %-42s ok\n' "${label}" "${actual}"
  else
    printf '    %-30s %-42s EXPECTED %s\n' "${label}" "${actual:-<unset>}" "${expected}"
    failures=$((failures + 1))
  fi
}

check_present() {
  local label="$1" value="$2"
  if [[ -n "${value}" ]]; then
    printf '    %-30s %-42s ok\n' "${label}" "(set, not shown)"
  else
    printf '    %-30s %-42s MISSING\n' "${label}" "<unset>"
    failures=$((failures + 1))
  fi
}

echo "=== Account under measurement ==="
check_value "COSMOS_URI"              "${COSMOS_URI:-}"              "${EXPECT_URI}"
check_value "COSMOS_DATABASE"         "${COSMOS_DATABASE:-}"         "${EXPECT_DATABASE}"
check_value "COSMOS_CONTAINER"        "${COSMOS_CONTAINER:-}"        "${EXPECT_CONTAINER}"
check_value "COSMOS_PARTITION_KEY"    "${COSMOS_PARTITION_KEY:-}"    "${EXPECT_PARTITION_KEY}"
check_value "COSMOS_THROUGHPUT"       "${COSMOS_THROUGHPUT:-}"       "${EXPECT_THROUGHPUT}"
check_value "COSMOS_PREFERRED_LOCATIONS" "${COSMOS_PREFERRED_LOCATIONS:-}" "${EXPECT_PREFERRED_LOCATIONS}"

echo
echo "=== Item range this session will read ==="
# MAX_ITEM_INDEX is the highest SUFFIX and is inclusive, so N yields N+1 items.
# initial-setup.py creates MAX_ITEM_INDEX + 1 of them; workload_utils.py picks
# random.randint(0, MAX_ITEM_INDEX), which includes both endpoints.
check_value "COSMOS_MAX_ITEM_INDEX" "${COSMOS_MAX_ITEM_INDEX:-}" "${EXPECT_MAX_ITEM_INDEX}"
printf '    %-30s test-0 .. test-%s (%s items)\n' \
  "readable ids" "${COSMOS_MAX_ITEM_INDEX:-?}" \
  "$(( ${COSMOS_MAX_ITEM_INDEX:-0} + 1 ))"

echo
echo "=== Load shape ==="
check_value "WORKLOAD_NUM_CLIENTS"       "${WORKLOAD_NUM_CLIENTS:-}"       "${EXPECT_NUM_CLIENTS}"
check_value "COSMOS_CONCURRENT_REQUESTS" "${COSMOS_CONCURRENT_REQUESTS:-}" "${EXPECT_CONCURRENT_REQUESTS}"
check_value "WORKLOAD_ARRIVAL_RATE"      "${WORKLOAD_ARRIVAL_RATE:-}"      "${EXPECT_ARRIVAL_RATE}"
check_value "WORKLOAD_OPERATIONS"        "${WORKLOAD_OPERATIONS:-}"        "${EXPECT_OPERATIONS}"
check_value "COSMOS_REQUEST_TIMEOUT"     "${COSMOS_REQUEST_TIMEOUT:-}"     "${EXPECT_REQUEST_TIMEOUT}"
check_value "WORKLOAD_MAX_INFLIGHT"      "${WORKLOAD_MAX_INFLIGHT:-}"      "${EXPECT_MAX_INFLIGHT}"
check_value "WORKLOAD_USE_SYNC"          "${WORKLOAD_USE_SYNC:-}"          "${EXPECT_USE_SYNC}"
check_value "WORKLOAD_GC_FREEZE"         "${WORKLOAD_GC_FREEZE:-}"         "${EXPECT_GC_FREEZE}"
check_value "WORKLOAD_LOOP_LAG_MONITOR"  "${WORKLOAD_LOOP_LAG_MONITOR:-}"  "${EXPECT_LOOP_LAG_MONITOR}"
# A proxy would add latency that does not belong to the SDK.
check_value "WORKLOAD_USE_PROXY"         "${WORKLOAD_USE_PROXY:-}"         "${EXPECT_USE_PROXY}"
check_value "COSMOS_LOG_LEVEL"            "${COSMOS_LOG_LEVEL:-}"            "${EXPECT_LOG_LEVEL}"
check_value "COSMOS_ENABLE_DIAGNOSTICS_LOGGING" "${COSMOS_ENABLE_DIAGNOSTICS_LOGGING:-}" "${EXPECT_DIAGNOSTICS_LOGGING}"
check_value "COSMOS_USE_MULTIPLE_WRITABLE_LOCATIONS" "${COSMOS_USE_MULTIPLE_WRITABLE_LOCATIONS:-}" "${EXPECT_MULTIPLE_WRITABLE_LOCATIONS}"
check_value "COSMOS_CLIENT_EXCLUDED_LOCATIONS" "${COSMOS_CLIENT_EXCLUDED_LOCATIONS:-}" "${EXPECT_CLIENT_EXCLUDED_LOCATIONS}"
check_value "COSMOS_REQUEST_EXCLUDED_LOCATIONS" "${COSMOS_REQUEST_EXCLUDED_LOCATIONS:-}" "${EXPECT_REQUEST_EXCLUDED_LOCATIONS}"
check_value "PERF_REPORT_INTERVAL"       "${PERF_REPORT_INTERVAL:-}"       "${EXPECT_REPORT_INTERVAL}"

echo
echo "=== Where results are written ==="
check_value "RESULTS_COSMOS_URI"       "${RESULTS_COSMOS_URI:-}"       "${EXPECT_RESULTS_URI}"
check_value "RESULTS_COSMOS_DATABASE"  "${RESULTS_COSMOS_DATABASE:-}"  "${EXPECT_RESULTS_DATABASE}"
check_value "RESULTS_COSMOS_CONTAINER" "${RESULTS_COSMOS_CONTAINER:-}" "${EXPECT_RESULTS_CONTAINER}"

echo
echo "=== Credentials present ==="
check_present "COSMOS_KEY"         "${COSMOS_KEY:-}"
check_present "RESULTS_COSMOS_KEY" "${RESULTS_COSMOS_KEY:-}"

echo
echo "=== Live container configuration ==="
python3 - "${EXPECT_PARTITION_KEY}" "${EXPECT_THROUGHPUT}" <<'PY'
import os
import sys

from azure.cosmos import CosmosClient

expected_pk, expected_throughput = sys.argv[1], int(sys.argv[2])
client = CosmosClient(os.environ["COSMOS_URI"], os.environ["COSMOS_KEY"])
try:
    container = (
        client.get_database_client(os.environ["COSMOS_DATABASE"])
        .get_container_client(os.environ["COSMOS_CONTAINER"])
    )
    properties = container.read()
    paths = (properties.get("partitionKey") or {}).get("paths") or []
    actual_path = paths[0] if len(paths) == 1 else repr(paths)
    wanted_path = "/" + expected_pk.lstrip("/")
    throughput = container.get_throughput().offer_throughput
    print(f"    partition-key path            {actual_path}")
    print(f"    dedicated throughput          {throughput} RU/s")
    if actual_path != wanted_path or throughput != expected_throughput:
        raise SystemExit(
            f"live container mismatch: expected partition key {wanted_path} "
            f"and {expected_throughput} RU/s"
        )
finally:
    client.close()
PY
if [[ $? -ne 0 ]]; then
  failures=$((failures + 1))
fi

echo
echo "=== Python environment ==="
printf '    %-30s %s\n' "virtualenv" "${VIRTUAL_ENV:-none}"
printf '    %-30s %s\n' "python3" "$(command -v python3)"

echo
echo "=== Capture tools ==="
check_tool() {
  local label="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    printf '    %-30s ok\n' "${label}"
  else
    printf '    %-30s MISSING\n' "${label}"
    failures=$((failures + 1))
  fi
}
check_tool "py-spy"   py-spy --version
check_tool "memray"   python3 -m memray --version
check_tool "perf"     perf --version
check_tool "pidstat"  pidstat -V
check_tool "timeout"  command -v timeout

echo
printf '    %-30s %s\n' "free disk on $PWD" "$(df -h "$PWD" | awk 'NR==2 {print $4}')"

echo
if [[ ${failures} -ne 0 ]]; then
  echo "!! ${failures} check(s) failed. Fix these before capturing or seeding; a" >&2
  echo "   profile taken against the wrong target, or without the tools, cannot" >&2
  echo "   be used." >&2
  exit 1
fi
echo "=== Target and tooling confirmed ==="
exit 0
