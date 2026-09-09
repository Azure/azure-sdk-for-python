# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tests that the Content-Length header on outgoing requests is the
UTF-8 byte count of the body, not the number of characters."""
import unittest
from unittest import mock

import pytest

from azure.cosmos import _synchronized_request, http_constants
from azure.cosmos.aio import _asynchronous_request
from azure.cosmos.documents import _OperationType
from azure.cosmos.http_constants import HttpHeaders


# Payloads chosen so the byte count differs from the character count
# by an increasing amount: 1, 2, 3, then 4 bytes per non-ASCII char.
# The string forms are passed as-is (not as dicts) because that's the
# input shape that exercises the byte-count code path.
_STR_PAYLOADS = [
    ("ascii_baseline", '{"name":"hello"}'),       # 1 byte per char
    ("two_byte_latin", '{"name":"café"}'),        # 2-byte 'é'
    ("three_byte_cjk", '{"name":"日本"}'),         # 3-byte CJK
    ("four_byte_emoji", '{"name":"🎉🎊"}'),        # 4-byte emoji
]


class _DummyRequestParams:
    """Stand-in for RequestObject with hedging disabled and a plain item
    create, so requests reach the mocked executor directly."""
    def __init__(self):
        self.availability_strategy = None
        self.is_hedging_request = False
        self.resource_type = http_constants.ResourceType.Document
        self.operation_type = _OperationType.Create
        self.retry_write = 0


class _DummyGlobalEndpointManager:
    """Endpoint manager stub reporting per-partition failover as off."""
    @staticmethod
    def is_per_partition_automatic_failover_enabled():
        return False


class _DummyRequest:
    """Minimal HttpRequest stand-in capturing body and headers."""
    def __init__(self):
        self.headers = {}
        self.data = None


class _DummyClient:
    """Client stub with the compact UTF-8 option off, so these tests cover
    the default serialization path."""
    _enable_compact_utf8_item_writes = False


# These tests need no emulator, but the Cosmos CI lane selects tests with
# "-m cosmosEmulator" (see eng/pipelines/templates/stages/cosmos-sdk-client.yml),
# so an unmarked test is silently deselected and would never run.
@pytest.mark.cosmosEmulator
class TestContentLengthWiringSync(unittest.TestCase):
    """Checks the sync request path sets Content-Length to the byte
    count of the body."""

    def _capture_outgoing_request(self, request_data):
        """Run one request through the sync path with the retry executor
        mocked out, returning the body and Content-Length that would be sent."""
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
                client=_DummyClient(),
                request_params=params,
                global_endpoint_manager=manager,
                connection_policy=object(),
                pipeline_client=object(),
                request=request,
                request_data=request_data,
            )
        return captured

    def test_str_bodies_set_utf8_byte_content_length(self):
        """For each payload, Content-Length equals the UTF-8 byte count
        of the body. For the multi-byte cases it must also differ from
        the character count."""
        for label, payload in _STR_PAYLOADS:
            with self.subTest(payload=label):
                captured = self._capture_outgoing_request(payload)
                body = captured["body"]
                self.assertIsInstance(body, str)
                expected_bytes = len(body.encode("utf-8"))
                self.assertEqual(captured["content_length"], expected_bytes)
                # ASCII is the same in both counts, so only check the
                # difference for the multi-byte cases.
                if label != "ascii_baseline":
                    self.assertNotEqual(captured["content_length"], len(body))

    def test_none_body_sets_content_length_zero(self):
        """A request with no body should still get Content-Length 0."""
        captured = self._capture_outgoing_request(None)
        self.assertEqual(captured["content_length"], 0)

    def test_bytes_body_is_coerced_to_none_and_content_length_zero(self):
        """A bytes payload is currently converted to None inside the
        SDK, so Content-Length ends up as 0. This test pins the current
        behavior so any change to bytes handling is forced to be deliberate."""
        captured = self._capture_outgoing_request(b'{"x":1}')
        self.assertIsNone(captured["body"])
        self.assertEqual(captured["content_length"], 0)

    def test_bytearray_body_is_coerced_to_none_and_content_length_zero(self):
        """Same contract as for bytes. Bytearray inputs are also
        converted to None and get Content-Length 0."""
        captured = self._capture_outgoing_request(bytearray(b'{"x":1}'))
        self.assertIsNone(captured["body"])
        self.assertEqual(captured["content_length"], 0)


@pytest.mark.cosmosEmulator
class TestContentLengthWiringAsync(unittest.IsolatedAsyncioTestCase):
    """Async version of the sync class above. Same checks."""

    async def _capture_outgoing_request(self, request_data):
        """Async twin of the sync capture helper."""
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
                client=_DummyClient(),
                request_params=params,
                global_endpoint_manager=manager,
                connection_policy=object(),
                pipeline_client=object(),
                request=request,
                request_data=request_data,
            )
        return captured

    async def test_str_bodies_set_utf8_byte_content_length(self):
        """Async twin: Content-Length is the UTF-8 byte count, and for
        multi-byte payloads it differs from the character count."""
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
        """Async twin: a request with no body still gets Content-Length 0."""
        captured = await self._capture_outgoing_request(None)
        self.assertEqual(captured["content_length"], 0)

    async def test_bytes_body_is_coerced_to_none_and_content_length_zero(self):
        """Async version of the bytes-body check. Same contract: bytes
        come out as None and Content-Length is set to 0."""
        captured = await self._capture_outgoing_request(b'{"x":1}')
        self.assertIsNone(captured["body"])
        self.assertEqual(captured["content_length"], 0)

    async def test_bytearray_body_is_coerced_to_none_and_content_length_zero(self):
        """Async version of the bytearray check."""
        captured = await self._capture_outgoing_request(bytearray(b'{"x":1}'))
        self.assertIsNone(captured["body"])
        self.assertEqual(captured["content_length"], 0)


if __name__ == "__main__":
    unittest.main()
