"""End-to-end smoke test for the Rust binding's ``upsert_item``.

Exercises the full Rust path (Python -> PyO3 -> driver -> HTTPS ->
Cosmos -> back) for insert-or-replace semantics:

1. upsert a brand-new id                 -> expect 201 Created (insert)
2. upsert the same id with a new body     -> expect 200 OK      (replace)
3. version-guarded replace with a stale
   ``If-Match`` etag                       -> expect 412         (precondition)

Step 3 proves the access-condition path the Python helper builds from
``etag`` + ``match_condition=IfNotModified`` reaches the wire through the
binding's ``custom_headers`` and the service enforces it. (Insert-only
via ``If-None-Match: *`` is deliberately *not* asserted as a 412: Cosmos
upsert lets the is-upsert flag win and replaces, returning 200 on both
the legacy and the rust path -- so it is parity, not a precondition.)

Not a pytest test: needs a real account (or the local emulator) and
prints visible output so a human can confirm the round trip.

Set ``ACCOUNT_HOST`` + ``ACCOUNT_KEY`` to your Cosmos account. The db
(``parity_db``) and container (``smoke_upsert``) are created if missing
(override with ``COSMOS_DB`` / ``COSMOS_COLL``).

Prerequisites: ``maturin develop`` has been run so ``_rust.{pyd,so}``
exists with the ``upsert_item`` entry point.

Exit codes:

* 0 -- insert (201) + replace (200) + insert-only (412) all as expected.
* 1 -- a request executed but an outcome was wrong, the backend returned
       None, or env vars are missing.
* 2 -- the compiled ``_rust`` module (or its ``upsert_item``) is missing.
"""
from __future__ import annotations

import json
import os
import sys
import uuid

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos._backend.base import OP_UPSERT_ITEM, PreparedRequest
from azure.cosmos._backend.rust import RustBackend

ENDPOINT = os.environ.get("ACCOUNT_HOST")
KEY = os.environ.get("ACCOUNT_KEY")
DB = os.environ.get("COSMOS_DB", "parity_db")
COLL = os.environ.get("COSMOS_COLL", "smoke_upsert")

CONTAINER_LINK = f"dbs/{DB}/colls/{COLL}"
PK_HEADER = '["smokeA"]'


def _ensure_db_and_container() -> None:
    """Create the db + container via the legacy backend if missing, so the
    rust path is never asked to resolve a container that does not exist."""
    client = CosmosClient(ENDPOINT, KEY)
    db = client.create_database_if_not_exists(DB)
    db.create_container_if_not_exists(id=COLL, partition_key=PartitionKey(path="/pk"))


def _upsert(backend, item_id, value, headers=None):
    body = json.dumps({"id": item_id, "pk": "smokeA", "value": value}).encode()
    prepared = PreparedRequest(
        op=OP_UPSERT_ITEM,
        container_link=CONTAINER_LINK,
        body_bytes=body,
        partition_key_header=PK_HEADER,
        headers=headers or {},
    )
    return backend.execute(prepared)


def main() -> int:
    """Run the smoke test and return a process exit code (see module docstring)."""
    if not ENDPOINT or not KEY:
        print(
            "FAIL: set ACCOUNT_HOST + ACCOUNT_KEY to your Cosmos account "
            "before running this script.",
            file=sys.stderr,
        )
        return 1

    try:
        from azure.cosmos import _rust  # pylint: disable=import-outside-toplevel
    except ImportError as e:
        print(f"FAIL: _rust not built: {e}", file=sys.stderr)
        print("Run `maturin develop` from the repo root.", file=sys.stderr)
        return 2

    if not hasattr(_rust, "upsert_item"):
        print("FAIL: _rust module does not export `upsert_item`.", file=sys.stderr)
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

    item_id = f"smoke-upsert-{uuid.uuid4()}"
    print(f"Item id  : {item_id}")
    backend = RustBackend(endpoint=ENDPOINT, master_key=KEY)

    # ---- 1) insert: brand-new id -> 201 Created ------------------------
    print("\n[1] upsert new id (expect 201 insert) ...", flush=True)
    try:
        r1 = _upsert(backend, item_id, 1)
    except Exception as e:  # pylint: disable=broad-except
        print(f"FAIL on insert: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if r1 is None:
        print("FAIL: insert returned None.", file=sys.stderr)
        return 1
    print(f"    status={r1.status_code}")
    if r1.status_code != 201:
        print(f"    body={r1.body[:300]!r}", file=sys.stderr)
        print("Expected 201 on the first upsert (insert).", file=sys.stderr)
        return 1
    etag_v1 = r1.headers["etag"]  # captured for the stale-precondition check below

    # ---- 2) replace: same id, new body -> 200 OK -----------------------
    print("[2] upsert same id, new body (expect 200 replace) ...", flush=True)
    try:
        r2 = _upsert(backend, item_id, 2)
    except Exception as e:  # pylint: disable=broad-except
        print(f"FAIL on replace: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if r2 is None:
        print("FAIL: replace returned None.", file=sys.stderr)
        return 1
    print(f"    status={r2.status_code}")
    if r2.status_code != 200:
        print(f"    body={r2.body[:300]!r}", file=sys.stderr)
        print("Expected 200 on the second upsert (replace).", file=sys.stderr)
        return 1

    # ---- 3) version-guarded replace with a STALE etag -> 412 -----------
    # Step 2 replaced the document, so the etag captured at insert time is
    # now stale. A guarded replace (If-Match: <stale-etag>, built by the
    # Python helper from match_condition=IfNotModified) must fail with 412.
    # This is the upsert precondition Cosmos actually honours, and it
    # proves the access-condition header reaches the wire through the
    # binding's custom_headers. (Insert-only via If-None-Match: * is NOT
    # tested as a 412: Cosmos upsert lets the is-upsert flag win and
    # replaces, returning 200 on both the legacy and the rust path -- so
    # it is parity, not a precondition.)
    print("[3] guarded replace with stale If-Match (expect 412) ...", flush=True)
    try:
        r3 = _upsert(backend, item_id, 3, headers={"If-Match": etag_v1})
    except Exception as e:  # pylint: disable=broad-except
        print(f"FAIL on guarded replace: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if r3 is None:
        print("FAIL: guarded replace returned None.", file=sys.stderr)
        return 1
    print(f"    status={r3.status_code} sub_status={r3.sub_status}")
    if r3.status_code != 412:
        print(f"    body={r3.body[:300]!r}", file=sys.stderr)
        print("Expected 412 on a guarded replace with a stale If-Match etag.", file=sys.stderr)
        return 1

    print(
        "\nOK -- Rust upsert round trip succeeded: "
        "insert(201) + replace(200) + guarded-replace-stale-etag(412), all as expected."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

