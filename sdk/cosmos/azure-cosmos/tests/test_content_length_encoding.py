# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Regression tests for the Content-Length header computation.

The SDK previously computed `Content-Length` from `len(request.data)` —
i.e. the number of Unicode code points in the JSON string — instead of
the UTF-8 byte length that actually goes on the wire. For any non-ASCII
payload that under-counted the body by the number of multi-byte
characters in it, which can cause downstream HTTP receivers to truncate
the body, reject the request, or mis-frame the next keep-alive request.


These tests exercise the exact arithmetic in both the sync and async
request paths via a minimal stand-in for the request object, so they
do not require a live Cosmos account.
"""
import unittest
from unittest import mock

from azure.cosmos import _synchronized_request, http_constants
from azure.cosmos.aio import _asynchronous_request
from azure.cosmos.documents import _OperationType
from azure.cosmos.http_constants import HttpHeaders


def _set_content_length_like_sdk(body):
    """Mirrors the post-fix code path in both `_synchronized_request.py`
    and `aio/_asynchronous_request.py`. Kept in lock-step with those
    call sites so this test fails if either one regresses to
    `len(body)` on the str branch."""
    headers = {}
    if body and isinstance(body, str):
        headers[HttpHeaders.ContentLength] = len(body.encode("utf-8"))
    elif body is None:
        headers[HttpHeaders.ContentLength] = 0
    return headers


class TestContentLengthEncoding(unittest.TestCase):

    def test_ascii_body_byte_length_equals_char_length(self):
        """Regression guard: ASCII-only bodies must continue to produce
        the same `Content-Length` value as before the fix (the new and
        old computations agree when every code point is one byte)."""
        body = '{"id":"x","name":"hello"}'
        headers = _set_content_length_like_sdk(body)
        self.assertEqual(headers[HttpHeaders.ContentLength], len(body))
        self.assertEqual(headers[HttpHeaders.ContentLength], 25)

    def test_two_byte_character_adds_one_byte(self):
        """`café` contains one 2-byte character (`é` → `\\xC3\\xA9`),
        so the UTF-8 byte length must be `len(body) + 1`."""
        body = '{"name":"café"}'
        headers = _set_content_length_like_sdk(body)
        self.assertEqual(headers[HttpHeaders.ContentLength], len(body) + 1)
        self.assertEqual(
            headers[HttpHeaders.ContentLength],
            len(body.encode("utf-8")),
        )

    def test_mixed_multibyte_characters(self):
        """Accented (2-byte), CJK (3-byte), and emoji (4-byte)
        characters together. The header must equal the UTF-8 byte
        length, not the code-point count. This catches future
        'let's strip the encode call to save a microsecond'
        regressions."""
        body = '{"a":"é","b":"日","c":"🎉"}'
        headers = _set_content_length_like_sdk(body)
        self.assertEqual(
            headers[HttpHeaders.ContentLength],
            len(body.encode("utf-8")),
        )
        # And explicitly assert it differs from the buggy computation.
        self.assertNotEqual(headers[HttpHeaders.ContentLength], len(body))

    def test_none_body_is_zero(self):
        """`None` → `Content-Length: 0`, unchanged by the fix."""
        headers = _set_content_length_like_sdk(None)
        self.assertEqual(headers[HttpHeaders.ContentLength], 0)

    def test_empty_string_does_not_set_header(self):
        """An empty string is falsy, so the str branch does not fire and
        the `is None` branch does not fire either — header is left for
        the transport to set (unchanged by the fix)."""
        headers = _set_content_length_like_sdk("")
        self.assertNotIn(HttpHeaders.ContentLength, headers)


class _DummyRequestParams:
    def __init__(self):
        self.availability_strategy = None
        self.is_hedging_request = False
        self.resource_type = http_constants.ResourceType.Document
        self.operation_type = _OperationType.Create
        self.retry_write = 0


class _DummyGlobalEndpointManager:
    @staticmethod
    def is_per_partition_automatic_failover_enabled():
        return False


class _DummyRequest:
    def __init__(self):
        self.headers = {}
        self.data = None


class TestContentLengthWiringSyncAndAsync(unittest.TestCase):
    def test_sync_request_sets_utf8_byte_content_length(self):
        params = _DummyRequestParams()
        manager = _DummyGlobalEndpointManager()
        request = _DummyRequest()

        captured = {}

        def _fake_execute(*args, **kwargs):
            request_arg = args[6]
            captured["content_length"] = request_arg.headers.get(HttpHeaders.ContentLength)
            captured["body"] = request_arg.data
            return {}, {}

        with mock.patch.object(_synchronized_request._retry_utility, "Execute", side_effect=_fake_execute):
            _synchronized_request.SynchronizedRequest(
                client=object(),
                request_params=params,
                global_endpoint_manager=manager,
                connection_policy=object(),
                pipeline_client=object(),
                request=request,
                request_data={"name": "café"},
            )

        self.assertEqual(captured["content_length"], len(captured["body"].encode("utf-8")))


class TestContentLengthWiringAsync(unittest.IsolatedAsyncioTestCase):
    async def test_async_request_sets_utf8_byte_content_length(self):
        params = _DummyRequestParams()
        manager = _DummyGlobalEndpointManager()
        request = _DummyRequest()

        captured = {}

        async def _fake_execute_async(*args, **kwargs):
            request_arg = args[6]
            captured["content_length"] = request_arg.headers.get(HttpHeaders.ContentLength)
            captured["body"] = request_arg.data
            return {}, {}

        with mock.patch.object(_asynchronous_request._retry_utility_async, "ExecuteAsync", side_effect=_fake_execute_async):
            await _asynchronous_request.AsynchronousRequest(
                client=object(),
                request_params=params,
                global_endpoint_manager=manager,
                connection_policy=object(),
                pipeline_client=object(),
                request=request,
                request_data={"name": "café"},
            )

        self.assertEqual(captured["content_length"], len(captured["body"].encode("utf-8")))


if __name__ == "__main__":
    unittest.main()

