# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Tests for the error-budget polling semantics in the async ``_poll``.

This is the async mirror of ``test_post_and_poll_error_budget.py``: the async
``_poll`` shares the same ``_ErrorBudget`` model as the sync ``_post_and_poll``,
so both clients behave identically.

  * Healthy ``pending`` 200s (queued for capacity / in progress) clear the
    budget, so an operation can wait in the queue indefinitely.
  * A sustained streak of 5xx / 408 / 429 / transient network errors is bounded
    by ``error_budget_sec`` and raises ``TimeoutError``.
  * Any healthy 200 in between disarms the budget, so intermittent blips never
    trip it.
  * ``error_budget_sec=None`` disables the budget (retry forever).
"""

from __future__ import annotations

import itertools

import pytest

from azure.core.exceptions import ServiceResponseError

from azure.ai.finetuningsessions import _patch as _patch_mod
from azure.ai.finetuningsessions.aio import _patch as _aio_mod
from azure.ai.finetuningsessions.aio._patch import _poll

_SESSION_ID = "session_deadbeef"
_REQUEST_ID = "req-1"
_OP_TYPE = "optim_step"
_BUDGET = 5.0

_COMPLETED = {"status": "completed", "result": {}}
_PENDING = {"status": "pending"}


class _FakeResponse:
    def __init__(self, status_code: int, body: dict | None = None, retry_after: str | None = None):
        self.status_code = status_code
        self._body = body or {}
        self.headers = {} if retry_after is None else {"Retry-After": retry_after}

    def json(self) -> dict:
        return self._body

    def raise_for_status(self) -> None:  # pragma: no cover - not hit in these tests
        raise AssertionError(f"unexpected raise_for_status on {self.status_code}")


class _FakeAsyncClient:
    """Yields scripted GET responses from an async ``send_request``.

    A scripted entry may be a ``_FakeResponse`` (returned) or an ``Exception``
    instance (raised, to simulate a transport error).
    """

    def __init__(self, get_responses):
        self._get = iter(get_responses)

    async def send_request(self, req):
        item = next(self._get)
        if isinstance(item, Exception):
            raise item
        return item


@pytest.fixture
def clock(monkeypatch):
    """Deterministic monotonic clock; ``asyncio.sleep`` advances it by its arg."""

    class _Clock:
        now: float = 1000.0

    c = _Clock()

    async def _fake_sleep(dt):
        c.now += dt

    monkeypatch.setattr(_aio_mod._time, "monotonic", lambda: c.now)
    monkeypatch.setattr(_aio_mod.asyncio, "sleep", _fake_sleep)
    return c


@pytest.fixture(autouse=True)
def _reset_poll_state():
    _patch_mod._poll_log_last.clear()
    _patch_mod._request_active_since.clear()
    yield
    _patch_mod._poll_log_last.clear()
    _patch_mod._request_active_since.clear()


def _poll_coro(get_responses, *, error_budget_sec=_BUDGET):
    client = _FakeAsyncClient(get_responses)
    return _poll(
        client,
        _SESSION_ID,
        _REQUEST_ID,
        _OP_TYPE,
        error_budget_sec=error_budget_sec,
    )


@pytest.mark.asyncio
async def test_long_queue_wait_then_complete_does_not_time_out(clock):
    # 20 healthy pending polls (clock advances well past the 5s budget via
    # backoff sleeps) followed by completion — must NOT raise.
    responses = [_FakeResponse(200, _PENDING) for _ in range(20)] + [_FakeResponse(200, _COMPLETED)]

    result = await _poll_coro(responses)

    assert result is not None
    # Sanity: we really did spend more wall-clock than the budget while healthy.
    assert clock.now >= 1000.0 + _BUDGET


@pytest.mark.asyncio
async def test_sustained_5xx_raises_timeout(clock):
    with pytest.raises(TimeoutError):
        await _poll_coro(itertools.repeat(_FakeResponse(503)))

    # The streak must have lasted at least the budget before failing.
    assert clock.now >= 1000.0 + _BUDGET


@pytest.mark.asyncio
async def test_sustained_network_error_raises_timeout(clock):
    with pytest.raises(TimeoutError):
        await _poll_coro(itertools.repeat(ServiceResponseError("boom")))


@pytest.mark.asyncio
async def test_healthy_poll_resets_error_budget(clock):
    # 503s that never run long enough *consecutively* to exceed the budget
    # because a healthy pending poll disarms it in between -> must complete.
    responses = [
        _FakeResponse(503),
        _FakeResponse(503),
        _FakeResponse(503),
        _FakeResponse(200, _PENDING),  # disarms the budget
        _FakeResponse(503),
        _FakeResponse(503),
        _FakeResponse(503),
        _FakeResponse(200, _COMPLETED),
    ]

    result = await _poll_coro(responses)

    assert result is not None


@pytest.mark.asyncio
async def test_disabled_budget_retries_through_errors(clock):
    # With the budget disabled (None) a finite error streak followed by
    # completion must still succeed (no TimeoutError).
    responses = [_FakeResponse(503) for _ in range(50)] + [_FakeResponse(200, _COMPLETED)]

    result = await _poll_coro(responses, error_budget_sec=None)

    assert result is not None
