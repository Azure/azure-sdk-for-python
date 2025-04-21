# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import os

from azure.storage.blob import BlobServiceClient
from opentelemetry.trace import SpanKind, StatusCode
from opentelemetry.sdk.trace import ReadableSpan
from devtools_testutils import get_credential


class TestTracing:

    @pytest.mark.live_test_only
    def test_blob_service_client_tracing(self, tracing_helper):
        """Test that tracing captures client method calls and HTTP requests.

        This test validates that the distributed tracing functionality properly
        captures spans when using the Blob service client, ensuring parent-child
        relationships are maintained and attributes are correctly populated.
        """
        account_url = os.environ.get("AZURE_STORAGE_BLOB_ENDPOINT")
        if not account_url:
            pytest.skip("AZURE_STORAGE_BLOB_ENDPOINT environment variable is not set.")

        client = BlobServiceClient(account_url=account_url, credential=get_credential())

        with tracing_helper.tracer.start_as_current_span(name="root") as parent:
            client.get_service_properties()

        spans = tracing_helper.exporter.get_finished_spans()
        span_names_list = [span.name for span in spans]
        # Check that last 3 spans are the expected ones (auth-related ones may vary)
        assert span_names_list[-3:] == ["GET", "BlobServiceClient.get_service_properties", "root"]

        http_span: ReadableSpan = spans[-3]
        assert http_span.kind == SpanKind.CLIENT
        assert http_span.parent
        assert http_span.parent.span_id == spans[-2].context.span_id

        assert http_span.attributes
        assert http_span.attributes["http.request.method"] == "GET"
        assert http_span.attributes["url.full"]
        assert http_span.attributes["server.address"]
        assert http_span.attributes["http.response.status_code"] == 200
        user_agent = http_span.attributes.get("user_agent.original", "")
        assert isinstance(user_agent, str) and "storage" in user_agent

        method_span: ReadableSpan = spans[-2]
        assert method_span.kind == SpanKind.INTERNAL
        assert method_span.parent
        assert method_span.parent.span_id == spans[-1].context.span_id

    @pytest.mark.live_test_only
    def test_error_handling_with_tracing(self, tracing_helper) -> None:
        """Test that tracing properly captures error information in operations.

        This test validates that when exceptions occur during operations,
        the spans correctly capture the error information.

        :param tracing_helper: Helper fixture that provides tracing functionality
        :type tracing_helper: Any
        """
        account_name = "nonexistentaccount"
        invalid_url = f"https://{account_name}.blob.core.windows.net/"

        client = BlobServiceClient(account_url=invalid_url, credential=get_credential())

        # Expecting this operation to fail
        with tracing_helper.tracer.start_as_current_span(name="root") as parent:
            try:
                client.get_service_properties()
            except Exception:
                # We expect an exception but want to verify the spans
                pass

        spans = tracing_helper.exporter.get_finished_spans()
        span_names_list = [span.name for span in spans]
        # Check that last 3 spans are the expected ones (auth-related ones may vary)
        assert span_names_list[-3:] == ["GET", "BlobServiceClient.get_service_properties", "root"]

        http_span: ReadableSpan = spans[-3]
        assert http_span.kind == SpanKind.CLIENT
        assert http_span.attributes
        assert http_span.attributes["error.type"] == "azure.core.exceptions.ServiceRequestError"
        assert http_span.status.status_code == StatusCode.ERROR
