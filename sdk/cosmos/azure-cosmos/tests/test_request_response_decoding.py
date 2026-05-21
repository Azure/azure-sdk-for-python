# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Wiring tests for the response-body decode call in the core sync/async
``_Request()`` paths.

Background: ``_synchronized_request._Request`` and
``_asynchronous_request._Request`` are the highest-traffic code paths in
the SDK — every CRUD, query, and change-feed read flows through them.
Both call ``decode_response_body_for_status`` to decode the HTTP
response body before the status-code branching that builds typed
``CosmosResourceNotFoundError`` / ``CosmosHttpResponseError`` exceptions.

These tests lock in two contracts:

1. **Wiring** — the call sites actually invoke the shared decoder. If
   someone reverts the call back to ``data.decode("utf-8")`` we want a
   unit test to fail immediately. Mirrors the wiring tests already in
   place for the inference service in ``test_semantic_reranker_unit``.

2. **Behavior** — when an HTTP error response body contains invalid
   UTF-8, ``_Request`` surfaces the real typed exception
   (``CosmosResourceNotFoundError`` etc.) instead of letting a
   ``UnicodeDecodeError`` escape. This is the property the
   ``decode_response_body_for_status`` helper was introduced to
   guarantee; without an end-to-end test on ``_Request``, the helper
   could quietly fall out of use and the regression would not be
   caught at unit-test time.
"""
import asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from azure.core.exceptions import DecodeError

from azure.cosmos import _synchronized_request, exceptions
from azure.cosmos.aio import _asynchronous_request
from azure.cosmos.http_constants import ResourceType


# Same invalid UTF-8 used in test_response_decoding.py
_INVALID_UTF8 = b'{"note":"hello \xc3\x28 world"}'
_VALID_UTF8 = b'{"ok":true}'

_FAKE_ENDPOINT = "https://example.documents.azure.com:443/"


def _build_request_args(status_code: int, body: bytes):
    """Build the minimal set of mocked dependencies ``_Request`` needs to
    reach the decode call site. Returns (args_tuple, mock_response)."""
    # ``endpoint_override`` short-circuits endpoint resolution so we do
    # not need a real GlobalEndpointManager. ``DatabaseAccount`` skips
    # ``refresh_endpoint_list`` for the same reason.
    request_params = MagicMock()
    request_params.healthy_tentative_location = False
    request_params.resource_type = ResourceType.DatabaseAccount
    request_params.read_timeout_override = None
    request_params.endpoint_override = _FAKE_ENDPOINT
    request_params.should_cancel_request.return_value = False
    request_params.operation_type = "Read"
    request_params.availability_strategy = None

    connection_policy = MagicMock()
    connection_policy.RequestTimeout = 30
    connection_policy.ReadTimeout = 30
    connection_policy.RecoveryReadTimeout = 5
    connection_policy.DBAReadTimeout = 5
    connection_policy.DBAConnectionTimeout = 5
    connection_policy.SSLConfiguration = None
    connection_policy.DisableSSLVerification = False

    global_endpoint_manager = MagicMock()

    pipeline_client = MagicMock()

    request = MagicMock()
    request.url = _FAKE_ENDPOINT + "dbs"
    request.headers = {}

    # The fake pipeline response that _PipelineRunFunction will return.
    mock_response = MagicMock()
    mock_response.http_response.status_code = status_code
    mock_response.http_response.headers = {}
    mock_response.http_response.body.return_value = body

    return (
        (global_endpoint_manager, request_params, connection_policy, pipeline_client, request),
        mock_response,
    )


class TestSyncRequestUsesSharedDecoder(unittest.TestCase):
    """Wiring + behavioral tests for ``_synchronized_request._Request``."""

    def test_request_invokes_shared_response_decoder(self):
        """Reverting the call site back to ``data.decode('utf-8')`` would
        make this test fail. Locks in the wiring."""
        args, mock_response = _build_request_args(status_code=200, body=_VALID_UTF8)

        with patch(
            "azure.cosmos._synchronized_request._PipelineRunFunction",
            return_value=mock_response,
        ), patch(
            "azure.cosmos._synchronized_request.decode_response_body_for_status",
            return_value='{"ok":true}',
        ) as mock_decode:
            _synchronized_request._Request(*args)

            mock_decode.assert_called_once_with(_VALID_UTF8, 200, "Read")

    def test_invalid_utf8_on_404_surfaces_resource_not_found(self):
        """Behavioral guarantee: a 404 carrying a malformed-UTF-8 body
        must surface as ``CosmosResourceNotFoundError``, not as a
        ``UnicodeDecodeError``. Customer error handlers branch on the
        typed exception; a decode error here would skip those handlers
        entirely."""
        args, mock_response = _build_request_args(status_code=404, body=_INVALID_UTF8)

        with patch(
            "azure.cosmos._synchronized_request._PipelineRunFunction",
            return_value=mock_response,
        ):
            with self.assertRaises(exceptions.CosmosResourceNotFoundError):
                _synchronized_request._Request(*args)

    def test_invalid_utf8_on_503_surfaces_http_response_error(self):
        """Same guarantee for the generic ``status_code >= 400`` branch.
        503 specifically matters: it drives cross-region retry; masking
        it with a decode error would stop failover from happening."""
        args, mock_response = _build_request_args(status_code=503, body=_INVALID_UTF8)

        with patch(
            "azure.cosmos._synchronized_request._PipelineRunFunction",
            return_value=mock_response,
        ):
            with self.assertRaises(exceptions.CosmosHttpResponseError) as ctx:
                _synchronized_request._Request(*args)
            self.assertEqual(ctx.exception.status_code, 503)


class TestAsyncRequestUsesSharedDecoder(unittest.TestCase):
    """Wiring + behavioral tests for ``_asynchronous_request._Request``."""

    def test_request_invokes_shared_response_decoder(self):
        async def run_test():
            args, mock_response = _build_request_args(status_code=200, body=_VALID_UTF8)

            with patch(
                "azure.cosmos.aio._asynchronous_request._PipelineRunFunction",
                new=AsyncMock(return_value=mock_response),
            ), patch(
                "azure.cosmos.aio._asynchronous_request.decode_response_body_for_status",
                return_value='{"ok":true}',
            ) as mock_decode:
                await _asynchronous_request._Request(*args)

                mock_decode.assert_called_once_with(_VALID_UTF8, 200, "Read")

        asyncio.run(run_test())

    def test_invalid_utf8_on_404_surfaces_resource_not_found(self):
        async def run_test():
            args, mock_response = _build_request_args(status_code=404, body=_INVALID_UTF8)

            with patch(
                "azure.cosmos.aio._asynchronous_request._PipelineRunFunction",
                new=AsyncMock(return_value=mock_response),
            ):
                with self.assertRaises(exceptions.CosmosResourceNotFoundError):
                    await _asynchronous_request._Request(*args)

        asyncio.run(run_test())

    def test_invalid_utf8_on_503_surfaces_http_response_error(self):
        async def run_test():
            args, mock_response = _build_request_args(status_code=503, body=_INVALID_UTF8)

            with patch(
                "azure.cosmos.aio._asynchronous_request._PipelineRunFunction",
                new=AsyncMock(return_value=mock_response),
            ):
                with self.assertRaises(exceptions.CosmosHttpResponseError) as ctx:
                    await _asynchronous_request._Request(*args)
                self.assertEqual(ctx.exception.status_code, 503)

        asyncio.run(run_test())


class TestRequestWrapsResidualUnicodeDecodeErrorAsDecodeError(unittest.TestCase):
    """For a successful (2xx) response carrying invalid UTF-8 in default
    strict mode, ``_Request`` must surface the failure as
    ``azure.core.exceptions.DecodeError`` — not as a stdlib
    ``UnicodeDecodeError``. This contract matches the existing JSON-parse
    failure path (which also raises ``DecodeError``) and keeps the wire
    truth intact:

    * ``e.response.status_code`` is the real wire status (e.g. 200) —
      no synthetic 400, no faked sub-status.
    * ``e.__cause__`` is the original ``UnicodeDecodeError`` so
      operators can still see the byte offset and the env-var hint.

    Customer middleware keyed on ``HttpResponseError`` /
    ``CosmosHttpResponseError`` continues to work because ``DecodeError``
    is a subclass of ``HttpResponseError``."""

    def test_sync_2xx_with_invalid_utf8_raises_decode_error(self):
        args, mock_response = _build_request_args(status_code=200, body=_INVALID_UTF8)

        with patch(
            "azure.cosmos._synchronized_request._PipelineRunFunction",
            return_value=mock_response,
        ):
            with self.assertRaises(DecodeError) as ctx:
                _synchronized_request._Request(*args)

        self.assertEqual(ctx.exception.response.status_code, 200)
        self.assertIsInstance(ctx.exception.__cause__, UnicodeDecodeError)

    def test_async_2xx_with_invalid_utf8_raises_decode_error(self):
        async def run_test():
            args, mock_response = _build_request_args(status_code=200, body=_INVALID_UTF8)

            with patch(
                "azure.cosmos.aio._asynchronous_request._PipelineRunFunction",
                new=AsyncMock(return_value=mock_response),
            ):
                with self.assertRaises(DecodeError) as ctx:
                    await _asynchronous_request._Request(*args)

            self.assertEqual(ctx.exception.response.status_code, 200)
            self.assertIsInstance(ctx.exception.__cause__, UnicodeDecodeError)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()

