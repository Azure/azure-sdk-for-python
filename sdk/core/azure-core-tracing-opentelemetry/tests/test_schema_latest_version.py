from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySchema


def test_get_latest_version_returns_last_supported_version():
    latest_version = OpenTelemetrySchema.get_latest_version()

    assert latest_version == OpenTelemetrySchema.SUPPORTED_VERSIONS[-1]
    assert OpenTelemetrySchema.get_attribute_mappings(latest_version)
