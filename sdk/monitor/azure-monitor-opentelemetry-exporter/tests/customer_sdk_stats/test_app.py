import os
import sys
import time
from unittest.mock import patch, Mock
from azure.core.exceptions import ServiceRequestError

# Set up environment variables FIRST
os.environ["APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW"] = "true"
os.environ["APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL"] = "true"
os.environ["APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL"] = "25"  # 25 seconds for testing

# Add the package to the path
sys.path.insert(0, r"C:\azure-sdk-for-python\sdk\monitor\azure-monitor-opentelemetry-exporter")

from azure.monitor.opentelemetry.exporter.export.trace._exporter import AzureMonitorTraceExporter
from azure.monitor.opentelemetry.exporter.statsbeat.customer._manager import CustomerSdkStatsManager
from azure.monitor.opentelemetry.exporter._storage import StorageExportResult
from azure.monitor.opentelemetry.exporter.export._base import ExportResult
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace
from opentelemetry.trace import SpanKind


def print_customer_sdkstats_state(customer_sdkstats):
    """Print the internal state of customer sdkstats"""
    if customer_sdkstats and customer_sdkstats.is_enabled:
        print("📊 Customer SDKStats internal state:")
        print(f"  Success count: {dict(customer_sdkstats._counters.total_item_success_count)}")
        print(f"  Drop count: {dict(customer_sdkstats._counters.total_item_drop_count)}")
        print(f"  Retry count: {dict(customer_sdkstats._counters.total_item_retry_count)}")
    else:
        print("❌ Customer SDKStats not available")


def main():
    print("=" * 70)
    print("Customer SDKStats Demo - Success, Retry, and Dropped Items")
    print("=" * 70)
    print()

    # Configuration
    connection_string = "InstrumentationKey=363331ca-f431-4119-bdcd-31a75920f958;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/"

    print("Configuration:")
    print(f"  Customer SDKStats: {os.environ.get('APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW', 'false')}")
    print(
        f"  SDKStats Export Interval: {os.environ.get('APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL', '900')} seconds"
    )
    print(f"  Connection String: {connection_string[:50]}...")
    print()

    # Set up tracing
    print("🔧 Setting up Azure Monitor tracing...")
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)

    azure_exporter = AzureMonitorTraceExporter(connection_string=connection_string)
    span_processor = BatchSpanProcessor(azure_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    print("✅ Azure Monitor tracing configured")

    # Initialize customer sdkstats
    customer_sdkstats = CustomerSdkStatsManager(connection_string)
    if customer_sdkstats and customer_sdkstats.is_enabled:
        print("✅ Customer SDKStats initialized")
    else:
        print("❌ Customer SDKStats not enabled")

    print_customer_sdkstats_state(customer_sdkstats)
    print()

    # Step 1: Generate successful telemetry
    print("🚀 Step 1: Generate successful dependency telemetry...")
    for i in range(3):
        with tracer.start_as_current_span(f"successful_dependency_{i}", kind=SpanKind.CLIENT) as span:
            span.set_attribute("http.method", "GET")
            span.set_attribute("http.url", f"https://api.example.com/item/{i}")
            span.set_attribute("http.status_code", 200)

    print("  Generated 3 successful dependency spans")
    span_processor.force_flush()
    time.sleep(2)

    print_customer_sdkstats_state(customer_sdkstats)
    print()

    # Step 2: Generate retry items (network errors)
    print("🚀 Step 2: Simulate network errors to generate retry items...")

    # Mock at the HTTP request level so the retry tracking logic in _base.py gets triggered
    from unittest.mock import MagicMock

    def mock_request_network_error(*args, **kwargs):
        print("    🌐 Simulated network error at HTTP level")
        raise ServiceRequestError("Connection timeout")

    # Patch the azure-core client's track method which is called by _transmit
    from azure.monitor.opentelemetry.exporter._generated import AzureMonitorClient

    with patch.object(AzureMonitorClient, "track", side_effect=mock_request_network_error):
        print("  📦 Mocking AzureMonitorClient.track() to raise ServiceRequestError")
        print("  🎯 Generating telemetry that will trigger retry tracking...")

        for i in range(4):
            with tracer.start_as_current_span(f"retry_dependency_{i}", kind=SpanKind.CLIENT) as span:
                span.set_attribute("http.method", "POST")
                span.set_attribute("http.url", f"https://api.retry.com/data/{i}")
                span.set_attribute("http.status_code", 200)
                span.set_attribute("test.scenario", "network_error")

        print("    Generated 4 dependency spans with network error simulation")
        print("    🔄 Forcing export (should trigger retry tracking)...")
        span_processor.force_flush()
        time.sleep(2)

    print_customer_sdkstats_state(customer_sdkstats)
    print()

    # Step 2.5: Generate retry items with integer retry codes (HTTP status codes like 429)
    print("🚀 Step 2.5: Simulate HTTP 429 (Too Many Requests) to generate retry items with integer retry code...")

    from azure.core.exceptions import HttpResponseError
    from azure.core.pipeline.transport import HttpResponse

    def mock_track_429(*args, **kwargs):
        print("    🔄 Track mocked: raising HttpResponseError with status 429")
        # Create a mock response object
        mock_response = Mock(spec=HttpResponse)
        mock_response.status_code = 429
        mock_response.reason = "Too Many Requests"
        raise HttpResponseError(response=mock_response)

    with patch.object(AzureMonitorClient, "track", side_effect=mock_track_429):

        print("  📦 Mocking AzureMonitorClient.track() to raise HTTP 429 (retryable)")
        print("  🎯 Generating telemetry that will be retried with integer retry code 429...")

        for i in range(3):
            with tracer.start_as_current_span(f"retryable_429_dependency_{i}", kind=SpanKind.CLIENT) as span:
                span.set_attribute("http.method", "POST")
                span.set_attribute("http.url", f"https://api.retryable.com/data/{i}")
                span.set_attribute("http.status_code", 200)
                span.set_attribute("test.scenario", "http_429_retry")

        print("    Generated 3 dependency spans that will be retried with HTTP 429")
        print("    🔄 Forcing export (should trigger retry tracking with retry_code=429)...")
        span_processor.force_flush()
        time.sleep(2)

    print_customer_sdkstats_state(customer_sdkstats)
    print()

    # Step 3: Generate dropped items (storage disabled)
    print("🚀 Step 3: Simulate storage failures to generate dropped items...")

    def mock_storage_disabled(*args, **kwargs):
        print("    📁 Storage mocked: returning CLIENT_STORAGE_DISABLED")
        return StorageExportResult.CLIENT_STORAGE_DISABLED

    def mock_transmit_failed_retryable(*args, **kwargs):
        print("    🌐 Transmission mocked: returning FAILED_RETRYABLE")
        return ExportResult.FAILED_RETRYABLE

    with patch.object(azure_exporter.storage, "put", side_effect=mock_storage_disabled), patch.object(
        azure_exporter, "_transmit", side_effect=mock_transmit_failed_retryable
    ):

        print("  📦 Mocking transmission failure + storage disabled")
        print("  🎯 Generating telemetry that will be dropped...")

        for i in range(5):
            with tracer.start_as_current_span(f"dropped_dependency_{i}", kind=SpanKind.CLIENT) as span:
                span.set_attribute("http.method", "POST")
                span.set_attribute("http.url", f"https://api.dropped.com/upload/{i}")
                span.set_attribute("http.status_code", 200)
                span.set_attribute("test.scenario", "storage_disabled")

        print("    Generated 5 dependency spans that will be dropped")
        print("    🔄 Forcing export (should trigger dropped tracking)...")
        span_processor.force_flush()
        time.sleep(2)

    print_customer_sdkstats_state(customer_sdkstats)
    print()

    # Step 3.5: Generate dropped items with integer drop codes (HTTP status codes)
    print("🚀 Step 3.5: Simulate HTTP 402 (Throttle/Quota) to generate dropped items with integer drop code...")

    from azure.core.exceptions import HttpResponseError
    from azure.core.pipeline.transport import HttpResponse

    def mock_track_402(*args, **kwargs):
        print("    🚫 Track mocked: raising HttpResponseError with status 402")
        # Create a mock response object
        mock_response = Mock(spec=HttpResponse)
        mock_response.status_code = 402
        mock_response.reason = "Payment Required - Quota Exceeded"
        raise HttpResponseError(response=mock_response)

    with patch.object(AzureMonitorClient, "track", side_effect=mock_track_402):

        print("  📦 Mocking AzureMonitorClient.track() to raise HTTP 402 (throttle/quota)")
        print("  🎯 Generating telemetry that will be dropped with integer drop code 402...")

        for i in range(3):
            with tracer.start_as_current_span(f"throttled_dependency_{i}", kind=SpanKind.CLIENT) as span:
                span.set_attribute("http.method", "POST")
                span.set_attribute("http.url", f"https://api.throttled.com/data/{i}")
                span.set_attribute("http.status_code", 200)
                span.set_attribute("test.scenario", "http_402_throttle")

        print("    Generated 3 dependency spans that will be dropped with HTTP 402")
        print("    🔄 Forcing export (should trigger dropped tracking with drop_code=402)...")
        span_processor.force_flush()
        time.sleep(2)

    print_customer_sdkstats_state(customer_sdkstats)
    print()

    # Step 4: Generate more successful telemetry
    print("🚀 Step 4: Generate final successful telemetry...")
    for i in range(2):
        with tracer.start_as_current_span(f"final_dependency_{i}", kind=SpanKind.CLIENT) as span:
            span.set_attribute("http.method", "GET")
            span.set_attribute("http.url", f"https://api.final.com/item/{i}")
            span.set_attribute("http.status_code", 200)

    print("  Generated 2 final successful dependency spans")
    span_processor.force_flush()
    time.sleep(2)

    print_customer_sdkstats_state(customer_sdkstats)
    print()

    # Wait for customer sdkstats export
    print("⏱️ Waiting 30 seconds for customer sdkstats export...")
    for i in range(30):
        if i % 5 == 0:
            print(f"  Waiting... {i+1}/30s")
        time.sleep(1)

    print()
    print("=" * 70)
    print("DEMO COMPLETED")
    print("=" * 70)
    print()
    print("📊 Final customer sdkstats state:")
    print_customer_sdkstats_state(customer_sdkstats)
    print()
    print("🔍 Check Application Insights for these metrics:")
    print("   - 'itemSuccessCount' (telemetry_type='dependency') ← Should show ~5 items")
    print("   - 'itemRetryCount' (telemetry_type='dependency') ← Should show ~7 items")
    print("      • retry_code='CLIENT_TIMEOUT' (4 items)")
    print("      • retry_code='429' (3 items)")
    print("   - 'itemDroppedCount' (telemetry_type='dependency') ← Should show ~8 items")
    print("      • drop_code='CLIENT_STORAGE_DISABLED' (5 items)")
    print("      • drop_code='402' (3 items)")
    print()
    print("Expected results:")
    print("   ✅ Success: ~5 items (3 initial + 2 final)")
    print("   🔄 Retry: ~7 items (4 network timeout + 3 HTTP 429)")
    print("   ❌ Dropped: ~8 items (5 storage disabled + 3 HTTP 402)")
    print()
    print("Query in Application Insights:")
    print("customMetrics")
    print("| where name in ('itemSuccessCount', 'itemRetryCount', 'itemDroppedCount')")
    print("| where timestamp > ago(5m)")
    print("| extend telemetry_type = tostring(customDimensions.telemetry_type)")
    print("| extend drop_code = tostring(customDimensions['drop.code'])")
    print("| extend retry_code = tostring(customDimensions['retry.code'])")
    print("| project timestamp, name, value, telemetry_type, drop_code, retry_code")
    print("| order by timestamp desc")
    print()
    print("✅ Demo completed!")
    print()


if __name__ == "__main__":
    main()
