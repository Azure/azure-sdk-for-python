# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import uuid

from opentelemetry.trace import SpanKind as OpenTelemetrySpanKind

from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.core.tracing.ext.opentelemetry_span._schema import OpenTelemetrySchema, OpenTelemetrySchemaVersion


class TestOpenTelemetrySchema:
    @staticmethod
    def _get_span_schema_url(span_instance):
        scope = getattr(span_instance, "instrumentation_scope", None)
        if scope is None:
            scope = getattr(span_instance, "instrumentation_info", None)
        return getattr(scope, "schema_url", None)

    def test_latest_schema_attributes_renamed(self):
        with OpenTelemetrySpan(name="Root") as wrapped_class:
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

    def test_latest_schema_attributes_not_renamed(self):
        with OpenTelemetrySpan(name="Root") as wrapped_class:
            wrapped_class.add_attribute("foo", "bar")
            wrapped_class.add_attribute("baz", "qux")

            assert wrapped_class.span_instance.attributes.get("foo") == "bar"
            assert wrapped_class.span_instance.attributes.get("baz") == "qux"

    def test_schema_url_in_instrumentation_scope(self):
        with OpenTelemetrySpan(name="span") as span:
            schema_url = OpenTelemetrySchema.get_schema_url(span._schema_version)
            assert self._get_span_schema_url(span.span_instance) == schema_url

    def test_schema_version_argument(self):
        with OpenTelemetrySpan(name="span", schema_version="1.0.0") as span:
            assert span._schema_version == "1.0.0"
            assert span._attribute_mappings == {}
            assert self._get_span_schema_url(span.span_instance) == "https://opentelemetry.io/schemas/1.0.0"

    def test_schema_version_formats(self):
        assert OpenTelemetrySchema.get_attribute_mappings(OpenTelemetrySchemaVersion.V1_19_0)
        assert OpenTelemetrySchema.get_attribute_mappings(OpenTelemetrySchemaVersion.V1_23_1)
        assert OpenTelemetrySchema.get_attribute_mappings("1.19.0")
        assert OpenTelemetrySchema.get_attribute_mappings("1.23.1")
        assert not OpenTelemetrySchema.get_attribute_mappings("1.0.0")

    def test_get_latest_version_returns_last_supported_version(self):
        latest = OpenTelemetrySchema.get_latest_version()

        assert latest == OpenTelemetrySchemaVersion.V1_23_1
        assert latest == OpenTelemetrySchema.SUPPORTED_VERSIONS[-1]
