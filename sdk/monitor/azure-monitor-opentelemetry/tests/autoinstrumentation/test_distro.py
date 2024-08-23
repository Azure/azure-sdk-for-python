from os import environ
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
    @patch.dict("os.environ", {}, clear=True)
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
        self.assertEqual(
            environ,
            {
                "OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED": "true",
                "OTEL_EXPERIMENTAL_RESOURCE_DETECTORS": "azure_app_service",
            }
        )

    @patch.dict("os.environ", {
        # "OTEL_METRICS_EXPORTER": "custom_metrics_exporter",
        # "OTEL_TRACES_EXPORTER": "custom_traces_exporter",
        # "OTEL_LOGS_EXPORTER": "custom_logs_exporter",
        # "OTEL_TRACES_SAMPLER": "custom_traces_sampler",
        "OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED": "false",
        "OTEL_EXPERIMENTAL_RESOURCE_DETECTORS": "custom_resource_detector",
    }, clear=True)
    @patch("azure.monitor.opentelemetry._autoinstrumentation.distro._is_attach_enabled", return_value=True)
    @patch("azure.monitor.opentelemetry._autoinstrumentation.distro.settings")
    @patch(
        "azure.monitor.opentelemetry._autoinstrumentation.distro.AzureDiagnosticLogging"
    )
    def test_configure_env_vars_set(self, mock_diagnostics, azure_core_mock, attach_mock):
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
        self.assertEqual(
            environ,
            {
                # "OTEL_METRICS_EXPORTER": "custom_metrics_exporter",
                # "OTEL_TRACES_EXPORTER": "custom_traces_exporter",
                # "OTEL_LOGS_EXPORTER": "custom_logs_exporter",
                # "OTEL_TRACES_SAMPLER": "custom_traces_sampler",
                "OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED": "false",
                "OTEL_EXPERIMENTAL_RESOURCE_DETECTORS": "custom_resource_detector",
            }
        )

    @patch.dict("os.environ", {"OTEL_PYTHON_DISABLED_INSTRUMENTATIONS": " flask,azure_sdk , urllib3"}, clear=True)
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
