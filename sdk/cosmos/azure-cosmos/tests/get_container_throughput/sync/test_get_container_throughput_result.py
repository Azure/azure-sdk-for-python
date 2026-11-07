# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Rust behavior test
"""Container ``get_throughput`` on Rust returns the exact offer and keeps caller state private."""

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
        with owned_database(client, "rust_get_container_throughput_" + uuid.uuid4().hex) as db:
            db.create_container("manual", partition_key=PartitionKey(path="/pk"), offer_throughput=400)
            db.create_container(
                "autoscale", partition_key=PartitionKey(path="/pk"),
                offer_throughput=ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=0),
            )
            yield db.id


@pytest.mark.parametrize("kind", ["manual", "autoscale"])
@pytest.mark.parametrize("warm", [False, True], ids=["cold", "warm"])
def test_get_container_throughput_returns_offer_fields_and_isolates_hook_rust(database_id, kind, warm):
    """Manual 400 or autoscale 5000 (0 increment) comes back exactly, charges RU, and the hook cannot alter it.

    The request options are not mutated, and the hook receives the result's own headers.
    """
    options = {"initialHeaders": {"x-ms-client-request-id": "container-throughput-rust"}}
    original = deepcopy(options)
    callbacks = []

    def hook(headers, offers):
        callbacks.append(dict(headers))
        headers.clear()
        offers[0]["content"]["offerThroughput"] = 999
        offers.clear()

    with _rust_client() as client:
        container = client.get_database_client(database_id).get_container_client(kind)
        if warm:
            container.read()
        result = run_on_rust(client, lambda: container.get_throughput(request_options=options, response_hook=hook))

    assert options == original
    assert callbacks == [dict(result.get_response_headers())]
    assert float(result.get_response_headers()["x-ms-request-charge"]) > 0
    assert result.properties["content"]
    if kind == "manual":
        assert result.offer_throughput == 400
        assert result.auto_scale_max_throughput is None
    else:
        assert result.offer_throughput is None
        assert result.auto_scale_max_throughput == 5000
        assert result.auto_scale_increment_percent == 0
