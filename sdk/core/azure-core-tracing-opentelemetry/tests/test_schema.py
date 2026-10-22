# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import uuid

from opentelemetry.trace import SpanKind as OpenTelemetrySpanKind

from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.core.tracing.ext.opentelemetry_span._schema import OpenTelemetrySchema, OpenTelemetrySchemaVersion


class TestOpenTelemetrySchema:
    def test_latest_schema_attributes_renamed(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root", kind=OpenTelemetrySpanKind.CLIENT) as parent:
            wrapped_class = OpenTelemetrySpan(span=parent)
            schema_version = wrapped_class._schema_version
            attribute_mappings = OpenTelemetrySchema.get_attribute_mappings(schema_version)
            attribute_values = {}
            for key, value in attribute_mappings.items():
                attribute_values[value] = uuid.uuid4().hex
                # Add attribute using key that is not following OpenTelemetry semantic conventions.
                wrapped_class.add_attribute(key, attribute_values[value])

            for attribute, expected_value in attribute_values.items():
                # Check that expected renamed attribute is present with the correct value.
                assert wrapped_class.span_instance.attributes.get(attribute) == expected_value

            for key in attribute_mappings:
                # Check that original attribute is not present.
                assert wrapped_class.span_instance.attributes.get(key) is None

    def test_latest_schema_attributes_not_renamed(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("Root", kind=OpenTelemetrySpanKind.CLIENT) as parent:
            wrapped_class = OpenTelemetrySpan(span=parent)

            wrapped_class.add_attribute("foo", "bar")
            wrapped_class.add_attribute("baz", "qux")

            assert wrapped_class.span_instance.attributes.get("foo") == "bar"
            assert wrapped_class.span_instance.attributes.get("baz") == "qux"

    def test_schema_url_in_instrumentation_scope(self):
        with OpenTelemetrySpan(name="span") as span:
            schema_url = OpenTelemetrySchema.get_schema_url(span._schema_version)
            assert span.span_instance.instrumentation_scope.schema_url == schema_url

    def test_schema_version_argument(self, tracing_helper):
        with OpenTelemetrySpan(name="span", schema_version="1.0.0") as span:
            assert span._schema_version == "1.0.0"
            assert span._attribute_mappings == {}
            assert span.span_instance.instrumentation_scope.schema_url == "https://opentelemetry.io/schemas/1.0.0"

    def test_schema_version_formats(self, tracing_helper):
        assert OpenTelemetrySchema.get_attribute_mappings(OpenTelemetrySchemaVersion.V1_19_0)
        assert OpenTelemetrySchema.get_attribute_mappings(OpenTelemetrySchemaVersion.V1_23_1)
        assert OpenTelemetrySchema.get_attribute_mappings("1.19.0")
        assert OpenTelemetrySchema.get_attribute_mappings("1.23.1")
        assert not OpenTelemetrySchema.get_attribute_mappings("1.0.0")
