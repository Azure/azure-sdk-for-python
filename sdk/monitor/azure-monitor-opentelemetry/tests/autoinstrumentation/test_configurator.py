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


@patch.dict("os.environ", {}, clear=True)
class TestConfigurator(TestCase):
    @patch("azure.monitor.opentelemetry._autoinstrumentation.configurator.super")
    @patch("azure.monitor.opentelemetry._autoinstrumentation.configurator.ApplicationInsightsSampler")
    @patch("azure.monitor.opentelemetry._autoinstrumentation.configurator._is_attach_enabled", return_value=True)
    @patch(
        "azure.monitor.opentelemetry._autoinstrumentation.configurator.AzureDiagnosticLogging"
    )
    def test_configure(self, mock_diagnostics, attach_mock, sampler_mock, super_mock):
        sampler_mock.return_value = "TEST_SAMPLER"
        configurator = AzureMonitorConfigurator()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            configurator._configure(auto_instrumentation_version="TEST_VERSION")
        sampler_mock.assert_called_once_with(1.0)
        super_mock()._configure.assert_called_once_with(
            auto_instrumentation_version="TEST_VERSION",
            trace_exporter_names=["azure_monitor_opentelemetry_exporter"],
            metric_exporter_names=["azure_monitor_opentelemetry_exporter"],
            log_exporter_names=["azure_monitor_opentelemetry_exporter"],
            sampler="TEST_SAMPLER",
        )
        mock_diagnostics.info.assert_called_once_with(
            "Azure Monitor Configurator configured successfully.",
            _ATTACH_SUCCESS_CONFIGURATOR
        )


    @patch.dict("os.environ", {"OTEL_TRACES_SAMPLER_ARG": "0.5"}, clear=True)
    @patch("azure.monitor.opentelemetry._autoinstrumentation.configurator.super")
    @patch("azure.monitor.opentelemetry._autoinstrumentation.configurator.ApplicationInsightsSampler")
    @patch("azure.monitor.opentelemetry._autoinstrumentation.configurator._is_attach_enabled", return_value=True)
    @patch(
        "azure.monitor.opentelemetry._autoinstrumentation.configurator.AzureDiagnosticLogging"
    )
    def test_configure_sampler_arg(self, mock_diagnostics, attach_mock, sampler_mock, super_mock):
        sampler_mock.return_value = "TEST_SAMPLER"
        configurator = AzureMonitorConfigurator()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            configurator._configure(auto_instrumentation_version="TEST_VERSION")
        sampler_mock.assert_called_once_with(0.5)
        super_mock()._configure.assert_called_once_with(
            auto_instrumentation_version="TEST_VERSION",
            trace_exporter_names=["azure_monitor_opentelemetry_exporter"],
            metric_exporter_names=["azure_monitor_opentelemetry_exporter"],
            log_exporter_names=["azure_monitor_opentelemetry_exporter"],
            sampler="TEST_SAMPLER",
        )
        mock_diagnostics.info.assert_called_once_with(
            "Azure Monitor Configurator configured successfully.",
            _ATTACH_SUCCESS_CONFIGURATOR
        )


    @patch("azure.monitor.opentelemetry._autoinstrumentation.configurator.super")
    @patch("azure.monitor.opentelemetry._autoinstrumentation.configurator.ApplicationInsightsSampler")
    @patch("azure.monitor.opentelemetry._autoinstrumentation.configurator._is_attach_enabled", return_value=False)
    @patch(
        "azure.monitor.opentelemetry._autoinstrumentation.configurator.AzureDiagnosticLogging"
    )
    def test_configure_preview(self, mock_diagnostics, attach_mock, sampler_mock, super_mock):
        sampler_mock.return_value = "TEST_SAMPLER"
        configurator = AzureMonitorConfigurator()
        with self.assertWarns(Warning):
            configurator._configure()
        sampler_mock.assert_called_once_with(1.0)
        super_mock()._configure.assert_called_once_with(
            trace_exporter_names=["azure_monitor_opentelemetry_exporter"],
            metric_exporter_names=["azure_monitor_opentelemetry_exporter"],
            log_exporter_names=["azure_monitor_opentelemetry_exporter"],
            sampler="TEST_SAMPLER",
        )
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
