# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Error-budget polling semantics for the async ``_poll`` loop.

The async client shares the same :class:`_ErrorBudget` helper as the sync
``_post_and_poll`` (see ``test_post_and_poll_error_budget.py`` for the helper's
unit tests). These tests exercise the async loop integration: healthy pending
200s are unbounded and clear the budget, while a sustained error streak past
``error_budget_sec`` raises ``TimeoutError``.
"""

from __future__ import annotations

import itertools
import logging

import pytest

from azure.core.exceptions import ServiceResponseError

from azure.ai.finetuningsessions import _patch as _patch_mod
from azure.ai.finetuningsessions.aio import _patch as _aio_mod

_COMPLETED = {"status": "completed", "result": {}}
_PENDING = {"status": "pending"}


class _FakeResponse:
    def __init__(self, status_code: int, body: dict | None = None, retry_after: str | None = None):
        self.status_code = status_code
        self._body = body or {}
        self.headers = {} if retry_after is None else {"Retry-After": retry_after}

    def json(self) -> dict:
        return self._body

    def raise_for_status(self) -> None:
        if self.status_code >= 400:  # pragma: no cover - error paths classify first
            raise AssertionError(f"unexpected raise_for_status on {self.status_code}")


class _FakeAsyncClient:
    """Yields scripted GET responses to the async ``_poll`` loop.

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


class _FakeAsyncPostPollClient:
    async def send_request(self, req, **kwargs):
        if req.method == "POST":
            return _FakeResponse(
                200,
                {"request_id": "req-1", "session_id": "session_deadbeef"},
            )
        return _FakeResponse(200, _COMPLETED)


@pytest.fixture
def clock(monkeypatch):
    """Deterministic monotonic clock; ``sleep`` advances it by its argument."""

    class _Clock:
        now: float = 1000.0

    c = _Clock()

    async def _fake_sleep(dt):
        c.now += dt

    # The async loop reads its own module's ``_time``; ``_maybe_log_poll_progress``
    # reads the sync module's ``_time``. Patch both so they share one clock.
    monkeypatch.setattr(_aio_mod._time, "monotonic", lambda: c.now)
    monkeypatch.setattr(_patch_mod._time, "monotonic", lambda: c.now)
    monkeypatch.setattr(_aio_mod.asyncio, "sleep", _fake_sleep)
    return c


@pytest.fixture(autouse=True)
def _reset_poll_state():
    _patch_mod._poll_log_last.clear()
    _patch_mod._request_active_since.clear()
    _patch_mod._poll_warn_last.clear()
    yield
    _patch_mod._poll_log_last.clear()
    _patch_mod._request_active_since.clear()
    _patch_mod._poll_warn_last.clear()


_BUDGET = 5.0


async def _poll(
    get_responses,
    *,
    error_budget_sec=_BUDGET,
    operation_started_at=None,
    poll_min_sec=None,
    poll_max_sec=None,
):
    client = _FakeAsyncClient(get_responses)
    return await _aio_mod._poll(
        client,
        "session_deadbeef",
        "req-1",
        "optim_step",
        error_budget_sec=error_budget_sec,
        operation_started_at=operation_started_at,
        poll_min_sec=poll_min_sec,
        poll_max_sec=poll_max_sec,
    )


async def test_long_queue_wait_then_complete_does_not_time_out(clock):
    # 20 healthy pending polls (clock advances well past the 5s budget via
    # backoff sleeps) followed by completion -- must NOT raise.
    responses = [_FakeResponse(200, _PENDING) for _ in range(20)] + [_FakeResponse(200, _COMPLETED)]

    result = await _poll(responses)

    assert result is not None
    assert clock.now >= 1000.0 + _BUDGET


async def test_async_operation_timeline_includes_label_and_stable_fields(clock, caplog):
    client = _FakeAsyncPostPollClient()
    token = _aio_mod.set_operation_label("step=4")
    try:
        with caplog.at_level(logging.INFO, logger=_aio_mod.__name__):
            result = await _aio_mod._post_and_poll(
                client,
                "session_deadbeef",
                "/fine_tuning_sessions/session_deadbeef/optim_step",
                {},
            )
    finally:
        _aio_mod.reset_operation_label(token)

    assert result is not None
    assert "submit_queued session_id=session_deadbeef op=optim_step" in caplog.text
    assert (
        "submit_started session_id=session_deadbeef op=optim_step "
        "path=/fine_tuning_sessions/session_deadbeef/optim_step queue_wait_ms=0.0 "
        "label=step=4"
    ) in caplog.text
    assert (
        "submit_completed session_id=session_deadbeef request_id=req-1 " "op=optim_step elapsed_ms=0.0 label=step=4"
    ) in caplog.text
    assert (
        "result_consumed session_id=session_deadbeef request_id=req-1 op=optim_step "
        "poll_attempts=1 elapsed_ms=0.0 poll_elapsed_ms=0.0 label=step=4"
    ) in caplog.text


async def test_result_timeline_separates_operation_and_poll_elapsed(clock, caplog):
    with caplog.at_level(logging.INFO, logger=_aio_mod.__name__):
        await _poll(
            [
                _FakeResponse(200, _PENDING),
                _FakeResponse(200, _COMPLETED),
            ],
            operation_started_at=990.0,
        )

    assert "elapsed_ms=11000.0 poll_elapsed_ms=1000.0" in caplog.text


async def test_fixed_poll_interval(clock):
    responses = [
        _FakeResponse(200, _PENDING),
        _FakeResponse(200, _PENDING),
        _FakeResponse(200, _PENDING),
        _FakeResponse(200, _COMPLETED),
    ]

    await _poll(responses, poll_min_sec=0.5, poll_max_sec=0.5)

    assert clock.now == 1001.5


async def test_invalid_poll_interval_is_rejected(clock):
    with pytest.raises(ValueError, match="poll_max_sec"):
        await _poll(
            [_FakeResponse(200, _COMPLETED)],
            poll_min_sec=1.0,
            poll_max_sec=0.5,
        )


async def test_sustained_5xx_raises_timeout(clock):
    with pytest.raises(TimeoutError):
        await _poll(itertools.repeat(_FakeResponse(503)))

    assert clock.now >= 1000.0 + _BUDGET


async def test_sustained_network_error_raises_timeout(clock):
    with pytest.raises(TimeoutError):
        await _poll(itertools.repeat(ServiceResponseError("boom")))


async def test_healthy_poll_resets_error_budget(clock):
    # A healthy pending poll disarms the budget between error streaks, so a
    # finite series of 503s never exceeds it consecutively -> must complete.
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

    result = await _poll(responses)

    assert result is not None


async def test_fresh_request_not_found_retries_then_completes(clock, caplog):
    with caplog.at_level(logging.WARNING, logger=_aio_mod.__name__):
        result = await _poll(
            [
                _FakeResponse(404, {"detail": "Request not found"}),
                _FakeResponse(200, _COMPLETED),
            ]
        )

    assert result is not None
    assert clock.now == 1001.0
    assert (
        "transient request-store 404 for session_deadbeef/req-1 " "(op=optim_step, 0.0s/120.0s grace); retrying in 1.0s"
    ) in caplog.text


async def test_request_not_found_stops_retrying_after_grace(clock):
    with pytest.raises(AssertionError, match="unexpected raise_for_status on 404"):
        await _poll(itertools.repeat(_FakeResponse(404, {"detail": "Request not found"})))

    assert clock.now == 1120.0


async def test_other_404_is_retried(clock):
    result = await _poll(
        [
            _FakeResponse(404, {"detail": "Model not found"}),
            _FakeResponse(200, _COMPLETED),
        ]
    )

    assert result is not None
    assert clock.now == 1001.0


@pytest.mark.parametrize(
    "body",
    [
        {"detail": "request not found"},
        {"detail": " Request not found "},
        {"detail": "Request not found", "code": "missing"},
    ],
)
async def test_404_body_variants_are_retried(clock, body):
    result = await _poll([_FakeResponse(404, body), _FakeResponse(200, _COMPLETED)])

    assert result is not None
    assert clock.now == 1001.0


async def test_request_not_found_does_not_clear_armed_error_budget(clock):
    responses = [
        _FakeResponse(503),
        _FakeResponse(404, {"detail": "Request not found"}),
        *[_FakeResponse(503) for _ in range(10)],
    ]

    with pytest.raises(TimeoutError):
        await _poll(responses)

    assert clock.now >= 1000.0 + _BUDGET


async def test_disabled_budget_retries_through_errors(clock):
    # With the budget disabled (None) a finite error streak followed by
    # completion must still succeed (no TimeoutError).
    responses = [_FakeResponse(503) for _ in range(50)] + [_FakeResponse(200, _COMPLETED)]

    result = await _poll(responses, error_budget_sec=None)

    assert result is not None


async def test_poll_raises_retryable_on_should_retry(clock):
    # A failed envelope flagged should_retry surfaces as RequestRetryableError
    # so the async _post_and_poll wrapper can resubmit with a new request id.
    from azure.ai.finetuningsessions import RequestRetryableError

    envelope = {
        "status": "failed",
        "should_retry": True,
        "retry_after_sec": 5,
        "error": "serving task gone",
    }
    with pytest.raises(RequestRetryableError) as ei:
        await _poll([_FakeResponse(200, envelope)])
    assert ei.value.retry_after_sec == 5.0


async def test_poll_raises_completed_result_unavailable_without_retry(clock):
    from azure.ai.finetuningsessions import OperationResultUnavailableError

    envelope = {
        "status": "failed",
        "error": "Operation completed, but its result is unavailable.",
        "error_code": "operation_completed_result_unavailable",
        # The terminal code must override an accidental retry signal.
        "should_retry": True,
    }

    with pytest.raises(OperationResultUnavailableError) as exc_info:
        await _poll([_FakeResponse(200, envelope)])

    assert exc_info.value.operation_completed is True


# ---------------------------------------------------------------------------
# PendingRequests.poll_result() must resubmit on retryable failures too, so the
# pipelined *_post()/*_async() public surfaces get the same recovery as the
# direct _post_and_poll path (they all route through _poll_with_resubmit).
# ---------------------------------------------------------------------------


def _patch_poll_post(monkeypatch, *, poll_side_effects):
    """Stub _aio_mod._poll (scripted) and _aio_mod._post (records resubmits)."""
    from azure.ai.finetuningsessions import RequestRetryableError

    poll_calls: list[str] = []
    effects = iter(poll_side_effects)

    async def fake_poll(
        self,
        session_id,
        request_id,
        op_type,
        extra_result_fields=None,
        *,
        error_budget_sec=None,
        operation_started_at=None,
        poll_started_at=None,
    ):
        poll_calls.append(request_id)
        outcome = next(effects)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    post_calls: list[str] = []

    async def fake_post(self, subpath, body_model, extra_params=None):
        post_calls.append(subpath)
        return (f"resubmit-{len(post_calls)}", "optim_step")

    monkeypatch.setattr(_aio_mod, "_poll", fake_poll)
    monkeypatch.setattr(_aio_mod, "_post", fake_post)
    return poll_calls, post_calls, RequestRetryableError


async def test_pending_requests_resubmits_then_completes(clock, monkeypatch):
    from azure.ai.finetuningsessions import RequestRetryableError as _RRE

    poll_calls, post_calls, _ = _patch_poll_post(
        monkeypatch,
        poll_side_effects=[
            _RRE("gone", error_code="request_orphaned", retry_after_sec=1.0),
            "RESULT",
        ],
    )

    spec = _aio_mod._PostSpec("req-1", "optim_step", "/sub", object(), None)
    pending = _aio_mod.PendingRequests(None, "session_deadbeef", [spec])

    result = await pending.poll_result()

    assert result == "RESULT"
    # Exactly one resubmit (fresh POST), and the second poll targeted it.
    assert post_calls == ["/sub"]
    assert poll_calls == ["req-1", "resubmit-1"]


async def test_pending_requests_resubmit_exhausts_and_raises(clock, monkeypatch):
    from azure.ai.finetuningsessions import RequestRetryableError as _RRE

    always_retryable = [
        _RRE("gone", error_code="request_orphaned", retry_after_sec=1.0)
        for _ in range(_aio_mod._MAX_REQUEST_RETRIES + 5)
    ]
    poll_calls, post_calls, _ = _patch_poll_post(monkeypatch, poll_side_effects=always_retryable)

    spec = _aio_mod._PostSpec("req-1", "optim_step", "/sub", object(), None)
    pending = _aio_mod.PendingRequests(None, "session_deadbeef", [spec])

    with pytest.raises(_RRE):
        await pending.poll_result()

    # Bounded: initial attempt + _MAX_REQUEST_RETRIES resubmits, no more.
    assert len(post_calls) == _aio_mod._MAX_REQUEST_RETRIES
