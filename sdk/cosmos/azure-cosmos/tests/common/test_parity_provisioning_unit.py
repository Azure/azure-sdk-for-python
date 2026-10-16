# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Keep fixture recovery bounded, observable, and separate from target calls."""
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest
from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.cosmos import PartitionKey, ThroughputProperties, exceptions

from common import parity_provisioning as provisioning


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    sleep = Mock()
    monkeypatch.setattr(provisioning.time, "sleep", sleep)
    return sleep


def test_success_does_not_read_or_retry():
    resource = object()
    create = Mock(return_value=resource)
    read = Mock()
    assert provisioning._create_or_reconcile("owned", create, read) is resource
    create.assert_called_once_with()
    read.assert_not_called()


@pytest.mark.parametrize("error_type", [ServiceRequestError, ServiceResponseError])
def test_lost_response_recovers_without_repeating_create(error_type, caplog, no_sleep):
    resource = object()
    create = Mock(side_effect=error_type("lost response"))
    read = Mock(return_value=resource)
    assert provisioning._create_or_reconcile("owned", create, read) is resource
    create.assert_called_once_with()
    read.assert_called_once_with()
    no_sleep.assert_called_once_with(1)
    assert "transport failure" in caplog.text
    assert "recovered verified resource" in caplog.text


def test_only_confirmed_absence_allows_create_retry():
    resource = object()
    create = Mock(side_effect=[ServiceResponseError("reset"), resource])
    read = Mock(side_effect=exceptions.CosmosResourceNotFoundError(status_code=404))
    assert provisioning._create_or_reconcile("owned", create, read) is resource
    assert create.call_count == 2
    read.assert_called_once_with()


def test_read_transport_failure_never_replays_create():
    resource = object()
    create = Mock(side_effect=ServiceResponseError("lost create response"))
    read = Mock(side_effect=[ServiceResponseError("lost read response"), resource])
    assert provisioning._create_or_reconcile("owned", create, read) is resource
    create.assert_called_once_with()
    assert read.call_count == 2


def test_repeated_read_failures_exhaust_budget_and_propagate(no_sleep, caplog):
    error = ServiceResponseError("read failed")
    create = Mock(side_effect=ServiceResponseError("create failed"))
    read = Mock(side_effect=error)
    with pytest.raises(ServiceResponseError) as caught:
        provisioning._create_or_reconcile("owned", create, read)
    assert caught.value is error
    create.assert_called_once_with()
    assert read.call_count == 2
    assert no_sleep.call_args_list == [call(1), call(2)]
    assert "exhausted three attempts" in caplog.text


def test_repeated_uncommitted_creates_are_bounded():
    error = ServiceResponseError("create failed")
    create = Mock(side_effect=error)
    read = Mock(side_effect=exceptions.CosmosResourceNotFoundError(status_code=404))
    with pytest.raises(ServiceResponseError) as caught:
        provisioning._create_or_reconcile("owned", create, read)
    assert caught.value is error
    assert create.call_count == 3
    assert read.call_count == 2


@pytest.mark.parametrize("error", [
    exceptions.CosmosResourceExistsError(status_code=409),
    exceptions.CosmosHttpResponseError(status_code=403),
    ValueError("invalid setup"),
])
def test_non_transport_create_failures_are_not_adopted_or_retried(error):
    create = Mock(side_effect=error)
    read = Mock()
    with pytest.raises(type(error)) as caught:
        provisioning._create_or_reconcile("owned", create, read)
    assert caught.value is error
    create.assert_called_once_with()
    read.assert_not_called()


@pytest.mark.parametrize("expected", [
    None,
    1000,
    ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=2),
])
def test_database_recovery_verifies_id_and_requested_throughput(expected):
    throughput = ThroughputProperties(offer_throughput=expected) if isinstance(expected, int) else expected
    database = SimpleNamespace(
        read=Mock(return_value={"id": "owned"}),
        get_throughput=Mock(return_value=throughput),
    )
    if expected is None:
        database.get_throughput.side_effect = exceptions.CosmosResourceNotFoundError(status_code=404)
    client = SimpleNamespace(
        create_database=Mock(side_effect=ServiceResponseError("reset")),
        get_database_client=Mock(return_value=database),
    )
    assert provisioning.create_owned_database(client, id="owned", offer_throughput=expected) is database
    client.create_database.assert_called_once_with(id="owned", offer_throughput=expected)
    client.get_database_client.assert_called_once_with("owned")
    database.read.assert_called_once_with()
    database.get_throughput.assert_called_once_with()


@pytest.mark.parametrize("mismatch", ["id", "fixed", "mode", "missing", "unexpected", "autoscale"])
def test_database_mismatch_is_not_treated_as_recoverable_absence(mismatch):
    expected = 1000
    actual = ThroughputProperties(offer_throughput=1000)
    if mismatch == "fixed":
        actual = ThroughputProperties(offer_throughput=2000)
    if mismatch == "mode":
        actual = ThroughputProperties(auto_scale_max_throughput=5000)
    if mismatch == "unexpected":
        expected = None
    if mismatch == "autoscale":
        expected = ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=2)
        actual = ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=5)
    database = SimpleNamespace(
        read=Mock(return_value={"id": "other" if mismatch == "id" else "owned"}),
        get_throughput=Mock(return_value=actual),
    )
    if mismatch == "missing":
        database.get_throughput.side_effect = exceptions.CosmosResourceNotFoundError(status_code=404)
    client = SimpleNamespace(
        create_database=Mock(side_effect=ServiceResponseError("reset")),
        get_database_client=Mock(return_value=database),
    )
    with pytest.raises(AssertionError, match="Recovered database"):
        provisioning.create_owned_database(client, id="owned", offer_throughput=expected)
    client.create_database.assert_called_once()


@pytest.mark.parametrize("mismatch", [None, "id", "paths", "kind", "version"])
def test_container_recovery_verifies_requested_partition_definition(mismatch):
    key = PartitionKey(path="/pk")
    properties = {"id": "owned", "partitionKey": dict(key)}
    if mismatch == "id":
        properties["id"] = "other"
    elif mismatch is not None:
        properties["partitionKey"][mismatch] = "different"
    container = SimpleNamespace(read=Mock(return_value=properties))
    database = SimpleNamespace(
        create_container=Mock(side_effect=ServiceResponseError("reset")),
        get_container_client=Mock(return_value=container),
    )
    if mismatch is None:
        assert provisioning.create_owned_container(database, id="owned", partition_key=key) is container
    else:
        with pytest.raises(AssertionError, match="Recovered container"):
            provisioning.create_owned_container(database, id="owned", partition_key=key)
    database.create_container.assert_called_once_with(id="owned", partition_key=key)
