import warnings
from unittest import TestCase
from unittest.mock import patch

from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.monitor.opentelemetry._autoinstrumentation.distro import (
    AzureMonitorDistro,
)
from azure.monitor.opentelemetry._diagnostics.diagnostic_logging import (
    _ATTACH_FAILURE_DISTRO,
    _ATTACH_SUCCESS_DISTRO
)


class TestDistro(TestCase):
    @patch("azure.monitor.opentelemetry._autoinstrumentation.distro._is_attach_enabled", return_value=True)
    @patch("azure.monitor.opentelemetry._autoinstrumentation.distro.settings")
    @patch(
        "azure.monitor.opentelemetry._autoinstrumentation.distro.AzureDiagnosticLogging"
    )
    def test_configure(self, mock_diagnostics, azure_core_mock, attach_mock):
        distro = AzureMonitorDistro()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            distro.configure()
        mock_diagnostics.info.assert_called_once_with(
            "Azure Monitor OpenTelemetry Distro configured successfully.",
            _ATTACH_SUCCESS_DISTRO
        )
        self.assertEqual(
            azure_core_mock.tracing_implementation, OpenTelemetrySpan
        )

    @patch.dict("os.environ", {"OTEL_PYTHON_DISABLED_INSTRUMENTATIONS": " flask,azure_sdk , urllib3"})
    @patch("azure.monitor.opentelemetry._autoinstrumentation.distro._is_attach_enabled", return_value=True)
    @patch("azure.monitor.opentelemetry._autoinstrumentation.distro.settings")
    @patch(
        "azure.monitor.opentelemetry._autoinstrumentation.distro.AzureDiagnosticLogging"
    )
    def test_configure_disable_azure_core(self, mock_diagnostics, azure_core_mock, attach_mock):
        distro = AzureMonitorDistro()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            distro.configure()
        mock_diagnostics.info.assert_called_once_with(
            "Azure Monitor OpenTelemetry Distro configured successfully.",
            _ATTACH_SUCCESS_DISTRO
        )
        self.assertNotEqual(
            azure_core_mock.tracing_implementation, OpenTelemetrySpan
        )
    @patch("azure.monitor.opentelemetry._autoinstrumentation.distro._is_attach_enabled", return_value=False)
    @patch("azure.monitor.opentelemetry._autoinstrumentation.distro.settings")
    @patch(
        "azure.monitor.opentelemetry._autoinstrumentation.distro.AzureDiagnosticLogging"
    )
    def test_configure_preview(self, mock_diagnostics, azure_core_mock, attach_mock):
        distro = AzureMonitorDistro()
        with self.assertWarns(Warning):
            distro.configure()
        mock_diagnostics.info.assert_called_once_with(
            "Azure Monitor OpenTelemetry Distro configured successfully.",
            _ATTACH_SUCCESS_DISTRO
        )
        self.assertEqual(
            azure_core_mock.tracing_implementation, OpenTelemetrySpan
        )

    @patch("azure.monitor.opentelemetry._autoinstrumentation.distro._configure_auto_instrumentation")
    @patch("azure.monitor.opentelemetry._autoinstrumentation.distro._is_attach_enabled", return_value=True)
    @patch("azure.monitor.opentelemetry._autoinstrumentation.distro.settings")
    @patch(
        "azure.monitor.opentelemetry._autoinstrumentation.distro.AzureDiagnosticLogging"
    )
    def test_configure_exc(self, mock_diagnostics, azure_core_mock, attach_mock, configure_mock):
        distro = AzureMonitorDistro()
        configure_mock.side_effect = Exception("Test Exception")
        with self.assertRaises(Exception):
            distro.configure()
        mock_diagnostics.error.assert_called_once_with(
            "Azure Monitor OpenTelemetry Distro failed during configuration: Test Exception",
            _ATTACH_FAILURE_DISTRO
        )
