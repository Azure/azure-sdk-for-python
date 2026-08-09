# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Token-credential (AAD) parity tests -- async.

Signs the rust async client in with an async token credential and diffs its
create/read results against a core-python baseline that uses the account key.
This exercises the async sign-in path, where the client fetches each token on a
background loop.

Uses asyncio.run directly (no pytest-asyncio). Skips unless an account and the
rust binding are present; builds the token from ACCOUNT_KEY unless COSMOS_AAD_*
is set for a real Entra run.
"""
from __future__ import annotations

import asyncio
import os
import uuid

import pytest

from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey

from common._parity_helpers import skip_unless_emulator, skip_unless_rust_binding
from auth._token_credentials import make_async_token_credential, skip_unless_token_auth

# Same gating as the sync lane: cosmosEmulator pulls it into the emulator CI lane,
# cosmosRustAAD lets a dedicated AAD job pick it out; all three skips keep it green
# without the binding/token auth.
pytestmark = [pytest.mark.cosmosEmulator, pytest.mark.cosmosRustAAD,
              skip_unless_emulator(), skip_unless_rust_binding(), skip_unless_token_auth()]

_STRIP = {"_rid", "_self", "_ts", "_etag", "_attachments"}


def _clean(item):
    """Remove service-generated fields before comparing item content."""
    return {k: v for k, v in dict(item).items() if k not in _STRIP}


async def _run(item_id, backend, credential):
    """Create and read an item with the selected backend and credential."""
    async with CosmosClient(os.environ["ACCOUNT_HOST"], credential, _backend=backend) as client:
        db = await client.create_database_if_not_exists("parity_db")
        cname = "auth_aio_" + uuid.uuid4().hex[:8]
        cont = await db.create_container(id=cname, partition_key=PartitionKey(path="/pk"))
        try:
            created = await cont.create_item(body={"id": item_id, "pk": "a", "n": 1})
            read = await cont.read_item(item_id, partition_key="a")
            return _clean(created), _clean(read)
        finally:
            await db.delete_container(cname)


def test_async_token_credential_parity():
    """rust with an async token credential must match the core-python baseline."""
    async def main():
        base_c, base_r = await _run(uuid.uuid4().hex, "core-python", os.environ["ACCOUNT_KEY"])
        rust_c, rust_r = await _run(uuid.uuid4().hex, "rust", make_async_token_credential())
        # ids differ by construction; compare every other field.
        for field in (base_c.keys() | rust_c.keys()) - {"id"}:
            assert base_c.get(field) == rust_c.get(field), "create field {!r} diverged".format(field)
        assert rust_r["pk"] == rust_c["pk"], "read must return the item we just created"
    asyncio.run(main())

