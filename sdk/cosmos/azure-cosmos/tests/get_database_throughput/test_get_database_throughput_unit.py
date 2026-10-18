# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Database-read budgets and failures at the Python-to-binding boundary."""

import asyncio
import inspect
import json
from unittest.mock import MagicMock

import pytest

from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from common.test_client_timeout_defaults_unit import case as case, clock as clock


def _complete(value):
    return asyncio.run(value) if inspect.isawaitable(value) else value


def _response(body, status=200):
    return status, 0, {"x-ms-request-charge": "1", "x-ms-substatus": "0"}, json.dumps(body).encode(), None


def _offer():
    return {"Offers": [{"content": {"offerThroughput": 4000}, "_self": "offers/offer/"}]}


@pytest.mark.parametrize(
    "options,budget",
    [
        ({}, 1),
        ({"timeout": None}, 1),
        ({"timeout": 2}, 2),
        ({"request_options": {"timeout": 2}}, 2),
        ({"timeout": 3, "request_options": {"timeout": 2}}, 3),
    ],
)
@pytest.mark.parametrize("warm", [False, True])
def test_read_shares_budget_and_next_call_resets(case, clock, options, budget, warm):
    calls = []

    def metadata(*args, **kwargs):
        calls.append(("metadata", kwargs["timeout_seconds"]))
        clock[0] += 0.75
        return _response({"id": "sales", "_self": "dbs/rid/", "_rid": "rid"})

    def offers(*args, **kwargs):
        calls.append(("offers", kwargs["timeout_seconds"]))
        return _response(_offer())

    case.install("read_database", side_effect=metadata)
    case.install("get_throughput", side_effect=offers)
    database = case.client.get_database_client("sales")
    if warm:
        _complete(database.read())
        calls.clear()
    original = json.loads(json.dumps(options))
    assert _complete(database.get_throughput(**options)).offer_throughput == 4000
    assert calls == ([("metadata", budget)] if not warm else []) + [
        ("offers", budget - (0.75 if not warm else 0)),
    ]
    assert options == original
    calls.clear()
    _complete(database.get_throughput())
    assert calls == [("offers", 1)]


@pytest.mark.parametrize("phase", ["metadata", "offers"])
def test_expired_read_skips_callback_and_does_not_replay(case, clock, phase):
    hook = MagicMock()

    def metadata(*args, **kwargs):
        clock[0] += 1.25 if phase == "metadata" else 0.25
        return _response({"id": "sales", "_self": "dbs/rid/", "_rid": "rid"})

    def offers(*args, **kwargs):
        assert kwargs["timeout_seconds"] == 0.75
        clock[0] += 1
        return _response(_offer())

    case.install("read_database", side_effect=metadata)
    dispatch = case.install("get_throughput", side_effect=offers)
    with pytest.raises(CosmosClientTimeoutError):
        _complete(case.client.get_database_client("sales").get_throughput(response_hook=hook))
    assert dispatch.call_count == (phase == "offers")
    hook.assert_not_called()


@pytest.mark.parametrize("phase", ["metadata", "offers"])
def test_read_service_failure_keeps_error_and_skips_callback(case, phase):
    hook = MagicMock()
    case.install(
        "read_database",
        result=_response({"id": "sales", "_self": "dbs/rid/"}, 403 if phase == "metadata" else 200),
    )
    dispatch = case.install("get_throughput", result=_response({"message": "denied"}, 403))
    with pytest.raises(CosmosHttpResponseError) as caught:
        _complete(case.client.get_database_client("sales").get_throughput(response_hook=hook))
    assert caught.value.status_code == 403
    assert caught.value.headers["x-ms-request-charge"] == "1"
    assert dispatch.call_count == (phase == "offers")
    hook.assert_not_called()


def test_read_callback_timeout_is_not_reclassified(case):
    failure = TimeoutError("customer callback")
    hook = MagicMock(side_effect=failure)
    case.install("get_throughput", result=_response(_offer()))
    database = case.client.get_database_client("sales")
    database._properties = {"_self": "dbs/rid/"}
    with pytest.raises(TimeoutError) as caught:
        _complete(database.get_throughput(response_hook=hook))
    assert caught.value is failure
    hook.assert_called_once()


@pytest.mark.parametrize("phase", ["metadata", "offers"])
@pytest.mark.parametrize("case", [True], indirect=True, ids=["async"])
def test_async_cancellation_stops_current_phase_and_skips_callback(case, phase):
    async def run():
        entered = asyncio.Event()
        cancelled = asyncio.Event()
        hook = MagicMock()

        async def pending(*args, **kwargs):
            entered.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

        case.install(
            "read_database",
            side_effect=pending if phase == "metadata" else None,
            result=_response({"id": "sales", "_self": "dbs/rid/"}),
        )
        dispatch = case.install(
            "get_throughput",
            side_effect=pending if phase == "offers" else None,
            result=_response(_offer()),
        )
        task = asyncio.create_task(case.client.get_database_client("sales").get_throughput(response_hook=hook))
        await entered.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert cancelled.is_set()
        assert dispatch.call_count == (phase == "offers")
        hook.assert_not_called()

    asyncio.run(run())


@pytest.mark.parametrize("phase", ["metadata", "offers"])
@pytest.mark.parametrize("case", [True], indirect=True, ids=["async"])
def test_async_deadline_cancels_pending_phase_and_awaits_cleanup(case, phase):
    async def run():
        cancelled = asyncio.Event()
        hook = MagicMock()

        async def pending(*args, **kwargs):
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

        case.install(
            "read_database",
            side_effect=pending if phase == "metadata" else None,
            result=_response({"id": "sales", "_self": "dbs/rid/"}),
        )
        dispatch = case.install(
            "get_throughput",
            side_effect=pending if phase == "offers" else None,
            result=_response(_offer()),
        )
        with pytest.raises(CosmosClientTimeoutError):
            await asyncio.wait_for(
                case.client.get_database_client("sales").get_throughput(response_hook=hook),
                timeout=3,
            )
        assert cancelled.is_set()
        assert dispatch.call_count == (phase == "offers")
        hook.assert_not_called()

    asyncio.run(run())
