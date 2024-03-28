# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.storage.blob import BlobServiceClient
from opentelemetry.trace import SpanKind
from opentelemetry.sdk.trace import ReadableSpan


class TestStorageTracing:
    @pytest.mark.live_test_only
    def test_blob_service_client_tracing(self, config, tracing_helper):
        connection_string = config["storage_connection_string"]
        client = BlobServiceClient.from_connection_string(connection_string)

        with tracing_helper.tracer.start_as_current_span(name="root") as parent:
            client.get_service_properties()

        spans = tracing_helper.exporter.get_finished_spans()

        # We expect 3 spans, one for the root span, one for the method call, and one for the HTTP request.
        assert len(spans) == 3
        span_names_list = [span.name for span in spans]
        assert span_names_list == ["/", "BlobServiceClient.get_service_properties", "root"]

        http_span: ReadableSpan = spans[0]
        assert http_span.kind == SpanKind.CLIENT
        assert http_span.parent
        assert http_span.parent.span_id == spans[1].context.span_id

        assert http_span.attributes
        assert http_span.attributes["http.request.method"] == "GET"
        assert http_span.attributes["url.full"]
        assert http_span.attributes["server.address"]
        assert http_span.attributes["http.response.status_code"] == 200
        assert http_span.attributes["az.client_request_id"]
        assert http_span.attributes["az.service_request_id"]

        method_span: ReadableSpan = spans[1]
        assert method_span.kind == SpanKind.INTERNAL
        assert method_span.parent
        assert method_span.parent.span_id == spans[2].context.span_id
