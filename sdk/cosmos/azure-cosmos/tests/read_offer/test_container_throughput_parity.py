# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Compare complete throughput results for the same container on both implementations."""

import asyncio
from copy import deepcopy
import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, ThroughputProperties, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from common._parity_helpers import (
    run_on_both_backends, run_on_both_backends_async,
    run_target_operation, run_target_operation_async,
    skip_unless_emulator, skip_unless_rust_binding,
)


pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture(scope="module")
def resources():
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python") as client:
        db = client.create_database("container_read_parity_" + uuid.uuid4().hex, offer_throughput=400)
        try:
            db.create_container("manual", partition_key=PartitionKey(path="/pk"), offer_throughput=400)
            db.create_container(
                "autoscale", partition_key=PartitionKey(path="/pk"),
                offer_throughput=ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=0),
            )
            db.create_container("shared", partition_key=PartitionKey(path="/pk"))
            yield db
        finally:
            client.delete_database(db.id)


def fields(result):
    return {
        "offer_throughput": result.offer_throughput,
        "auto_scale_max_throughput": result.auto_scale_max_throughput,
        "auto_scale_increment_percent": result.auto_scale_increment_percent,
        "properties": result.properties,
    }


def comparison_for(asynchronous, sync_call, async_call, description):
    if asynchronous:
        comparison = asyncio.run(run_on_both_backends_async(async_call, description=description))
    else:
        comparison = run_on_both_backends(sync_call, description=description)
    comparison.print_report()
    comparison.assert_functional_parity()
    return comparison


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("kind", ["manual", "autoscale"])
@pytest.mark.parametrize("warm", [False, True], ids=["cold", "warm"])
def test_same_container_fields_headers_and_ownership(resources, asynchronous, kind, warm):
    def prepare(client):
        container = client.get_database_client(resources.id).get_container_client(kind)
        options = {"initialHeaders": {"x-ms-client-request-id": "container-throughput-parity"}}
        original = deepcopy(options)
        callbacks = []

        def hook(headers, offers):
            callbacks.append(dict(headers))
            headers.clear()
            offers[0]["content"]["offerThroughput"] = 999
            offers.clear()

        def finish(result):
            assert options == original
            assert callbacks == [dict(result.get_response_headers())]
            assert float(result.get_response_headers()["x-ms-request-charge"]) > 0
            if kind == "manual":
                assert result.offer_throughput == 400
            else:
                assert result.offer_throughput is None
                assert result.auto_scale_max_throughput == 5000
                assert result.auto_scale_increment_percent == 0
            return fields(result)

        return container, options, hook, finish

    def sync_call(client):
        container, options, hook, finish = prepare(client)
        if warm:
            container.read()
        result = run_target_operation(client, lambda: container.get_throughput(
            request_options=options, response_hook=hook,
        ))
        return finish(result)

    async def async_call(client):
        container, options, hook, finish = prepare(client)
        if warm:
            await container.read()
        result = await run_target_operation_async(client, lambda: container.get_throughput(
            request_options=options, response_hook=hook,
        ))
        return finish(result)

    comparison_for(asynchronous, sync_call, async_call, f"container {kind}, warm={warm}")


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_shared_database_throughput_is_not_a_container_offer(resources, asynchronous):
    def sync_call(client):
        container = client.get_database_client(resources.id).get_container_client("shared")
        return run_target_operation(client, container.get_throughput)

    async def async_call(client):
        container = client.get_database_client(resources.id).get_container_client("shared")
        return await run_target_operation_async(client, container.get_throughput)

    comparison = comparison_for(asynchronous, sync_call, async_call, "container without dedicated throughput")
    for outcome in (comparison.core_python, comparison.rust):
        assert isinstance(outcome.raised, exceptions.CosmosResourceNotFoundError)
        assert outcome.raised.status_code == 404
        assert outcome.raised.sub_status == 10004


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_recreated_container_uses_new_offer(resources, asynchronous):
    name = "recreated_" + uuid.uuid4().hex
    resources.create_container(name, partition_key=PartitionKey(path="/pk"), offer_throughput=400)
    try:
        if asynchronous:
            async def check():
                async with AsyncCosmosClient(
                    os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python",
                ) as legacy, AsyncCosmosClient(
                    os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust",
                ) as rust:
                    containers = [c.get_database_client(resources.id).get_container_client(name) for c in (legacy, rust)]
                    for c, container in zip((legacy, rust), containers):
                        assert (await run_target_operation_async(c, container.get_throughput)).offer_throughput == 400
                    resources.delete_container(name)
                    resources.create_container(name, partition_key=PartitionKey(path="/pk"), offer_throughput=800)
                    results = [
                        await run_target_operation_async(c, container.get_throughput)
                        for c, container in zip((legacy, rust), containers)
                    ]
                    assert results[0].offer_throughput == results[1].offer_throughput == 800
                    assert fields(results[0]) == fields(results[1])
            asyncio.run(check())
        else:
            with CosmosClient(
                os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python",
            ) as legacy, CosmosClient(
                os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust",
            ) as rust:
                containers = [c.get_database_client(resources.id).get_container_client(name) for c in (legacy, rust)]
                for c, container in zip((legacy, rust), containers):
                    assert run_target_operation(c, container.get_throughput).offer_throughput == 400
                resources.delete_container(name)
                resources.create_container(name, partition_key=PartitionKey(path="/pk"), offer_throughput=800)
                results = [run_target_operation(c, container.get_throughput) for c, container in zip((legacy, rust), containers)]
                assert results[0].offer_throughput == results[1].offer_throughput == 800
                assert fields(results[0]) == fields(results[1])
    finally:
        resources.delete_container(name)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("options", [
    {"read_timeout": 2}, {"availability_strategy": True}, {"initial_headers": {"Accept": "unsupported"}},
])
def test_unsupported_input_never_enters_binding_or_legacy(monkeypatch, asynchronous, options):
    def configure(client):
        container = client.get_database_client("not-requested").get_container_client("not-requested")

        def forbidden(*args, **kwargs):
            pytest.fail("unsupported input reached metadata or legacy query")

        monkeypatch.setattr(container, "_get_properties", forbidden)
        monkeypatch.setattr(container, "read", forbidden)
        monkeypatch.setattr(client.client_connection, "QueryOffers", forbidden)
        return container

    if asynchronous:
        async def check():
            async with AsyncCosmosClient(
                os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust",
            ) as client:
                container = configure(client)
                with pytest.raises(NotImplementedError, match="legacy Python path"):
                    await run_target_operation_async(
                        client, lambda: container.get_throughput(**options), expect_rust=False,
                    )
        asyncio.run(check())
    else:
        with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
            container = configure(client)
            with pytest.raises(NotImplementedError, match="legacy Python path"):
                run_target_operation(client, lambda: container.get_throughput(**options), expect_rust=False)
