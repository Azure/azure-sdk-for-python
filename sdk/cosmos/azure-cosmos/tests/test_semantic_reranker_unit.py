# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
# cspell:ignore rerank reranker reranking
"""Unit tests for semantic reranker inference service timeout policy."""
import asyncio
import json
import os
import threading
import unittest
from unittest.mock import MagicMock, patch

from azure.core.exceptions import DecodeError, ServiceRequestError, ServiceResponseError

import azure.cosmos.exceptions as exceptions
from azure.cosmos._cosmos_client_connection import CosmosClientConnection as _SyncCosmosClientConnection
from azure.cosmos._inference_service import _InferenceService as _SyncInferenceService
from azure.cosmos.aio._cosmos_client_connection_async import (
    CosmosClientConnection as _AsyncCosmosClientConnection,
)
from azure.cosmos.aio._inference_service_async import _InferenceService as _AsyncInferenceService
from azure.cosmos.documents import ConnectionPolicy

_INFERENCE_ENDPOINT_ENV_VAR = "AZURE_COSMOS_SEMANTIC_RERANKER_INFERENCE_ENDPOINT"
_MALFORMED_INPUT_ENV_VAR = "AZURE_COSMOS_CHARSET_DECODER_ERROR_ACTION_ON_MALFORMED_INPUT"


class TestInferenceServiceTimeout(unittest.TestCase):
    """Unit tests for inference service timeout behavior."""

    def setUp(self):
        """Set the inference endpoint env var before each test."""
        self._saved_endpoint = os.environ.get(_INFERENCE_ENDPOINT_ENV_VAR)
        os.environ[_INFERENCE_ENDPOINT_ENV_VAR] = "https://example.com"
        self._saved_malformed = os.environ.get(_MALFORMED_INPUT_ENV_VAR)
        os.environ.pop(_MALFORMED_INPUT_ENV_VAR, None)

    def tearDown(self):
        """Restore the inference endpoint env var after each test."""
        if self._saved_endpoint is not None:
            os.environ[_INFERENCE_ENDPOINT_ENV_VAR] = self._saved_endpoint
        else:
            os.environ.pop(_INFERENCE_ENDPOINT_ENV_VAR, None)
        if self._saved_malformed is not None:
            os.environ[_MALFORMED_INPUT_ENV_VAR] = self._saved_malformed
        else:
            os.environ.pop(_MALFORMED_INPUT_ENV_VAR, None)

    def _create_mock_connection(self, inference_request_timeout=5):
        """Create a mock cosmos client connection with configurable inference timeout."""
        mock_connection = MagicMock()
        mock_connection.aad_credentials = MagicMock()
        mock_connection.connection_policy.InferenceRequestTimeout = inference_request_timeout
        mock_connection.connection_policy.ConnectionRetryConfiguration = 3
        mock_connection.connection_policy.ProxyConfiguration = None
        mock_connection._user_agent = "test-agent"
        mock_connection._enable_diagnostics_logging = False
        return mock_connection

    def test_sync_inference_timeout_raises_408(self):
        """Test that sync inference service converts ServiceRequestError to 408."""
        mock_connection = self._create_mock_connection()
        service = _SyncInferenceService(mock_connection)

        with patch.object(
            service._inference_pipeline_client._pipeline, "run",
            side_effect=ServiceRequestError("Connection timeout")
        ):
            with self.assertRaises(exceptions.CosmosHttpResponseError) as ctx:
                service.rerank(
                    reranking_context="test query",
                    documents=["doc1", "doc2"]
                )
            self.assertEqual(ctx.exception.status_code, 408)
            self.assertIn("Inference Service Request Timeout", str(ctx.exception))

    def test_async_inference_timeout_raises_408(self):
        """Test that async inference service converts ServiceRequestError to 408."""
        async def run_test():
            mock_connection = self._create_mock_connection()
            mock_connection.connection_policy.DisableSSLVerification = False
            service = _AsyncInferenceService(mock_connection)

            with patch.object(
                service._inference_pipeline_client._pipeline, "run",
                side_effect=ServiceRequestError("Connection timeout")
            ):
                with self.assertRaises(exceptions.CosmosHttpResponseError) as ctx:
                    await service.rerank(
                        reranking_context="test query",
                        documents=["doc1", "doc2"]
                    )
                self.assertEqual(ctx.exception.status_code, 408)
                self.assertIn("Inference Service Request Timeout", str(ctx.exception))

        asyncio.run(run_test())

    def test_sync_inference_timeout_value_from_connection_policy(self):
        """Test that sync inference service reads timeout from connection policy."""
        mock_connection = self._create_mock_connection(inference_request_timeout=10)
        service = _SyncInferenceService(mock_connection)

        self.assertEqual(service._inference_request_timeout, 10)

    def test_async_inference_timeout_value_from_connection_policy(self):
        """Test that async inference service reads timeout from connection policy."""
        mock_connection = self._create_mock_connection(inference_request_timeout=15)
        mock_connection.connection_policy.DisableSSLVerification = False
        service = _AsyncInferenceService(mock_connection)

        self.assertEqual(service._inference_request_timeout, 15)

    def test_sync_inference_passes_timeout_to_pipeline(self):
        """Test that sync inference service passes timeout kwargs to pipeline.run()."""
        mock_connection = self._create_mock_connection(inference_request_timeout=7)
        service = _SyncInferenceService(mock_connection)

        mock_response = MagicMock()
        mock_response.http_response.status_code = 200
        mock_response.http_response.headers = {}
        mock_response.http_response.body.return_value = b'{"Scores": []}'

        with patch.object(
            service._inference_pipeline_client._pipeline, "run",
            return_value=mock_response
        ) as mock_run:
            service.rerank(
                reranking_context="test query",
                documents=["doc1"]
            )
            mock_run.assert_called_once()
            call_kwargs = mock_run.call_args[1]
            self.assertEqual(call_kwargs["connection_timeout"], 7)
            self.assertEqual(call_kwargs["read_timeout"], 7)

    def test_async_inference_passes_timeout_to_pipeline(self):
        """Test that async inference service passes timeout kwargs to pipeline.run()."""
        async def run_test():
            mock_connection = self._create_mock_connection(inference_request_timeout=12)
            mock_connection.connection_policy.DisableSSLVerification = False
            service = _AsyncInferenceService(mock_connection)

            mock_response = MagicMock()
            mock_response.http_response.status_code = 200
            mock_response.http_response.headers = {}
            mock_response.http_response.body.return_value = b'{"Scores": []}'

            with patch.object(
                service._inference_pipeline_client._pipeline, "run",
                return_value=mock_response
            ) as mock_run:
                await service.rerank(
                    reranking_context="test query",
                    documents=["doc1"]
                )
                mock_run.assert_called_once()
                call_kwargs = mock_run.call_args[1]
                self.assertEqual(call_kwargs["connection_timeout"], 12)
                self.assertEqual(call_kwargs["read_timeout"], 12)

        asyncio.run(run_test())

    def test_sync_inference_uses_shared_response_decoder(self):
        """Checks the sync inference service decodes response bytes
        through the shared decode helper, not an inline decode call."""
        mock_connection = self._create_mock_connection()
        service = _SyncInferenceService(mock_connection)

        raw_response_data = b'{"Scores": []}'
        mock_response = MagicMock()
        mock_response.http_response.status_code = 200
        mock_response.http_response.headers = {}
        mock_response.http_response.body.return_value = raw_response_data

        with patch.object(
            service._inference_pipeline_client._pipeline, "run",
            return_value=mock_response
        ), patch(
            "azure.cosmos._inference_service.decode_response_body_for_status",
            return_value='{"Scores": []}'
        ) as mock_decode:
            service.rerank(
                reranking_context="test query",
                documents=["doc1"]
            )
            mock_decode.assert_called_once_with(raw_response_data, 200, "inference_request")

    def test_async_inference_uses_shared_response_decoder(self):
        """Async version of the wiring check above."""
        async def run_test():
            mock_connection = self._create_mock_connection()
            mock_connection.connection_policy.DisableSSLVerification = False
            service = _AsyncInferenceService(mock_connection)

            raw_response_data = b'{"Scores": []}'
            mock_response = MagicMock()
            mock_response.http_response.status_code = 200
            mock_response.http_response.headers = {}
            mock_response.http_response.body.return_value = raw_response_data

            with patch.object(
                service._inference_pipeline_client._pipeline, "run",
                return_value=mock_response
            ), patch(
                "azure.cosmos.aio._inference_service_async.decode_response_body_for_status",
                return_value='{"Scores": []}'
            ) as mock_decode:
                await service.rerank(
                    reranking_context="test query",
                    documents=["doc1"]
                )
                mock_decode.assert_called_once_with(raw_response_data, 200, "inference_request")

        asyncio.run(run_test())

    def test_sync_inference_2xx_with_invalid_utf8_raises_decode_error(self):
        """A 200 inference response with invalid bytes should come
        out as DecodeError, keeping the real status and original cause."""
        mock_connection = self._create_mock_connection()
        service = _SyncInferenceService(mock_connection)

        invalid_utf8 = b'{"Scores": "caf\xc3\x28"}'
        mock_response = MagicMock()
        mock_response.http_response.status_code = 200
        mock_response.http_response.headers = {}
        mock_response.http_response.body.return_value = invalid_utf8

        with patch.object(
            service._inference_pipeline_client._pipeline, "run",
            return_value=mock_response
        ):
            with self.assertRaises(DecodeError) as ctx:
                service.rerank(
                    reranking_context="test query",
                    documents=["doc1"]
                )

        self.assertEqual(ctx.exception.response.status_code, 200)
        self.assertIsInstance(ctx.exception.__cause__, UnicodeDecodeError)

    def test_async_inference_2xx_with_invalid_utf8_raises_decode_error(self):
        """Async version of the 2xx invalid-bytes check above."""
        async def run_test():
            mock_connection = self._create_mock_connection()
            mock_connection.connection_policy.DisableSSLVerification = False
            service = _AsyncInferenceService(mock_connection)

            invalid_utf8 = b'{"Scores": "caf\xc3\x28"}'
            mock_response = MagicMock()
            mock_response.http_response.status_code = 200
            mock_response.http_response.headers = {}
            mock_response.http_response.body.return_value = invalid_utf8

            with patch.object(
                service._inference_pipeline_client._pipeline, "run",
                return_value=mock_response
            ):
                with self.assertRaises(DecodeError) as ctx:
                    await service.rerank(
                        reranking_context="test query",
                        documents=["doc1"]
                    )

            self.assertEqual(ctx.exception.response.status_code, 200)
            self.assertIsInstance(ctx.exception.__cause__, UnicodeDecodeError)

        asyncio.run(run_test())

    # Tests below check that the permissive decode env var also works
    # through the inference service path, not just the regular request
    # path. Without these, a regression that only breaks one path
    # would not be caught.

    def test_sync_inference_replace_env_var_lets_2xx_with_invalid_utf8_succeed(self):
        """With REPLACE set, a 200 response containing invalid UTF-8
        in a string value should parse successfully and not raise."""
        mock_connection = self._create_mock_connection()
        service = _SyncInferenceService(mock_connection)

        # Valid JSON envelope; the bad byte sits inside a string value.
        invalid_utf8 = b'{"Scores":[{"index":0,"score":0.5,"label":"caf\xc3\x28"}]}'
        mock_response = MagicMock()
        mock_response.http_response.status_code = 200
        mock_response.http_response.headers = {}
        mock_response.http_response.body.return_value = invalid_utf8

        saved = os.environ.get(_MALFORMED_INPUT_ENV_VAR)
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"
        try:
            with patch.object(
                service._inference_pipeline_client._pipeline, "run",
                return_value=mock_response,
            ):
                result = service.rerank(
                    reranking_context="test query",
                    documents=["doc1"],
                )
            # The replacement character ends up inside the string value;
            # surrounding text is preserved.
            self.assertIn("Scores", result)
            self.assertEqual(len(result["Scores"]), 1)
            self.assertIn("\ufffd", result["Scores"][0]["label"])
            self.assertIn("caf", result["Scores"][0]["label"])
        finally:
            if saved is None:
                os.environ.pop(_MALFORMED_INPUT_ENV_VAR, None)
            else:
                os.environ[_MALFORMED_INPUT_ENV_VAR] = saved
        # Confirm the result is a parsed object, not a raw string.
        self.assertNotIsInstance(result, str)
        _ = json.dumps(result)

    def test_async_inference_replace_env_var_lets_2xx_with_invalid_utf8_succeed(self):
        """Async version of the REPLACE check above."""
        async def run_test():
            mock_connection = self._create_mock_connection()
            mock_connection.connection_policy.DisableSSLVerification = False
            service = _AsyncInferenceService(mock_connection)

            invalid_utf8 = b'{"Scores":[{"index":0,"score":0.5,"label":"caf\xc3\x28"}]}'
            mock_response = MagicMock()
            mock_response.http_response.status_code = 200
            mock_response.http_response.headers = {}
            mock_response.http_response.body.return_value = invalid_utf8

            saved = os.environ.get(_MALFORMED_INPUT_ENV_VAR)
            os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"
            try:
                with patch.object(
                    service._inference_pipeline_client._pipeline, "run",
                    return_value=mock_response,
                ):
                    result = await service.rerank(
                        reranking_context="test query",
                        documents=["doc1"],
                    )
            finally:
                if saved is None:
                    os.environ.pop(_MALFORMED_INPUT_ENV_VAR, None)
                else:
                    os.environ[_MALFORMED_INPUT_ENV_VAR] = saved

            self.assertIn("Scores", result)
            self.assertEqual(len(result["Scores"]), 1)
            self.assertIn("\ufffd", result["Scores"][0]["label"])
            self.assertIn("caf", result["Scores"][0]["label"])

        asyncio.run(run_test())

    def test_sync_inference_ignore_env_var_lets_2xx_with_invalid_utf8_succeed(self):
        """With IGNORE set, the bad byte is dropped and the response
        still parses cleanly."""
        mock_connection = self._create_mock_connection()
        service = _SyncInferenceService(mock_connection)

        invalid_utf8 = b'{"Scores":[{"index":0,"score":0.5,"label":"caf\xc3\x28"}]}'
        mock_response = MagicMock()
        mock_response.http_response.status_code = 200
        mock_response.http_response.headers = {}
        mock_response.http_response.body.return_value = invalid_utf8

        saved = os.environ.get(_MALFORMED_INPUT_ENV_VAR)
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "IGNORE"
        try:
            with patch.object(
                service._inference_pipeline_client._pipeline, "run",
                return_value=mock_response,
            ):
                result = service.rerank(
                    reranking_context="test query",
                    documents=["doc1"],
                )
        finally:
            if saved is None:
                os.environ.pop(_MALFORMED_INPUT_ENV_VAR, None)
            else:
                os.environ[_MALFORMED_INPUT_ENV_VAR] = saved

        self.assertIn("Scores", result)
        self.assertEqual(len(result["Scores"]), 1)
        # IGNORE drops the bad byte instead of replacing it.
        self.assertNotIn("\ufffd", result["Scores"][0]["label"])
        self.assertIn("caf", result["Scores"][0]["label"])

    def test_async_inference_ignore_env_var_lets_2xx_with_invalid_utf8_succeed(self):
        """Async equivalent of the sync IGNORE test above: with IGNORE set, the
        bad byte is dropped from the async inference response and parsing succeeds."""
        async def run_test():
            mock_connection = self._create_mock_connection()
            mock_connection.connection_policy.DisableSSLVerification = False
            service = _AsyncInferenceService(mock_connection)

            invalid_utf8 = b'{"Scores":[{"index":0,"score":0.5,"label":"caf\xc3\x28"}]}'
            mock_response = MagicMock()
            mock_response.http_response.status_code = 200
            mock_response.http_response.headers = {}
            mock_response.http_response.body.return_value = invalid_utf8

            # patch.dict scopes the env var to this test and restores the prior
            # value when the block exits, even if rerank below raises.
            with patch.dict(os.environ, {_MALFORMED_INPUT_ENV_VAR: "IGNORE"}):
                with patch.object(
                    service._inference_pipeline_client._pipeline, "run",
                    return_value=mock_response,
                ):
                    result = await service.rerank(
                        reranking_context="test query",
                        documents=["doc1"],
                    )

            self.assertIn("Scores", result)
            self.assertEqual(len(result["Scores"]), 1)
            # IGNORE drops the bad byte instead of replacing it.
            self.assertNotIn("\ufffd", result["Scores"][0]["label"])
            self.assertIn("caf", result["Scores"][0]["label"])

        asyncio.run(run_test())

    def test_sync_inference_response_timeout_raises_408(self):
        """Test that sync inference service converts ServiceResponseError to 408."""
        mock_connection = self._create_mock_connection()
        service = _SyncInferenceService(mock_connection)

        with patch.object(
            service._inference_pipeline_client._pipeline, "run",
            side_effect=ServiceResponseError("Read timeout")
        ):
            with self.assertRaises(exceptions.CosmosHttpResponseError) as ctx:
                service.rerank(
                    reranking_context="test query",
                    documents=["doc1", "doc2"]
                )
            self.assertEqual(ctx.exception.status_code, 408)
            self.assertIn("Inference Service Request Timeout", str(ctx.exception))

    def test_async_inference_response_timeout_raises_408(self):
        """Test that async inference service converts ServiceResponseError to 408."""
        async def run_test():
            mock_connection = self._create_mock_connection()
            mock_connection.connection_policy.DisableSSLVerification = False
            service = _AsyncInferenceService(mock_connection)

            with patch.object(
                service._inference_pipeline_client._pipeline, "run",
                side_effect=ServiceResponseError("Read timeout")
            ):
                with self.assertRaises(exceptions.CosmosHttpResponseError) as ctx:
                    await service.rerank(
                        reranking_context="test query",
                        documents=["doc1", "doc2"]
                    )
                self.assertEqual(ctx.exception.status_code, 408)
                self.assertIn("Inference Service Request Timeout", str(ctx.exception))

        asyncio.run(run_test())

    def test_connection_policy_default_inference_timeout(self):
        """Test that ConnectionPolicy defaults InferenceRequestTimeout to 5 seconds."""
        policy = ConnectionPolicy()
        self.assertEqual(policy.InferenceRequestTimeout, 5)

    def test_connection_policy_custom_inference_timeout(self):
        """Test that ConnectionPolicy InferenceRequestTimeout can be set."""
        policy = ConnectionPolicy()
        policy.InferenceRequestTimeout = 30
        self.assertEqual(policy.InferenceRequestTimeout, 30)

    def test_sync_lazy_init_raises_error_without_env_var(self):
        """Test that _InferenceService raises ValueError when env var is missing.
        With lazy init, this error is deferred from client construction to first use."""
        os.environ.pop(_INFERENCE_ENDPOINT_ENV_VAR, None)
        mock_connection = self._create_mock_connection()
        with self.assertRaises(ValueError) as ctx:
            _SyncInferenceService(mock_connection)
        self.assertIn(_INFERENCE_ENDPOINT_ENV_VAR, str(ctx.exception))

    def test_async_lazy_init_raises_error_without_env_var(self):
        """Test that async _InferenceService raises ValueError when env var is missing.
        With lazy init, this error is deferred from client construction to first use."""
        os.environ.pop(_INFERENCE_ENDPOINT_ENV_VAR, None)
        mock_connection = self._create_mock_connection()
        mock_connection.connection_policy.DisableSSLVerification = False
        with self.assertRaises(ValueError) as ctx:
            _AsyncInferenceService(mock_connection)
        self.assertIn(_INFERENCE_ENDPOINT_ENV_VAR, str(ctx.exception))

    def test_sync_inference_service_created_with_env_var(self):
        """Test that sync _InferenceService can be created when env var is set."""
        mock_connection = self._create_mock_connection()
        service = _SyncInferenceService(mock_connection)
        self.assertIsNotNone(service)

    def test_async_inference_service_created_with_env_var(self):
        """Test that async _InferenceService can be created when env var is set."""
        mock_connection = self._create_mock_connection()
        mock_connection.connection_policy.DisableSSLVerification = False
        service = _AsyncInferenceService(mock_connection)
        self.assertIsNotNone(service)

    # ── _get_inference_service() direct call tests ──

    def test_sync_get_inference_service_returns_service_with_aad_and_env_var(self):
        """Test that _get_inference_service() returns an _InferenceService when AAD
        credentials are present and the env var is set."""
        mock_conn = self._create_mock_connection()
        mock_conn._inference_service = None
        mock_conn._inference_service_lock = threading.Lock()

        result = _SyncCosmosClientConnection._get_inference_service(mock_conn)
        self.assertIsNotNone(result)

    def test_async_get_inference_service_returns_service_with_aad_and_env_var(self):
        """Test that async _get_inference_service() returns an _InferenceService when AAD
        credentials are present and the env var is set."""
        mock_conn = self._create_mock_connection()
        mock_conn._inference_service = None
        mock_conn.connection_policy.DisableSSLVerification = False

        result = _AsyncCosmosClientConnection._get_inference_service(mock_conn)
        self.assertIsNotNone(result)

    def test_sync_get_inference_service_raises_error_without_env_var(self):
        """Test that _get_inference_service() wraps ValueError into CosmosHttpResponseError
        when the env var is missing."""
        os.environ.pop(_INFERENCE_ENDPOINT_ENV_VAR, None)
        mock_conn = self._create_mock_connection()
        mock_conn._inference_service = None
        mock_conn._inference_service_lock = threading.Lock()

        with self.assertRaises(exceptions.CosmosHttpResponseError) as ctx:
            _SyncCosmosClientConnection._get_inference_service(mock_conn)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Failed to initialize inference service", str(ctx.exception))

    def test_async_get_inference_service_raises_error_without_env_var(self):
        """Test that async _get_inference_service() wraps ValueError into CosmosHttpResponseError
        when the env var is missing."""
        os.environ.pop(_INFERENCE_ENDPOINT_ENV_VAR, None)
        mock_conn = self._create_mock_connection()
        mock_conn._inference_service = None
        mock_conn.connection_policy.DisableSSLVerification = False

        with self.assertRaises(exceptions.CosmosHttpResponseError) as ctx:
            _AsyncCosmosClientConnection._get_inference_service(mock_conn)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Failed to initialize inference service", str(ctx.exception))

    def test_sync_get_inference_service_returns_none_without_aad(self):
        """Test that _get_inference_service() returns None when no AAD credentials
        are present (master key auth)."""
        mock_conn = self._create_mock_connection()
        mock_conn.aad_credentials = None
        mock_conn._inference_service = None
        mock_conn._inference_service_lock = threading.Lock()

        result = _SyncCosmosClientConnection._get_inference_service(mock_conn)
        self.assertIsNone(result)

    def test_async_get_inference_service_returns_none_without_aad(self):
        """Test that async _get_inference_service() returns None when no AAD credentials
        are present (master key auth)."""
        mock_conn = self._create_mock_connection()
        mock_conn.aad_credentials = None
        mock_conn._inference_service = None

        result = _AsyncCosmosClientConnection._get_inference_service(mock_conn)
        self.assertIsNone(result)

    def test_sync_get_inference_service_caches_instance(self):
        """Test that _get_inference_service() returns the same cached instance on
        repeated calls."""
        mock_conn = self._create_mock_connection()
        mock_conn._inference_service = None
        mock_conn._inference_service_lock = threading.Lock()

        first = _SyncCosmosClientConnection._get_inference_service(mock_conn)
        second = _SyncCosmosClientConnection._get_inference_service(mock_conn)
        self.assertIsNotNone(first)
        self.assertIs(first, second)

    def test_async_get_inference_service_caches_instance(self):
        """Test that async _get_inference_service() returns the same cached instance on
        repeated calls."""
        mock_conn = self._create_mock_connection()
        mock_conn._inference_service = None
        mock_conn.connection_policy.DisableSSLVerification = False

        first = _AsyncCosmosClientConnection._get_inference_service(mock_conn)
        second = _AsyncCosmosClientConnection._get_inference_service(mock_conn)
        self.assertIsNotNone(first)
        self.assertIs(first, second)


if __name__ == "__main__":
    unittest.main()
