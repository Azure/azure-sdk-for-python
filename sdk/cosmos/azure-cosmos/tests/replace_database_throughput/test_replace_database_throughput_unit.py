# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Database replacement budgets and failures at the Python-to-binding boundary."""

import asyncio
from copy import deepcopy
import inspect
import json
from unittest.mock import MagicMock

import pytest

from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from common.test_client_timeout_defaults_unit import case as case, clock as clock


def _complete(value):
    return asyncio.run(value) if inspect.isawaitable(value) else value


def _response(body, status=200):
    return status, 0, {"x-ms-request-charge": "1"}, json.dumps(body).encode(), None


def _offer(throughput=1000):
    return {"_self": "offers/offer/", "content": {"offerThroughput": throughput}}


@pytest.mark.parametrize(
    "options,budget",
    [
        ({}, 1),
        ({"timeout": None}, 1),
        ({"timeout": 2}, 2),
        ({"request_options": {"timeout": 2}}, 2),
        ({"feed_options": {"timeout": 2}}, 2),
        ({"timeout": 3, "request_options": {"timeout": 2}}, 3),
    ],
)
@pytest.mark.parametrize("warm", [False, True])
def test_replacement_shares_budget_and_next_call_resets_rust(case, clock, options, budget, warm):
    calls = []

    def phase(name, body):
        def dispatch(*args, **kwargs):
            calls.append((name, kwargs["timeout_seconds"]))
            clock[0] += 0.25
            return _response(body)
        return dispatch

    case.install("read_database", side_effect=phase("metadata", {"id": "sales", "_self": "dbs/rid/"}))
    case.install("get_throughput", side_effect=phase("lookup", {"Offers": [_offer()]}))
    case.install("replace_throughput", side_effect=phase("write", _offer(2000)))
    database = case.client.get_database_client("sales")
    if warm:
        database._properties = {"id": "sales", "_self": "dbs/rid/"}
    original = deepcopy(options)
    assert _complete(database.replace_throughput(2000, **options)).offer_throughput == 2000
    elapsed = 0 if warm else 0.25
    assert calls == ([] if warm else [("metadata", budget)]) + [
        ("lookup", budget - elapsed), ("write", budget - elapsed - 0.25),
    ]
    assert options == original
    calls.clear()
    _complete(database.replace_throughput(2000))
    assert calls == [("lookup", 1), ("write", 0.75)]


@pytest.mark.parametrize("phase", ["metadata", "lookup", "write"])
def test_expired_replacement_skips_later_phases_and_callback_rust(case, clock, phase):
    calls = []
    hook = MagicMock()

    def dispatch(name, body):
        def run(*args, **kwargs):
            calls.append(name)
            clock[0] += 1.25 if name == phase else 0.25
            return _response(body)
        return run

    case.install("read_database", side_effect=dispatch("metadata", {"id": "sales", "_self": "dbs/rid/"}))
    case.install("get_throughput", side_effect=dispatch("lookup", {"Offers": [_offer()]}))
    case.install("replace_throughput", side_effect=dispatch("write", _offer(2000)))
    with pytest.raises(CosmosClientTimeoutError):
        _complete(case.client.get_database_client("sales").replace_throughput(2000, response_hook=hook))
    assert calls == ["metadata", "lookup", "write"][:["metadata", "lookup", "write"].index(phase) + 1]
    hook.assert_not_called()


def test_driver_setup_uses_remaining_budget_before_lookup_rust(case, clock):
    def setup():
        clock[0] += 1.25
        return "test-driver"

    database = case.client.get_database_client("sales")
    database._properties = {"_self": "dbs/rid/"}
    case.acquisition.side_effect = setup
    lookup = case.install("get_throughput", result=_response({"Offers": [_offer()]}))
    write = case.install("replace_throughput", result=_response(_offer(2000)))
    with pytest.raises(CosmosClientTimeoutError):
        _complete(database.replace_throughput(2000))
    lookup.assert_not_called()
    write.assert_not_called()


@pytest.mark.parametrize("phase", ["metadata", "lookup", "write"])
def test_service_failure_keeps_error_headers_and_skips_later_phases_rust(case, phase):
    hook = MagicMock()
    metadata = case.install(
        "read_database",
        result=_response({"id": "sales", "_self": "dbs/rid/"}, 403 if phase == "metadata" else 200),
    )
    lookup = case.install(
        "get_throughput", result=_response({"Offers": [_offer()]}, 403 if phase == "lookup" else 200),
    )
    write = case.install("replace_throughput", result=_response({"message": "denied"}, 403))
    with pytest.raises(CosmosHttpResponseError) as caught:
        _complete(case.client.get_database_client("sales").replace_throughput(2000, response_hook=hook))
    assert caught.value.status_code == 403
    assert caught.value.headers["x-ms-request-charge"] == "1"
    assert metadata.call_count == 1
    assert lookup.call_count == (phase != "metadata")
    assert write.call_count == (phase == "write")
    hook.assert_not_called()


def test_callback_timeout_is_not_reclassified_or_replayed_rust(case):
    failure = TimeoutError("customer callback")
    hook = MagicMock(side_effect=failure)
    case.install("get_throughput", result=_response({"Offers": [_offer()]}))
    write = case.install("replace_throughput", result=_response(_offer(2000)))
    database = case.client.get_database_client("sales")
    database._properties = {"_self": "dbs/rid/"}
    with pytest.raises(TimeoutError) as caught:
        _complete(database.replace_throughput(2000, response_hook=hook))
    assert caught.value is failure
    write.assert_called_once()
    hook.assert_called_once()


@pytest.mark.parametrize("phase", ["metadata", "lookup", "write"])
@pytest.mark.parametrize("expire", [False, True], ids=["customer-cancellation", "deadline"])
@pytest.mark.parametrize("case", [True], indirect=True, ids=["async"])
def test_async_pending_phase_cancels_and_awaits_cleanup_rust(case, phase, expire):
    async def run():
        entered = asyncio.Event()
        cleaned = asyncio.Event()
        hook = MagicMock()

        async def pending(*args, **kwargs):
            entered.set()
            try:
                await asyncio.Event().wait()
            finally:
                cleaned.set()

        metadata = case.install(
            "read_database", side_effect=pending if phase == "metadata" else None,
            result=_response({"id": "sales", "_self": "dbs/rid/"}),
        )
        lookup = case.install(
            "get_throughput", side_effect=pending if phase == "lookup" else None,
            result=_response({"Offers": [_offer()]}),
        )
        write = case.install(
            "replace_throughput", side_effect=pending if phase == "write" else None,
            result=_response(_offer(2000)),
        )
        task = asyncio.create_task(
            case.client.get_database_client("sales").replace_throughput(2000, response_hook=hook)
        )
        try:
            await asyncio.wait_for(entered.wait(), 3)
            if not expire:
                task.cancel()
            with pytest.raises(CosmosClientTimeoutError if expire else asyncio.CancelledError):
                await asyncio.wait_for(task, 3)
            assert cleaned.is_set()
            assert metadata.call_count == 1
            assert lookup.call_count == (phase != "metadata")
            assert write.call_count == (phase == "write")
            hook.assert_not_called()
        finally:
            if not task.done():
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)

    asyncio.run(run())
