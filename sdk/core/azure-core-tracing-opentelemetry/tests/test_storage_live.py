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
    def test_blob_service_client_tracing(self, config, exporter, tracer):
        connection_string = config["storage_connection_string"]
        client = BlobServiceClient.from_connection_string(connection_string)

        with tracer.start_as_current_span(name="root") as parent:
            client.get_service_properties()

        spans = exporter.get_finished_spans()

        # We expect 3 spans, one for the root span, one for the method call, and one for the HTTP request.
        assert len(spans) == 3
        span_names_list = [span.name for span in spans]
        assert span_names_list == ["/", "BlobServiceClient.get_service_properties", "root"]

        http_span: ReadableSpan = spans[0]
        assert http_span.kind == SpanKind.CLIENT
        assert http_span.parent.span_id == spans[1].context.span_id

        method_span: ReadableSpan = spans[1]
        assert method_span.kind == SpanKind.INTERNAL
        assert method_span.parent.span_id == spans[2].context.span_id
