#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# RESPONSIBILITY: answer one question -- does this account advertise Gateway V2?
#
# Before a client sends any read it asks the account to describe itself: which
# regions hold the data, which accept writes, and which URLs to send requests
# to. That description is the account topology, and Gateway V2 appears in it as
# an extra set of URLs, the ThinClient URLs. If the account does not return
# them, no read can possibly use Gateway V2, whatever the client is configured
# to do -- so this check runs BEFORE the transport proof. A failure here means
# Gateway V2 cannot be the answer; it does NOT mean the transport proof should
# be skipped. That proof is what establishes which transport actually carried
# the read, and "standard Gateway" is a result it can prove rather than one
# this script may assume.
#
# WHY THIS ONE CHECK USES CORE PYTHON: the topology request has to carry the
# header x-ms-cosmos-use-thinclient: true, and the raw account response has to
# be readable. The Rust client consumes those fields internally and does not
# expose the raw response through the Python API. This script therefore asks
# core Python for the account description only. It performs NO point read, and
# proves nothing about which transport a read uses -- that is
# profiling_prove_transport.sh.
#
# WHY A PARTIAL LIST IS ITS OWN VERDICT: the baseline is attributed to an
# account that offers Gateway V2 for both reads and writes, so only two
# non-empty lists earn "advertised". But one non-empty list is not the same as
# none: if the readable list has URLs and the writable list does not, reads can
# still use Gateway V2 while writes fall back. Reporting that as "no ThinClient
# URLs were returned" would be false, so it gets a third verdict of its own.
#
# VERDICT: prints exactly one line beginning "TOPOLOGY VERDICT:" and exits
#   0  advertised      -- both lists non-empty
#   1  not advertised  -- the account returned no ThinClient URLs at all
#   3  partial         -- exactly one list non-empty; states which
#   2  could not ask   -- config, credential or connectivity failure
#
# Usage:
#   ./profiling_prove_topology.sh
# ---------------------------------------------------------------------------
set -uo pipefail
cd "$(dirname "$0")"

source ./profiling_common.sh
profiling_load_env || exit 2

# The output belongs to the session so it can be cited next to the latency it
# supports. Without a loaded session there is nowhere to file the evidence.
if [[ -z "${ARTIFACTS:-}" || ! -d "${ARTIFACTS}" ]]; then
  echo "ERROR: no profiling session is loaded, so this proof has nowhere to be filed." >&2
  echo "       Run:  source ./profiling_activate.sh" >&2
  exit 2
fi

OUT="${ARTIFACTS}/thin-client-topology.txt"

echo "=== Account topology: does this account advertise Gateway V2? ==="
echo "    account : ${COSMOS_URI}"
echo "    output  : ${OUT}"
echo

# COSMOS_BACKEND is forced for this one command: the question is about the
# account's own description, and only core Python surfaces the raw response.
COSMOS_BACKEND=core-python python3 - <<'PY' 2>&1 | tee "${OUT}"
import os
import sys

# A failed import must not be mistaken for "the account said no". Python would
# exit 1 on an uncaught ImportError, which is this script's "not advertised"
# code, so the import is guarded and reported as "could not ask" instead.
try:
    from azure.cosmos import CosmosClient
except Exception as exc:
    print(f"could not import azure.cosmos: {type(exc).__name__}: {exc}")
    print("TOPOLOGY VERDICT: could not ask -- the SDK failed to import")
    sys.exit(2)

captured = {}
try:
    client = CosmosClient(os.environ["COSMOS_URI"], credential=os.environ["COSMOS_KEY"])
except Exception as exc:
    print(f"could not create a client: {type(exc).__name__}: {exc}")
    print("TOPOLOGY VERDICT: could not ask -- the client could not be created")
    sys.exit(2)

try:
    connection = client.client_connection
    # Without this header the account describes itself the old way and omits
    # the ThinClient URLs even when it supports them, which would read as a
    # negative result rather than as a question that was never asked.
    connection.default_headers["x-ms-cosmos-use-thinclient"] = "true"
    connection.GetDatabaseAccount(
        response_hook=lambda _headers, body: captured.update(body)
    )
except Exception as exc:
    print(f"could not read the account topology: {type(exc).__name__}: {exc}")
    print("TOPOLOGY VERDICT: could not ask -- the account description could not be read")
    sys.exit(2)
finally:
    # close() runs while a SystemExit from the handlers above is propagating.
    # If it raised, that exception would replace the SystemExit -- turning a
    # deliberate exit 2 ("could not ask") into an uncaught-exception exit 1,
    # which is this script's "not advertised" code, after the "could not ask"
    # verdict had already been printed. Teardown must not be able to change a
    # decided answer, so its failure is reported and discarded.
    try:
        client.close()
    except Exception as exc:  # noqa: BLE001 - teardown must not alter the verdict
        print(f"note: closing the client failed: {type(exc).__name__}: {exc}")

readable = captured.get("thinClientReadableLocations") or []
writable = captured.get("thinClientWritableLocations") or []

print("thin client readable count:", len(readable))
for location in readable:
    print("readable:", location.get("name"), location.get("databaseAccountEndpoint"))
print("thin client writable count:", len(writable))
for location in writable:
    print("writable:", location.get("name"), location.get("databaseAccountEndpoint"))

if readable and writable:
    print("TOPOLOGY VERDICT: advertised -- the account offers Gateway V2 endpoints")
    sys.exit(0)
if readable or writable:
    have = "readable" if readable else "writable"
    missing = "writable" if readable else "readable"
    print(
        f"TOPOLOGY VERDICT: partial -- {have} ThinClient URLs were returned, "
        f"{missing} were not"
    )
    sys.exit(3)
print("TOPOLOGY VERDICT: not advertised -- no ThinClient URLs were returned")
sys.exit(1)
PY
rc=${PIPESTATUS[0]}

# The exit code alone is not trusted. If the interpreter died before reaching a
# verdict -- a crash, a kill, an exception in an unexpected place -- rc could
# still land on 0 or 1 and be read as a real answer. Require the verdict line
# the script promises to print, and downgrade anything else to "could not ask".
if ! grep -q '^TOPOLOGY VERDICT:' "${OUT}"; then
  echo >&2
  echo "!! No TOPOLOGY VERDICT line was produced, so there is no answer to record." >&2
  echo "   Treating this as 'could not ask'. See ${OUT} for what happened." >&2
  rc=2
else
  # A verdict line existing is not the same as it agreeing with the exit code.
  # Anything that runs after the decision -- client teardown, an interpreter
  # shutdown error -- can replace the intended exit code while the printed
  # verdict stands, and the wrong branch below would then be reported as the
  # account's answer. The text is the decision, so it wins.
  verdict_word="$(sed -n 's/^TOPOLOGY VERDICT: \([a-z ]*[a-z]\).*/\1/p' "${OUT}" | tail -n 1)"
  case "${verdict_word}" in
    advertised)     expected_rc=0 ;;
    "not advertised") expected_rc=1 ;;
    partial)        expected_rc=3 ;;
    "could not ask") expected_rc=2 ;;
    *)              expected_rc=2 ;;
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
    echo "    This proves the account OFFERS Gateway V2. It does not prove that any"
    echo "    read used it, or that this VM can reach those URLs. Prove that next:"
    echo "        ./profiling_prove_transport.sh"
    ;;
  1)
    echo "!! The account did not return ThinClient URLs." >&2
    echo "   No read against this account can use Gateway V2, so a Gateway V2" >&2
    echo "   result cannot be produced here. Do NOT record the run as standard" >&2
    echo "   Gateway on the strength of this check alone -- it says nothing" >&2
    echo "   about which transport a read used. Prove that:" >&2
    echo "        ./profiling_prove_transport.sh" >&2
    echo "   and expect its 'gateway' verdict. Or profile an account that does" >&2
    echo "   advertise ThinClient URLs." >&2
    ;;
  3)
    echo "!! The account advertised only one of the two ThinClient URL lists." >&2
    echo "   Reads and writes would not take the same transport, which is not" >&2
    echo "   the topology the baseline is attributed to. If the readable list" >&2
    echo "   is the populated one, a read may still use Gateway V2 -- so run" >&2
    echo "        ./profiling_prove_transport.sh" >&2
    echo "   to find out which transport actually carried it, and report the" >&2
    echo "   split topology alongside the result." >&2
    ;;
  *)
    echo "!! The question could not be asked -- see the error above." >&2
    echo "   This is NOT evidence that the account lacks Gateway V2." >&2
    ;;
esac
exit ${rc}
