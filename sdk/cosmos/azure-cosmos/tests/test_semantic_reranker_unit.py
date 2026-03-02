# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
# cspell:ignore rerank reranker reranking
"""Unit tests for semantic reranker inference service timeout policy."""
import asyncio
import os
import unittest
from unittest.mock import MagicMock, patch

from azure.core.exceptions import ServiceRequestError

import azure.cosmos.exceptions as exceptions

os.environ["AZURE_COSMOS_SEMANTIC_RERANKER_INFERENCE_ENDPOINT"] = "https://test.endpoint.com"


class TestInferenceServiceTimeout(unittest.TestCase):
    """Unit tests for inference service timeout behavior."""

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
        from azure.cosmos._inference_service import _InferenceService

        mock_connection = self._create_mock_connection()
        service = _InferenceService(mock_connection)

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
            from azure.cosmos.aio._inference_service_async import _InferenceService

            mock_connection = self._create_mock_connection()
            mock_connection.connection_policy.DisableSSLVerification = False
            service = _InferenceService(mock_connection)

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
        from azure.cosmos._inference_service import _InferenceService

        mock_connection = self._create_mock_connection(inference_request_timeout=10)
        service = _InferenceService(mock_connection)

        self.assertEqual(service._inference_request_timeout, 10)

    def test_async_inference_timeout_value_from_connection_policy(self):
        """Test that async inference service reads timeout from connection policy."""
        from azure.cosmos.aio._inference_service_async import _InferenceService

        mock_connection = self._create_mock_connection(inference_request_timeout=15)
        mock_connection.connection_policy.DisableSSLVerification = False
        service = _InferenceService(mock_connection)

        self.assertEqual(service._inference_request_timeout, 15)

    def test_sync_inference_passes_timeout_to_pipeline(self):
        """Test that sync inference service passes timeout kwargs to pipeline.run()."""
        from azure.cosmos._inference_service import _InferenceService

        mock_connection = self._create_mock_connection(inference_request_timeout=7)
        service = _InferenceService(mock_connection)

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
            from azure.cosmos.aio._inference_service_async import _InferenceService

            mock_connection = self._create_mock_connection(inference_request_timeout=12)
            mock_connection.connection_policy.DisableSSLVerification = False
            service = _InferenceService(mock_connection)

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

    def test_connection_policy_default_inference_timeout(self):
        """Test that ConnectionPolicy defaults InferenceRequestTimeout to 5 seconds."""
        from azure.cosmos.documents import ConnectionPolicy

        policy = ConnectionPolicy()
        self.assertEqual(policy.InferenceRequestTimeout, 5)

    def test_connection_policy_custom_inference_timeout(self):
        """Test that ConnectionPolicy InferenceRequestTimeout can be set."""
        from azure.cosmos.documents import ConnectionPolicy

        policy = ConnectionPolicy()
        policy.InferenceRequestTimeout = 30
        self.assertEqual(policy.InferenceRequestTimeout, 30)


if __name__ == "__main__":
    unittest.main()
