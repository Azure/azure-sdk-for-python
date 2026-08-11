#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# RESPONSIBILITY: prove, from one real completed point read, that the read
# entered the compiled Rust binding AND which transport carried it.
#
# COSMOS_BACKEND=rust states an intention. A failed extension load leaves a
# working Python path that still looks Rust-configured, so the label alone is
# not evidence. This script issues one read of a known seeded item and checks
# two independent things about it:
#
#   1  the binding counters moved   -> the operation really entered Rust
#   2  the driver's own diagnostic  -> which transport that operation used
#
# WHY BOTH: the counters prove Rust but say nothing about transport; the
# diagnostic string names the transport but is only meaningful if the read it
# describes actually went through Rust. Either alone is partial evidence.
#
# THE DIAGNOSTIC IS SYNTHETIC: the binding formats the driver's per-attempt
# record and Python stores it in a LOCAL response-header dictionary under
# x-ms-cosmos-sdk-diagnostics. Cosmos DB never sends that header despite the
# x-ms- name, so it will not appear in a network capture. It is produced by the
# code under test, which is exactly why the counter check above it matters.
#
# WHY THE DURATION HERE IS NOT LATENCY: this is a single first read on a fresh
# client, so it includes connection and TLS setup. It is a path proof, not a
# measurement. The latency baseline comes from the 250-read/s run.
#
# VERDICT: prints exactly one line beginning "TRANSPORT VERDICT:" and exits
#   0  gateway_v2      -- Rust proved, Gateway V2 proved
#   1  gateway         -- Rust proved, standard Gateway (a valid but different
#                         claim; the baseline must be attributed accordingly)
#   2  invalid sample  -- the read did not complete, did not enter Rust,
#                         produced no transport evidence, or named more than
#                         one data-plane transport. Prove nothing from it.
#
# THIS SCRIPT IS STILL WORTH RUNNING AFTER A TOPOLOGY FAILURE. If the account
# advertises no ThinClient URLs, Gateway V2 is ruled out -- but which transport
# DID carry the read is still unproven, and verdict 1 is what proves it.
#
# Usage:
#   ./profiling_prove_transport.sh              # reads test-1 by default
#   PROFILING_PROOF_ITEM=test-7 ./profiling_prove_transport.sh
# After a baseline, the script automatically reads that run's saved target.
# Override it explicitly with PROFILING_PROOF_DATABASE,
# PROFILING_PROOF_CONTAINER, and PROFILING_PROOF_PARTITION_KEY.
# ---------------------------------------------------------------------------
set -uo pipefail
cd "$(dirname "$0")"

source ./profiling_common.sh
profiling_load_env || exit 2

if [[ -z "${ARTIFACTS:-}" || ! -d "${ARTIFACTS}" ]]; then
  echo "ERROR: no profiling session is loaded, so this proof has nowhere to be filed." >&2
  echo "       Run:  source ./profiling_activate.sh" >&2
  exit 2
fi

# The extension that answers this proof must be the one the session recorded,
# or the proof describes a different build from the one being measured.
profiling_verify_extension_build || exit 2

RECORDED_DATABASE=""
RECORDED_CONTAINER=""
RECORDED_PARTITION_KEY=""
BASELINE_TARGET_FILE="${ARTIFACTS}/light-load-baseline-${RUN_ID}/baseline-target.env"
if [[ -f "${BASELINE_TARGET_FILE}" ]]; then
  # Written with printf %q by run_light_load_baseline.sh.
  # shellcheck disable=SC1090
  source "${BASELINE_TARGET_FILE}" || {
    echo "ERROR: could not load baseline target ${BASELINE_TARGET_FILE}." >&2
    exit 2
  }
  RECORDED_DATABASE="${BASELINE_DATABASE:-}"
  RECORDED_CONTAINER="${BASELINE_CONTAINER:-}"
  RECORDED_PARTITION_KEY="${BASELINE_PARTITION_KEY:-}"
fi

PROOF_DATABASE="${PROFILING_PROOF_DATABASE:-${RECORDED_DATABASE:-${COSMOS_DATABASE}}}"
PROOF_CONTAINER="${PROFILING_PROOF_CONTAINER:-${RECORDED_CONTAINER:-${COSMOS_CONTAINER}}}"
PROOF_PARTITION_KEY="${PROFILING_PROOF_PARTITION_KEY:-${RECORDED_PARTITION_KEY:-${COSMOS_PARTITION_KEY:-id}}}"
export COSMOS_DATABASE="${PROOF_DATABASE}"
export COSMOS_CONTAINER="${PROOF_CONTAINER}"
export COSMOS_PARTITION_KEY="${PROOF_PARTITION_KEY}"

PROOF_ITEM="${PROFILING_PROOF_ITEM:-test-1}"
OUT="${ARTIFACTS}/rust-diagnostics-sample.txt"

echo "=== Path proof: did one real read enter Rust, and over which transport? ==="
echo "    container : ${COSMOS_DATABASE}/${COSMOS_CONTAINER}"
echo "    item      : ${PROOF_ITEM}"
echo "    output    : ${OUT}"
echo

COSMOS_BACKEND=rust PROFILING_PROOF_ITEM="${PROOF_ITEM}" \
python3 - <<'PY' 2>&1 | tee "${OUT}"
import asyncio
import os
import re
import sys

# Guarded for the same reason the verdicts are three-way: an ImportError would
# exit 1, which is this script's "standard Gateway" code. A missing extension
# would then be recorded as a successful Rust read over plain Gateway -- the
# exact confusion these counters exist to prevent.
try:
    from azure.cosmos.aio import CosmosClient
    from azure.cosmos import _rust
except Exception as exc:
    print(f"could not import the Rust-backed SDK: {type(exc).__name__}: {exc}")
    print("TRANSPORT VERDICT: invalid sample -- the SDK or _rust extension failed to import")
    sys.exit(2)

DIAGNOSTICS = "x-ms-cosmos-sdk-diagnostics"
ITEM = os.environ.get("PROFILING_PROOF_ITEM", "test-1")

# The seeded container partitions on /id, so the item id and the partition-key
# value are the same string. A container with a different path needs an id and
# a matching partition-key value instead.
PK_PATH = os.environ.get("COSMOS_PARTITION_KEY", "id").lstrip("/")


async def main() -> int:
    seen = {"diagnostics": None}

    def capture(headers, _body):
        seen["diagnostics"] = headers.get(DIAGNOSTICS)

    regions = [
        r.strip()
        for r in os.environ.get("COSMOS_PREFERRED_LOCATIONS", "").split(",")
        if r.strip()
    ]

    async with CosmosClient(
        os.environ["COSMOS_URI"], os.environ["COSMOS_KEY"], preferred_locations=regions
    ) as client:
        backend = type(client._backend).__name__
        print("runtime backend:", backend)
        if backend != "AsyncRustBackend":
            # Everything below would describe the core-Python path instead.
            print("TRANSPORT VERDICT: invalid sample -- the client is not Rust-backed")
            return 2

        container = client.get_database_client(
            os.environ["COSMOS_DATABASE"]
        ).get_container_client(os.environ["COSMOS_CONTAINER"])

        before_ops = _rust.operation_count()
        before_attempts = _rust.attempt_count()
        before_retries = _rust.retry_count()

        pk_value = ITEM if PK_PATH == "id" else os.environ.get("PROFILING_PROOF_PK", ITEM)
        try:
            item = await container.read_item(
                item=ITEM, partition_key=pk_value, response_hook=capture
            )
        except Exception as exc:
            print(f"read failed: {type(exc).__name__}: {exc}")
            print("TRANSPORT VERDICT: invalid sample -- the read did not complete")
            return 2

        ops = _rust.operation_count() - before_ops
        attempts = _rust.attempt_count() - before_attempts
        retries = _rust.retry_count() - before_retries

    print("item id:", item.get("id"))
    print("binding operation delta:", ops)
    print("wire attempt delta:", attempts)
    print("retry delta:", retries)
    print("diagnostics:", seen["diagnostics"] or "(diagnostics header missing)")

    # 1. Did this read enter Rust? One operation, at least one attempt. Retries
    #    are reported rather than failed: a retried read still proves the path,
    #    it just is not the clean single-attempt shape the baseline wants.
    if ops != 1:
        print(f"TRANSPORT VERDICT: invalid sample -- binding counted {ops} operations, expected 1")
        return 2
    if attempts < 1:
        print("TRANSPORT VERDICT: invalid sample -- the driver recorded no attempt")
        return 2
    if retries:
        print(f"note: {retries} retry/failover/hedge attempt(s) on this read")

    # 2. Which transport carried it?
    #
    #    The diagnostics list every transport the driver touched, metadata
    #    lookups included, as transports=[metadata/gateway,data_plane/gateway_v2].
    #    Only the data-plane entries answer this question. A substring test for
    #    "gateway_v2" anywhere in that text is not safe: a retried read can have
    #    attempted standard Gateway and Gateway V2 in the same sample, and the
    #    substring would report Gateway V2 for a read that was mostly not. So
    #    collect the distinct data-plane transports and require exactly one --
    #    a sample that names two proves the path but cannot attribute latency.
    text = seen["diagnostics"] or ""
    data_plane = []
    for group in re.findall(r"transports=\[([^\]]*)\]", text):
        for entry in group.split(","):
            entry = entry.strip()
            if entry.startswith("data_plane/") and entry not in data_plane:
                data_plane.append(entry)
    if not data_plane:
        print("TRANSPORT VERDICT: invalid sample -- no data-plane transport in the diagnostics")
        return 2
    if len(data_plane) > 1:
        print(
            "TRANSPORT VERDICT: invalid sample -- this read used more than one "
            f"data-plane transport ({', '.join(data_plane)}), so the latency "
            "cannot be attributed to either"
        )
        return 2
    if data_plane[0] == "data_plane/gateway_v2":
        print("TRANSPORT VERDICT: gateway_v2 -- Rust proved, Gateway V2 proved")
        return 0
    if data_plane[0] == "data_plane/gateway":
        print("TRANSPORT VERDICT: gateway -- Rust proved, standard Gateway carried the read")
        return 1
    print(
        "TRANSPORT VERDICT: invalid sample -- unrecognised data-plane transport "
        f"{data_plane[0]!r}"
    )
    return 2


try:
    sys.exit(asyncio.run(main()))
except SystemExit:
    raise
except Exception as exc:
    # Anything unhandled still has to leave a verdict behind, or the caller
    # would be left with an exit code and no statement of what was proved.
    print(f"unexpected failure: {type(exc).__name__}: {exc}")
    print("TRANSPORT VERDICT: invalid sample -- the proof did not run to completion")
    sys.exit(2)
PY
rc=${PIPESTATUS[0]}

# rc is cross-checked against the printed verdict for the same reason the
# import is guarded: a process that dies before deciding anything can still
# exit 0 or 1, and either would be read here as a proved path.
if ! grep -q '^TRANSPORT VERDICT:' "${OUT}"; then
  echo >&2
  echo "!! No TRANSPORT VERDICT line was produced, so nothing was proved." >&2
  echo "   Treating this as an invalid sample. See ${OUT} for what happened." >&2
  rc=2
else
  # A printed verdict is the decision; the exit code is only how it was
  # reported. Anything running after the decision could change the code while
  # the text stands, so disagreement resolves in favour of the text.
  verdict_word="$(sed -n 's/^TRANSPORT VERDICT: \([a-z_ ]*[a-z_0-9]\).*/\1/p' "${OUT}" | tail -n 1)"
  case "${verdict_word}" in
    gateway_v2)      expected_rc=0 ;;
    gateway)         expected_rc=1 ;;
    "invalid sample") expected_rc=2 ;;
    *)               expected_rc=2 ;;
  esac
  if [[ "${rc}" != "${expected_rc}" ]]; then
    echo >&2
    echo "!! The printed verdict and the exit code disagree: verdict" >&2
    echo "   '${verdict_word}' implies ${expected_rc}, but the process exited ${rc}." >&2
    echo "   Something ran after the decision was made. Trusting the verdict text." >&2
    rc=${expected_rc}
  fi
fi

echo
case ${rc} in
  0)
    echo "    Recorded in ${OUT}."
    echo "    A completed read entered the Rust binding and used Gateway V2. The"
    echo "    baseline latency may be attributed to the Rust Gateway V2 path."
    ;;
  1)
    echo "    Recorded in ${OUT}."
    echo "    A completed read entered the Rust binding, but standard Gateway"
    echo "    carried it. This is a valid result with a different claim: report"
    echo "    the baseline as standard Gateway, not Gateway V2."
    ;;
  *)
    echo "!! This sample proves nothing -- see the reason above." >&2
    echo "   Do not attach latency to a path that was not proved. Fix the cause" >&2
    echo "   and re-run before measuring." >&2
    ;;
esac
exit ${rc}
