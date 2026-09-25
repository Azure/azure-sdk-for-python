# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Exercise the actual parity baseline assertions without a service account."""

import asyncio
import importlib
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from common import _parity_helpers


@pytest.mark.parametrize("surface", ["sync", "aio"])
@pytest.mark.parametrize(
    "result",
    [
        "correct", "wrong_id", "wrong_pk", "wrong_value", "missing_id",
        "read_error", "create_error", "setup_only_binding", "read_fallback",
    ],
)
def test_read_baseline_requires_each_expected_item(surface, result, monkeypatch):
    module_name = (
        "read_item.sync.test_read_item_parity"
        if surface == "sync"
        else "read_item.aio.test_read_item_parity_async"
    )
    baseline = importlib.import_module(module_name)
    stored_items = []
    counters = {"binding": 0, "fallback": 0}
    monkeypatch.setattr(_parity_helpers, "_binding_operation_count", lambda: counters["binding"])
    monkeypatch.setattr(_parity_helpers, "_rust_fallback_count", lambda: counters["fallback"])

    def factory(backend):
        stored = {}

        def create_item(body):
            if backend == "rust":
                counters["binding"] += 1
            if result == "create_error":
                raise ValueError("controlled create failure")
            stored.update(body)
            stored_items.append(dict(body))
            return dict(body)

        def read_item(item, *, partition_key):
            assert item == stored["id"]
            assert partition_key == stored["pk"]
            if backend == "rust":
                if result != "setup_only_binding":
                    counters["binding"] += 1
                if result == "read_fallback":
                    counters["fallback"] += 1
            if result == "read_error":
                raise ValueError("controlled read failure")
            actual = dict(stored)
            if result.startswith("wrong_"):
                field = result.removeprefix("wrong_")
                actual[field] = "incorrect"
            elif result == "missing_id":
                del actual["id"]
            return actual

        container = SimpleNamespace(
            create_item=AsyncMock(side_effect=create_item) if surface == "aio" else Mock(side_effect=create_item),
            read_item=AsyncMock(side_effect=read_item) if surface == "aio" else Mock(side_effect=read_item),
        )
        database = SimpleNamespace(get_container_client=Mock(return_value=container))
        client = Mock()
        client.get_database_client.return_value = database
        client.client_connection = SimpleNamespace(
            _backend=SimpleNamespace(name=backend), last_response_headers={}
        )
        return client

    original_runner = _parity_helpers.run_on_both_backends
    if surface == "sync":
        monkeypatch.setattr(
            baseline, "run_on_both_backends",
            lambda call, **kwargs: original_runner(call, client_factory=factory, **kwargs),
        )
    else:
        def async_client(_endpoint, _key, *, _backend):
            context = AsyncMock()
            context.__aenter__.return_value = factory(_backend)
            context.__aexit__.return_value = False
            return context

        monkeypatch.setenv(_parity_helpers.ENV_ENDPOINT, "https://unused.invalid")
        monkeypatch.setenv(_parity_helpers.ENV_KEY, "unused-test-key")
        monkeypatch.setattr(_parity_helpers, "AioCosmosClient", async_client)

    def run():
        outcome = baseline.test_baseline_read_by_id(SimpleNamespace(id="isolated-orders"))
        if surface == "aio":
            asyncio.run(outcome)

    if result == "correct":
        run()
        assert len(stored_items) == 2
        assert stored_items[0]["id"] != stored_items[1]["id"]
    else:
        message = {
            "setup_only_binding": "target operation did not enter the Rust binding",
            "read_fallback": "target operation fell back to core-python",
        }.get(result)
        with pytest.raises(AssertionError, match=message):
            run()
        if result in ("setup_only_binding", "read_fallback"):
            assert len(stored_items) == 2
            assert counters["binding"] == (1 if result == "setup_only_binding" else 2)
            assert counters["fallback"] == (1 if result == "read_fallback" else 0)
