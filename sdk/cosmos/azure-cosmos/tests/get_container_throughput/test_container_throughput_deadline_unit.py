# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Whole-call container throughput budgets at the Python-to-binding boundary."""

import asyncio
from copy import deepcopy
import inspect
import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from common.test_client_timeout_defaults_unit import case as case, clock as clock


PROPERTIES = {
    "id": "orders", "_rid": "rid", "_self": "dbs/db/colls/rid/",
    "partitionKey": {"paths": ["/id"], "kind": "Hash", "version": 2},
}
OFFER = {"_self": "offers/offer/", "content": {"offerThroughput": 800}}


def complete(value):
    return asyncio.run(value) if inspect.isawaitable(value) else value


def response(body, status=200):
    return status, 0, {"x-ms-request-charge": "1"}, json.dumps(body).encode(), None


@pytest.fixture(params=["get", "replace"])
def operation(request):
    return request.param


def invoke(container, operation, **kwargs):
    return (
        container.get_throughput(**kwargs) if operation == "get"
        else container.replace_throughput(800, **kwargs)
    )


@pytest.mark.parametrize("warm", [False, True])
@pytest.mark.parametrize("options,budget", [
    ({}, 1), ({"timeout": None}, 1), ({"timeout": 2}, 2),
    ({"request_options": {"timeout": 2}}, 2), ({"feed_options": {"timeout": 2}}, 2),
    ({"timeout": 3, "request_options": {"timeout": 2}}, 3),
])
def test_shared_budget_and_independent_next_call_rust(case, clock, operation, warm, options, budget):
    calls = []

    def phase(name, body):
        def dispatch(*args, **kwargs):
            calls.append((name, kwargs["timeout_seconds"]))
            clock[0] += 0.125
            return response(body)
        return dispatch

    case.install("read_container", side_effect=phase("metadata", PROPERTIES))
    case.install("get_throughput", side_effect=phase("lookup", {"Offers": [OFFER]}))
    case.install("replace_throughput", side_effect=phase("write", OFFER))
    container = case.client.get_database_client("sales").get_container_client("orders")
    if warm:
        complete(container.read())
    calls.clear()
    original = deepcopy(options)
    assert complete(invoke(container, operation, **options)).offer_throughput == 800
    names = ([] if warm else ["metadata"]) + ["lookup"] + (["write"] if operation == "replace" else [])
    assert calls == [(name, budget - i * 0.125) for i, name in enumerate(names)]
    assert options == original
    calls.clear()
    complete(invoke(container, operation))
    names = ["lookup"] + (["write"] if operation == "replace" else [])
    assert calls == [(name, 1 - i * 0.125) for i, name in enumerate(names)]


@pytest.mark.parametrize("phase", ["metadata", "lookup", "write"])
@pytest.mark.parametrize("failure", ["expiry", "service"])
def test_failure_skips_later_phases_and_callback_rust(case, clock, operation, phase, failure):
    if operation == "get" and phase == "write":
        return
    calls = []
    hook = MagicMock()

    def dispatch(name, body):
        def run(*args, **kwargs):
            calls.append(name)
            clock[0] += 1.25 if failure == "expiry" and name == phase else 0.125
            return response(body, 403 if failure == "service" and name == phase else 200)
        return run

    case.install("read_container", side_effect=dispatch("metadata", PROPERTIES))
    case.install("get_throughput", side_effect=dispatch("lookup", {"Offers": [OFFER]}))
    case.install("replace_throughput", side_effect=dispatch("write", OFFER))
    container = case.client.get_database_client("sales").get_container_client("orders")
    with pytest.raises(CosmosClientTimeoutError if failure == "expiry" else CosmosHttpResponseError) as caught:
        complete(invoke(container, operation, response_hook=hook))
    assert calls == ["metadata", "lookup", "write"][:["metadata", "lookup", "write"].index(phase) + 1]
    if failure == "service":
        assert caught.value.status_code == 403
        assert caught.value.headers["x-ms-request-charge"] == "1"
    hook.assert_not_called()


@pytest.mark.parametrize("expire", [None, "refresh", "retry"])
def test_recovery_uses_remaining_budget_rust(case, clock, operation, expire):
    calls = []
    container = case.client.get_database_client("sales").get_container_client("orders")
    complete_cache = case.client.client_connection._container_properties_cache
    complete_cache[container.container_link] = deepcopy(PROPERTIES)
    hook = MagicMock()

    def metadata(*args, **kwargs):
        calls.append(("refresh", kwargs["timeout_seconds"]))
        clock[0] += 1.25 if expire == "refresh" else 0.125
        return response(dict(PROPERTIES, _rid="new", _self="dbs/db/colls/new/"))

    def lookup(*args, **kwargs):
        name = "lookup" if not calls else "retry"
        calls.append((name, kwargs["timeout_seconds"]))
        clock[0] += 1.25 if expire == name else 0.125
        return response({"Offers": [] if name == "lookup" else [OFFER]})

    def write(*args, **kwargs):
        calls.append(("write", kwargs["timeout_seconds"]))
        return response(OFFER)

    case.install("read_container", side_effect=metadata)
    case.install("get_throughput", side_effect=lookup)
    case.install("replace_throughput", side_effect=write)
    if expire:
        with pytest.raises(CosmosClientTimeoutError):
            complete(invoke(container, operation, response_hook=hook))
        hook.assert_not_called()
    else:
        assert complete(invoke(container, operation, response_hook=hook)).offer_throughput == 800
        hook.assert_called_once()
    names = ["lookup", "refresh"] + ([] if expire == "refresh" else ["retry"])
    if operation == "replace" and expire is None:
        names.append("write")
    assert calls == [(name, 1 - i * 0.125) for i, name in enumerate(names)]


def test_driver_initialization_cannot_start_request_after_expiry_rust(case, clock, operation):
    container = case.client.get_database_client("sales").get_container_client("orders")
    case.client.client_connection._container_properties_cache[container.container_link] = deepcopy(PROPERTIES)

    def setup():
        clock[0] += 1.25
        return "driver"

    case.acquisition.side_effect = setup
    lookup = case.install("get_throughput", result=response({"Offers": [OFFER]}))
    write = case.install("replace_throughput", result=response(OFFER))
    with pytest.raises(CosmosClientTimeoutError):
        complete(invoke(container, operation))
    lookup.assert_not_called()
    write.assert_not_called()


def test_internal_metadata_budget_can_be_less_than_public_minimum_rust(case, clock):
    read = case.install("read_container", result=response(PROPERTIES))
    container = case.client.get_database_client("sales").get_container_client("orders")
    complete(container._get_properties(_item_operation_deadline=clock[0] + 0.5))
    assert read.call_args.kwargs["timeout_seconds"] == 0.5


@pytest.mark.parametrize("case", [False], indirect=True, ids=["sync"])
def test_sync_cache_lock_wait_consumes_budget_rust(case, clock, operation):
    container = case.client.get_database_client("sales").get_container_client("orders")

    def acquire(*, timeout):
        assert timeout == 1
        clock[0] += 1.25
        return False

    release = MagicMock()
    container.container_cache_lock = SimpleNamespace(acquire=acquire, release=release)
    metadata = case.install("read_container", result=response(PROPERTIES))
    with pytest.raises(CosmosClientTimeoutError):
        complete(invoke(container, operation))
    metadata.assert_not_called()
    release.assert_not_called()


@pytest.mark.parametrize("case", [True], indirect=True, ids=["async"])
@pytest.mark.parametrize("phase", ["metadata", "lookup", "refresh", "retry", "write", "lock"])
@pytest.mark.parametrize("expire", [False, True], ids=["cancellation", "deadline"])
def test_async_cancellation_awaits_cleanup_rust(case, operation, phase, expire):
    if operation == "get" and phase == "write":
        return

    async def run():
        entered = asyncio.Event()
        cleaned = asyncio.Event()
        container = case.client.get_database_client("sales").get_container_client("orders")
        recovery = phase in ("refresh", "retry")
        lookup_count = 0
        hook = MagicMock()
        if recovery:
            case.client.client_connection._container_properties_cache[container.container_link] = deepcopy(PROPERTIES)

        async def pending():
            entered.set()
            try:
                await asyncio.Future()
            finally:
                cleaned.set()

        async def metadata(*args, **kwargs):
            if phase in ("metadata", "refresh"):
                return await pending()
            return response(dict(PROPERTIES, _rid="new"))

        async def lookup(*args, **kwargs):
            nonlocal lookup_count
            lookup_count += 1
            if phase == "lookup" or phase == "retry" and lookup_count == 2:
                return await pending()
            return response({"Offers": [] if recovery and lookup_count == 1 else [OFFER]})

        async def write(*args, **kwargs):
            return await pending()

        case.install("read_container", side_effect=metadata)
        case.install("get_throughput", side_effect=lookup)
        write_call = case.install("replace_throughput", side_effect=write)
        if phase == "lock":
            await container.container_cache_lock.acquire()
            entered.set()
        task = asyncio.create_task(invoke(container, operation, response_hook=hook))
        try:
            await asyncio.wait_for(entered.wait(), 3)
            if not expire:
                task.cancel()
            with pytest.raises(CosmosClientTimeoutError if expire else asyncio.CancelledError):
                await asyncio.wait_for(task, 3)
            assert phase == "lock" or cleaned.is_set()
            assert write_call.call_count == int(phase == "write")
            hook.assert_not_called()
        finally:
            if not task.done():
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
            if phase == "lock":
                container.container_cache_lock.release()

    asyncio.run(run())
