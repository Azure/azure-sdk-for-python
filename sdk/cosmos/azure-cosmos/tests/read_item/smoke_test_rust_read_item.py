"""End-to-end smoke test for the Rust binding's ``read_item``.

Exercises the full Rust path (Python -> PyO3 -> driver -> HTTPS ->
Cosmos -> back) by creating a single item via the Rust create path and
then reading it back via the Rust read path. Not a pytest test: needs
a real account or the local emulator and prints visible output so a
human can confirm the round trip.

Sibling of ``tests/delete_item/smoke_test_rust_delete_item.py``;
same env-var contract, same exit codes, same friendly error when the
``_rust`` module is missing.

Set ``ACCOUNT_HOST`` + ``ACCOUNT_KEY`` to your Cosmos account.
* ``COSMOS_DB`` (default ``parity_db``) and ``COSMOS_COLL`` (default
  ``smoke_read``). Both are created with the legacy backend if missing.

Prerequisites: ``maturin develop`` has been run **after** the
``lib.rs`` change that added the ``read_item`` pyfunction. Without
that rebuild, the script bails with exit code 2 and points at the
build command. A stale ``_rust.pyd`` from before the change will
report ``_rust module does not export 'read_item'``.

Exit codes:

* 0 -- create + read round trip both returned 2xx.
* 1 -- a request executed but the service returned non-2xx, the
       backend returned None, or env vars are missing.
* 2 -- the compiled ``_rust`` module is missing OR does not export
       ``read_item`` (run ``maturin develop`` from the repo root).
"""
from __future__ import annotations

import os
import sys
import uuid

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos._backend.base import (
    OP_CREATE_ITEM,
    OP_READ_ITEM,
    PreparedRequest,
)
from azure.cosmos._backend.rust import RustBackend

ENDPOINT = os.environ.get("ACCOUNT_HOST")
KEY = os.environ.get("ACCOUNT_KEY")
DB = os.environ.get("COSMOS_DB", "parity_db")
COLL = os.environ.get("COSMOS_COLL", "smoke_read")


def _ensure_db_and_container() -> None:
    """Create the db and container via the legacy backend if missing.

    Done up-front so the rust path is not asked to resolve a container
    that does not exist yet; otherwise the binding would surface a 404
    that looks like a binding bug.
    """
    client = CosmosClient(ENDPOINT, KEY)
    db = client.create_database_if_not_exists(DB)
    db.create_container_if_not_exists(id=COLL, partition_key=PartitionKey(path="/pk"))


def main() -> int:
    """Run the smoke test and return a process exit code (see module docstring)."""
    if not ENDPOINT or not KEY:
        print(
            "FAIL: set ACCOUNT_HOST + ACCOUNT_KEY "
            "to your Cosmos DB account before running this script.",
            file=sys.stderr,
        )
        return 1

    # The compiled module is imported here (not at the top) so we can
    # print a friendly "run maturin develop" message instead of a bare
    # ImportError when the wheel is not built yet.
    try:
        from azure.cosmos import _rust  # pylint: disable=import-outside-toplevel
    except ImportError as e:
        print(f"FAIL: _rust not built: {e}", file=sys.stderr)
        print("Run `maturin develop` from the repo root.", file=sys.stderr)
        return 2

    # Sanity: confirm the binding actually registers ``read_item``. A
    # stale ``_rust.pyd`` built before the lib.rs change will be
    # importable but missing the new entry point -- catch that explicitly
    # so the message is actionable rather than a generic AttributeError
    # from inside RustBackend.execute.
    if not hasattr(_rust, "read_item"):
        print("FAIL: _rust module does not export `read_item`.", file=sys.stderr)
        print("Rebuild with `maturin develop` after lib.rs changes.", file=sys.stderr)
        return 2

    print(f"Endpoint : {ENDPOINT}")
    print(f"Database : {DB}")
    print(f"Container: {COLL}")
    print("Ensuring database + container exist (legacy backend) ...", flush=True)
    try:
        _ensure_db_and_container()
    except Exception as e:  # pylint: disable=broad-except
        print(f"FAIL: could not provision db/container: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    item_id = f"smoke-read-{uuid.uuid4()}"
    container_link = f"dbs/{DB}/colls/{COLL}"
    pk_header = '["smokeA"]'

    backend = RustBackend(endpoint=ENDPOINT, master_key=KEY)

    # ---- create a row to read ------------------------------------------
    create_prepared = PreparedRequest(
        op=OP_CREATE_ITEM,
        container_link=container_link,
        body_bytes=f'{{"id":"{item_id}","pk":"smokeA","value":1}}'.encode(),
        partition_key_header=pk_header,
        headers={},
    )

    print(f"Item id  : {item_id}")
    print("Calling RustBackend.execute(create) ...", flush=True)
    try:
        create_resp = backend.execute(create_prepared)
    except Exception as e:  # pylint: disable=broad-except
        print(f"FAIL on create: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if create_resp is None:
        print("FAIL: create returned None.", file=sys.stderr)
        return 1
    print(f"create status_code = {create_resp.status_code}")
    if not 200 <= create_resp.status_code < 300:
        print(f"create body = {create_resp.body[:200]!r}", file=sys.stderr)
        print("Non-2xx on create. Cannot proceed with read.", file=sys.stderr)
        return 1

    # ---- read the row we just created ----------------------------------
    read_prepared = PreparedRequest(
        op=OP_READ_ITEM,
        container_link=container_link,
        body_bytes=b"",
        partition_key_header=pk_header,
        headers={},
        item_id=item_id,
    )

    print("Calling RustBackend.execute(read) ...", flush=True)
    try:
        read_resp = backend.execute(read_prepared)
    except Exception as e:  # pylint: disable=broad-except
        print(f"FAIL on read: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if read_resp is None:
        print("FAIL: read returned None.", file=sys.stderr)
        return 1
    print(f"\nread status_code = {read_resp.status_code}")
    print(f"read sub_status  = {read_resp.sub_status}")
    print(f"read body        = {read_resp.body[:200]!r}")
    if 200 <= read_resp.status_code < 300:
        print("\nOK -- round trip Python -> PyO3 -> driver -> Cosmos (create + read) succeeded.")
        return 0
    print("\nNon-2xx from service on read. Body above is the error payload.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

