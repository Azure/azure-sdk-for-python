# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from azure.cosmos import exceptions
from azure.cosmos._backend.client_config import _prepare_fault_injection_rules
from azure.cosmos.aio._backend import binding_adapter as async_binding
from fault_injection._delayed_create import assert_control, assert_failure, assert_route, create_rule
from fault_injection import conftest as fixtures


@pytest.mark.parametrize("inject", [True, False])
def test_rule_preserves_exact_delay_probability_and_unlimited_failures(inject):
    rule = create_rule("named-rule", "owned-container", inject)
    prepared, = _prepare_fault_injection_rules([rule])
    assert prepared.id == "named-rule"
    assert prepared.container_id == "owned-container"
    assert prepared.operation_type == "CreateItem"
    assert prepared.status_code == 502
    assert prepared.delay_ms == 10000
    assert prepared.probability == (1.0 if inject else 0.0)
    assert prepared.hit_limit is None
    assert prepared.enabled is True


@pytest.mark.parametrize("elapsed", [0, 9.99, 10.0, float("nan"), float("inf")])
def test_failure_rejects_missing_or_invalid_delay(elapsed):
    with pytest.raises(AssertionError, match="delay"):
        assert_failure(exceptions.CosmosHttpResponseError(502), elapsed, 1)


@pytest.mark.parametrize("error", [None, RuntimeError("wrong type"), exceptions.CosmosHttpResponseError(503)])
def test_failure_rejects_success_or_wrong_error(error):
    with pytest.raises(AssertionError):
        assert_failure(error, 10.1, 1)


@pytest.mark.parametrize("hits", [0, -1])
def test_failure_rejects_unapplied_fault(hits):
    with pytest.raises(AssertionError, match="did not apply"):
        assert_failure(exceptions.CosmosHttpResponseError(502), 10.1, hits)


@pytest.mark.parametrize("hits", [1, 3])
def test_failure_accepts_applied_delay_without_inventing_retry_count(hits):
    assert_failure(exceptions.CosmosHttpResponseError(502), 10.1, hits)


@pytest.mark.parametrize("target", ["returned", "stored"])
@pytest.mark.parametrize("field", ["id", "pk", "name", "key"])
@pytest.mark.parametrize("missing", [False, True])
def test_control_detects_missing_or_changed_customer_fields(target, field, missing):
    item = {"id": "order", "pk": "customer", "name": "sample document", "key": "value"}
    responses = {"returned": dict(item), "stored": dict(item)}
    if missing:
        responses[target].pop(field)
    else:
        responses[target][field] = "wrong"
    with pytest.raises((AssertionError, KeyError)):
        assert_control(responses["returned"], responses["stored"], item, 0)


def test_control_rejects_applied_fault_and_accepts_service_fields():
    item = {"id": "order", "pk": "customer"}
    with pytest.raises(AssertionError, match="applied"):
        assert_control(item, item, item, 1)
    assert_control({**item, "_etag": "a"}, {**item, "_etag": "b"}, item, 0)


@pytest.mark.parametrize("backend,binding_delta,fallback_delta", [
    ("rust", 0, 0), ("rust", 2, 0), ("rust", 1, 1), ("core-python", 1, 0),
])
def test_route_rejects_wrong_path_or_fallback(backend, binding_delta, fallback_delta):
    with pytest.raises(AssertionError):
        assert_route((7, 2), (7 + binding_delta, 2 + fallback_delta), backend)


@pytest.mark.asyncio
async def test_async_hit_count_awaits_acquisition_and_forwards_rule_id(monkeypatch):
    adapter = async_binding.AsyncBindingAdapter("https://fault.example", master_key="key")
    acquire = AsyncMock(return_value="owned-handle")
    counter = Mock(return_value=3)
    monkeypatch.setattr(adapter, "_ensure_driver_handle", acquire)
    monkeypatch.setattr(async_binding, "_rust_module", SimpleNamespace(_debug_fault_injection_rule_hit_count=counter))
    try:
        assert await adapter._debug_fault_injection_rule_hit_count("named-rule") == 3
        acquire.assert_awaited_once_with()
        counter.assert_called_once_with("owned-handle", "named-rule")
    finally:
        await adapter.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["acquisition", "counter", "missing_binding", "closed"])
async def test_async_hit_count_does_not_hide_errors(monkeypatch, failure):
    adapter = async_binding.AsyncBindingAdapter("https://fault.example", master_key="key")
    counter = Mock(return_value=0)
    monkeypatch.setattr(async_binding, "_rust_module", SimpleNamespace(_debug_fault_injection_rule_hit_count=counter))
    expected = RuntimeError
    if failure == "missing_binding":
        monkeypatch.setattr(async_binding, "_rust_module", None)
        expected = NotImplementedError
    elif failure == "closed":
        await adapter.close()
    else:
        monkeypatch.setattr(
            adapter, "_ensure_driver_handle",
            AsyncMock(side_effect=RuntimeError("acquisition failed")) if failure == "acquisition"
            else AsyncMock(return_value="owned-handle"),
        )
        if failure == "counter":
            counter.side_effect = RuntimeError("unknown rule")
    try:
        with pytest.raises(expected):
            await adapter._debug_fault_injection_rule_hit_count("named-rule")
        if failure != "counter":
            counter.assert_not_called()
    finally:
        await adapter.close()


@pytest.fixture
def fake_setup(monkeypatch):
    client = MagicMock()
    client.__enter__.return_value = client
    client.get_database_client.return_value.read.side_effect = exceptions.CosmosResourceNotFoundError(404)
    monkeypatch.setattr(fixtures, "CosmosClient", Mock(return_value=client))
    monkeypatch.setenv("ACCOUNT_HOST", "https://fault.example")
    monkeypatch.setenv("ACCOUNT_KEY", "fake-key")
    monkeypatch.setattr(fixtures, "create_owned_database", Mock(return_value=Mock()))
    monkeypatch.setattr(fixtures, "create_owned_container", Mock(return_value=Mock()))
    request = SimpleNamespace(node=SimpleNamespace(nodeid="controlled-case"))
    return client, fixtures.owned_target.__wrapped__(request)


def test_fixture_cleans_owned_database_after_assertion_failure(fake_setup):
    client, fixture = fake_setup
    database_id, _ = next(fixture)
    with pytest.raises(AssertionError, match="case failed"):
        fixture.throw(AssertionError("case failed"))
    client.delete_database.assert_called_once_with(database_id)
    assert client.get_database_client.return_value.read.call_count == 2
    client.__exit__.assert_called_once()


def test_fixture_does_not_delete_resource_when_create_conflicts(fake_setup):
    client, fixture = fake_setup
    fixtures.create_owned_database.side_effect = exceptions.CosmosResourceExistsError(409)
    with pytest.raises(exceptions.CosmosResourceExistsError):
        next(fixture)
    client.delete_database.assert_not_called()
    client.__exit__.assert_called_once()


def test_fixture_surfaces_cleanup_failure(fake_setup):
    client, fixture = fake_setup
    next(fixture)
    client.delete_database.side_effect = exceptions.CosmosHttpResponseError(500)
    with pytest.raises(exceptions.CosmosHttpResponseError) as error:
        fixture.close()
    assert error.value.status_code == 500
    client.__exit__.assert_called_once()


def test_fixture_cleans_ambiguous_setup_failure(fake_setup):
    client, fixture = fake_setup
    fixtures.create_owned_database.side_effect = RuntimeError("setup failed")
    client.delete_database.side_effect = exceptions.CosmosResourceNotFoundError(404)
    with pytest.raises(RuntimeError, match="setup failed"):
        next(fixture)
    client.delete_database.assert_called_once()
    assert client.get_database_client.return_value.read.call_count == 2
