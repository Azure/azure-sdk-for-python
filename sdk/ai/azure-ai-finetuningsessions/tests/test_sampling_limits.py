# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Tests for the SDK sampling rate-limit handling.

Covers the two behaviors added for Redis-based server rate limiting:

1. A sample submit throttled with HTTP 429 is retried in place (honoring
   ``Retry-After`` + jitter) until a wall-clock throttle deadline, then raises
   the typed ``RateLimitedError`` (a ``NoCapacityError`` subclass). A 429 that
   clears before the deadline proceeds normally.
2. ``sample()`` holds a lifecycle-scoped semaphore across the FULL submit+poll
   lifecycle, bounding overall concurrent samples (not just the in-flight POST).
"""

from __future__ import annotations

import asyncio
import threading
from types import SimpleNamespace

import pytest

from azure.ai.finetuning_sessions._exceptions import (
    _classify_http_error,
    NoCapacityError,
    RateLimitedError,
)
from azure.ai.finetuning_sessions import _patch as _patch_mod
from azure.ai.finetuning_sessions.aio import _patch as _aio_mod
from azure.ai.finetuning_sessions.aio._patch import _post, _post_sample, sample

# ---------------------------------------------------------------------------
# Exception typing / classification
# ---------------------------------------------------------------------------


def test_rate_limited_is_no_capacity_subclass():
    """RateLimitedError must remain catchable as NoCapacityError (back-compat)."""
    assert issubclass(RateLimitedError, NoCapacityError)


def test_classify_429_uses_body_retry_after():
    exc = _classify_http_error(429, {"retry_after_sec": 12, "reason": "budget"})
    assert isinstance(exc, RateLimitedError)
    assert exc.retry_after_sec == 12.0
    assert exc.reason == "budget"


def test_classify_429_falls_back_to_header_retry_after():
    exc = _classify_http_error(429, {}, response=_FakeResponse(429, retry_after="7"))
    assert isinstance(exc, RateLimitedError)
    assert exc.retry_after_sec == 7.0
    assert exc.reason == "rate_limited"


# ---------------------------------------------------------------------------
# Test doubles
# ---------------------------------------------------------------------------


class _FakeResponse:
    reason = None  # azure HttpResponseError reads this when response is passed

    def __init__(self, status_code, body=None, retry_after=None):
        self.status_code = status_code
        self._body = body or {}
        self.headers = {} if retry_after is None else {"Retry-After": retry_after}

    def json(self):
        return self._body

    def raise_for_status(self):
        if self.status_code >= 400:  # pragma: no cover - not expected in these tests
            raise AssertionError(f"unexpected raise_for_status on {self.status_code}")


class _FakeAsyncClient:
    """Minimal client whose async ``send_request`` yields scripted responses."""

    def __init__(self, responses):
        self._responses = iter(responses)
        self.calls = 0

    async def send_request(self, req, **kwargs):
        self.calls += 1
        item = next(self._responses)
        if isinstance(item, BaseException):
            raise item
        return item


@pytest.fixture
def clock(monkeypatch):
    """Deterministic monotonic clock; ``asyncio.sleep`` advances it by its arg."""

    class _Clock:
        now = 1000.0

    c = _Clock()

    async def _fake_sleep(dt):
        c.now += dt

    monkeypatch.setattr(_aio_mod._time, "monotonic", lambda: c.now)
    monkeypatch.setattr(_aio_mod.asyncio, "sleep", _fake_sleep)
    return c


# ---------------------------------------------------------------------------
# 429 throttle retry loop (async _post)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_throttled_submit_retries_then_succeeds(clock):
    """429 that clears before the deadline is retried in place, then succeeds."""
    client = _FakeAsyncClient(
        [
            _FakeResponse(429, retry_after="2"),
            _FakeResponse(429, retry_after="2"),
            _FakeResponse(200, {"request_id": "req-9"}),
        ]
    )
    request_id, _op = await _post_sample(
        client,
        "/fine_tuning_sessions/session_deadbeef/sample",
        _aio_mod.SamplingParams(),
    )
    assert request_id == "req-9"
    assert client.calls == 3


@pytest.mark.asyncio
async def test_throttled_submit_raises_rate_limited_past_deadline(clock, monkeypatch):
    """A sustained 429 past the throttle deadline raises RateLimitedError."""
    monkeypatch.setattr(_aio_mod, "_SAMPLE_THROTTLE_TIMEOUT_SEC", 10)
    client = _FakeAsyncClient([_FakeResponse(429, {"reason": "budget"}, retry_after="5") for _ in range(100)])
    with pytest.raises(RateLimitedError):
        await _post_sample(
            client,
            "/fine_tuning_sessions/session_deadbeef/sample",
            _aio_mod.SamplingParams(),
        )


@pytest.mark.asyncio
async def test_throttle_sleep_clamped_to_remaining_deadline(clock, monkeypatch):
    """A huge Retry-After must not overshoot the wall-clock throttle cap.

    Regression: a 429 carrying ``Retry-After: 3600`` with a 10s cap previously
    slept the full hour before rechecking the deadline. The sleep must be clamped
    to the remaining budget so RateLimitedError is raised near the cap, not an
    hour late.
    """
    monkeypatch.setattr(_aio_mod, "_SAMPLE_THROTTLE_TIMEOUT_SEC", 10)
    start = clock.now
    client = _FakeAsyncClient([_FakeResponse(429, {"reason": "budget"}, retry_after="3600") for _ in range(100)])
    with pytest.raises(RateLimitedError):
        await _post_sample(
            client,
            "/fine_tuning_sessions/session_deadbeef/sample",
            _aio_mod.SamplingParams(),
        )
    # The loop may sleep once (clamped to <= the 10s remaining budget) before the
    # next iteration crosses the deadline; total elapsed must stay near the cap,
    # not balloon to the 3600s Retry-After value.
    assert clock.now - start <= 20.0


@pytest.mark.asyncio
async def test_non_sampling_429_is_not_held_in_place(clock):
    """On a non-sample endpoint, 429 is a normal fault (bounded retries)."""
    client = _FakeAsyncClient([_FakeResponse(429, {"reason": "budget"}) for _ in range(10)])
    with pytest.raises(RateLimitedError):
        await _post(client, "/fine_tuning_sessions/session_deadbeef/optim_step", _aio_mod.SamplingParams())
    # max_retries=2 -> at most 3 attempts before giving up (not held forever).
    assert client.calls <= 3


@pytest.mark.asyncio
async def test_sample_submit_retries_transient_5xx_then_succeeds(clock):
    """A transient 5xx during sample submit is retried (bounded), then succeeds.

    Regression: the dedicated ``_post_sample`` path must keep the same bounded
    fault-retry behavior as ``_post`` for non-429 transient failures, not fail
    the sample on the first blip.
    """
    client = _FakeAsyncClient(
        [
            _FakeResponse(500, {"reason": "boom"}),
            _FakeResponse(200, {"request_id": "req-ok"}),
        ]
    )
    request_id, _op = await _post_sample(
        client,
        "/fine_tuning_sessions/session_deadbeef/sample",
        _aio_mod.SamplingParams(),
    )
    assert request_id == "req-ok"
    assert client.calls == 2


@pytest.mark.asyncio
async def test_sample_submit_retries_transient_network_error_then_succeeds(clock):
    """A transient ServiceResponseError during sample submit is retried."""
    from azure.core.exceptions import ServiceResponseError

    client = _FakeAsyncClient(
        [
            ServiceResponseError("connection reset"),
            _FakeResponse(200, {"request_id": "req-net"}),
        ]
    )
    request_id, _op = await _post_sample(
        client,
        "/fine_tuning_sessions/session_deadbeef/sample",
        _aio_mod.SamplingParams(),
    )
    assert request_id == "req-net"
    assert client.calls == 2


# ---------------------------------------------------------------------------
# Lifecycle-scoped semaphore (async sample)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_sample_bounds_concurrency_over_full_lifecycle(monkeypatch):
    """sample() holds the lifecycle semaphore across submit+poll, so no more
    than ``_MAX_CONCURRENT_SAMPLES`` samples run their lifecycle at once."""
    monkeypatch.setattr(_aio_mod, "_MAX_CONCURRENT_SAMPLES", 2)

    state = {"live": 0, "peak": 0}
    gate = asyncio.Event()

    async def _fake_post_sample(self, subpath, body, extra_params=None):
        state["live"] += 1
        state["peak"] = max(state["peak"], state["live"])
        await gate.wait()  # hold the permit until released
        return "req", "sample"

    async def _fake_poll(
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
        state["live"] -= 1
        return object()

    monkeypatch.setattr(_aio_mod, "_post_sample", _fake_post_sample)
    monkeypatch.setattr(_aio_mod, "_poll", _fake_poll)

    client = _FakeAsyncClient([])

    async def _one():
        return await sample(
            client,
            "session_deadbeef",
            [1, 2, 3],
            _aio_mod.SamplingParams(),
            checkpoint_id="ckpt-1",
        )

    tasks = [asyncio.create_task(_one()) for _ in range(6)]
    await asyncio.sleep(0.05)  # let tasks reach the gate
    assert state["peak"] <= 2  # bounded by the lifecycle semaphore
    gate.set()
    await asyncio.gather(*tasks)
    assert state["peak"] <= 2


@pytest.mark.asyncio
async def test_sample_posts_to_sample_endpoint(monkeypatch):
    """async sample() routes to ``_post_sample`` on the ``/sample`` endpoint,
    which is what holds the throttle-in-place backpressure."""
    seen = {}

    async def _fake_post_sample(self, subpath, body, extra_params=None):
        seen["subpath"] = subpath
        return "req", "sample"

    async def _fake_poll(
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
        return object()

    monkeypatch.setattr(_aio_mod, "_post_sample", _fake_post_sample)
    monkeypatch.setattr(_aio_mod, "_poll", _fake_poll)

    client = _FakeAsyncClient([])
    await sample(client, "session_deadbeef", [1], _aio_mod.SamplingParams(), checkpoint_id="c")
    assert seen["subpath"].endswith("/sample")


@pytest.mark.asyncio
async def test_sample_resubmits_through_throttled_post_path(clock, monkeypatch):
    """A retryable sample failure reuses _post_sample under one semaphore permit."""
    from azure.ai.finetuning_sessions import RequestRetryableError

    monkeypatch.setattr(_aio_mod, "_MAX_CONCURRENT_SAMPLES", 1)
    post_calls = []
    poll_calls = []

    async def _fake_post_sample(self, subpath, body, extra_params=None):
        assert self._sample_semaphore.locked()
        post_calls.append((subpath, extra_params))
        return f"req-{len(post_calls)}", "sample"

    async def _generic_post_must_not_run(*args, **kwargs):
        raise AssertionError("sample resubmission bypassed _post_sample")

    async def _fake_poll(
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
        assert self._sample_semaphore.locked()
        poll_calls.append(request_id)
        if len(poll_calls) == 1:
            raise RequestRetryableError(
                "serving task gone",
                error_code="request_orphaned",
                retry_after_sec=1,
            )
        return "RESULT"

    monkeypatch.setattr(_aio_mod, "_post_sample", _fake_post_sample)
    monkeypatch.setattr(_aio_mod, "_post", _generic_post_must_not_run)
    monkeypatch.setattr(_aio_mod, "_poll", _fake_poll)

    client = _FakeAsyncClient([])
    result = await sample(
        client,
        "session_deadbeef",
        [1],
        _aio_mod.SamplingParams(),
        checkpoint_id="ckpt-1",
    )

    assert result == "RESULT"
    assert poll_calls == ["req-1", "req-2"]
    assert [call[1] for call in post_calls] == [
        {"checkpoint_id": "ckpt-1"},
        {"checkpoint_id": "ckpt-1"},
    ]


# ---------------------------------------------------------------------------
# Sync FineTuningSession sample endpoint
# ---------------------------------------------------------------------------


def test_sync_sample_posts_to_sample_endpoint():
    """Sync FineTuningSession.sample() routes to the ``/sample`` endpoint."""
    from azure.ai.finetuning_sessions._patch import FineTuningSession

    # Bypass __init__ (heartbeat thread / network) — exercise sample() directly.
    session = object.__new__(FineTuningSession)
    session.session_id = "session_deadbeef"
    session._client = SimpleNamespace(_sample_semaphore=threading.BoundedSemaphore(1))

    seen = {}

    def _fake_post_and_poll(subpath, body, extra_params=None, extra_result_fields=None):
        seen["subpath"] = subpath
        return object()

    session._post_and_poll = _fake_post_and_poll
    session.sample(
        prompt_tokens=[1, 2],
        sampling_params=_patch_mod.SamplingParams(),
        checkpoint_id="ckpt-1",
    )
    assert seen["subpath"].endswith("/sample")


def test_sync_sample_preserves_structured_prompt():
    """Sync sampling forwards multimodal ModelInput chunks unchanged."""
    from azure.ai.finetuning_sessions._patch import FineTuningSession
    from azure.ai.finetuning_sessions.models import ImageChunk, ModelInput, ModelInputChunk

    session = object.__new__(FineTuningSession)
    session.session_id = "model_s1"
    session._client = SimpleNamespace(_sample_semaphore=threading.BoundedSemaphore(1))
    prompt = ModelInput(
        chunks=[
            ModelInputChunk(tokens=[1]),
            ImageChunk(data=b"\xff\xd8\xffjpeg", format="jpeg", expected_tokens=4),
            ModelInputChunk(tokens=[2]),
        ]
    )
    seen = {}

    def _fake_post_and_poll(subpath, body, extra_params=None, extra_result_fields=None):
        seen["prompt"] = body.prompt
        return object()

    session._post_and_poll = _fake_post_and_poll
    session.sample(
        prompt_tokens=prompt,
        sampling_params=_patch_mod.SamplingParams(),
        checkpoint_id="ckpt-1",
    )

    assert seen["prompt"] is prompt
