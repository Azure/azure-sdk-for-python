"""End-to-end smoke test for the Rust binding's ``patch_item``.

Exercises the full Rust path (Python -> PyO3 -> driver -> HTTPS ->
Cosmos -> back) by creating one item, patching it, then confirming the
missing-id path returns 404. Not a pytest test: it needs a real account
or the local emulator and prints visible output for quick manual checks.

Set ``ACCOUNT_HOST`` + ``ACCOUNT_KEY`` to your Cosmos account.
* ``COSMOS_DB`` (default ``parity_db``) and ``COSMOS_COLL`` (default
  ``smoke_patch``). Both are created with the legacy backend if missing.

Prerequisites: ``maturin develop`` has been run so ``_rust.{pyd,so}``
exists; one of the env-var pairs above is set.

Exit codes:

* 0 -- create + patch-existing + patch-missing all returned expected status.
* 1 -- a request executed but the service returned unexpected status, the
       backend returned None, or env vars are missing.
* 2 -- the compiled ``_rust`` module is missing (run ``maturin develop``).
"""
from __future__ import annotations

import json
import os
import sys
import uuid

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos._backend.base import OP_CREATE_ITEM, OP_PATCH_ITEM, PreparedRequest
from azure.cosmos._backend.rust import RustBackend

ENDPOINT = os.environ.get("ACCOUNT_HOST")
KEY = os.environ.get("ACCOUNT_KEY")
DB = os.environ.get("COSMOS_DB", "parity_db")
COLL = os.environ.get("COSMOS_COLL", "smoke_patch")


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

    # Sanity: confirm the binding actually registers ``patch_item``.
    if not hasattr(_rust, "patch_item"):
        print("FAIL: _rust module does not export `patch_item`.", file=sys.stderr)
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

    item_id = f"smoke-patch-{uuid.uuid4()}"
    container_link = f"dbs/{DB}/colls/{COLL}"
    pk_header = '["smokeA"]'

    backend = RustBackend(endpoint=ENDPOINT, master_key=KEY)

    # ---- create a row to patch -----------------------------------------
    create_prepared = PreparedRequest(
        op=OP_CREATE_ITEM,
        container_link=container_link,
        body_bytes=f'{{"id":"{item_id}","pk":"smokeA","n":1}}'.encode(),
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
    if create_resp.status_code != 201:
        print(f"create body = {create_resp.body[:300]!r}", file=sys.stderr)
        print("Expected 201 on create. Cannot proceed with patch.", file=sys.stderr)
        return 1

    # ---- patch the row we just created ---------------------------------
    patch_body = json.dumps({"operations": [{"op": "set", "path": "/n", "value": 99}]}).encode()
    patch_prepared = PreparedRequest(
        op=OP_PATCH_ITEM,
        container_link=container_link,
        body_bytes=patch_body,
        partition_key_header=pk_header,
        headers={},
        item_id=item_id,
    )

    print("Calling RustBackend.execute(patch existing id) ...", flush=True)
    try:
        patch_resp = backend.execute(patch_prepared)
    except Exception as e:  # pylint: disable=broad-except
        print(f"FAIL on patch(existing): {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if patch_resp is None:
        print("FAIL: patch(existing) returned None.", file=sys.stderr)
        return 1
    print(f"patch(existing) status_code = {patch_resp.status_code}")
    print(f"patch(existing) sub_status  = {patch_resp.sub_status}")
    if patch_resp.status_code != 200:
        print(f"patch(existing) body = {patch_resp.body[:300]!r}", file=sys.stderr)
        print("Expected 200 on patch(existing).", file=sys.stderr)
        return 1

    # When the body is present (default no_response=False), assert the patched field.
    if patch_resp.body:
        try:
            patched = json.loads(patch_resp.body)
            if patched.get("n") != 99:
                print(f"FAIL: patch body did not apply /n=99: {patch_resp.body[:300]!r}", file=sys.stderr)
                return 1
        except Exception as e:  # pylint: disable=broad-except
            print(f"FAIL: patch(existing) body was not valid JSON: {e}", file=sys.stderr)
            return 1

    # ---- patch a missing id -> 404 -------------------------------------
    missing_id = f"smoke-patch-missing-{uuid.uuid4()}"
    patch_missing_prepared = PreparedRequest(
        op=OP_PATCH_ITEM,
        container_link=container_link,
        body_bytes=patch_body,
        partition_key_header=pk_header,
        headers={},
        item_id=missing_id,
    )

    print("Calling RustBackend.execute(patch missing id) ...", flush=True)
    try:
        missing_resp = backend.execute(patch_missing_prepared)
    except Exception as e:  # pylint: disable=broad-except
        print(f"FAIL on patch(missing): {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if missing_resp is None:
        print("FAIL: patch(missing) returned None.", file=sys.stderr)
        return 1
    print(f"patch(missing) status_code = {missing_resp.status_code}")
    print(f"patch(missing) sub_status  = {missing_resp.sub_status}")
    if missing_resp.status_code != 404:
        print(f"patch(missing) body = {missing_resp.body[:300]!r}", file=sys.stderr)
        print("Expected 404 on patch(missing).", file=sys.stderr)
        return 1

    print(
        "\nOK -- Rust patch round trip succeeded: "
        "create(201) + patch(existing=200) + patch(missing=404), all as expected."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
