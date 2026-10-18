# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Separate, test-owned replacement targets for the two comparison backends."""

from contextlib import contextmanager
import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, ThroughputProperties, exceptions
from common._parity_helpers import _observed_backend_name
from common.parity_provisioning import create_owned_database


@contextmanager
def _container_pair(throughput):
    database_id = "parity_throughput_" + uuid.uuid4().hex
    with CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust"
    ) as client:
        try:
            database = create_owned_database(client, id=database_id)
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
        finally:
            try:
                client.delete_database(database_id)
            except exceptions.CosmosResourceNotFoundError:
                pass


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
