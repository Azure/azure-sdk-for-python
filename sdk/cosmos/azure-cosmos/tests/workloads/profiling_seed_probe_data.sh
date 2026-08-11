#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# RESPONSIBILITY: make sure every item the profiled reads can ask for exists.
#
# The point-read workload does not create what it reads. It picks an id with
# random.randint(0, COSMOS_MAX_ITEM_INDEX) and reads it. Any id in that range
# that was never seeded comes back 404, and a 404 takes a different code path:
# it is an error row, not a latency sample. A partially seeded container
# therefore quietly contaminates the very numbers the session exists to
# produce.
#
# WHY IT CHECKS THE WHOLE RANGE: an interior item can be missing while both
# ends are present -- a single delete, or a seeding run that failed partway.
# Sampling the endpoints would call that container ready. The range is 1,001
# items, so verifying all of them costs about 1,001 RU once, against a 400 RU/s
# container: a few seconds, run once per environment rather than per session.
#
# WHY ONLY "NOT FOUND" COUNTS AS MISSING: a timeout, 403, 429, DNS or TLS
# failure means the probe could not answer the question. Treating those as
# "missing" would reseed 1,001 items because of a transient fault, and would
# hide a real credential or connectivity problem behind a write storm. Anything
# that is not a 404 stops this script instead.
#
# Usage:
#   ./profiling_seed_probe_data.sh          # verify, seed only if items missing
#   PROFILING_FORCE_SEED=1 ./profiling_seed_probe_data.sh   # always reseed
# ---------------------------------------------------------------------------
set -uo pipefail
cd "$(dirname "$0")"

source ./profiling_common.sh
profiling_load_env || exit 2

echo "=== Probe data ==="
echo "    target : ${COSMOS_DATABASE}/${COSMOS_CONTAINER}"
echo "    range  : test-0 .. test-${COSMOS_MAX_ITEM_INDEX} ($(( COSMOS_MAX_ITEM_INDEX + 1 )) items)"

needs_seed=0
if [[ "${PROFILING_FORCE_SEED:-0}" == "1" ]]; then
  echo "    PROFILING_FORCE_SEED=1, reseeding without checking."
  needs_seed=1
else
  python3 - <<'PY'
import os
import sys

from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError

uri = os.environ["COSMOS_URI"]
key = os.environ["COSMOS_KEY"]
database = os.environ["COSMOS_DATABASE"]
container_name = os.environ["COSMOS_CONTAINER"]
max_index = int(os.environ["COSMOS_MAX_ITEM_INDEX"])

# initial-setup.py gives every seeded item both id="test-N" and pk="pk-N", but
# only one of those fields is the partition key. workload_configs.py reads the
# path from COSMOS_PARTITION_KEY and defaults it to "id", so on this target the
# partition key VALUE is the id itself. Using the wrong field would make every
# read miss and trigger a pointless reseed.
pk_field = os.environ.get("COSMOS_PARTITION_KEY", "id")


def probe_ids(index):
    fields = {"id": f"test-{index}", "pk": f"pk-{index}"}
    return fields["id"], fields.get(pk_field, fields["id"])


try:
    container = (
        CosmosClient(uri, key)
        .get_database_client(database)
        .get_container_client(container_name)
    )
except Exception as exc:
    print(f"    cannot reach {database}/{container_name}: {exc}")
    sys.exit(3)

missing = []
total = max_index + 1
for index in range(total):
    item_id, pk_value = probe_ids(index)
    try:
        container.read_item(item_id, partition_key=pk_value)
    except CosmosResourceNotFoundError:
        missing.append(item_id)
    except Exception as exc:
        # Not an answer to "does this item exist?". Stop rather than reseed.
        print(f"    probe failed on {item_id}: {type(exc).__name__}: {exc}")
        sys.exit(3)

if missing:
    shown = ", ".join(missing[:10])
    more = f" (and {len(missing) - 10} more)" if len(missing) > 10 else ""
    print(f"    missing {len(missing)} of {total}: {shown}{more}")
    sys.exit(1)
print(f"    verified all {total} items (partition key /{pk_field})")
sys.exit(0)
PY
  case $? in
    0) needs_seed=0 ;;
    1) needs_seed=1 ;;
    *)
      echo "!! Could not verify the probe data, so it will not be seeded blindly." >&2
      echo "   Fix the connectivity or permission problem above and re-run." >&2
      exit 1
      ;;
  esac
fi

if [[ ${needs_seed} -eq 0 ]]; then
  echo "=== Probe data complete; nothing to do ==="
  exit 0
fi

echo "    Seeding $(( COSMOS_MAX_ITEM_INDEX + 1 )) items with initial-setup.py ..."
# initial-setup.py upserts, so re-running it repairs a partial range without
# needing to work out which ids are absent.
if ! python3 initial-setup.py; then
  echo "ERROR: seeding failed; reads would return 404 instead of latency samples." >&2
  exit 1
fi
echo "=== Probe data seeded ==="
exit 0
