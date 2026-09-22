# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Bounded recovery from Envoy JWT rejections before application execution."""
from __future__ import annotations

import asyncio
import itertools
import json
import logging
import threading
from unittest.mock import Mock

import pytest
from azure.core.exceptions import HttpResponseError

from azure.ai.finetuningsessions import _patch as sync
from azure.ai.finetuningsessions.aio import _patch as aio


_SESSION_ID = "session_deadbeef"
_ACCEPTED = {"request_id": "req-accepted", "session_id": _SESSION_ID}
_PENDING = {"status": "pending"}
_COMPLETED = {"status": "completed", "result": {"sequences": []}}
_PROXY_HEADERS = {
    "server": "istio-envoy",
    "www-authenticate": 'Bearer realm="https://loomrl.example/", error="invalid_token"',
    "apim-request-id": "request-correlation",
}


class _Response:
    reason = "Unauthorized"

    def __init__(self, status_code, body, headers=None):
        self.status_code = status_code
        self.headers = dict(headers or {})
        self._text = body if isinstance(body, str) else json.dumps(body)

    def text(self):
        return self._text

    def json(self):
        return json.loads(self._text)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise HttpResponseError(message=self._text, response=self)


def _rejection(body="Jwt verification fails", **kwargs):
    return _Response(401, body, kwargs.pop("headers", _PROXY_HEADERS), **kwargs)


class _Client:
    def __init__(self, posts, polls):
        self.posts = iter(posts)
        self.polls = iter(polls)
        self.requests = []
        self._sample_semaphore = threading.BoundedSemaphore(1)

    def send_request(self, request, **kwargs):
        self.requests.append(request)
        return next(self.posts if request.method == "POST" else self.polls)


class _AsyncClient(_Client):
    def __init__(self, posts, polls):
        super().__init__(posts, polls)
        self._sample_semaphore = asyncio.Semaphore(1)
        self._post_semaphore = asyncio.Semaphore(1)

    async def send_request(self, request, **kwargs):
        return super().send_request(request, **kwargs)


@pytest.fixture(params=[_Client, _AsyncClient], ids=["sync", "async"])
def client_factory(request):
    def create(*, posts=None, polls=None):
        return request.param(
            posts if posts is not None else [_Response(200, _ACCEPTED)],
            polls if polls is not None else [_Response(200, _COMPLETED)],
        )
    return create


@pytest.fixture
def clock(monkeypatch):
    class Clock:
        now = 1000.0
        sleeps = None
        on_sleep = None

        def sleep(self, delay):
            assert delay > 0
            if self.on_sleep is not None:
                self.on_sleep()
            self.sleeps.append(delay)
            self.now += delay

    result = Clock()
    result.sleeps = []

    async def async_sleep(delay):
        result.sleep(delay)

    monkeypatch.setattr(sync._time, "monotonic", lambda: result.now)
    monkeypatch.setattr(sync._time, "sleep", result.sleep)
    monkeypatch.setattr(aio.asyncio, "sleep", async_sleep)
    monkeypatch.setattr(sync._random, "random", lambda: 0.0)
    return result


async def _sample(client):
    if isinstance(client, _AsyncClient):
        return await aio.sample(
            client, _SESSION_ID, [1, 2], sync.SamplingParams(), checkpoint_id="ckpt-1"
        )
    session = sync.FineTuningSession.__new__(sync.FineTuningSession)
    session.session_id = _SESSION_ID
    session._client = client
    return session.sample([1, 2], sync.SamplingParams(), checkpoint_id="ckpt-1")


def _requests(client, method):
    return [request for request in client.requests if request.method == method]


@pytest.mark.asyncio
@pytest.mark.parametrize("verbose", [False, True])
@pytest.mark.parametrize("body", [
    {"error": {"code": "Unauthorized", "message": "Token expired"}},
    "Jwt verification fails",
], ids=["json", "plaintext"])
async def test_sync_submit_error_logging_preserves_json_body(clock, monkeypatch, caplog, verbose, body):
    response = _Response(401, body)
    response.json = Mock(wraps=response.json)
    client = _Client([response], [])
    monkeypatch.setattr(sync, "VERBOSE_HTTP", verbose)

    with caplog.at_level(logging.INFO):
        with pytest.raises(HttpResponseError) as caught:
            await _sample(client)

    assert caught.value.response is response
    response.json.assert_called_once_with()
    response_logs = [
        record.getMessage() for record in caplog.records
        if record.getMessage().startswith("[HTTP] <-- POST")
    ]
    expected = f"[HTTP] <-- POST /fine_tuning/sessions/{_SESSION_ID}/sample  status=401"
    if isinstance(body, dict):
        expected += "\n" + json.dumps(body, indent=2)
    assert response_logs == ([expected] if verbose else [])
    assert len(_requests(client, "POST")) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("verbose", [False, True])
async def test_sync_submit_success_logs_body_parsed_once(clock, monkeypatch, caplog, verbose):
    response = _Response(200, _ACCEPTED)
    response.json = Mock(wraps=response.json)
    client = _Client([response], [_Response(200, _COMPLETED)])
    monkeypatch.setattr(sync, "VERBOSE_HTTP", verbose)

    with caplog.at_level(logging.INFO):
        result = await _sample(client)

    assert result.operation_id == "req-accepted"
    response.json.assert_called_once_with()
    response_logs = [
        record.getMessage() for record in caplog.records
        if record.getMessage().startswith("[HTTP] <-- POST")
    ]
    expected = (
        f"[HTTP] <-- POST /fine_tuning/sessions/{_SESSION_ID}/sample  status=200\n"
        + json.dumps(_ACCEPTED, indent=2)
    )
    assert response_logs == ([expected] if verbose else [])


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["submit", "poll"])
@pytest.mark.parametrize("failure_seconds", [34, 90])
async def test_recovers_after_transient_proxy_failure(client_factory, clock, stage, failure_seconds):
    started = clock.now

    def responses():
        while clock.now - started < failure_seconds:
            yield _rejection()
        yield _Response(200, _ACCEPTED if stage == "submit" else _COMPLETED)

    client = client_factory(**{"posts" if stage == "submit" else "polls": responses()})
    result = await _sample(client)

    assert result.operation_id == "req-accepted"
    assert failure_seconds <= clock.now - started <= 120
    posts = _requests(client, "POST")
    polls = _requests(client, "GET")
    assert len({request.url for request in posts}) == 1
    assert len({request.content for request in posts}) == 1
    assert all("/request/req-accepted?" in request.url for request in polls)
    assert len(polls if stage == "submit" else posts) == 1


@pytest.mark.asyncio
async def test_poll_recovers_after_long_healthy_wait(client_factory, clock):
    client = client_factory(polls=[
        *[_Response(200, _PENDING) for _ in range(20)],
        _rejection(),
        _rejection(),
        _Response(200, _COMPLETED),
    ])

    result = await _sample(client)

    assert result.operation_id == "req-accepted"
    assert clock.now - 1000 > 120
    assert len(_requests(client, "POST")) == 1
    assert len(_requests(client, "GET")) == 23
    assert clock.sleeps[-2:] == [1.0, 2.0]


@pytest.mark.asyncio
async def test_healthy_poll_resets_proxy_retry_window(client_factory, clock):
    client = client_factory(polls=[
        *[_rejection() for _ in range(10)],
        _Response(200, _PENDING),
        *[_rejection() for _ in range(10)],
        _Response(200, _COMPLETED),
    ])

    result = await _sample(client)

    assert result.operation_id == "req-accepted"
    assert clock.now - 1000 == 151
    assert len(_requests(client, "POST")) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("prior_error", [False, True], ids=["fresh-budget", "expired-budget"])
async def test_proxy_poll_recovers_despite_shorter_error_budget(
    client_factory, clock, monkeypatch, prior_error
):
    monkeypatch.setattr(sync, "_DEFAULT_OPERATION_TIMEOUT_SEC", 2.0)
    monkeypatch.setattr(aio, "_DEFAULT_OPERATION_TIMEOUT_SEC", 2.0)

    def polls():
        if prior_error:
            yield _Response(503, {"message": "unavailable"})
            clock.now += 3
        jwt_started = clock.now
        while clock.now - jwt_started < 90:
            yield _rejection()
        yield _Response(200, _COMPLETED)

    client = client_factory(polls=polls())
    result = await _sample(client)

    assert result.operation_id == "req-accepted"
    assert clock.now - 1000 == (99 if prior_error else 95)
    assert len(_requests(client, "POST")) == 1


@pytest.mark.asyncio
async def test_proxy_retries_do_not_reset_existing_error_budget(client_factory, clock, monkeypatch):
    monkeypatch.setattr(sync, "_DEFAULT_OPERATION_TIMEOUT_SEC", 2.0)
    monkeypatch.setattr(aio, "_DEFAULT_OPERATION_TIMEOUT_SEC", 2.0)
    client = client_factory(polls=[
        _Response(503, {"message": "unavailable"}),
        _rejection(),
        _rejection(),
        _Response(503, {"message": "unavailable"}),
    ])

    with pytest.raises(TimeoutError, match="HTTP 503"):
        await _sample(client)

    assert clock.now - 1000 == 4
    assert len(_requests(client, "POST")) == 1
    assert len(_requests(client, "GET")) == 4


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["submit", "poll"])
async def test_json_wrapped_proxy_rejection_recovers(client_factory, clock, stage):
    responses = [
        _rejection(body={"error": {
            "code": "Unauthorized",
            "message": "Jwt verification fails",
        }}),
        _Response(200, _ACCEPTED if stage == "submit" else _COMPLETED),
    ]
    client = client_factory(**{"posts" if stage == "submit" else "polls": responses})

    result = await _sample(client)

    assert result.operation_id == "req-accepted"
    assert clock.sleeps == [1]


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["submit", "poll"])
@pytest.mark.parametrize("error_budget_sec", [None, 2.0])
async def test_persistent_rejection_raises_original_http_error(
    client_factory, clock, monkeypatch, stage, error_budget_sec
):
    monkeypatch.setattr(sync, "_DEFAULT_OPERATION_TIMEOUT_SEC", error_budget_sec)
    monkeypatch.setattr(aio, "_DEFAULT_OPERATION_TIMEOUT_SEC", error_budget_sec)
    rejection = _rejection()
    client = client_factory(**{
        "posts" if stage == "submit" else "polls": itertools.repeat(rejection),
    })
    started = clock.now

    with pytest.raises(HttpResponseError) as caught:
        await _sample(client)

    assert caught.value.status_code == 401
    assert caught.value.response is rejection
    assert clock.now - started == 120
    assert len(_requests(client, "POST" if stage == "submit" else "GET")) <= 18
    assert len(_requests(client, "GET" if stage == "submit" else "POST")) == (
        0 if stage == "submit" else 1
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["submit", "poll"])
@pytest.mark.parametrize(
    "response",
    [
        _Response(401, {"error": {"code": "Unauthorized", "message": "Token expired"}}),
        _rejection(body="Jwt is expired"),
        _rejection(headers={}),
        _rejection(headers={**_PROXY_HEADERS, "server": "application"}),
        _rejection(headers={**_PROXY_HEADERS, "www-authenticate": "Bearer"}),
        _rejection(body="upstream error: Jwt verification fails"),
        _rejection(body="{invalid json"),
        _Response(403, "Jwt verification fails", _PROXY_HEADERS),
    ],
    ids=[
        "ordinary-401", "expired-token", "no-proxy-headers", "application-response",
        "no-invalid-token-challenge", "substring-only", "malformed-json", "forbidden",
    ],
)
async def test_other_authentication_errors_are_not_retried(
    client_factory, clock, stage, response
):
    client = client_factory(**{"posts" if stage == "submit" else "polls": [response]})

    with pytest.raises(HttpResponseError) as caught:
        await _sample(client)

    assert caught.value.response is response
    assert len(_requests(client, "POST" if stage == "submit" else "GET")) == 1
    assert clock.sleeps == []


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["submit", "poll"])
@pytest.mark.parametrize(
    "challenge",
    [
        'Bearer x-error="invalid_token"',
        'Bearer x.error="invalid_token"',
        'Bearer error="expired", x-error="invalid_token"',
        'Bearer realm="example,error="invalid_token"',
        'Bearer error="invalid_token"trailing',
        'Bearer realm="example, error=\\"invalid_token\\""',
        r'Bearer error="invalid_token\"',
        'Bearer error="invalid_token", realm="unfinished',
    ],
    ids=[
        "hyphenated-name", "dotted-name", "extension-after-error",
        "malformed-quoted-realm", "trailing-value", "quoted-realm",
        "unclosed-escaped-value", "unclosed-realm",
    ],
)
async def test_invalid_token_lookalikes_are_not_retried(
    client_factory, clock, stage, challenge
):
    response = _rejection(headers={**_PROXY_HEADERS, "www-authenticate": challenge})
    client = client_factory(**{"posts" if stage == "submit" else "polls": [response]})

    with pytest.raises(HttpResponseError) as caught:
        await _sample(client)

    assert caught.value.response is response
    assert len(_requests(client, "POST" if stage == "submit" else "GET")) == 1
    assert clock.sleeps == []


@pytest.mark.asyncio
async def test_terminal_operation_error_is_not_replayed(client_factory, clock):
    client = client_factory(polls=[_Response(200, {
        "status": "failed",
        "error": "Jwt verification fails",
        "should_retry": False,
    })])

    with pytest.raises(RuntimeError, match="Jwt verification fails"):
        await _sample(client)

    assert len(_requests(client, "POST")) == 1
    assert len(_requests(client, "GET")) == 1
    assert clock.sleeps == []


@pytest.mark.parametrize(
    "body",
    [
        "Jwt verification fails",
        {"error": {"code": "Unauthorized", "message": "Jwt verification fails"}},
        {"message": "Jwt verification fails"},
    ],
)
def test_recognizes_plain_and_json_proxy_errors_with_case_insensitive_headers(body):
    response = _rejection(
        body=body,
        headers={name.upper(): value for name, value in _PROXY_HEADERS.items()},
    )
    assert sync._is_proxy_jwt_rejection(response)


@pytest.mark.parametrize(
    "challenge",
    [
        'Bearer error="invalid_token"',
        'Bearer error="invalid_token", realm="example"',
        'Bearer realm="example,with=punctuation", error="invalid_token"',
        r'Bearer realm="example, \"quoted\"", error="invalid_token"',
        'bEaReR\tErRoR \t= \t"invalid_token"',
        'Basic realm="legacy", Bearer error="invalid_token"',
    ],
)
def test_recognizes_exact_error_parameter_in_valid_challenges(challenge):
    response = _rejection(headers={**_PROXY_HEADERS, "www-authenticate": challenge})

    assert sync._is_proxy_jwt_rejection(response)


@pytest.mark.asyncio
async def test_retry_budget_starts_at_first_rejection_and_resets_on_success(client_factory, clock):
    def polls():
        clock.now += 10 * 60 * 60
        yield _rejection()
        clock.now += 120
        yield _Response(200, _PENDING)
        clock.now += 10 * 60 * 60
        yield _rejection()
        yield _Response(200, _COMPLETED)

    client = client_factory(polls=polls())
    result = await _sample(client)

    assert result.operation_id == "req-accepted"
    assert clock.sleeps == [1, 1, 1]
    assert len(_requests(client, "POST")) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["submit", "poll"])
async def test_jitter_is_clamped_to_remaining_retry_window(client_factory, clock, monkeypatch, stage):
    monkeypatch.setattr(sync._random, "random", lambda: 1.0)
    rejection = _rejection()
    started = clock.now

    def responses():
        yield rejection
        clock.now = started + 119.75
        yield rejection
        yield rejection

    client = client_factory(**{"posts" if stage == "submit" else "polls": responses()})

    with pytest.raises(HttpResponseError) as caught:
        await _sample(client)

    assert caught.value.response is rejection
    assert clock.sleeps == [1.25, 0.25]
    assert clock.now - started == 120
    assert len(_requests(client, "POST" if stage == "submit" else "GET")) == 3


@pytest.mark.asyncio
async def test_other_errors_do_not_reset_proxy_retry_window(client_factory, clock):
    rejection = _rejection()

    def polls():
        yield rejection
        clock.now += 60
        yield _Response(503, {"message": "unavailable"})
        clock.now += 60
        yield rejection

    client = client_factory(polls=polls())

    with pytest.raises(HttpResponseError) as caught:
        await _sample(client)

    assert caught.value.response is rejection
    assert clock.now - 1000 == 122
    assert len(_requests(client, "GET")) == 3
    assert len(_requests(client, "POST")) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["submit", "poll"])
async def test_retry_logs_correlation_without_credentials(client_factory, clock, caplog, stage):
    response = _rejection(headers={
        **_PROXY_HEADERS,
        "authorization": "Bearer test-secret-not-for-logs",
    })
    client = client_factory(**{
        "posts" if stage == "submit" else "polls": itertools.repeat(response),
    })
    with caplog.at_level(logging.WARNING):
        with pytest.raises(HttpResponseError) as caught:
            await _sample(client)
    assert caught.value.response is response
    assert "request-correlation" in caplog.text
    assert "exhausted" in caplog.text
    assert "test-secret-not-for-logs" not in caplog.text


@pytest.mark.asyncio
async def test_proxy_retries_do_not_spend_async_sample_fault_budget(clock):
    client = _AsyncClient(
        [
            *[_rejection() for _ in range(4)],
            _Response(500, {"message": "transient"}),
            _Response(500, {"message": "transient"}),
            _Response(200, _ACCEPTED),
        ],
        [_Response(200, _COMPLETED)],
    )

    result = await _sample(client)

    assert result.operation_id == "req-accepted"
    assert len(_requests(client, "POST")) == 7
    assert len(_requests(client, "GET")) == 1


@pytest.mark.asyncio
async def test_async_submit_releases_post_permit_during_retry(clock):
    client = _AsyncClient(
        [_rejection(), _Response(200, _ACCEPTED)],
        [_Response(200, _COMPLETED)],
    )

    def check_permits():
        assert not client._post_semaphore.locked()
        assert client._sample_semaphore.locked()

    clock.on_sleep = check_permits
    await _sample(client)
    assert clock.sleeps == [1]
    assert not client._sample_semaphore.locked()


@pytest.mark.asyncio
async def test_cancellation_during_retry_releases_permits(clock, monkeypatch):
    client = _AsyncClient([_rejection()], [])

    async def cancel(delay):
        raise asyncio.CancelledError

    monkeypatch.setattr(aio.asyncio, "sleep", cancel)
    with pytest.raises(asyncio.CancelledError):
        await _sample(client)
    assert not client._sample_semaphore.locked()
    assert not client._post_semaphore.locked()
    assert len(client.requests) == 1
