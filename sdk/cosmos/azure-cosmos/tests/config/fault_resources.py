# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Rust-only live resources shared by driver and network fault tests."""

import os
import uuid

import pytest

from azure.cosmos import PartitionKey, exceptions
from config import clients, resources
from config.diagnostics import emit


def load_account(endpoint, key):
    """Require the real account document; propagate the missing Rust API error."""
    with clients.create_fault_setup_client(endpoint, key) as client:
        client.get_database_account()
    # The public DatabaseAccount model does not retain the complete response.
    raise NotImplementedError(
        "Fault-test topology requires the complete account document through the Rust binding. "
        "Implement raw account retrieval here when that capability is exposed; the public "
        "DatabaseAccount model alone is insufficient."
    )


@pytest.fixture
def owned_target(request):
    endpoint, key = os.environ.get("ACCOUNT_HOST"), os.environ.get("ACCOUNT_KEY")
    if not endpoint or not key:
        pytest.fail("Set ACCOUNT_HOST and ACCOUNT_KEY to an isolated test account")
    database_id = "fault_create_" + uuid.uuid4().hex
    container_id = "orders_" + uuid.uuid4().hex
    with clients.create_fault_setup_client(endpoint, key) as client:
        with pytest.raises(exceptions.CosmosResourceNotFoundError) as absent:
            client.get_database_client(database_id).read()
        assert absent.value.status_code == 404
        emit("owned_database", database_id=database_id, nodeid=request.node.nodeid)
        database = None
        cleanup_allowed = True
        try:
            try:
                database = resources.create_owned_database(client, id=database_id)
            except exceptions.CosmosResourceExistsError:
                cleanup_allowed = False
                emit("ownership_conflict", database_id=database_id)
                raise
            container = resources.create_owned_container(database, id=container_id, partition_key=PartitionKey("/pk"))
            yield database_id, container
        finally:
            if cleanup_allowed:
                try:
                    resources.retry_control_plane(client.delete_database, database_id)
                except exceptions.CosmosResourceNotFoundError as error:
                    if database is not None or error.status_code != 404:
                        raise
                with pytest.raises(exceptions.CosmosResourceNotFoundError) as absent:
                    client.get_database_client(database_id).read()
                assert absent.value.status_code == 404
                emit("cleanup", database_id=database_id, status=404)
