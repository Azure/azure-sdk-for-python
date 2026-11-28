# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline checks for migrated fixtures; these do not prove live regional parity."""
import io
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from read_item._routing import ReadRoutingCapture
from read_item import test_read_consistency_emulator as consistency


def _payload():
    return {
        "activity_id": "read-operation", "request_count": 1, "retained_request_count": 1,
        "result_status": 200,
        "requests": [{"pipeline": "data_plane", "region": "westus",
                      "endpoint": "https://account-westus.documents.azure.com/", "status": 200}],
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_read_capture_preserves_native_result_and_exclusions_rust(monkeypatch, asynchronous):
    if asynchronous:
        from azure.cosmos.aio._backend import binding_adapter as module
    else:
        from azure.cosmos._backend import binding_adapter as module
    response = (200, 0, {}, b'{"id":"doc1"}', None)
    native = (AsyncMock if asynchronous else Mock)(return_value=(response, _payload()))
    other = Mock()
    monkeypatch.setattr(module, "_binding_function_for_op", lambda op: native if op == "read_item" else other)
    capture = ReadRoutingCapture(monkeypatch, asynchronous=asynchronous)
    prepared = SimpleNamespace(
        container_link="dbs/db/colls/orders", item_id="doc1",
        settings=SimpleNamespace(excluded_locations=("East US",)),
    )
    result = module._binding_function_for_op("read_item")("handle", prepared, timeout_seconds=5)
    if asynchronous:
        result = await result
        native.assert_awaited_once()
    assert result is response
    native.assert_called_once_with("handle", prepared, timeout_seconds=5, include_fault_diagnostics=True)
    assert module._binding_function_for_op("create_item") is other
    capture.assert_destination("db", ["East US"], ["West US"])


@pytest.mark.parametrize("fault", ["wrong-region", "incomplete-history", "metadata-only", "wrong-item"])
def test_read_capture_rejects_misleading_routing_evidence_rust(monkeypatch, fault):
    capture = ReadRoutingCapture(monkeypatch)
    payload = _payload()
    prepared = SimpleNamespace(
        container_link="dbs/db/colls/orders", item_id="doc1", settings=SimpleNamespace(excluded_locations=None)
    )
    if fault == "wrong-region":
        payload["requests"][0]["region"] = "eastus"
    elif fault == "incomplete-history":
        payload["request_count"] = 2
    elif fault == "metadata-only":
        payload["requests"][0]["pipeline"] = "metadata"
    else:
        prepared.item_id = "another-item"
    capture.calls.append((prepared, payload))
    with pytest.raises(AssertionError):
        capture.assert_destination("db", None, ["West US"])


@pytest.mark.parametrize("level,multi_write,expected", [
    ("Strong", False, True), ("Strong", True, False), ("Session", False, False),
])
def test_consistency_fixture_reads_account_without_legacy_sdk_rust(monkeypatch, level, multi_write, expected):
    document = {
        "userConsistencyPolicy": {"defaultConsistencyLevel": level},
        "enableMultipleWriteLocations": multi_write,
    }
    response = io.BytesIO(json.dumps(document).encode())
    request = Mock(return_value=response)
    monkeypatch.setattr(consistency, "urlopen", request)
    assert consistency._account_supports_strong_reads("https://account.invalid/", "ZmFrZQ==") is expected
    sent = request.call_args.args[0]
    assert sent.get_method() == "GET"
    assert sent.full_url == "https://account.invalid/"
    assert sent.get_header("Authorization").startswith("type%3Dmaster%26ver%3D1.0%26sig%3D")
    assert request.call_args.kwargs["timeout"] == 30


def test_consistency_fixture_propagates_account_discovery_failure_rust(monkeypatch):
    failure = OSError("account unavailable")
    monkeypatch.setattr(consistency, "urlopen", Mock(side_effect=failure))
    with pytest.raises(OSError) as caught:
        consistency._account_supports_strong_reads("https://account.invalid/", "ZmFrZQ==")
    assert caught.value is failure
