# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tests that check the sync and async request functions both call the
shared decode helper, and that a response body with invalid bytes
still surfaces the right typed exception based on the HTTP status."""
import asyncio
import os
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from azure.core.exceptions import DecodeError

from azure.cosmos import _synchronized_request, exceptions
from azure.cosmos.aio import _asynchronous_request
from azure.cosmos.http_constants import ResourceType


_INVALID_UTF8 = b'{"note":"hello \xc3\x28 world"}'
_VALID_UTF8 = b'{"ok":true}'
_MALFORMED_INPUT_ENV_VAR = "AZURE_COSMOS_CHARSET_DECODER_ERROR_ACTION_ON_MALFORMED_INPUT"

_FAKE_ENDPOINT = "https://example.documents.azure.com:443/"


def _build_request_args(status_code: int, body: bytes):
    """Builds the smallest set of mocks the request function needs."""
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

    # Fake HTTP response with the given body and status.
    mock_response = MagicMock()
    mock_response.http_response.status_code = status_code
    mock_response.http_response.headers = {}
    mock_response.http_response.body.return_value = body

    return (
        (global_endpoint_manager, request_params, connection_policy, pipeline_client, request),
        mock_response,
    )


class TestSyncRequestUsesSharedDecoder(unittest.TestCase):
    """Sync request function: uses the shared decoder, and turns
    error responses into typed exceptions."""

    def test_request_invokes_shared_response_decoder(self):
        """Checks the sync request function actually calls the shared
        decode helper with the response bytes and status."""
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
        """A 404 with invalid bytes in the body should still come
        out as the typed not-found exception, not a decode error."""
        args, mock_response = _build_request_args(status_code=404, body=_INVALID_UTF8)

        with patch(
            "azure.cosmos._synchronized_request._PipelineRunFunction",
            return_value=mock_response,
        ):
            with self.assertRaises(exceptions.CosmosResourceNotFoundError):
                _synchronized_request._Request(*args)

    def test_invalid_utf8_on_503_surfaces_http_response_error(self):
        """A 503 with invalid bytes still comes out as the generic
        HTTP error with the right status, not a decode error."""
        args, mock_response = _build_request_args(status_code=503, body=_INVALID_UTF8)

        with patch(
            "azure.cosmos._synchronized_request._PipelineRunFunction",
            return_value=mock_response,
        ):
            with self.assertRaises(exceptions.CosmosHttpResponseError) as ctx:
                _synchronized_request._Request(*args)
            self.assertEqual(ctx.exception.status_code, 503)


class TestAsyncRequestUsesSharedDecoder(unittest.TestCase):
    """Async request function: same checks as the sync class."""

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
    """A 200 response with invalid bytes (in default strict mode)
    should be raised as DecodeError, keeping the real wire status and
    the original cause attached."""

    def setUp(self):
        self._saved_malformed = os.environ.get(_MALFORMED_INPUT_ENV_VAR)
        os.environ.pop(_MALFORMED_INPUT_ENV_VAR, None)

    def tearDown(self):
        if self._saved_malformed is not None:
            os.environ[_MALFORMED_INPUT_ENV_VAR] = self._saved_malformed
        else:
            os.environ.pop(_MALFORMED_INPUT_ENV_VAR, None)

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
