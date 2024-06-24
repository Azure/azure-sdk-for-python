# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest
from unittest.mock import Mock, call, patch

from opentelemetry.sdk.resources import Resource

from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.monitor.opentelemetry._configure import (
    _send_attach_warning,
    _setup_instrumentations,
    _setup_live_metrics,
    _setup_logging,
    _setup_metrics,
    _setup_tracing,
    configure_azure_monitor,
)
from azure.monitor.opentelemetry._diagnostics.diagnostic_logging import _DISTRO_DETECTS_ATTACH


TEST_RESOURCE = Resource({"foo": "bar"})


class TestConfigure(unittest.TestCase):
    @patch(
        "azure.monitor.opentelemetry._configure._send_attach_warning",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_instrumentations",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_live_metrics",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_metrics",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_logging",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_tracing",
    )
    def test_configure_azure_monitor(
        self,
        tracing_mock,
        logging_mock,
        metrics_mock,
        live_metrics_mock,
        instrumentation_mock,
        detect_attach_mock,
    ):
        kwargs = {
            "connection_string": "test_cs",
        }
        configure_azure_monitor(**kwargs)
        tracing_mock.assert_called_once()
        logging_mock.assert_called_once()
        metrics_mock.assert_called_once()
        live_metrics_mock.assert_not_called()
        instrumentation_mock.assert_called_once()
        detect_attach_mock.assert_called_once()

    @patch(
        "azure.monitor.opentelemetry._configure._setup_instrumentations",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_live_metrics",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_metrics",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_logging",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_tracing",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._get_configurations",
    )
    def test_configure_azure_monitor_disable_tracing(
        self,
        config_mock,
        tracing_mock,
        logging_mock,
        metrics_mock,
        live_metrics_mock,
        instrumentation_mock,
    ):
        configurations = {
            "connection_string": "test_cs",
            "disable_tracing": True,
            "disable_logging": False,
            "disable_metrics": False,
            "instrumentation_options": {
                "flask": {
                    "enabled": False
                },
                "django": {
                    "enabled": False
                },
                "requests": {
                    "enabled": False
                },
            },
            "enable_live_metrics": False,
            "resource": TEST_RESOURCE,
        }
        config_mock.return_value = configurations
        configure_azure_monitor()
        tracing_mock.assert_not_called()
        logging_mock.assert_called_once_with(configurations)
        metrics_mock.assert_called_once_with(configurations)
        live_metrics_mock.assert_not_called()
        instrumentation_mock.assert_called_once_with(configurations)

    @patch(
        "azure.monitor.opentelemetry._configure._setup_instrumentations",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_live_metrics",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_metrics",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_logging",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_tracing",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._get_configurations",
    )
    def test_configure_azure_monitor_disable_logging(
        self,
        config_mock,
        tracing_mock,
        logging_mock,
        metrics_mock,
        live_metrics_mock,
        instrumentation_mock,
    ):
        configurations = {
            "connection_string": "test_cs",
            "disable_tracing": False,
            "disable_logging": True,
            "disable_metrics": False,
            "enable_live_metrics": False,
            "resource": TEST_RESOURCE,
        }
        config_mock.return_value = configurations
        configure_azure_monitor()
        tracing_mock.assert_called_once_with(configurations)
        logging_mock.assert_not_called()
        metrics_mock.assert_called_once_with(configurations)
        live_metrics_mock.assert_not_called()
        instrumentation_mock.assert_called_once_with(configurations)

    @patch(
        "azure.monitor.opentelemetry._configure._setup_instrumentations",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_live_metrics",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_metrics",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_logging",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_tracing",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._get_configurations",
    )
    def test_configure_azure_monitor_disable_metrics(
        self,
        config_mock,
        tracing_mock,
        logging_mock,
        metrics_mock,
        live_metrics_mock,
        instrumentation_mock,
    ):
        configurations = {
            "connection_string": "test_cs",
            "disable_tracing": False,
            "disable_logging": False,
            "disable_metrics": True,
            "enable_live_metrics": False,
            "resource": TEST_RESOURCE,
        }
        config_mock.return_value = configurations
        configure_azure_monitor()
        tracing_mock.assert_called_once_with(configurations)
        logging_mock.assert_called_once_with(configurations)
        metrics_mock.assert_not_called()
        live_metrics_mock.assert_not_called()
        instrumentation_mock.assert_called_once_with(configurations)

    @patch(
        "azure.monitor.opentelemetry._configure._setup_instrumentations",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_live_metrics",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_metrics",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_logging",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._setup_tracing",
    )
    @patch(
        "azure.monitor.opentelemetry._configure._get_configurations",
    )
    def test_configure_azure_monitor_enable_live_metrics(
        self,
        config_mock,
        tracing_mock,
        logging_mock,
        metrics_mock,
        live_metrics_mock,
        instrumentation_mock,
    ):
        configurations = {
            "connection_string": "test_cs",
            "disable_tracing": False,
            "disable_logging": False,
            "disable_metrics": False,
            "enable_live_metrics": True,
            "resource": TEST_RESOURCE,
        }
        config_mock.return_value = configurations
        configure_azure_monitor()
        tracing_mock.assert_called_once_with(configurations)
        logging_mock.assert_called_once_with(configurations)
        metrics_mock.assert_called_once_with(configurations)
        live_metrics_mock.assert_called_once_with(configurations)
        instrumentation_mock.assert_called_once_with(configurations)

    @patch(
        "azure.monitor.opentelemetry._configure.settings",
    )
    @patch(
        "azure.monitor.opentelemetry._configure.BatchSpanProcessor",
    )
    @patch(
        "azure.monitor.opentelemetry._configure.AzureMonitorTraceExporter",
    )
    @patch(
        "azure.monitor.opentelemetry._configure.set_tracer_provider",
    )
    @patch(
        "azure.monitor.opentelemetry._configure.TracerProvider",
        autospec=True,
    )
    @patch(
        "azure.monitor.opentelemetry._configure.ApplicationInsightsSampler",
    )
    def test_setup_tracing(
        self,
        sampler_mock,
        tp_mock,
        set_tracer_provider_mock,
        trace_exporter_mock,
        bsp_mock,
        azure_core_mock,
    ):
        sampler_init_mock = Mock()
        sampler_mock.return_value = sampler_init_mock
        tp_init_mock = Mock()
        tp_mock.return_value = tp_init_mock
        trace_exp_init_mock = Mock()
        trace_exporter_mock.return_value = trace_exp_init_mock
        bsp_init_mock = Mock()
        bsp_mock.return_value = bsp_init_mock
        custom_sp = Mock()

        configurations = {
            "connection_string": "test_cs",
            "instrumentation_options": {
                "azure_sdk": {"enabled": True}
            },
            "sampling_ratio": 0.5,
            "span_processors": [custom_sp],
            "resource": TEST_RESOURCE,
        }
        _setup_tracing(configurations)
        sampler_mock.assert_called_once_with(sampling_ratio=0.5)
        tp_mock.assert_called_once_with(
            sampler=sampler_init_mock,
            resource=TEST_RESOURCE
        )
        set_tracer_provider_mock.assert_called_once_with(tp_init_mock)
        trace_exporter_mock.assert_called_once_with(**configurations)
        bsp_mock.assert_called_once_with(trace_exp_init_mock)
        self.assertEqual(tp_init_mock.add_span_processor.call_count, 2)
        tp_init_mock.add_span_processor.assert_has_calls([call(custom_sp), call(bsp_init_mock)])
        self.assertEqual(
            azure_core_mock.tracing_implementation, OpenTelemetrySpan
        )

    @patch(
        "azure.monitor.opentelemetry._configure.getLogger",
    )
    @patch(
        "azure.monitor.opentelemetry._configure.LoggingHandler",
    )
    @patch(
        "azure.monitor.opentelemetry._configure.BatchLogRecordProcessor",
    )
    @patch(
        "azure.monitor.opentelemetry._configure.AzureMonitorLogExporter",
    )
    @patch(
        "azure.monitor.opentelemetry._configure.set_logger_provider",
    )
    @patch(
        "azure.monitor.opentelemetry._configure.LoggerProvider",
        autospec=True,
    )
    def test_setup_logging(
        self,
        lp_mock,
        set_logger_provider_mock,
        log_exporter_mock,
        blrp_mock,
        logging_handler_mock,
        get_logger_mock,
    ):
        lp_init_mock = Mock()
        lp_mock.return_value = lp_init_mock
        log_exp_init_mock = Mock()
        log_exporter_mock.return_value = log_exp_init_mock
        blrp_init_mock = Mock()
        blrp_mock.return_value = blrp_init_mock
        logging_handler_init_mock = Mock()
        logging_handler_mock.return_value = logging_handler_init_mock
        logger_mock = Mock()
        get_logger_mock.return_value = logger_mock

        configurations = {
            "connection_string": "test_cs",
            "logger_name": "test",
            "resource": TEST_RESOURCE,
        }
        _setup_logging(configurations)

        lp_mock.assert_called_once_with(resource=TEST_RESOURCE)
        set_logger_provider_mock.assert_called_once_with(lp_init_mock)
        log_exporter_mock.assert_called_once_with(**configurations)
        blrp_mock.assert_called_once_with(
            log_exp_init_mock,
        )
        lp_init_mock.add_log_record_processor.assert_called_once_with(
            blrp_init_mock
        )
        logging_handler_mock.assert_called_once_with(
            logger_provider=lp_init_mock
        )
        get_logger_mock.assert_called_once_with("test")
        logger_mock.addHandler.assert_called_once_with(
            logging_handler_init_mock
        )

    @patch(
        "azure.monitor.opentelemetry._configure.PeriodicExportingMetricReader",
    )
    @patch(
        "azure.monitor.opentelemetry._configure.AzureMonitorMetricExporter",
    )
    @patch(
        "azure.monitor.opentelemetry._configure.set_meter_provider",
    )
    @patch(
        "azure.monitor.opentelemetry._configure.MeterProvider",
        autospec=True,
    )
    def test_setup_metrics(
        self,
        mp_mock,
        set_meter_provider_mock,
        metric_exporter_mock,
        reader_mock,
    ):
        mp_init_mock = Mock()
        mp_mock.return_value = mp_init_mock
        metric_exp_init_mock = Mock()
        metric_exporter_mock.return_value = metric_exp_init_mock
        reader_init_mock = Mock()
        reader_mock.return_value = reader_init_mock

        configurations = {
            "connection_string": "test_cs",
            "resource": TEST_RESOURCE,
            "views": [],
        }
        _setup_metrics(configurations)
        mp_mock.assert_called_once_with(
            metric_readers=[reader_init_mock],
            resource=TEST_RESOURCE,
            views=[],
        )
        set_meter_provider_mock.assert_called_once_with(mp_init_mock)
        metric_exporter_mock.assert_called_once_with(**configurations)
        reader_mock.assert_called_once_with(metric_exp_init_mock)

    @patch(
        "azure.monitor.opentelemetry._configure.PeriodicExportingMetricReader",
    )
    @patch(
        "azure.monitor.opentelemetry._configure.AzureMonitorMetricExporter",
    )
    @patch(
        "azure.monitor.opentelemetry._configure.set_meter_provider",
    )
    @patch(
        "azure.monitor.opentelemetry._configure.MeterProvider",
        autospec=True,
    )
    def test_setup_metrics_views(
        self,
        mp_mock,
        set_meter_provider_mock,
        metric_exporter_mock,
        reader_mock,
    ):
        mp_init_mock = Mock()
        mp_mock.return_value = mp_init_mock
        metric_exp_init_mock = Mock()
        metric_exporter_mock.return_value = metric_exp_init_mock
        reader_init_mock = Mock()
        reader_mock.return_value = reader_init_mock        
        view_mock = Mock()

        configurations = {
            "connection_string": "test_cs",
            "resource": TEST_RESOURCE,
            "views": [view_mock],
        }
        _setup_metrics(configurations)
        mp_mock.assert_called_once_with(
            metric_readers=[reader_init_mock],
            resource=TEST_RESOURCE,
            views=[view_mock],
        )
        set_meter_provider_mock.assert_called_once_with(mp_init_mock)
        metric_exporter_mock.assert_called_once_with(**configurations)
        reader_mock.assert_called_once_with(metric_exp_init_mock)

    @patch(
        "azure.monitor.opentelemetry._configure.enable_live_metrics",
    )
    def test_setup_live_metrics(
        self,
        enable_live_metrics_mock,
    ):
        configurations = {
            "connection_string": "test_cs",
            "resource": TEST_RESOURCE,
        }
        _setup_live_metrics(configurations)

        enable_live_metrics_mock.assert_called_once_with(**configurations)

    @patch("azure.monitor.opentelemetry._configure._ALL_SUPPORTED_INSTRUMENTED_LIBRARIES", ("test_instr2"))
    @patch("azure.monitor.opentelemetry._configure._is_instrumentation_enabled")
    @patch("azure.monitor.opentelemetry._configure.get_dist_dependency_conflicts")
    @patch("azure.monitor.opentelemetry._configure.iter_entry_points")
    def test_setup_instrumentations_lib_not_supported(
        self,
        iter_mock,
        dep_mock,
        enabled_mock,
    ):
        ep_mock = Mock()
        ep2_mock = Mock()
        iter_mock.return_value = (ep_mock, ep2_mock)
        instrumentor_mock = Mock()
        instr_class_mock = Mock()
        instr_class_mock.return_value = instrumentor_mock
        ep_mock.name = "test_instr1"
        ep2_mock.name = "test_instr2"
        ep2_mock.load.return_value = instr_class_mock
        dep_mock.return_value = None
        enabled_mock.return_value = True
        _setup_instrumentations({})
        dep_mock.assert_called_with(ep2_mock.dist)
        ep_mock.load.assert_not_called()
        ep2_mock.load.assert_called_once()
        instrumentor_mock.instrument.assert_called_once()

    @patch("azure.monitor.opentelemetry._configure._ALL_SUPPORTED_INSTRUMENTED_LIBRARIES", ("test_instr"))
    @patch("azure.monitor.opentelemetry._configure._is_instrumentation_enabled")
    @patch("azure.monitor.opentelemetry._configure._logger")
    @patch("azure.monitor.opentelemetry._configure.get_dist_dependency_conflicts")
    @patch("azure.monitor.opentelemetry._configure.iter_entry_points")
    def test_setup_instrumentations_conflict(
        self,
        iter_mock,
        dep_mock,
        logger_mock,
        enabled_mock,
    ):
        ep_mock = Mock()
        iter_mock.return_value = (ep_mock,)
        instrumentor_mock = Mock()
        instr_class_mock = Mock()
        instr_class_mock.return_value = instrumentor_mock
        ep_mock.name = "test_instr"
        ep_mock.load.return_value = instr_class_mock
        dep_mock.return_value = True
        enabled_mock.return_value = True
        _setup_instrumentations({})
        dep_mock.assert_called_with(ep_mock.dist)
        ep_mock.load.assert_not_called()
        instrumentor_mock.instrument.assert_not_called()
        logger_mock.debug.assert_called_once()

    @patch("azure.monitor.opentelemetry._configure._ALL_SUPPORTED_INSTRUMENTED_LIBRARIES", ("test_instr"))
    @patch("azure.monitor.opentelemetry._configure._is_instrumentation_enabled")
    @patch("azure.monitor.opentelemetry._configure._logger")
    @patch("azure.monitor.opentelemetry._configure.get_dist_dependency_conflicts")
    @patch("azure.monitor.opentelemetry._configure.iter_entry_points")
    def test_setup_instrumentations_exception(
        self,
        iter_mock,
        dep_mock,
        logger_mock,
        enabled_mock,
    ):
        ep_mock = Mock()
        iter_mock.return_value = (ep_mock,)
        instrumentor_mock = Mock()
        instr_class_mock = Mock()
        instr_class_mock.return_value = instrumentor_mock
        ep_mock.name = "test_instr"
        ep_mock.load.side_effect = Exception()
        dep_mock.return_value = None
        enabled_mock.return_value = True
        _setup_instrumentations({})
        dep_mock.assert_called_with(ep_mock.dist)
        ep_mock.load.assert_called_once()
        instrumentor_mock.instrument.assert_not_called()
        logger_mock.warning.assert_called_once()

    @patch("azure.monitor.opentelemetry._configure._ALL_SUPPORTED_INSTRUMENTED_LIBRARIES", ("test_instr1", "test_instr2"))
    @patch("azure.monitor.opentelemetry._configure._is_instrumentation_enabled")
    @patch("azure.monitor.opentelemetry._configure._logger")
    @patch("azure.monitor.opentelemetry._configure.get_dist_dependency_conflicts")
    @patch("azure.monitor.opentelemetry._configure.iter_entry_points")
    def test_setup_instrumentations_disabled(
        self,
        iter_mock,
        dep_mock,
        logger_mock,
        enabled_mock,
    ):
        ep_mock = Mock()
        ep2_mock = Mock()
        iter_mock.return_value = (ep_mock, ep2_mock)
        instrumentor_mock = Mock()
        instr_class_mock = Mock()
        instr_class_mock.return_value = instrumentor_mock
        ep_mock.name = "test_instr1"
        ep2_mock.name = "test_instr2"
        ep2_mock.load.return_value = instr_class_mock
        dep_mock.return_value = None
        enabled_mock.side_effect = [False, True]
        _setup_instrumentations({})
        dep_mock.assert_called_with(ep2_mock.dist)
        ep_mock.load.assert_not_called()
        ep2_mock.load.assert_called_once()
        instrumentor_mock.instrument.assert_called_once()
        logger_mock.debug.assert_called_once()

    @patch("azure.monitor.opentelemetry._configure.AzureDiagnosticLogging")
    @patch("azure.monitor.opentelemetry._configure._is_attach_enabled")
    def test_send_attach_warning_true(
        self,
        is_attach_enabled_mock,
        mock_diagnostics,
    ):
        is_attach_enabled_mock.return_value = True
        _send_attach_warning()
        mock_diagnostics.warning.assert_called_once_with(
            "Distro detected that automatic attach may have occurred. Check your data to ensure that telemetry is not being duplicated. This may impact your cost.",
            _DISTRO_DETECTS_ATTACH,
        )

    @patch("azure.monitor.opentelemetry._configure.AzureDiagnosticLogging")
    @patch("azure.monitor.opentelemetry._configure._is_attach_enabled")
    def test_send_attach_warning_false(
        self,
        is_attach_enabled_mock,
        mock_diagnostics,
    ):
        is_attach_enabled_mock.return_value = False
        _send_attach_warning()
        mock_diagnostics.warning.assert_not_called()
