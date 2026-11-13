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

from config import provisioning


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    sleep = Mock()
    monkeypatch.setattr(provisioning.time, "sleep", sleep)
    return sleep


def test_success_does_not_read_or_retry_rust():
    resource = object()
    create = Mock(return_value=resource)
    read = Mock()
    assert provisioning._create_or_reconcile("owned", create, read) is resource
    create.assert_called_once_with()
    read.assert_not_called()


@pytest.mark.parametrize("error_type", [ServiceRequestError, ServiceResponseError])
def test_lost_response_recovers_without_repeating_create_rust(error_type, caplog, no_sleep):
    resource = object()
    create = Mock(side_effect=error_type("lost response"))
    read = Mock(return_value=resource)
    assert provisioning._create_or_reconcile("owned", create, read) is resource
    create.assert_called_once_with()
    read.assert_called_once_with()
    no_sleep.assert_called_once_with(1)
    assert "transport failure" in caplog.text
    assert "recovered verified resource" in caplog.text


def test_only_confirmed_absence_allows_create_retry_rust():
    resource = object()
    create = Mock(side_effect=[ServiceResponseError("reset"), resource])
    read = Mock(side_effect=exceptions.CosmosResourceNotFoundError(status_code=404))
    assert provisioning._create_or_reconcile("owned", create, read) is resource
    assert create.call_count == 2
    read.assert_called_once_with()


def test_read_transport_failure_never_replays_create_rust():
    resource = object()
    create = Mock(side_effect=ServiceResponseError("lost create response"))
    read = Mock(side_effect=[ServiceResponseError("lost read response"), resource])
    assert provisioning._create_or_reconcile("owned", create, read) is resource
    create.assert_called_once_with()
    assert read.call_count == 2


def test_repeated_read_failures_exhaust_budget_and_propagate_rust(no_sleep, caplog):
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


def test_repeated_uncommitted_creates_are_bounded_rust():
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
def test_non_transport_create_failures_are_not_adopted_or_retried_rust(error):
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
def test_database_recovery_verifies_id_and_requested_throughput_rust(expected):
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
def test_database_mismatch_is_not_treated_as_recoverable_absence_rust(mismatch):
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
def test_container_recovery_verifies_requested_partition_definition_rust(mismatch):
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


@pytest.mark.parametrize("actual_ttl", [10, 20, None])
def test_container_recovery_verifies_requested_ttl_rust(actual_ttl):
    key = PartitionKey(path="/id")
    container = SimpleNamespace(read=Mock(return_value={
        "id": "owned", "partitionKey": dict(key), "defaultTtl": actual_ttl,
    }))
    database = SimpleNamespace(
        create_container=Mock(side_effect=ServiceResponseError("reset")),
        get_container_client=Mock(return_value=container),
    )
    if actual_ttl == 10:
        assert provisioning.create_owned_container(database, id="owned", partition_key=key, default_ttl=10) is container
    else:
        with pytest.raises(AssertionError, match="different default TTL"):
            provisioning.create_owned_container(database, id="owned", partition_key=key, default_ttl=10)
    database.create_container.assert_called_once_with(id="owned", partition_key=key, default_ttl=10)


@pytest.mark.parametrize("status", [None, 404, 403, 500])
def test_variant_cleanup_reports_http_failure_without_swallowing_it_rust(monkeypatch, caplog, status):
    from create_item import _input_variants as variants

    database = SimpleNamespace(id="owned-database", delete_container=Mock())
    create = Mock(return_value=object())
    monkeypatch.setattr(variants, "create_owned_container", create)
    request = SimpleNamespace(node=SimpleNamespace(nodeid="test_variants.py::test_create[sync]"))
    fixture = variants._make_variant_container_fixture.__wrapped__(database, request)
    make_container = next(fixture)
    definition = PartitionKey(path="/pk")
    assert make_container(definition) is create.return_value
    name = create.call_args.kwargs["id"]
    create.assert_called_once_with(database, id=name, partition_key=definition)
    error = None
    if status is not None:
        error_type = exceptions.CosmosResourceNotFoundError if status == 404 else exceptions.CosmosHttpResponseError
        error = error_type(
            status_code=status,
            sub_status=5300 if status == 403 else None,
            message="The given request [DELETE /dbs/owned/colls/variant] cannot be authorized.",
        )
        error.headers.update({"x-ms-activity-id": "cleanup-activity", "authorization": "must-not-be-logged"})
        database.delete_container.side_effect = error

    if status in (403, 500):
        with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
            next(fixture)
        assert caught.value is error
        assert request.node.nodeid in caplog.text
        assert f"database={database.id} container={name}" in caplog.text
        assert "configured_auth=ACCOUNT_KEY backend=rust" in caplog.text
        assert f"status={status} substatus={error.sub_status}" in caplog.text
        assert "activity_id=cleanup-activity" in caplog.text
        assert error.http_error_message in caplog.text
        assert "must-not-be-logged" not in caplog.text
    else:
        with pytest.raises(StopIteration):
            next(fixture)
        assert "Variant container cleanup failed" not in caplog.text
    database.delete_container.assert_called_once_with(name)
