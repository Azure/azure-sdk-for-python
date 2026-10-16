# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""Regression coverage for Retry-After waits against the operation timeout.

The transport is purely in-memory. Long delays are *recorded*, not slept,
so these tests need neither an Azure account nor minutes of wall-clock time.
"""

import asyncio
from types import SimpleNamespace

import pytest

from azure.core.exceptions import ServiceResponseTimeoutError
from azure.core.pipeline import AsyncPipeline, Pipeline
from azure.core.pipeline.policies import AsyncRetryPolicy, RetryPolicy
from azure.core.pipeline.transport import HttpRequest


class RecordingTransport:
    def __init__(self, status_code, headers):
        self.calls = 0
        self.sleeps = []
        self.status_code = status_code
        self.headers = headers

    def open(self):
        pass

    def close(self):
        pass

    def send(self, request, **kwargs):
        self.calls += 1
        if self.calls == 1:
            return SimpleNamespace(status_code=self.status_code, headers=self.headers)
        return SimpleNamespace(status_code=200, headers={})

    def sleep(self, seconds):
        self.sleeps.append(seconds)


class AsyncRecordingTransport(RecordingTransport):
    async def send(self, request, **kwargs):
        return super().send(request, **kwargs)

    async def sleep(self, seconds):
        self.sleeps.append(seconds)


@pytest.mark.parametrize("header,value", [
    ("Retry-After", "120"),
    ("retry-after-ms", "120000"),
    ("x-ms-retry-after-ms", "120000"),
])
@pytest.mark.parametrize("retry_total", [1, 3])
def test_retry_after_exceeding_timeout_does_not_sleep_sync(header, value, retry_total):
    transport = RecordingTransport(429, {header: value})
    pipeline = Pipeline(transport, [RetryPolicy(timeout=1, retry_total=retry_total)])

    with pytest.raises(ServiceResponseTimeoutError):
        pipeline.run(HttpRequest("GET", "https://example.invalid"))

    assert transport.calls == 1
    assert transport.sleeps == []


@pytest.mark.parametrize("header,value", [
    ("Retry-After", "120"),
    ("retry-after-ms", "120000"),
    ("x-ms-retry-after-ms", "120000"),
])
@pytest.mark.parametrize("retry_total", [1, 3])
def test_retry_after_exceeding_timeout_does_not_sleep_async(header, value, retry_total):
    transport = AsyncRecordingTransport(429, {header: value})
    pipeline = AsyncPipeline(transport, [AsyncRetryPolicy(timeout=1, retry_total=retry_total)])

    async def run():
        await pipeline.run(HttpRequest("GET", "https://example.invalid"))

    with pytest.raises(ServiceResponseTimeoutError):
        asyncio.run(run())

    assert transport.calls == 1
    assert transport.sleeps == []


@pytest.mark.parametrize("async_mode", [False, True])
def test_retry_after_within_timeout_still_retries(async_mode):
    transport = (
        AsyncRecordingTransport(429, {"Retry-After": "0.25"})
        if async_mode else RecordingTransport(429, {"Retry-After": "0.25"})
    )
    request = HttpRequest("GET", "https://example.invalid")

    if async_mode:
        response = asyncio.run(
            AsyncPipeline(transport, [AsyncRetryPolicy(timeout=1, retry_total=1)]).run(request)
        )
    else:
        response = Pipeline(transport, [RetryPolicy(timeout=1, retry_total=1)]).run(request)

    assert response.http_response.status_code == 200
    assert transport.calls == 2
    assert transport.sleeps == [0.25]


@pytest.mark.parametrize("async_mode", [False, True])
def test_successful_response_ignores_retry_after(async_mode):
    transport = (
        AsyncRecordingTransport(200, {"Retry-After": "120"})
        if async_mode else RecordingTransport(200, {"Retry-After": "120"})
    )
    request = HttpRequest("GET", "https://example.invalid")

    if async_mode:
        response = asyncio.run(
            AsyncPipeline(transport, [AsyncRetryPolicy(timeout=1, retry_total=1)]).run(request)
        )
    else:
        response = Pipeline(transport, [RetryPolicy(timeout=1, retry_total=1)]).run(request)

    assert response.http_response.status_code == 200
    assert transport.calls == 1
    assert transport.sleeps == []
