from unittest import TestCase
from unittest.mock import patch

from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.monitor.opentelemetry.autoinstrumentation._distro import (
    AzureMonitorDistro,
)


class TestDistro(TestCase):
    @patch("azure.monitor.opentelemetry.autoinstrumentation._distro.settings")
    @patch(
        "azure.monitor.opentelemetry.autoinstrumentation._distro.AzureDiagnosticLogging.enable"
    )
    def test_configure(self, mock_diagnostics, azure_core_mock):
        distro = AzureMonitorDistro()
        distro.configure()
        self.assertEqual(mock_diagnostics.call_count, 2)
        self.assertEqual(
            azure_core_mock.tracing_implementation, OpenTelemetrySpan
        )
