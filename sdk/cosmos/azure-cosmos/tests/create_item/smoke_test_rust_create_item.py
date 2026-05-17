"""End-to-end smoke test for the Rust binding's ``create_item``.

What this script does\n---------------------\nThis is a one-shot manual smoke test you run after ``maturin develop``
to prove the *whole* Rust path actually works against a live Cosmos
account: Python → PyO3 binding → Rust driver → HTTPS → Cosmos →
back. It is deliberately *not* a pytest test — it expects a real
account (or the local emulator) and produces visible printed output
so you can tell at a glance whether the round-trip succeeded.

It bypasses the Python helper layer that would normally build the
``PreparedRequest`` (request-prep / options / PK serialization /
body request-byte / etc.). Building the prepared request by hand keeps the
failure mode focused on the binding and the driver — if this fails,
you know the problem is below the helper layer, not above it.

Defaults target the local Cosmos DB Emulator. Override with
``COSMOS_ENDPOINT``, ``COSMOS_KEY``, ``COSMOS_DB`` and
``COSMOS_COLL`` env vars to point at a real account.

Prerequisites
-------------
* ``maturin develop`` has been run, so ``azure/cosmos/_rust.pyd`` exists.
* The Cosmos DB Emulator is running on https://localhost:8081, **or**
  ``COSMOS_ENDPOINT`` + ``COSMOS_KEY`` are set to a real account.
* A database (default ``pyo3test``) and a container (default ``items``,
  partitioned on ``/pk``) already exist. Create with the portal, the
  emulator's Data Explorer, or the Azure CLI::

      az cosmosdb sql database create -a <acct> -g <rg> -n pyo3test
      az cosmosdb sql container create -a <acct> -g <rg> -d pyo3test \\
          -n items --partition-key-path /pk

Exit codes
----------
* 0 — round trip succeeded with a 2xx response.
* 1 — the binding executed but the service returned non-2xx, or the
       backend produced no response.
* 2 — the compiled ``_rust`` module is missing (run ``maturin develop``).
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
    """Run the smoke test and return a process exit code (see module docstring)."""
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
    #    The Python helper layer would normally do this; building it
    #    inline keeps the failure mode focused on the binding + driver.
    item_id = f"smoke-{uuid.uuid4()}"
    prepared = PreparedRequest(
        op=OP_CREATE_ITEM,
        container_link=f"dbs/{DB}/colls/{COLL}",
        body_bytes=f'{{"id":"{item_id}","pk":"smokeA","value":42}}'.encode(),
        partition_key_header='["smokeA"]',
        headers={},
    )

    # 3. Hand it to the backend and round-trip it through PyO3 → driver → Cosmos.
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

    # 4. Print the response so a human can eyeball the result.
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
