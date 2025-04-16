# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import os
from typing import Any

from azure.storage.blob.aio import BlobServiceClient
from opentelemetry.trace import SpanKind, StatusCode
from opentelemetry.sdk.trace import ReadableSpan
from devtools_testutils import get_credential


class TestTracingAsync:
    """Test class for validating async distributed tracing functionality."""

    @pytest.mark.live_test_only
    @pytest.mark.asyncio
    async def test_blob_service_client_tracing_async(self, tracing_helper) -> None:
        """Test that tracing captures async client method calls and HTTP requests.

        This test validates that the distributed tracing functionality properly
        captures spans when using the async Blob service client, ensuring parent-child
        relationships are maintained and attributes are correctly populated.
        """
        account_url = os.environ.get("AZURE_STORAGE_BLOB_ENDPOINT")
        if not account_url:
            pytest.skip("AZURE_STORAGE_BLOB_ENDPOINT environment variable is not set.")

        client = BlobServiceClient(account_url=account_url, credential=get_credential(is_async=True))

        with tracing_helper.tracer.start_as_current_span(name="root") as parent:
            await client.get_service_properties()

        # Close the client explicitly
        await client.close()

        spans = tracing_helper.exporter.get_finished_spans()
        span_names_list = [span.name for span in spans]
        # Check that last 3 spans are the expected ones (auth-related ones may vary)
        assert span_names_list[-3:] == ["GET", "BlobServiceClient.get_service_properties", "root"]

        http_span: ReadableSpan = spans[-3]
        assert http_span.kind == SpanKind.CLIENT
        assert http_span.parent
        assert http_span.parent.span_id == spans[-2].context.span_id

        # Validate HTTP span attributes
        assert http_span.attributes
        assert http_span.attributes["http.request.method"] == "GET"
        assert http_span.attributes["url.full"]
        assert http_span.attributes["server.address"]
        assert http_span.attributes["http.response.status_code"] == 200
        user_agent = http_span.attributes.get("user_agent.original", "")
        assert isinstance(user_agent, str) and "storage" in user_agent

        # Validate method span
        method_span: ReadableSpan = spans[-2]
        assert method_span.kind == SpanKind.INTERNAL
        assert method_span.parent
        assert method_span.parent.span_id == spans[-1].context.span_id

    @pytest.mark.live_test_only
    @pytest.mark.asyncio
    async def test_error_handling_with_tracing_async(self, tracing_helper) -> None:
        """Test that tracing properly captures error information in async operations.

        This test validates that when exceptions occur during async operations,
        the spans correctly capture the error information.
        """
        account_name = "nonexistentaccount"
        invalid_url = f"https://{account_name}.blob.core.windows.net/"

        client = BlobServiceClient(account_url=invalid_url, credential=get_credential(is_async=True))

        # Expecting this operation to fail
        with tracing_helper.tracer.start_as_current_span(name="root") as parent:
            try:
                await client.get_service_properties()
            except Exception:
                # We expect an exception but want to verify the spans
                pass

        # Close the client explicitly
        await client.close()

        spans = tracing_helper.exporter.get_finished_spans()
        span_names_list = [span.name for span in spans]
        # Check that last 3 spans are the expected ones (auth-related ones may vary)
        assert span_names_list[-3:] == ["GET", "BlobServiceClient.get_service_properties", "root"]

        http_span: ReadableSpan = spans[-3]
        assert http_span.kind == SpanKind.CLIENT
        assert http_span.attributes
        assert http_span.attributes["error.type"] == "azure.core.exceptions.ServiceRequestError"
        assert http_span.status.status_code == StatusCode.ERROR
