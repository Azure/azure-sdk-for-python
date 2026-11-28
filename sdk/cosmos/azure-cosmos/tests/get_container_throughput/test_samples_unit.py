# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Container throughput sample values and owned-resource cleanup."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos import PartitionKey, ThroughputProperties, exceptions
from get_database_throughput.test_samples_unit import _function


def complete(result, asynchronous):
    if asynchronous:
        asyncio.run(result)


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def sample(request):
    asynchronous = request.param
    mock = AsyncMock if asynchronous else MagicMock
    offer = SimpleNamespace(offer_throughput=500, get_response_headers=MagicMock(return_value={"etag": "offer"}))
    container = SimpleNamespace(id="orders", replace_throughput=mock(return_value=offer))
    database = SimpleNamespace(create_container=mock(return_value=container), delete_container=mock())
    filename = "cosmos_responses_management" + ("_async" if asynchronous else "") + ".py"
    function = _function(filename, "replace_throughput_container", {"exceptions": exceptions, "PartitionKey": PartitionKey})
    return SimpleNamespace(
        asynchronous=asynchronous, offer=offer, container=container, database=database,
        run=lambda: complete(function(database, "orders"), asynchronous),
    )


def test_response_sample_prints_returned_capacity_and_cleans_up_rust(sample, capsys):
    sample.offer.offer_throughput = 600
    sample.run()
    assert "Container throughput changed to 600 RU/s" in capsys.readouterr().out
    sample.container.replace_throughput.assert_called_once_with(500)
    sample.database.delete_container.assert_called_once_with("orders")


def test_failed_replacement_cleans_up_rust(sample, capsys):
    sample.container.replace_throughput.side_effect = exceptions.CosmosHttpResponseError(status_code=500, message="failed")
    sample.run()
    assert "Error changing container throughput" in capsys.readouterr().out
    sample.database.delete_container.assert_called_once_with("orders")


def test_create_conflict_does_not_delete_existing_resource_rust(sample, capsys):
    sample.database.create_container.side_effect = exceptions.CosmosResourceExistsError(status_code=409, message="exists")
    sample.run()
    assert "Error changing container throughput" in capsys.readouterr().out
    sample.database.delete_container.assert_not_called()


def test_cleanup_failure_surfaces_rust(sample):
    sample.database.delete_container.side_effect = RuntimeError("cleanup failed")
    with pytest.raises(RuntimeError, match="cleanup failed"):
        sample.run()


@pytest.mark.parametrize("asynchronous", [False, True])
def test_autoscale_sample_uses_public_fields_rust(asynchronous, capsys):
    mock = AsyncMock if asynchronous else MagicMock
    offer = SimpleNamespace(auto_scale_max_throughput=6000, auto_scale_increment_percent=0)
    container = SimpleNamespace(id="orders", replace_throughput=mock(return_value=offer))
    filename = "autoscale_throughput_management" + ("_async" if asynchronous else "") + ".py"
    function = _function(
        filename, "update_autoscale_max_throughput",
        {"exceptions": exceptions, "ThroughputProperties": ThroughputProperties},
    )
    complete(function(container, 6000), asynchronous)
    output = capsys.readouterr().out
    assert "New maximum throughput: 6000 RU/s" in output
    assert "Increment percent: 0" in output


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("missing", [False, True])
def test_management_sample_uses_public_values_and_stops_after_missing_offer_rust(asynchronous, missing, capsys):
    mock = AsyncMock if asynchronous else MagicMock
    container = SimpleNamespace(
        id="orders",
        get_throughput=mock(return_value=SimpleNamespace(offer_throughput=400)),
        replace_throughput=mock(return_value=SimpleNamespace(offer_throughput=500)),
    )
    if missing:
        container.get_throughput.side_effect = exceptions.CosmosResourceNotFoundError(status_code=404)
    database = SimpleNamespace(get_container_client=MagicMock(return_value=container))
    filename = "container_management" + ("_async" if asynchronous else "") + ".py"
    function = _function(filename, "manage_provisioned_throughput", {"exceptions": exceptions})
    complete(function(database, "orders"), asynchronous)
    if missing:
        container.replace_throughput.assert_not_called()
        assert "does not exist" in capsys.readouterr().out
    else:
        container.replace_throughput.assert_called_once_with(500)
        assert "Provisioned Throughput is now '500'" in capsys.readouterr().out
