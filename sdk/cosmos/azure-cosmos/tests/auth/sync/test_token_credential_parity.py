# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Token-credential (AAD) parity tests -- sync.

Builds both backends with a synchronous token credential and diffs the result,
so signing in with a token is checked for parity, not just the account key. The
two handle tests compare returned driver-handle strings for reused and distinct
credential objects at the same endpoint with default configuration. They do not
measure native driver construction or prove driver identity across lifetimes.

Runs when the account, binding, and token-lane gates pass. Uses an emulator-format
token or, when all COSMOS_AAD_* values are set, a real Entra credential.
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos._backend.binding import RustBinding

from common._parity_helpers import run_on_both_backends, skip_unless_emulator, skip_unless_rust_binding
from auth._token_credentials import make_sync_token_credential, skip_unless_token_auth

# cosmosEmulator: collected by the existing emulator CI lane (skips cleanly if the
# rust binding or token auth is absent). cosmosRustAAD: lets a dedicated job select
# just this lane with `-m cosmosRustAAD`.
pytestmark = [pytest.mark.cosmosEmulator, pytest.mark.cosmosRustAAD,
              skip_unless_emulator(), skip_unless_rust_binding(), skip_unless_token_auth()]


@pytest.fixture
def container_for(request):
    """Create a unique container for one token-authentication test."""
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    cname = "auth_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(id=cname, partition_key=PartitionKey(path="/pk"))
    yield container
    try:
        db.delete_container(cname)
    except Exception:  # pylint: disable=broad-except
        pass


def _factory_for(cred):
    # Reuse one credential object across both backends so the comparison
    # differs only by backend, not by credential shape.
    def factory(backend_name: str):
        return CosmosClient(os.environ["ACCOUNT_HOST"], cred, _backend=backend_name)  # type: ignore[arg-type]
    return factory


def test_create_item_parity_with_token_credential(container_for):
    """create_item must match across backends when authed by a token credential."""
    body = {"id": uuid.uuid4().hex, "pk": "a", "n": 1}
    cmp = run_on_both_backends(
        lambda c: c.get_database_client("parity_db")
                   .get_container_client(container_for.id).create_item(body=dict(body)),
        client_factory=_factory_for(make_sync_token_credential()),
        description="[AAD] create_item via sync token credential",
        request_body=body,
    )
    cmp.print_report()
    cmp.assert_functional_parity()


def test_read_item_parity_with_token_credential(container_for):
    """Read the account-key fixture's item using token credentials on both backends."""
    item_id = uuid.uuid4().hex
    container_for.create_item(body={"id": item_id, "pk": "a"})
    cmp = run_on_both_backends(
        lambda c: c.get_database_client("parity_db")
                   .get_container_client(container_for.id).read_item(item_id, partition_key="a"),
        client_factory=_factory_for(make_sync_token_credential()),
        description="[AAD] read_item via sync token credential",
    )
    cmp.print_report()
    cmp.assert_functional_parity()


def test_engine_shared_for_one_credential_object():
    """The same credential object and endpoint produce equal driver-handle strings."""
    cred = make_sync_token_credential()
    h1 = RustBinding(endpoint=os.environ["ACCOUNT_HOST"], token_credential=cred)._ensure_driver_handle()
    h2 = RustBinding(endpoint=os.environ["ACCOUNT_HOST"], token_credential=cred)._ensure_driver_handle()
    assert h1 == h2, "same credential object must reuse one engine handle"


def test_engine_multiplied_for_distinct_credential_objects():
    """The two distinct credential objects produce different driver-handle strings."""
    h1 = RustBinding(endpoint=os.environ["ACCOUNT_HOST"],
                     token_credential=make_sync_token_credential())._ensure_driver_handle()
    h2 = RustBinding(endpoint=os.environ["ACCOUNT_HOST"],
                     token_credential=make_sync_token_credential())._ensure_driver_handle()
    assert h1 != h2, "distinct credential objects must build distinct engine handles"


