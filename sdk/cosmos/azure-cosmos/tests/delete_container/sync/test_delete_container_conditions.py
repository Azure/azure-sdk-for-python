# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Conditional ``delete_container`` on Rust keeps the service's precondition behavior."""

import os
import uuid
from unittest.mock import patch

import pytest
from azure.core import MatchConditions

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.partition_key import PartitionKey
from common._rust_checks import run_on_rust

pytestmark = [pytest.mark.cosmosEmulator]


def _rust_client():
    return CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust"
    )


@pytest.fixture(scope="module")
def owned_database():
    name = "rust_delete_container_cond_" + uuid.uuid4().hex
    with _rust_client() as admin:
        try:
            yield admin.create_database(name)
        finally:
            try:
                admin.delete_database(name)
            except exceptions.CosmosResourceNotFoundError:
                pass


def _delete(database_id, name, **options):
    with _rust_client() as client:
        database = client.get_database_client(database_id)
        with patch.object(
            client.client_connection,
            "DeleteContainer",
            create=True,
            side_effect=AssertionError("Rust deletion used legacy Python"),
        ):
            return run_on_rust(
                client, lambda: database.delete_container(name, timeout=30, **options)
            )


@pytest.mark.cosmosLong
def test_delete_container_with_stale_etag_raises_precondition_failed_rust(
    owned_database,
):
    # Source: (new) Rejected conditional deletion preserves the container.
    """A delete with a stale If-Match etag fails with 412 and leaves the container in place."""
    name = "conditional_" + uuid.uuid4().hex
    owned_database.create_container(name, PartitionKey(path="/id"))

    with pytest.raises(exceptions.CosmosHttpResponseError) as raised:
        _delete(
            owned_database.id,
            name,
            etag='"deliberately-stale"',
            match_condition=MatchConditions.IfNotModified,
        )

    assert raised.value.status_code == 412
    assert owned_database.get_container_client(name).read()["id"] == name


@pytest.mark.cosmosLong
@pytest.mark.skip(
    reason="driver-gap: rejected container deletion corrupts later item-read session state; "
    "https://github.com/Azure/azure-sdk-for-rust/issues/5669"
)
def test_item_read_after_rejected_container_delete_preserves_session_rust(
    owned_database,
):
    """A rejected container deletion must not break later reads of an existing item."""
    # Source: (new) Regression for Azure/azure-sdk-for-rust#5669.
    with CosmosClient(
        os.environ["ACCOUNT_HOST"],
        os.environ["ACCOUNT_KEY"],
        consistency_level="Session",
        _backend="rust",
    ) as client:
        database = client.get_database_client(owned_database.id)
        container = database.create_container(
            "session_" + uuid.uuid4().hex, PartitionKey(path="/id")
        )
        item = container.create_item({"id": "order-42", "total": 149.50})
        assert container.read_item(item["id"], partition_key=item["id"]) == item

        with patch.object(
            client.client_connection,
            "DeleteContainer",
            create=True,
            side_effect=AssertionError("Rust deletion used legacy Python"),
        ):
            with pytest.raises(exceptions.CosmosHttpResponseError) as raised:
                run_on_rust(
                    client,
                    lambda: database.delete_container(
                        container.id,
                        etag='"deliberately-stale"',
                        match_condition=MatchConditions.IfNotModified,
                        timeout=30,
                    ),
                )

        assert raised.value.status_code == 412
        assert (
            container.read_item(item["id"], partition_key=item["id"], timeout=45)
            == item
        )


@pytest.mark.cosmosLong
def test_delete_container_with_if_missing_deletes_container_rust(owned_database):
    # Source: (new) IfMissing deletion succeeds and subsequent reads return 404.
    """A delete with IfMissing succeeds (204) and removes the container."""
    name = "conditional_" + uuid.uuid4().hex
    owned_database.create_container(name, PartitionKey(path="/id"))

    assert (
        _delete(owned_database.id, name, match_condition=MatchConditions.IfMissing)
        is None
    )

    with pytest.raises(exceptions.CosmosResourceNotFoundError):
        owned_database.get_container_client(name).read()


def test_delete_container_with_nonmatching_etag_if_modified_deletes_container_rust(
    owned_database,
):
    """Preserve main's IfModified deletion and subsequent container-read 404."""
    # Source: tests/test_backwards_compatibility.py::TestBackwardsCompatibility.test_etag_match_condition_compatibility
    # Deletion assertions verified against main 589ec311.
    container = owned_database.create_container(
        "conditional_" + uuid.uuid4().hex, PartitionKey(path="/pk")
    )

    assert (
        _delete(
            owned_database.id,
            container.id,
            etag=str(uuid.uuid4()),
            match_condition=MatchConditions.IfModified,
        )
        is None
    )

    try:
        container.read()
        pytest.fail("Container read should have failed")
    except exceptions.CosmosHttpResponseError as error:
        assert error.status_code == 404
