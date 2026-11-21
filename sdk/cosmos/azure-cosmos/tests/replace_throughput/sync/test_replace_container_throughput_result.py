# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Rust behavior test
"""Container ``replace_throughput`` on Rust returns and stores the exact new offer."""

from copy import deepcopy
import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, ThroughputProperties
from common._rust_checks import run_on_rust
from common.throughput_fixtures import owned_database

pytestmark = [pytest.mark.cosmosEmulator]


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


@pytest.fixture(scope="module")
def database_id():
    with _rust_client() as client:
        with owned_database(client, "rust_replace_throughput_" + uuid.uuid4().hex) as database:
            yield database.id


@pytest.mark.parametrize("autoscale", [False, True], ids=["manual", "autoscale"])
@pytest.mark.parametrize("warm", [False, True], ids=["cold", "warm"])
def test_replace_container_throughput_returns_and_persists_fields_rust(database_id, autoscale, warm):
    """Manual 500 or autoscale 6000 (0 increment) is returned and stored exactly.

    request_options is left unchanged, and the hook runs once with the result's headers without its edits leaking.
    """
    container_id = "throughput_" + uuid.uuid4().hex
    with _rust_client() as admin:
        admin.get_database_client(database_id).create_container(
            container_id, partition_key=PartitionKey(path="/pk"),
            offer_throughput=ThroughputProperties(auto_scale_max_throughput=5000) if autoscale else 400,
        )
    options = {"initialHeaders": {"x-ms-client-request-id": "container-replacement-rust"}}
    original = deepcopy(options)
    callbacks = []
    throughput = (
        ThroughputProperties(auto_scale_max_throughput=6000, auto_scale_increment_percent=0)
        if autoscale else ThroughputProperties(offer_throughput=500)
    )
    expected = {
        "offer_throughput": None if autoscale else 500,
        "auto_scale_max_throughput": 6000 if autoscale else None,
        "auto_scale_increment_percent": 0 if autoscale else None,
    }

    def hook(headers, offer):
        callbacks.append(dict(headers))
        headers.clear()
        offer["content"].clear()
        offer.clear()

    try:
        with _rust_client() as client:
            container = client.get_database_client(database_id).get_container_client(container_id)
            if warm:
                container.read(timeout=30)
            result = run_on_rust(client, lambda: container.replace_throughput(
                throughput, request_options=options, response_hook=hook, timeout=30,
            ))

            assert options == original
            assert callbacks == [dict(result.get_response_headers())]
            assert result.properties["content"]
            assert {
                "offer_throughput": result.offer_throughput,
                "auto_scale_max_throughput": result.auto_scale_max_throughput,
                "auto_scale_increment_percent": result.auto_scale_increment_percent,
            } == expected

            persisted = container.get_throughput(timeout=30)
            assert {
                "offer_throughput": persisted.offer_throughput,
                "auto_scale_max_throughput": persisted.auto_scale_max_throughput,
                "auto_scale_increment_percent": persisted.auto_scale_increment_percent,
            } == expected
    finally:
        with _rust_client() as admin:
            admin.get_database_client(database_id).delete_container(container_id)
