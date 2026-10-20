# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Own throughput fixtures; share read targets and isolate replacement targets."""

from contextlib import asynccontextmanager, contextmanager
import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, ThroughputProperties, exceptions
from common._parity_helpers import _observed_backend_name
from common.parity_provisioning import create_owned_database


@contextmanager
def owned_database(client, database_id, **kwargs):
    """Clean up a unique ID even when creation loses its response, but not on conflict."""
    owned = True
    try:
        try:
            database = create_owned_database(client, id=database_id, **kwargs)
        except exceptions.CosmosResourceExistsError:
            owned = False
            raise
        yield database
    finally:
        if owned:
            try:
                client.delete_database(database_id)
            except exceptions.CosmosResourceNotFoundError:
                pass


@asynccontextmanager
async def owned_database_async(client, database_id, **kwargs):
    """Async ownership also covers setup failure and cancellation."""
    owned = True
    try:
        try:
            database = await client.create_database(id=database_id, **kwargs)
        except exceptions.CosmosResourceExistsError:
            owned = False
            raise
        yield database
    finally:
        if owned:
            try:
                await client.delete_database(database_id)
            except exceptions.CosmosResourceNotFoundError:
                pass


@pytest.fixture
def shared_container_for():
    """Compare reads on one dedicated-throughput container in a test-owned database."""
    with CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust"
    ) as client:
        database_id = "parity_get_throughput_" + uuid.uuid4().hex
        with owned_database(client, database_id) as database:
            container = database.create_container(
                id="orders", partition_key=PartitionKey(path="/pk"), offer_throughput=400,
            )
            yield database_id, container.id


@contextmanager
def _container_pair(throughput):
    database_id = "parity_throughput_" + uuid.uuid4().hex
    with CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust"
    ) as client:
        with owned_database(client, database_id) as database:
            containers = {}
            for backend in ("core-python", "rust"):
                container_id = backend.replace("-", "")
                database.create_container(
                    id=container_id,
                    partition_key=PartitionKey(path="/pk"),
                    offer_throughput=throughput,
                )
                containers[backend] = container_id
            yield database_id, containers


@pytest.fixture
def container_for():
    with _container_pair(400) as resources:
        yield resources


@pytest.fixture
def autoscale_container_for():
    with _container_pair(
        ThroughputProperties(auto_scale_max_throughput=5000)
    ) as resources:
        yield resources


def container_for_backend(client, resources):
    database_id, containers = resources
    return client.get_database_client(database_id).get_container_client(
        containers[_observed_backend_name(client)]
    )
