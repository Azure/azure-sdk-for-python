"""End-to-end smoke test for the Rust binding's create_item.

Run after `maturin develop`. Targets either the local Cosmos DB
Emulator (default) or any account whose endpoint + key you set via
env vars.

Prerequisites:
  - `maturin develop` succeeded → azure/cosmos/_rust.pyd exists
  - Cosmos DB Emulator running locally on https://localhost:8081
    OR set COSMOS_ENDPOINT + COSMOS_KEY env vars to a real account
  - A database `pyo3test` and container `items` (partitioned on /pk)
    already exist in the target account. Create with the portal, the
    emulator's Data Explorer, or:
        az cosmosdb sql database create -a <acct> -g <rg> -n pyo3test
        az cosmosdb sql container create -a <acct> -g <rg> -d pyo3test \
            -n items --partition-key-path /pk

What this test does:
  1. Builds a PreparedRequest by hand (Python helper layer would
     normally build it; we skip that here to keep the test focused
     on the binding).
  2. Constructs RustBackend with the endpoint+key.
  3. Calls .execute(prepared) → goes through PyO3 → driver →
     real HTTP to Cosmos.
  4. Prints the BackendResponse it gets back.
"""
from __future__ import annotations

import os
import sys
import uuid

# Default to the Cosmos DB Emulator's well-known endpoint + key.
ENDPOINT = os.environ.get("COSMOS_ENDPOINT", "https://localhost:8081")
KEY = os.environ.get(
    "COSMOS_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)
DB = os.environ.get("COSMOS_DB", "pyo3test")
COLL = os.environ.get("COSMOS_COLL", "items")


def main() -> int:
    # 1. The binding must be importable. If not, maturin develop hasn't run.
    try:
        from azure.cosmos import _rust  # noqa: F401
    except ImportError as e:
        print(f"FAIL: _rust not built: {e}", file=sys.stderr)
        print("Run `maturin develop` from the repo root.", file=sys.stderr)
        return 2

    from azure.cosmos._backend.base import OP_CREATE_ITEM, PreparedRequest
    from azure.cosmos._backend.rust import RustBackend

    # 2. Build a PreparedRequest by hand (one create, single-string PK).
    item_id = f"smoke-{uuid.uuid4()}"
    prepared = PreparedRequest(
        op=OP_CREATE_ITEM,
        container_link=f"dbs/{DB}/colls/{COLL}",
        body_bytes=f'{{"id":"{item_id}","pk":"smokeA","value":42}}'.encode(),
        partition_key_header='["smokeA"]',
        headers={},
    )

    # 3. Hand it to the backend.
    print(f"Endpoint : {ENDPOINT}")
    print(f"Container: dbs/{DB}/colls/{COLL}")
    print(f"Item id  : {item_id}")
    print("Calling RustBackend.execute ...", flush=True)

    backend = RustBackend(endpoint=ENDPOINT, master_key=KEY)
    try:
        resp = backend.execute(prepared)
    except Exception as e:  # pylint: disable=broad-except
        print(f"FAIL: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    if resp is None:
        print("FAIL: backend returned None (no PreparedRequest dispatched).", file=sys.stderr)
        return 1

    # 4. Inspect.
    print(f"\nstatus_code = {resp.status_code}")
    print(f"sub_status  = {resp.sub_status}")
    print(f"body        = {resp.body[:200]!r}")
    if 200 <= resp.status_code < 300:
        print("\nOK — round trip Python → PyO3 → driver → Cosmos succeeded.")
        return 0
    print("\nNon-2xx from service. Body above is the error payload.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

