#!/usr/bin/env bash
# Validate the independently confirmed test target and live container properties.
# No item writes and no capture-tool requirements.
# Usage: bash profiling_check_target.sh --confirm-target <endpoint> <database> <container>
set -uo pipefail
cd "$(dirname "$0")"
source ./profiling_common.sh
profiling_load_env || exit 2
profiling_confirm_target "$@" || exit 2

if [[ "${COSMOS_URI%/}" == "${RESULTS_COSMOS_URI%/}" &&
      "$COSMOS_DATABASE" == "$RESULTS_COSMOS_DATABASE" &&
      "$COSMOS_CONTAINER" == "$RESULTS_COSMOS_CONTAINER" ]]; then
  echo "ERROR: the test container and results container must be different." >&2
  exit 2
fi

echo "=== Confirmed test target: ${COSMOS_URI} ${COSMOS_DATABASE}/${COSMOS_CONTAINER} ==="
python3 - "${COSMOS_PARTITION_KEY}" "${COSMOS_THROUGHPUT}" <<'PY'
import os
import sys
from azure.cosmos import CosmosClient

expected_pk, expected_throughput = sys.argv[1], int(sys.argv[2])
with CosmosClient(os.environ["COSMOS_URI"], os.environ["COSMOS_KEY"], _backend="core-python") as client:
    container = client.get_database_client(os.environ["COSMOS_DATABASE"]).get_container_client(
        os.environ["COSMOS_CONTAINER"])
    properties = container.read()
    paths = (properties.get("partitionKey") or {}).get("paths") or []
    offer = container.get_throughput()
    if paths != ["/" + expected_pk] or offer.offer_throughput != expected_throughput:
        raise SystemExit(
            f"live container mismatch: expected /{expected_pk} and {expected_throughput} RU/s; "
            f"received {paths!r} and {offer.offer_throughput!r}"
        )
    if offer.auto_scale_max_throughput is not None:
        raise SystemExit("Expected dedicated manual throughput, not autoscale")
    print(f"Test container: /{expected_pk}, dedicated manual {expected_throughput} RU/s")
PY
[[ $? -eq 0 ]] || exit 1

echo "=== Results container configuration ==="
python3 - <<'PY'
import os
from azure.cosmos import CosmosClient

client = CosmosClient(
    os.environ["RESULTS_COSMOS_URI"], os.environ["RESULTS_COSMOS_KEY"], _backend="core-python",
)
try:
    container = client.get_database_client(os.environ["RESULTS_COSMOS_DATABASE"]).get_container_client(
        os.environ["RESULTS_COSMOS_CONTAINER"])
    properties = container.read()
    paths = (properties.get("partitionKey") or {}).get("paths") or []
    if paths != ["/partition_key"]:
        raise SystemExit(
            f"results container partition-key mismatch: expected /partition_key, got {paths!r}"
        )
    print("Results container exists and uses /partition_key")
finally:
    client.close()
PY
[[ $? -eq 0 ]] || exit 1
echo "=== Test target and results container confirmed ==="
