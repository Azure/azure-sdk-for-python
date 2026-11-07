# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Rust behavior test
"""Conditional ``replace_container`` on Rust honors etags with cold and warm container metadata."""

import os
import uuid
from contextlib import ExitStack
from unittest.mock import MagicMock, patch

import pytest
from azure.core import MatchConditions

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.partition_key import PartitionKey
from common._rust_checks import run_on_rust

PK = PartitionKey(path="/pk")


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


@pytest.fixture(scope="module")
def owned_database():
    name = "rust_replace_container_cond_" + uuid.uuid4().hex
    with _rust_client() as admin:
        try:
            yield admin.create_database(name)
        finally:
            try:
                admin.delete_database(name)
            except exceptions.CosmosResourceNotFoundError:
                pass


def _replace(client, database, target, **kwargs):
    with ExitStack() as guards:
        for method in ("ReplaceContainer", "ReadContainer"):
            guards.enter_context(patch.object(
                client.client_connection, method,
                side_effect=AssertionError("Rust replacement entered legacy " + method),
            ))
        return run_on_rust(client, lambda: database.replace_container(target, PK, **kwargs))


@pytest.mark.parametrize("warm", [False, True], ids=["cold", "warm"])
def test_replace_container_honors_if_not_modified_rust(owned_database, warm):
    """A stale etag with IfNotModified fails with 412, skips the hook and leaves the container unchanged.

    Replacing with the current etag then succeeds and calls the hook once.
    """
    name = "conditional_" + uuid.uuid4().hex
    original = owned_database.create_container(name, PK, default_ttl=60)
    hook = MagicMock()
    with _rust_client() as client:
        database = client.get_database_client(owned_database.id)
        if warm:
            assert database.get_container_client(name).create_item({"id": "warm", "pk": "p"})["id"] == "warm"
        with pytest.raises(exceptions.CosmosHttpResponseError) as raised:
            _replace(
                client, database, name, default_ttl=3600, etag='"stale"',
                match_condition=MatchConditions.IfNotModified, response_hook=hook, timeout=30,
            )
        assert raised.value.status_code == 412
        hook.assert_not_called()
        current = original.read()
        assert current["defaultTtl"] == 60

        _, properties = _replace(
            client, database, name, default_ttl=3600, etag=current["_etag"],
            match_condition=MatchConditions.IfNotModified, return_properties=True, response_hook=hook, timeout=30,
        )
        assert properties["defaultTtl"] == 3600
        hook.assert_called_once()
    assert original.read()["defaultTtl"] == 3600
