import warnings
from unittest import TestCase
from unittest.mock import patch

from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.monitor.opentelemetry._autoinstrumentation.configurator import (
    AzureMonitorConfigurator,
)


class TestConfigurator(TestCase):
    @patch("azure.monitor.opentelemetry._autoinstrumentation.configurator._is_attach_enabled", return_value=True)
    @patch(
        "azure.monitor.opentelemetry._autoinstrumentation.configurator.AzureDiagnosticLogging.enable"
    )
    def test_configure(self, mock_diagnostics, attach_mock):
        configurator = AzureMonitorConfigurator()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            configurator._configure()
        mock_diagnostics.assert_called_once()

    @patch("azure.monitor.opentelemetry._autoinstrumentation.configurator._is_attach_enabled", return_value=False)
    @patch(
        "azure.monitor.opentelemetry._autoinstrumentation.configurator.AzureDiagnosticLogging.enable"
    )
    def test_configure_preview(self, mock_diagnostics, attach_mock):
        configurator = AzureMonitorConfigurator()
        with self.assertWarns(Warning):
            configurator._configure()
        mock_diagnostics.assert_called_once()
