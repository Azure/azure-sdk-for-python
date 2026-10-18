# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Check replacement sample output and cleanup without service requests."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos import exceptions
from get_database_throughput.test_samples_unit import _function


def _sample(asynchronous, client):
    filename = "cosmos_responses_management" + ("_async" if asynchronous else "") + ".py"
    sample = _function(filename, "replace_throughput_db", {"exceptions": exceptions})
    result = sample(client, "sales")
    if asynchronous:
        asyncio.run(result)


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def sample_case(request):
    mock_type = AsyncMock if request.param else MagicMock
    offer = SimpleNamespace(offer_throughput=500, get_response_headers=MagicMock(return_value={"etag": "offer"}))
    database = SimpleNamespace(id="sales1", replace_throughput=mock_type(return_value=offer))
    client = SimpleNamespace(
        create_database=mock_type(return_value=database),
        delete_database=mock_type(),
    )
    return request.param, client, database, offer


def test_sample_prints_returned_capacity_and_deletes_owned_database(sample_case, capsys):
    asynchronous, client, database, offer = sample_case
    offer.offer_throughput = 600
    _sample(asynchronous, client)
    assert "Database throughput changed to 600 RU/s" in capsys.readouterr().out
    client.create_database.assert_called_once_with(id="sales1", offer_throughput=400)
    database.replace_throughput.assert_called_once_with(500)
    client.delete_database.assert_called_once_with("sales1")


def test_sample_deletes_owned_database_after_replacement_failure(sample_case, capsys):
    asynchronous, client, database, _ = sample_case
    database.replace_throughput.side_effect = exceptions.CosmosHttpResponseError(status_code=500, message="failed")
    _sample(asynchronous, client)
    assert "Error changing database throughput" in capsys.readouterr().out
    client.delete_database.assert_called_once_with("sales1")


def test_sample_does_not_delete_a_database_it_did_not_create(sample_case, capsys):
    asynchronous, client, _, _ = sample_case
    client.create_database.side_effect = exceptions.CosmosResourceExistsError(status_code=409, message="exists")
    _sample(asynchronous, client)
    assert "Error changing database throughput" in capsys.readouterr().out
    client.delete_database.assert_not_called()


def test_sample_cleans_up_after_unexpected_response_failure(sample_case):
    asynchronous, client, _, offer = sample_case
    offer.get_response_headers.side_effect = RuntimeError("response failure")
    with pytest.raises(RuntimeError, match="response failure"):
        _sample(asynchronous, client)
    client.delete_database.assert_called_once_with("sales1")


def test_sample_surfaces_cleanup_failure(sample_case):
    asynchronous, client, _, _ = sample_case
    failure = exceptions.CosmosHttpResponseError(status_code=500, message="cleanup failed")
    client.delete_database.side_effect = failure
    with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
        _sample(asynchronous, client)
    assert caught.value is failure
