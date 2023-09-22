import warnings
from unittest import TestCase
from unittest.mock import patch

from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.monitor.opentelemetry._autoinstrumentation.configurator import (
    AzureMonitorConfigurator,
)
from azure.monitor.opentelemetry._diagnostics.diagnostic_logging import (
    _ATTACH_FAILURE_CONFIGURATOR,
    _ATTACH_SUCCESS_CONFIGURATOR
)


class TestConfigurator(TestCase):
    @patch("azure.monitor.opentelemetry._autoinstrumentation.configurator._is_attach_enabled", return_value=True)
    @patch(
        "azure.monitor.opentelemetry._autoinstrumentation.configurator.AzureDiagnosticLogging"
    )
    def test_configure(self, mock_diagnostics, attach_mock):
        configurator = AzureMonitorConfigurator()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            configurator._configure()
        mock_diagnostics.info.assert_called_once_with(
            "Azure Monitor Configurator configured successfully.",
            _ATTACH_SUCCESS_CONFIGURATOR
        )

    @patch("azure.monitor.opentelemetry._autoinstrumentation.configurator._is_attach_enabled", return_value=False)
    @patch(
        "azure.monitor.opentelemetry._autoinstrumentation.configurator.AzureDiagnosticLogging"
    )
    def test_configure_preview(self, mock_diagnostics, attach_mock):
        configurator = AzureMonitorConfigurator()
        with self.assertWarns(Warning):
            configurator._configure()
        mock_diagnostics.info.assert_called_once_with(
            "Azure Monitor Configurator configured successfully.",
            _ATTACH_SUCCESS_CONFIGURATOR
        )

    @patch("azure.monitor.opentelemetry._autoinstrumentation.configurator.super")
    @patch("azure.monitor.opentelemetry._autoinstrumentation.configurator._is_attach_enabled", return_value=True)
    @patch(
        "azure.monitor.opentelemetry._autoinstrumentation.configurator.AzureDiagnosticLogging"
    )
    def test_configure_exc(self, mock_diagnostics, attach_mock, super_mock):
        configurator = AzureMonitorConfigurator()
        super_mock()._configure.side_effect = Exception("Test Exception")
        with self.assertRaises(Exception):
            configurator._configure()
        mock_diagnostics.error.assert_called_once_with(
            "Azure Monitor Configurator failed during configuration: Test Exception",
            _ATTACH_FAILURE_CONFIGURATOR
        )
