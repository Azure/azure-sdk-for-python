# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Regression tests for the Content-Length header computation.

The SDK previously computed ``Content-Length`` from ``len(request.data)`` —
the number of Unicode code points in the JSON string — instead of the
UTF-8 byte length that actually goes on the wire. For any non-ASCII
payload that under-counted the body by the number of multi-byte
characters, which can cause downstream HTTP receivers to truncate the
body, reject the request, or mis-frame the next keep-alive request.

Every assertion in this file exercises the actual production code path
in ``_synchronized_request.SynchronizedRequest`` or
``_asynchronous_request.AsynchronousRequest`` by patching the retry
layer and inspecting the request object the SDK would have put on the
wire. A previous iteration of this file also contained "mirror" tests
that re-implemented the production formula locally — those have been
removed because they could not catch a production regression (they
only verified that ``len(s.encode("utf-8"))`` works, which is a Python
built-in).
"""
import unittest
from unittest import mock

from azure.cosmos import _synchronized_request, http_constants
from azure.cosmos.aio import _asynchronous_request
from azure.cosmos.documents import _OperationType
from azure.cosmos.http_constants import HttpHeaders


# Payload matrix covering the four interesting char-vs-byte cases. Each
# str payload is named by the most divergent character it contains.
# The 4-byte emoji case maximizes the difference between ``len(s)``
# (the old, buggy formula) and ``len(s.encode("utf-8"))`` (the new,
# correct formula), so a regression that reverts the fix will fail
# loudest on that case.
#
# Subtlety on why the payloads are pre-serialized JSON strings rather
# than dicts: the SDK's ``_request_body_from_data`` uses
# ``json.dumps(data, separators=(",", ":"))`` with default
# ``ensure_ascii=True``. That means dicts containing multi-byte chars
# get escaped to pure ASCII (e.g. ``"é"`` -> ``"\\u00e9"``) *before*
# Content-Length is computed — the byte-length code path is never
# actually exercised. The path that matters is when a customer passes
# a pre-serialized string, which ``_request_body_from_data`` returns
# unchanged. That is the path these tests exercise.
_STR_PAYLOADS = [
    ("ascii_baseline", '{"name":"hello"}'),       # 1 byte per char
    ("two_byte_latin", '{"name":"café"}'),        # 2-byte 'é'
    ("three_byte_cjk", '{"name":"日本"}'),         # 3-byte CJK
    ("four_byte_emoji", '{"name":"🎉🎊"}'),        # 4-byte emoji
]


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


class TestContentLengthWiringSync(unittest.TestCase):
    """Sync path: ``SynchronizedRequest`` → ``Execute`` should produce a
    request whose ``Content-Length`` header equals the UTF-8 byte count
    of the serialized body (not the code-point count)."""

    def _capture_outgoing_request(self, request_data):
        params = _DummyRequestParams()
        manager = _DummyGlobalEndpointManager()
        request = _DummyRequest()

        captured = {}

        def _fake_execute(*args, **kwargs):
            request_arg = args[6]
            captured["content_length"] = request_arg.headers.get(HttpHeaders.ContentLength)
            captured["body"] = request_arg.data
            return {}, {}

        with mock.patch.object(
            _synchronized_request._retry_utility, "Execute", side_effect=_fake_execute
        ):
            _synchronized_request.SynchronizedRequest(
                client=object(),
                request_params=params,
                global_endpoint_manager=manager,
                connection_policy=object(),
                pipeline_client=object(),
                request=request,
                request_data=request_data,
            )
        return captured

    def test_str_bodies_set_utf8_byte_content_length(self):
        """For each payload in the byte-divergence matrix, the
        ``Content-Length`` header the SDK puts on the wire must equal
        the UTF-8 byte count of the JSON-serialized body. For the emoji
        case in particular this exceeds the code-point count by 3×."""
        for label, payload in _STR_PAYLOADS:
            with self.subTest(payload=label):
                captured = self._capture_outgoing_request(payload)
                body = captured["body"]
                self.assertIsInstance(body, str)
                expected_bytes = len(body.encode("utf-8"))
                self.assertEqual(captured["content_length"], expected_bytes)
                # Explicitly assert the value differs from the buggy
                # formula for the multi-byte cases. ASCII is excluded
                # because for ASCII both formulas agree.
                if label != "ascii_baseline":
                    self.assertNotEqual(captured["content_length"], len(body))

    def test_none_body_sets_content_length_zero(self):
        """Covers the ``elif body is None`` branch in production: a
        request with no body should still get ``Content-Length: 0``."""
        captured = self._capture_outgoing_request(None)
        self.assertEqual(captured["content_length"], 0)


class TestContentLengthWiringAsync(unittest.IsolatedAsyncioTestCase):
    """Async path: same contract as the sync test class, routed through
    ``AsynchronousRequest`` → ``ExecuteAsync``."""

    async def _capture_outgoing_request(self, request_data):
        params = _DummyRequestParams()
        manager = _DummyGlobalEndpointManager()
        request = _DummyRequest()

        captured = {}

        async def _fake_execute_async(*args, **kwargs):
            request_arg = args[6]
            captured["content_length"] = request_arg.headers.get(HttpHeaders.ContentLength)
            captured["body"] = request_arg.data
            return {}, {}

        with mock.patch.object(
            _asynchronous_request._retry_utility_async,
            "ExecuteAsync",
            side_effect=_fake_execute_async,
        ):
            await _asynchronous_request.AsynchronousRequest(
                client=object(),
                request_params=params,
                global_endpoint_manager=manager,
                connection_policy=object(),
                pipeline_client=object(),
                request=request,
                request_data=request_data,
            )
        return captured

    async def test_str_bodies_set_utf8_byte_content_length(self):
        for label, payload in _STR_PAYLOADS:
            with self.subTest(payload=label):
                captured = await self._capture_outgoing_request(payload)
                body = captured["body"]
                self.assertIsInstance(body, str)
                expected_bytes = len(body.encode("utf-8"))
                self.assertEqual(captured["content_length"], expected_bytes)
                if label != "ascii_baseline":
                    self.assertNotEqual(captured["content_length"], len(body))

    async def test_none_body_sets_content_length_zero(self):
        captured = await self._capture_outgoing_request(None)
        self.assertEqual(captured["content_length"], 0)


if __name__ == "__main__":
    unittest.main()

