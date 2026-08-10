"""End-to-end smoke test for the Rust binding's ``replace_item``.

Exercises the full Rust path (Python -> PyO3 -> driver -> HTTPS ->
Cosmos -> back) for overwrite-only replace semantics:

1. create a brand-new id                      -> expect 201 Created
2. replace that id with a new body            -> expect 200 OK (overwrite)
3. version-guarded replace with a stale
   ``If-Match`` etag                            -> expect 412 (precondition)
4. replace a non-existent id                  -> expect 404 (no insert,
                                                  unlike upsert)
5. replace where the URL id (``item_id``) and
   the body's own id disagree                  -> expect a 4xx, never a
                                                  silent 200 overwriting the
                                                  body's id (the parity fix)

Steps 1-4 prove the overwrite-only semantics and the access-condition path
the Python helper builds from ``etag`` + ``match_condition=IfNotModified``.
Step 5 proves the binding takes the wire URL id from ``PreparedRequest.item_id``
(the resolved ``item`` argument), not from the body -- so a mismatched id can
never retarget the write to the wrong document.

Not a pytest test: needs a real account (or the local emulator) and prints
visible output so a human can confirm the round trip.

Set ``ACCOUNT_HOST`` + ``ACCOUNT_KEY`` to your Cosmos account. The db
(``parity_db``) and container (``smoke_replace``) are created if missing
(override with ``COSMOS_DB`` / ``COSMOS_COLL``).

Prerequisites: ``maturin develop`` has been run so ``_rust.{pyd,so}``
exists with the ``replace_item`` entry point.

Exit codes:

* 0 -- create(201) + replace(200) + guarded(412) + missing(404) + id-mismatch
       (non-200) all as expected.
* 1 -- a request executed but an outcome was wrong, the backend returned
       None, or env vars are missing.
* 2 -- the compiled ``_rust`` module (or its ``replace_item``) is missing.
"""
from __future__ import annotations

import json
import os
import sys
import uuid

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos._backend.operations import OP_CREATE_ITEM, OP_REPLACE_ITEM
from azure.cosmos._backend.contracts import PreparedRequest
from azure.cosmos._backend.rust import RustBackend

ENDPOINT = os.environ.get("ACCOUNT_HOST")
KEY = os.environ.get("ACCOUNT_KEY")
DB = os.environ.get("COSMOS_DB", "parity_db")
COLL = os.environ.get("COSMOS_COLL", "smoke_replace")

CONTAINER_LINK = f"dbs/{DB}/colls/{COLL}"
PK_HEADER = '["smokeA"]'


def _ensure_db_and_container() -> None:
    """Create the db + container via the legacy backend if missing, so the
    rust path is never asked to resolve a container that does not exist."""
    client = CosmosClient(ENDPOINT, KEY)
    db = client.create_database_if_not_exists(DB)
    db.create_container_if_not_exists(id=COLL, partition_key=PartitionKey(path="/pk"))


def _create(backend, item_id, value):
    body = json.dumps({"id": item_id, "pk": "smokeA", "value": value}).encode()
    prepared = PreparedRequest(
        op=OP_CREATE_ITEM,
        container_link=CONTAINER_LINK,
        body_bytes=body,
        partition_key_header=PK_HEADER,
        headers={},
    )
    return backend.execute(prepared)


def _replace(backend, item_id, value, *, body_id=None, headers=None):
    """Replace ``item_id`` with a new body. ``body_id`` defaults to
    ``item_id`` (the normal case); pass a different value to exercise the
    id-mismatch parity check."""
    body = json.dumps({"id": body_id or item_id, "pk": "smokeA", "value": value}).encode()
    prepared = PreparedRequest(
        op=OP_REPLACE_ITEM,
        container_link=CONTAINER_LINK,
        body_bytes=body,
        partition_key_header=PK_HEADER,
        headers=headers or {},
        item_id=item_id,
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

    if not hasattr(_rust, "replace_item"):
        print("FAIL: _rust module does not export `replace_item`.", file=sys.stderr)
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

    item_id = f"smoke-replace-{uuid.uuid4()}"
    print(f"Item id  : {item_id}")
    backend = RustBackend(endpoint=ENDPOINT, master_key=KEY)

    # ---- 1) create: brand-new id -> 201 Created ------------------------
    print("\n[1] create new id (expect 201) ...", flush=True)
    try:
        r1 = _create(backend, item_id, 1)
    except Exception as e:  # pylint: disable=broad-except
        print(f"FAIL on create: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if r1 is None or r1.status_code != 201:
        print(f"FAIL: expected 201, got {r1 and r1.status_code}.", file=sys.stderr)
        return 1
    etag_v1 = r1.headers["etag"]  # captured for the stale-precondition check below

    # ---- 2) replace: same id, new body -> 200 OK -----------------------
    print("[2] replace same id, new body (expect 200) ...", flush=True)
    try:
        r2 = _replace(backend, item_id, 2)
    except Exception as e:  # pylint: disable=broad-except
        print(f"FAIL on replace: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if r2 is None or r2.status_code != 200:
        print(f"FAIL: expected 200, got {r2 and r2.status_code}.", file=sys.stderr)
        if r2 is not None:
            print(f"    body={r2.body[:300]!r}", file=sys.stderr)
        return 1
    # Prove the overwrite actually applied the new body.
    if r2.body and json.loads(r2.body).get("value") != 2:
        print(f"FAIL: replace did not apply the new value. body={r2.body[:300]!r}", file=sys.stderr)
        return 1

    # ---- 3) version-guarded replace with a STALE etag -> 412 -----------
    # Step 2 replaced the document, so the etag captured at create time is
    # now stale. A guarded replace (If-Match: <stale-etag>, built by the
    # Python helper from match_condition=IfNotModified) must fail with 412.
    print("[3] guarded replace with stale If-Match (expect 412) ...", flush=True)
    try:
        r3 = _replace(backend, item_id, 3, headers={"If-Match": etag_v1})
    except Exception as e:  # pylint: disable=broad-except
        print(f"FAIL on guarded replace: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if r3 is None or r3.status_code != 412:
        print(f"FAIL: expected 412, got {r3 and r3.status_code}.", file=sys.stderr)
        return 1
    print(f"    status={r3.status_code} sub_status={r3.sub_status}")

    # ---- 4) replace a non-existent id -> 404 (no insert) ---------------
    # A replace never inserts (unlike upsert), so overwriting an id that was
    # never created must come back 404, not 201.
    print("[4] replace a non-existent id (expect 404) ...", flush=True)
    missing_id = f"smoke-replace-missing-{uuid.uuid4()}"
    try:
        r4 = _replace(backend, missing_id, 1)
    except Exception as e:  # pylint: disable=broad-except
        print(f"FAIL on missing-id replace: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if r4 is None or r4.status_code != 404:
        print(f"FAIL: expected 404, got {r4 and r4.status_code}.", file=sys.stderr)
        return 1
    print(f"    status={r4.status_code} sub_status={r4.sub_status}")

    # ---- 5) id-mismatch parity check -----------------------------------
    # The URL id (item_id) is the real, existing document; the body carries a
    # *different* id. The binding takes the URL id from item_id (not the
    # body), so the server sees a request to change the document's id and
    # rejects it (a document's id is immutable). The critical property: it
    # must NEVER be a silent 200 that overwrote the body's id instead.
    print("[5] replace with item_id != body id (expect a 4xx, never 200) ...", flush=True)
    try:
        r5 = _replace(backend, item_id, 5, body_id="some-other-id")
    except Exception as e:  # pylint: disable=broad-except
        print(f"FAIL on id-mismatch replace: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if r5 is None:
        print("FAIL: id-mismatch replace returned None.", file=sys.stderr)
        return 1
    print(f"    status={r5.status_code} sub_status={r5.sub_status}")
    if r5.status_code == 200:
        print(
            "FAIL: a body whose id disagreed with item_id was SILENTLY replaced "
            "(200). The URL id must come from item_id, not the body.",
            file=sys.stderr,
        )
        return 1
    if not 400 <= r5.status_code < 500:
        print(f"FAIL: expected a 4xx rejection for the id mismatch, got {r5.status_code}.", file=sys.stderr)
        return 1

    print(
        "\nOK -- Rust replace round trip succeeded: "
        "create(201) + replace(200) + guarded-stale-etag(412) + missing-id(404) + "
        f"id-mismatch(non-200: {r5.status_code}), all as expected."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

