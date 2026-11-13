# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original exclusion matrix, asserting regions from real Rust attempt diagnostics."""

from dataclasses import replace
import time
import uuid

import pytest

from azure.cosmos import PartitionKey, _telemetry
from config.clients import (
    create_data_client,
    create_data_client_async,
    create_setup_client,
)
from config.settings import TestSettings
from query_items.sync.test_excluded_locations import read_item_test_data


@pytest.fixture(scope="module")
def regional_container():
    if not TestSettings.WRITE_LOCATION or not TestSettings.READ_LOCATION:
        pytest.skip(
            "environment-gap: WRITE_LOCATION and READ_LOCATION must identify the account's regions"
        )
    assert TestSettings.WRITE_LOCATION != TestSettings.READ_LOCATION
    with create_setup_client(_backend="rust") as client:
        database = client.create_database("read-all-regions-" + uuid.uuid4().hex)
        try:
            container = database.create_container(
                "items",
                partition_key=PartitionKey(path=["/pk1", "/pk2"], kind="MultiHash"),
                offer_throughput=TestSettings.THROUGHPUT_FOR_5_PARTITIONS,
            )
            container.upsert_item({"id": "doc1", "pk1": "value1", "pk2": "value2"})
            time.sleep(3)
            yield database.id, container.id
        finally:
            client.delete_database(database.id)


def assert_serving_regions(completions, expected):
    for completion in completions:
        if completion.diagnostics is not None:
            assert completion.diagnostics.request_count == len(
                completion.diagnostics.attempts
            ), "Truncated attempt diagnostics cannot verify every request's region"
    attempts = [
        attempt
        for completion in completions
        if completion.diagnostics is not None
        for attempt in completion.diagnostics.attempts
    ]
    assert attempts, "Rust feed execution must report request attempts"
    expected_regions = {region.replace(" ", "").lower() for region in expected}
    for attempt in attempts:
        assert (
            attempt.region
        ), "A request without its serving region cannot verify exclusions"
        assert attempt.region.replace(" ", "").lower() in expected_regions


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosMultiRegion
@pytest.mark.cosmosAADCircuitBreaker
@pytest.mark.asyncio
@pytest.mark.parametrize("test_data", read_item_test_data())
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_read_all_items_excluded_locations_rust(
    regional_container, test_data, asynchronous
):
    # Source: tests/test_excluded_locations.py::TestExcludedLocations.test_read_all_items
    # Source: tests/test_excluded_locations_async.py::TestExcludedLocationsAsync.test_read_all_items_async
    preferred, client_excluded, request_excluded, expected = test_data
    completions = []

    def prepare(client):
        container = client.get_database_client(
            regional_container[0]
        ).get_container_client(regional_container[1])
        container._item_context = replace(
            container._item_context,
            telemetry_handlers=(
                _telemetry.CompletionHandler(completions.append, collect_attempts=True),
            ),
        )
        return container

    options = dict(
        _backend="rust",
        preferred_locations=preferred,
        excluded_locations=client_excluded,
    )
    request_options = (
        {} if request_excluded is None else {"excluded_locations": request_excluded}
    )
    if asynchronous:
        async with create_data_client_async(**options) as client:
            container = prepare(client)
            items = [item async for item in container.read_all_items(**request_options)]
    else:
        with create_data_client(**options) as client:
            container = prepare(client)
            items = list(container.read_all_items(**request_options))
    assert {item["id"] for item in items} == {"doc1"}
    assert_serving_regions(completions, expected)
