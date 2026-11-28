# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
# cspell:ignore rerank reranker reranking
"""Original semantic reranker inference-service unit tests, kept with the new tests.

Source: ``tests/test_semantic_reranker_unit.py``. These tests now supply
client-owned inference settings rather than mocked connections;
``semantic_rerank`` has no Rust implementation, so no backend is selected.
"""
import asyncio
import json
import os
from dataclasses import replace
import unittest
from unittest.mock import MagicMock, patch

from azure.core.exceptions import DecodeError, ServiceRequestError, ServiceResponseError

import azure.cosmos.exceptions as exceptions
from azure.cosmos._inference_client import InferenceClient, InferenceClientSettings
from azure.cosmos._inference_service import _InferenceService as _SyncInferenceService
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

    def _create_settings(self, inference_request_timeout=5):
        """Create inference settings with a mock credential and configurable timeout."""
        return InferenceClientSettings(
            aad_credentials=MagicMock(),
            request_timeout=inference_request_timeout,
            retry_configuration=3,
            user_agent="test-agent",
            enable_diagnostics_logging=False,
        )

    def test_sync_inference_timeout_raises_408_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_sync_inference_timeout_raises_408
        """Test that sync inference service converts ServiceRequestError to 408."""
        settings = self._create_settings()
        service = _SyncInferenceService(settings)

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

    def test_async_inference_timeout_raises_408_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_async_inference_timeout_raises_408
        """Test that async inference service converts ServiceRequestError to 408."""
        async def run_test():
            settings = self._create_settings()
            service = _AsyncInferenceService(settings)

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

    def test_sync_inference_timeout_value_from_connection_policy_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_sync_inference_timeout_value_from_connection_policy
        """Test that sync inference service reads timeout from client settings."""
        settings = self._create_settings(inference_request_timeout=10)
        service = _SyncInferenceService(settings)

        self.assertEqual(service._inference_request_timeout, 10)

    def test_async_inference_timeout_value_from_connection_policy_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_async_inference_timeout_value_from_connection_policy
        """Test that async inference service reads timeout from client settings."""
        settings = self._create_settings(inference_request_timeout=15)
        service = _AsyncInferenceService(settings)

        self.assertEqual(service._inference_request_timeout, 15)

    def test_sync_inference_passes_timeout_to_pipeline_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_sync_inference_passes_timeout_to_pipeline
        """Test that sync inference service passes timeout kwargs to pipeline.run()."""
        settings = self._create_settings(inference_request_timeout=7)
        service = _SyncInferenceService(settings)

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

    def test_async_inference_passes_timeout_to_pipeline_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_async_inference_passes_timeout_to_pipeline
        """Test that async inference service passes timeout kwargs to pipeline.run()."""
        async def run_test():
            settings = self._create_settings(inference_request_timeout=12)
            service = _AsyncInferenceService(settings)

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

    def test_sync_inference_uses_shared_response_decoder_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_sync_inference_uses_shared_response_decoder
        """Checks the sync inference service decodes response bytes
        through the shared decode helper, not an inline decode call."""
        settings = self._create_settings()
        service = _SyncInferenceService(settings)

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

    def test_async_inference_uses_shared_response_decoder_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_async_inference_uses_shared_response_decoder
        """Async version of the wiring check above."""
        async def run_test():
            settings = self._create_settings()
            service = _AsyncInferenceService(settings)

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

    def test_sync_inference_2xx_with_invalid_utf8_raises_decode_error_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_sync_inference_2xx_with_invalid_utf8_raises_decode_error
        """A 200 inference response with invalid bytes should come
        out as DecodeError, keeping the real status and original cause."""
        settings = self._create_settings()
        service = _SyncInferenceService(settings)

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

    def test_async_inference_2xx_with_invalid_utf8_raises_decode_error_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_async_inference_2xx_with_invalid_utf8_raises_decode_error
        """Async version of the 2xx invalid-bytes check above."""
        async def run_test():
            settings = self._create_settings()
            service = _AsyncInferenceService(settings)

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

    def test_sync_inference_replace_env_var_lets_2xx_with_invalid_utf8_succeed_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_sync_inference_replace_env_var_lets_2xx_with_invalid_utf8_succeed
        """With REPLACE set, a 200 response containing invalid UTF-8
        in a string value should parse successfully and not raise."""
        settings = self._create_settings()
        service = _SyncInferenceService(settings)

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

    def test_async_inference_replace_env_var_lets_2xx_with_invalid_utf8_succeed_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_async_inference_replace_env_var_lets_2xx_with_invalid_utf8_succeed
        """Async version of the REPLACE check above."""
        async def run_test():
            settings = self._create_settings()
            service = _AsyncInferenceService(settings)

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

    def test_sync_inference_ignore_env_var_lets_2xx_with_invalid_utf8_succeed_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_sync_inference_ignore_env_var_lets_2xx_with_invalid_utf8_succeed
        """With IGNORE set, the bad byte is dropped and the response
        still parses cleanly."""
        settings = self._create_settings()
        service = _SyncInferenceService(settings)

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

    def test_async_inference_ignore_env_var_lets_2xx_with_invalid_utf8_succeed_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_async_inference_ignore_env_var_lets_2xx_with_invalid_utf8_succeed
        """Async equivalent of the sync IGNORE test above: with IGNORE set, the
        bad byte is dropped from the async inference response and parsing succeeds."""
        async def run_test():
            settings = self._create_settings()
            service = _AsyncInferenceService(settings)

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

    def test_sync_inference_response_timeout_raises_408_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_sync_inference_response_timeout_raises_408
        """Test that sync inference service converts ServiceResponseError to 408."""
        settings = self._create_settings()
        service = _SyncInferenceService(settings)

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

    def test_async_inference_response_timeout_raises_408_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_async_inference_response_timeout_raises_408
        """Test that async inference service converts ServiceResponseError to 408."""
        async def run_test():
            settings = self._create_settings()
            service = _AsyncInferenceService(settings)

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

    def test_connection_policy_default_inference_timeout_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_connection_policy_default_inference_timeout
        """Test that ConnectionPolicy defaults InferenceRequestTimeout to 5 seconds."""
        policy = ConnectionPolicy()
        self.assertEqual(policy.InferenceRequestTimeout, 5)

    def test_connection_policy_custom_inference_timeout_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_connection_policy_custom_inference_timeout
        """Test that ConnectionPolicy InferenceRequestTimeout can be set."""
        policy = ConnectionPolicy()
        policy.InferenceRequestTimeout = 30
        self.assertEqual(policy.InferenceRequestTimeout, 30)

    def test_sync_lazy_init_raises_error_without_env_var_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_sync_lazy_init_raises_error_without_env_var
        """Test that _InferenceService raises ValueError when env var is missing.
        With lazy init, this error is deferred from client construction to first use."""
        os.environ.pop(_INFERENCE_ENDPOINT_ENV_VAR, None)
        settings = self._create_settings()
        with self.assertRaises(ValueError) as ctx:
            _SyncInferenceService(settings)
        self.assertIn(_INFERENCE_ENDPOINT_ENV_VAR, str(ctx.exception))

    def test_async_lazy_init_raises_error_without_env_var_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_async_lazy_init_raises_error_without_env_var
        """Test that async _InferenceService raises ValueError when env var is missing.
        With lazy init, this error is deferred from client construction to first use."""
        os.environ.pop(_INFERENCE_ENDPOINT_ENV_VAR, None)
        settings = self._create_settings()
        with self.assertRaises(ValueError) as ctx:
            _AsyncInferenceService(settings)
        self.assertIn(_INFERENCE_ENDPOINT_ENV_VAR, str(ctx.exception))

    def test_sync_inference_service_created_with_env_var_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_sync_inference_service_created_with_env_var
        """Test that sync _InferenceService can be created when env var is set."""
        settings = self._create_settings()
        service = _SyncInferenceService(settings)
        self.assertIsNotNone(service)

    def test_async_inference_service_created_with_env_var_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_async_inference_service_created_with_env_var
        """Test that async _InferenceService can be created when env var is set."""
        settings = self._create_settings()
        service = _AsyncInferenceService(settings)
        self.assertIsNotNone(service)

    # ── InferenceClient.get_service() direct call tests ──

    def test_sync_get_inference_service_returns_service_with_aad_and_env_var_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_sync_get_inference_service_returns_service_with_aad_and_env_var
        """Test that InferenceClient.get_service() returns an _InferenceService when AAD
        credentials are present and the env var is set."""
        settings = self._create_settings()
        client = InferenceClient(settings, _SyncInferenceService)

        result = client.get_service()
        self.assertIsNotNone(result)

    def test_async_get_inference_service_returns_service_with_aad_and_env_var_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_async_get_inference_service_returns_service_with_aad_and_env_var
        """Test that async InferenceClient.get_service() returns an _InferenceService when AAD
        credentials are present and the env var is set."""
        settings = self._create_settings()
        client = InferenceClient(settings, _AsyncInferenceService)

        result = client.get_service()
        self.assertIsNotNone(result)

    def test_sync_get_inference_service_raises_error_without_env_var_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_sync_get_inference_service_raises_error_without_env_var
        """Test that InferenceClient.get_service() wraps ValueError into CosmosHttpResponseError
        when the env var is missing."""
        os.environ.pop(_INFERENCE_ENDPOINT_ENV_VAR, None)
        settings = self._create_settings()
        client = InferenceClient(settings, _SyncInferenceService)

        with self.assertRaises(exceptions.CosmosHttpResponseError) as ctx:
            client.get_service()
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Failed to initialize inference service", str(ctx.exception))

    def test_async_get_inference_service_raises_error_without_env_var_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_async_get_inference_service_raises_error_without_env_var
        """Test that async InferenceClient.get_service() wraps ValueError into CosmosHttpResponseError
        when the env var is missing."""
        os.environ.pop(_INFERENCE_ENDPOINT_ENV_VAR, None)
        settings = self._create_settings()
        client = InferenceClient(settings, _AsyncInferenceService)

        with self.assertRaises(exceptions.CosmosHttpResponseError) as ctx:
            client.get_service()
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Failed to initialize inference service", str(ctx.exception))

    def test_sync_get_inference_service_returns_none_without_aad_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_sync_get_inference_service_returns_none_without_aad
        """Test that InferenceClient.get_service() returns None when no AAD credentials
        are present (master key auth)."""
        settings = replace(self._create_settings(), aad_credentials=None)
        client = InferenceClient(settings, _SyncInferenceService)

        result = client.get_service()
        self.assertIsNone(result)

    def test_async_get_inference_service_returns_none_without_aad_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_async_get_inference_service_returns_none_without_aad
        """Test that async InferenceClient.get_service() returns None when no AAD credentials
        are present (master key auth)."""
        settings = replace(self._create_settings(), aad_credentials=None)
        client = InferenceClient(settings, _AsyncInferenceService)

        result = client.get_service()
        self.assertIsNone(result)

    def test_sync_get_inference_service_caches_instance_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_sync_get_inference_service_caches_instance
        """Test that InferenceClient.get_service() returns the same cached instance on
        repeated calls."""
        settings = self._create_settings()
        client = InferenceClient(settings, _SyncInferenceService)

        first = client.get_service()
        second = client.get_service()
        self.assertIsNotNone(first)
        self.assertIs(first, second)

    def test_async_get_inference_service_caches_instance_rust(self):
        # Source: tests/test_semantic_reranker_unit.py::TestInferenceServiceTimeout.test_async_get_inference_service_caches_instance
        """Test that async InferenceClient.get_service() returns the same cached instance on
        repeated calls."""
        settings = self._create_settings()
        client = InferenceClient(settings, _AsyncInferenceService)

        first = client.get_service()
        second = client.get_service()
        self.assertIsNotNone(first)
        self.assertIs(first, second)


if __name__ == "__main__":
    unittest.main()
