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

Set ``ACCOUNT_HOST`` + ``ACCOUNT_KEY`` to your Cosmos account (the emulator
or a live account). The db (``parity_db``) and container (``smoke_create``)
are created if missing.

Prerequisites
-------------
* ``maturin develop`` has been run, so ``azure/cosmos/_rust.pyd`` exists.
* ``ACCOUNT_HOST`` + ``ACCOUNT_KEY`` point at a reachable Cosmos account.

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

from azure.cosmos import CosmosClient, PartitionKey

ENDPOINT = os.environ.get("ACCOUNT_HOST")
KEY = os.environ.get("ACCOUNT_KEY")
DB = os.environ.get("COSMOS_DB", "parity_db")
COLL = os.environ.get("COSMOS_COLL", "smoke_create")


def _ensure_db_and_container() -> None:
    """Create the db + container via the legacy backend if missing, so the
    rust path is never asked to resolve a container that does not exist."""
    client = CosmosClient(ENDPOINT, KEY)
    db = client.create_database_if_not_exists(DB)
    db.create_container_if_not_exists(id=COLL, partition_key=PartitionKey(path="/pk"))


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

    # 2. Make sure the target db + container exist (created via the legacy
    #    backend), then build a PreparedRequest by hand (one create,
    #    single-string PK). Building it inline keeps the failure mode focused
    #    on the binding + driver.
    if not ENDPOINT or not KEY:
        print("FAIL: set ACCOUNT_HOST + ACCOUNT_KEY first.", file=sys.stderr)
        return 1
    _ensure_db_and_container()
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
