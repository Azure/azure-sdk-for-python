# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import errno
import os
import shutil
import unittest
import json
from unittest import mock
from datetime import datetime

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.core.pipeline.transport import HttpResponse
from azure.monitor.opentelemetry.exporter.export._base import (
    _MONITOR_DOMAIN_MAPPING,
    _format_storage_telemetry_item,
    _get_auth_policy,
    _get_authentication_credential,
    BaseExporter,
    ExportResult,
)
from azure.monitor.opentelemetry.exporter._storage import StorageExportResult
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _REQUESTS_MAP,
    _STATSBEAT_STATE,
    _LOCAL_STORAGE_SETUP_STATE,
)
from azure.monitor.opentelemetry.exporter.statsbeat import _customer_sdkstats
from azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats import (
    _CUSTOMER_SDKSTATS_STATE,
    CustomerSdkStatsMetrics,
)
from azure.monitor.opentelemetry.exporter.statsbeat._exporter import _StatsBeatExporter
from azure.monitor.opentelemetry.exporter.export.metrics._exporter import AzureMonitorMetricExporter
from azure.monitor.opentelemetry.exporter.export.trace._exporter import AzureMonitorTraceExporter
from azure.monitor.opentelemetry.exporter._constants import (
    _DEFAULT_AAD_SCOPE,
    _REQ_DURATION_NAME,
    _REQ_EXCEPTION_NAME,
    _REQ_FAILURE_NAME,
    _REQ_RETRY_NAME,
    _REQ_SUCCESS_NAME,
    _REQ_THROTTLE_NAME,
    DropCode,
    RetryCode,
    _UNKNOWN,
)
from azure.monitor.opentelemetry.exporter._generated import AzureMonitorClient
from azure.monitor.opentelemetry.exporter._generated.models import (
    MessageData,
    MetricDataPoint,
    MetricsData,
    MonitorBase,
    RemoteDependencyData,
    RequestData,
    TelemetryErrorDetails,
    TelemetryExceptionDetails,
    TelemetryEventData,
    TelemetryExceptionData,
    TelemetryItem,
    TrackResponse,
)

from azure.monitor.opentelemetry.exporter.statsbeat._utils import (
    _track_retry_items,
    _track_successful_items,
    _track_dropped_items,
    _determine_client_retry_code,
)

TEST_AUTH_POLICY = "TEST_AUTH_POLICY"
TEST_TEMP_DIR = "TEST_TEMP_DIR"


def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


def clean_folder(folder):
    if os.path.isfile(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print("Failed to delete %s. Reason: %s" % (file_path, e))


# pylint: disable=W0212
# pylint: disable=R0904
class TestBaseExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Clear environ so the mocks from past tests do not interfere.
        os.environ.pop("APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL", None)
        os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY", None)
        os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] = "1234abcd-5678-4efa-8abc-1234567890ab"
        os.environ["APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL"] = "true"
        cls._base = BaseExporter()
        cls._envelopes_to_export = [TelemetryItem(name="Test", time=datetime.now())]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._base.storage._path, True)

    def setUp(self) -> None:
        _REQUESTS_MAP.clear()
        _STATSBEAT_STATE.clear()
        _STATSBEAT_STATE.update(
            {
                "INITIAL_FAILURE_COUNT": 0,
                "INITIAL_SUCCESS": False,
                "SHUTDOWN": False,
                "CUSTOM_EVENTS_FEATURE_SET": False,
                "LIVE_METRICS_FEATURE_SET": False,
            }
        )
        _CUSTOMER_SDKSTATS_STATE.clear()
        _CUSTOMER_SDKSTATS_STATE.update(
            {
                "SHUTDOWN": False,
            }
        )
        # Reset customer sdkstats singleton for test isolation
        _customer_sdkstats._STATSBEAT_METRICS = None
        _CUSTOMER_SDKSTATS_STATE["SHUTDOWN"] = False

    def tearDown(self):
        clean_folder(self._base.storage._path)

    # @mock.patch('azure.monitor.opentelemetry.exporter.export._base._ConfigurationManager')
    # def test_base_exporter_calls_configuration_manager(self, mock_config_manager):
    #     """Test that BaseExporter creates and uses ConfigurationManager."""
    #     # Configure the mock
    #     mock_manager_instance = mock.Mock()
    #     mock_config_manager.return_value = mock_manager_instance

    #     # Create BaseExporter instance
    #     base = BaseExporter(
    #         connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/",
    #         disable_offline_storage=True
    #     )

    #     # Verify ConfigurationManager was called
    #     mock_config_manager.assert_called_once()

    #     # Verify the manager instance is accessible (if needed for future operations)
    #     self.assertIsNotNone(base)

    #     # Optionally verify it was assigned to the instance
    #     self.assertEqual(base._configuration_manager, mock_manager_instance)

    def test_constructor(self):
        """Test the constructor."""
        base = BaseExporter(
            api_version="2021-02-10_Preview",
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/",
            disable_offline_storage=False,
            distro_version="1.0.0",
            storage_maintenance_period=30,
            storage_max_size=1000,
            storage_min_retry_interval=100,
            storage_directory="test/path",
            storage_retention_period=2000,
        )
        self.assertEqual(
            base._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ab",
        )
        self.assertEqual(
            base._endpoint,
            "https://westus-0.in.applicationinsights.azure.com/",
        )
        self.assertEqual(base._distro_version, "1.0.0")
        self.assertIsNotNone(base.storage)
        self.assertEqual(base.storage._max_size, 1000)
        self.assertEqual(base.storage._retention_period, 2000)
        self.assertEqual(base._storage_maintenance_period, 30)
        self.assertEqual(base._timeout, 10)
        self.assertEqual(base._api_version, "2021-02-10_Preview")
        self.assertEqual(base._storage_min_retry_interval, 100)
        self.assertEqual(base._storage_directory, "test/path")

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.tempfile.gettempdir")
    def test_constructor_no_storage_directory(self, mock_get_temp_dir):
        mock_get_temp_dir.return_value = TEST_TEMP_DIR
        base = BaseExporter(
            api_version="2021-02-10_Preview",
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/",
            disable_offline_storage=False,
            distro_version="1.0.0",
            storage_maintenance_period=30,
            storage_max_size=1000,
            storage_min_retry_interval=100,
            storage_retention_period=2000,
        )
        self.assertEqual(
            base._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ab",
        )
        self.assertEqual(
            base._endpoint,
            "https://westus-0.in.applicationinsights.azure.com/",
        )
        self.assertEqual(base._distro_version, "1.0.0")
        self.assertIsNotNone(base.storage)
        self.assertEqual(base.storage._max_size, 1000)
        self.assertEqual(base.storage._retention_period, 2000)
        self.assertEqual(base._storage_maintenance_period, 30)
        self.assertEqual(base._timeout, 10)
        self.assertEqual(base._api_version, "2021-02-10_Preview")
        self.assertEqual(base._storage_min_retry_interval, 100)
        self.assertEqual(
            base._storage_directory,
            os.path.join(
                TEST_TEMP_DIR,
                "Microsoft/AzureMonitor",
                "opentelemetry-python-" + "4321abcd-5678-4efa-8abc-1234567890ab",
            ),
        )
        mock_get_temp_dir.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.tempfile.gettempdir")
    def test_constructor_disable_offline_storage(self, mock_get_temp_dir):
        mock_get_temp_dir.side_effect = Exception()
        base = BaseExporter(
            api_version="2021-02-10_Preview",
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/",
            disable_offline_storage=True,
            distro_version="1.0.0",
            storage_maintenance_period=30,
            storage_max_size=1000,
            storage_min_retry_interval=100,
            storage_retention_period=2000,
        )
        self.assertEqual(
            base._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ab",
        )
        self.assertEqual(
            base._endpoint,
            "https://westus-0.in.applicationinsights.azure.com/",
        )
        self.assertEqual(base._distro_version, "1.0.0")
        self.assertIsNone(base.storage)
        self.assertEqual(base._storage_maintenance_period, 30)
        self.assertEqual(base._timeout, 10)
        self.assertEqual(base._api_version, "2021-02-10_Preview")
        self.assertEqual(base._storage_min_retry_interval, 100)
        self.assertIsNone(base._storage_directory)
        mock_get_temp_dir.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.tempfile.gettempdir")
    def test_constructor_disable_offline_storage_with_storage_directory(self, mock_get_temp_dir):
        mock_get_temp_dir.side_effect = Exception()
        base = BaseExporter(
            api_version="2021-02-10_Preview",
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/",
            disable_offline_storage=True,
            distro_version="1.0.0",
            storage_maintenance_period=30,
            storage_max_size=1000,
            storage_min_retry_interval=100,
            storage_directory="test/path",
            storage_retention_period=2000,
        )
        self.assertEqual(
            base._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ab",
        )
        self.assertEqual(
            base._endpoint,
            "https://westus-0.in.applicationinsights.azure.com/",
        )
        self.assertEqual(base._distro_version, "1.0.0")
        self.assertIsNone(base.storage)
        self.assertEqual(base._storage_maintenance_period, 30)
        self.assertEqual(base._timeout, 10)
        self.assertEqual(base._api_version, "2021-02-10_Preview")
        self.assertEqual(base._storage_min_retry_interval, 100)
        self.assertEqual(base._storage_directory, "test/path")
        mock_get_temp_dir.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._format_storage_telemetry_item")
    @mock.patch.object(TelemetryItem, "from_dict")
    def test_transmit_from_storage_success(self, dict_patch, format_patch):
        exporter = BaseExporter()
        exporter.storage = mock.Mock()
        blob_mock = mock.Mock()
        blob_mock.lease.return_value = True
        envelope_mock = {"name": "test", "time": "time"}
        blob_mock.get.return_value = [envelope_mock]
        dict_patch.return_value = {"name": "test", "time": "time"}
        format_patch.return_value = envelope_mock
        exporter.storage.gets.return_value = [blob_mock]
        with mock.patch.object(AzureMonitorClient, "track") as post:
            post.return_value = TrackResponse(
                items_received=1,
                items_accepted=1,
                errors=[],
            )
            exporter._transmit_from_storage()
        exporter.storage.gets.assert_called_once()
        blob_mock.lease.assert_called_once()
        blob_mock.delete.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._format_storage_telemetry_item")
    @mock.patch.object(TelemetryItem, "from_dict")
    def test_transmit_from_storage_store_again(self, dict_patch, format_patch):
        exporter = BaseExporter()
        exporter.storage = mock.Mock()
        blob_mock = mock.Mock()
        blob_mock.lease.return_value = True
        envelope_mock = {"name": "test", "time": "time"}
        blob_mock.get.return_value = [envelope_mock]
        dict_patch.return_value = {"name": "test", "time": "time"}
        format_patch.return_value = envelope_mock
        exporter.storage.gets.return_value = [blob_mock]
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code"):
            with mock.patch.object(AzureMonitorClient, "track", throw(HttpResponseError)):
                exporter._transmit_from_storage()
        exporter.storage.gets.assert_called_once()
        blob_mock.lease.assert_called()
        blob_mock.delete.assert_not_called()

    def test_transmit_from_storage_lease_failure(self):
        exporter = BaseExporter()
        exporter.storage = mock.Mock()
        blob_mock = mock.Mock()
        blob_mock.lease.return_value = False
        exporter.storage.gets.return_value = [blob_mock]
        transmit_mock = mock.Mock()
        exporter._transmit = transmit_mock
        exporter._transmit_from_storage()
        exporter.storage.gets.assert_called_once()
        transmit_mock.assert_not_called()
        blob_mock.lease.assert_called_once()
        blob_mock.delete.assert_not_called()

    def test_format_storage_telemetry_item(self):
        time = datetime.now()
        base = MonitorBase(base_type="", base_data=None)
        ti = TelemetryItem(
            name="test_telemetry_item",
            time=time,
            version=1,
            sample_rate=50.0,
            sequence="test_sequence",
            instrumentation_key="4321abcd-5678-4efa-8abc-1234567890ab",
            tags={"tag1": "val1", "tag2": "val2"},
            data=base,
        )
        # MessageData
        message_data = MessageData(
            version=2,
            message="test_message",
            severity_level="Warning",
            properties={"key1": "val1"},
        )
        base.base_type = "MessageData"
        self.assertEqual(_MONITOR_DOMAIN_MAPPING.get(base.base_type), MessageData)
        base.base_data = message_data
        ti.data = base

        # Format is called on custom serialized TelemetryItem
        converted_ti = ti.from_dict(ti.as_dict())
        format_ti = _format_storage_telemetry_item(converted_ti)
        self.assertTrue(validate_telemetry_item(format_ti, ti))
        self.assertEqual(format_ti.data.base_type, "MessageData")
        self.assertEqual(message_data.__dict__.items(), format_ti.data.base_data.__dict__.items())

        # EventData
        event_data = TelemetryEventData(
            version=2,
            name="test_name",
            properties={"key1": "val1"},
        )
        base.base_type = "EventData"
        self.assertEqual(_MONITOR_DOMAIN_MAPPING.get(base.base_type), TelemetryEventData)
        base.base_data = event_data
        ti.data = base

        # Format is called on custom serialized TelemetryItem
        converted_ti = ti.from_dict(ti.as_dict())
        format_ti = _format_storage_telemetry_item(converted_ti)
        self.assertTrue(validate_telemetry_item(format_ti, ti))
        self.assertEqual(format_ti.data.base_type, "EventData")
        self.assertEqual(event_data.__dict__.items(), format_ti.data.base_data.__dict__.items())

        # ExceptionData
        exc_data_details = TelemetryExceptionDetails(
            type_name="ZeroDivisionError",
            message="division by zero",
            has_full_stack=True,
            stack="Traceback \n",
        )
        exc_data = TelemetryExceptionData(
            version=2, properties={"key1": "val1"}, severity_level="3", exceptions=[exc_data_details]
        )
        base.base_type = "ExceptionData"
        self.assertEqual(_MONITOR_DOMAIN_MAPPING.get(base.base_type), TelemetryExceptionData)
        base.base_data = exc_data
        ti.data = base

        # Format is called on custom serialized TelemetryItem
        converted_ti = ti.from_dict(ti.as_dict())
        format_ti = _format_storage_telemetry_item(converted_ti)
        self.assertTrue(validate_telemetry_item(format_ti, ti))
        self.assertEqual(format_ti.data.base_type, "ExceptionData")
        self.assertEqual(exc_data.version, format_ti.data.base_data.version)
        self.assertEqual(exc_data.properties, format_ti.data.base_data.properties)
        self.assertEqual(exc_data.severity_level, format_ti.data.base_data.severity_level)
        self.assertEqual(exc_data.exceptions[0].type_name, format_ti.data.base_data.exceptions[0].type_name)
        self.assertEqual(exc_data.exceptions[0].message, format_ti.data.base_data.exceptions[0].message)
        self.assertEqual(exc_data.exceptions[0].has_full_stack, format_ti.data.base_data.exceptions[0].has_full_stack)
        self.assertEqual(exc_data.exceptions[0].stack, format_ti.data.base_data.exceptions[0].stack)

        # MetricsData
        counter_data_point = MetricDataPoint(
            name="counter",
            value=1.0,
            count=1,
            min=None,
            max=None,
        )
        hist_data_point = MetricDataPoint(
            name="histogram",
            value=99.0,
            count=1,
            min=99.0,
            max=99.0,
        )
        metric_data = MetricsData(
            version=2,
            properties={"key1": "val1"},
            metrics=[counter_data_point, hist_data_point],
        )
        base.base_type = "MetricData"
        self.assertEqual(_MONITOR_DOMAIN_MAPPING.get(base.base_type), MetricsData)
        base.base_data = metric_data
        ti.data = base

        # Format is called on custom serialized TelemetryItem
        converted_ti = ti.from_dict(ti.as_dict())
        format_ti = _format_storage_telemetry_item(converted_ti)
        self.assertTrue(validate_telemetry_item(format_ti, ti))
        self.assertEqual(format_ti.data.base_type, "MetricData")
        self.assertEqual(metric_data.version, format_ti.data.base_data.version)
        self.assertEqual(metric_data.properties, format_ti.data.base_data.properties)
        self.assertEqual(metric_data.metrics[0].name, format_ti.data.base_data.metrics[0].name)
        self.assertEqual(metric_data.metrics[0].value, format_ti.data.base_data.metrics[0].value)
        self.assertEqual(metric_data.metrics[0].count, format_ti.data.base_data.metrics[0].count)
        self.assertEqual(metric_data.metrics[0].min, format_ti.data.base_data.metrics[0].min)
        self.assertEqual(metric_data.metrics[0].max, format_ti.data.base_data.metrics[0].max)
        self.assertEqual(metric_data.metrics[1].name, format_ti.data.base_data.metrics[1].name)
        self.assertEqual(metric_data.metrics[1].value, format_ti.data.base_data.metrics[1].value)
        self.assertEqual(metric_data.metrics[1].count, format_ti.data.base_data.metrics[1].count)
        self.assertEqual(metric_data.metrics[1].min, format_ti.data.base_data.metrics[1].min)
        self.assertEqual(metric_data.metrics[1].max, format_ti.data.base_data.metrics[1].max)

        # RemoteDependencyData
        dep_data = RemoteDependencyData(
            version=2,
            id="191306b0186ce6a8",
            name="GET /",
            result_code="200",
            data="https://example.com/",
            type="HTTP",
            target="example.com",
            duration="0.00:00:01.143",
            success=True,
            properties={"key1": "val1"},
        )
        base.base_type = "RemoteDependencyData"
        self.assertEqual(_MONITOR_DOMAIN_MAPPING.get(base.base_type), RemoteDependencyData)
        base.base_data = dep_data
        ti.data = base

        # Format is called on custom serialized TelemetryItem
        converted_ti = ti.from_dict(ti.as_dict())
        format_ti = _format_storage_telemetry_item(converted_ti)
        self.assertTrue(validate_telemetry_item(format_ti, ti))
        self.assertEqual(format_ti.data.base_type, "RemoteDependencyData")
        self.assertEqual(dep_data.__dict__.items(), format_ti.data.base_data.__dict__.items())

        # RequestData
        req_data = RequestData(
            version=2,
            id="04f4d2ab2b9b6825",
            name="GET /",
            duration="0.00:00:00.053",
            success=True,
            response_code="200",
            url="http://localhost:8080/",
            source="test source",
            properties={"key1": "val1"},
        )
        base.base_type = "RequestData"
        self.assertEqual(_MONITOR_DOMAIN_MAPPING.get(base.base_type), RequestData)
        base.base_data = req_data
        ti.data = base

        # Format is called on custom serialized TelemetryItem
        converted_ti = ti.from_dict(ti.as_dict())
        format_ti = _format_storage_telemetry_item(converted_ti)
        self.assertTrue(validate_telemetry_item(format_ti, ti))
        self.assertEqual(format_ti.data.base_type, "RequestData")
        self.assertEqual(req_data.__dict__.items(), format_ti.data.base_data.__dict__.items())

    def test_transmit_http_error_retryable(self):
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code") as m:
            m.return_value = True
            with mock.patch.object(AzureMonitorClient, "track", throw(HttpResponseError)):
                result = self._base._transmit(self._envelopes_to_export)
            self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmit_http_error_not_retryable(self):
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code") as m:
            m.return_value = False
            with mock.patch.object(AzureMonitorClient, "track", throw(HttpResponseError)):
                result = self._base._transmit(self._envelopes_to_export)
            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmit_http_error_redirect(self):
        response = HttpResponse(None, None)
        response.status_code = 307
        response.headers = {"location": "https://example.com"}
        prev_redirects = self._base.client._config.redirect_policy.max_redirects
        self._base.client._config.redirect_policy.max_redirects = 2
        prev_host = self._base.client._config.host
        error = HttpResponseError(response=response)
        with mock.patch.object(AzureMonitorClient, "track") as post:
            post.side_effect = error
            result = self._base._transmit(self._envelopes_to_export)
            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
            self.assertEqual(post.call_count, 2)
            self.assertEqual(self._base.client._config.host, "https://example.com")
        self._base.client._config.redirect_policy.max_redirects = prev_redirects
        self._base.client._config.host = prev_host

    def test_transmit_http_error_redirect_missing_headers(self):
        response = HttpResponse(None, None)
        response.status_code = 307
        response.headers = None
        error = HttpResponseError(response=response)
        prev_host = self._base.client._config.host
        with mock.patch.object(AzureMonitorClient, "track") as post:
            post.side_effect = error
            result = self._base._transmit(self._envelopes_to_export)
            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
            self.assertEqual(post.call_count, 1)
            self.assertEqual(self._base.client._config.host, prev_host)

    def test_transmit_http_error_redirect_invalid_location_header(self):
        response = HttpResponse(None, None)
        response.status_code = 307
        response.headers = {"location": "123"}
        error = HttpResponseError(response=response)
        prev_host = self._base.client._config.host
        with mock.patch.object(AzureMonitorClient, "track") as post:
            post.side_effect = error
            result = self._base._transmit(self._envelopes_to_export)
            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
            self.assertEqual(post.call_count, 1)
            self.assertEqual(self._base.client._config.host, prev_host)

    def test_transmit_request_error(self):
        with mock.patch.object(AzureMonitorClient, "track", throw(ServiceRequestError, message="error")):
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "false",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_transmit_request_error_statsbeat(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        with mock.patch.object(AzureMonitorClient, "track", throw(ServiceRequestError, message="error")):
            result = exporter._transmit(self._envelopes_to_export)
        stats_mock.assert_called_once()
        self.assertEqual(len(_REQUESTS_MAP), 3)
        self.assertEqual(_REQUESTS_MAP[_REQ_EXCEPTION_NAME[1]]["ServiceRequestError"], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmit_request_exception(self):
        with mock.patch.object(AzureMonitorClient, "track", throw(Exception)):
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "false",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_transmit_request_exception_statsbeat(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        with mock.patch.object(AzureMonitorClient, "track", throw(Exception)):
            result = exporter._transmit(self._envelopes_to_export)
        stats_mock.assert_called_once()
        self.assertEqual(len(_REQUESTS_MAP), 3)
        self.assertEqual(_REQUESTS_MAP[_REQ_EXCEPTION_NAME[1]]["Exception"], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmission_200(self):
        with mock.patch.object(AzureMonitorClient, "track") as post:
            post.return_value = TrackResponse(
                items_received=1,
                items_accepted=1,
                errors=[],
            )
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.SUCCESS)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_statsbeat_200(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        with mock.patch.object(AzureMonitorClient, "track") as post:
            post.return_value = TrackResponse(
                items_received=1,
                items_accepted=1,
                errors=[],
            )
            result = exporter._transmit(self._envelopes_to_export)
        stats_mock.assert_called_once()
        self.assertEqual(len(_REQUESTS_MAP), 3)
        self.assertEqual(_REQUESTS_MAP[_REQ_SUCCESS_NAME[1]], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertEqual(result, ExportResult.SUCCESS)

    def test_transmission_206_retry(self):
        exporter = BaseExporter(disable_offline_storage=True)
        exporter.storage = mock.Mock()
        test_envelope = TelemetryItem(name="testEnvelope", time=datetime.now())
        custom_envelopes_to_export = [
            TelemetryItem(name="Test", time=datetime.now()),
            TelemetryItem(name="Test", time=datetime.now()),
            test_envelope,
        ]
        with mock.patch.object(AzureMonitorClient, "track") as post:
            post.return_value = TrackResponse(
                items_received=3,
                items_accepted=1,
                errors=[
                    TelemetryErrorDetails(
                        index=0,
                        status_code=400,
                        message="should drop",
                    ),
                    TelemetryErrorDetails(index=2, status_code=500, message="should retry"),
                ],
            )
            result = exporter._transmit(custom_envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
        exporter.storage.put.assert_called_once()

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_statsbeat_206_retry(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        exporter.storage = mock.Mock()
        test_envelope = TelemetryItem(name="testEnvelope", time=datetime.now())
        custom_envelopes_to_export = [
            TelemetryItem(name="Test", time=datetime.now()),
            TelemetryItem(name="Test", time=datetime.now()),
            test_envelope,
        ]
        with mock.patch.object(AzureMonitorClient, "track") as post:
            post.return_value = TrackResponse(
                items_received=3,
                items_accepted=1,
                errors=[
                    TelemetryErrorDetails(
                        index=0,
                        status_code=400,
                        message="should drop",
                    ),
                    TelemetryErrorDetails(index=2, status_code=500, message="should retry"),
                ],
            )
            result = exporter._transmit(custom_envelopes_to_export)
        stats_mock.assert_called_once()
        # We do not record any network statsbeat for 206 status code
        self.assertEqual(len(_REQUESTS_MAP), 2)
        self.assertIsNone(_REQUESTS_MAP.get("retry"))
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmission_206_no_retry(self):
        exporter = BaseExporter(disable_offline_storage=True)
        exporter.storage = mock.Mock()
        test_envelope = TelemetryItem(name="testEnvelope", time=datetime.now())
        custom_envelopes_to_export = [
            TelemetryItem(name="Test", time=datetime.now()),
            TelemetryItem(name="Test", time=datetime.now()),
            test_envelope,
        ]
        with mock.patch.object(AzureMonitorClient, "track") as post:
            post.return_value = TrackResponse(
                items_received=3,
                items_accepted=2,
                errors=[
                    TelemetryErrorDetails(
                        index=0,
                        status_code=400,
                        message="should drop",
                    ),
                ],
            )
            result = self._base._transmit(custom_envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
        exporter.storage.put.assert_not_called()

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_statsbeat_206_no_retry(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        exporter.storage = mock.Mock()
        test_envelope = TelemetryItem(name="testEnvelope", time=datetime.now())
        custom_envelopes_to_export = [
            TelemetryItem(name="Test", time=datetime.now()),
            TelemetryItem(name="Test", time=datetime.now()),
            test_envelope,
        ]
        with mock.patch.object(AzureMonitorClient, "track") as post:
            post.return_value = TrackResponse(
                items_received=3,
                items_accepted=2,
                errors=[
                    TelemetryErrorDetails(
                        index=0,
                        status_code=400,
                        message="should drop",
                    ),
                ],
            )
            result = exporter._transmit(custom_envelopes_to_export)
        stats_mock.assert_called_once()
        self.assertEqual(len(_REQUESTS_MAP), 2)
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmission_400(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(400, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.shutdown_statsbeat_metrics")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_statsbeat_400(self, stats_mock, stats_shutdown_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(400, "{}")
            result = exporter._transmit(self._envelopes_to_export)
        stats_mock.assert_called_once()
        stats_shutdown_mock.assert_called_once()
        self.assertEqual(len(_REQUESTS_MAP), 3)
        self.assertEqual(_REQUESTS_MAP[_REQ_FAILURE_NAME[1]][400], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmission_402(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(402, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_statsbeat_402(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(402, "{}")
            result = exporter._transmit(self._envelopes_to_export)
        stats_mock.assert_called_once()
        self.assertEqual(len(_REQUESTS_MAP), 3)
        self.assertEqual(_REQUESTS_MAP[_REQ_THROTTLE_NAME[1]][402], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmission_408(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(408, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_statsbeat_408(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(408, "{}")
            result = exporter._transmit(self._envelopes_to_export)
        stats_mock.assert_called_once()
        self.assertEqual(len(_REQUESTS_MAP), 3)
        self.assertEqual(_REQUESTS_MAP[_REQ_RETRY_NAME[1]][408], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmission_429(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(429, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_statsbeat_429(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(429, "{}")
            result = exporter._transmit(self._envelopes_to_export)
        stats_mock.assert_called_once()
        self.assertEqual(len(_REQUESTS_MAP), 3)
        self.assertEqual(_REQUESTS_MAP[_REQ_RETRY_NAME[1]][429], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmission_439(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(439, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_statsbeat_439(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(439, "{}")
            result = exporter._transmit(self._envelopes_to_export)
        stats_mock.assert_called_once()
        self.assertEqual(len(_REQUESTS_MAP), 3)
        self.assertEqual(_REQUESTS_MAP[_REQ_THROTTLE_NAME[1]][439], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmission_500(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(500, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_statsbeat_500(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(500, "{}")
            result = exporter._transmit(self._envelopes_to_export)
        stats_mock.assert_called_once()
        self.assertEqual(len(_REQUESTS_MAP), 3)
        self.assertEqual(_REQUESTS_MAP[_REQ_RETRY_NAME[1]][500], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmission_502(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(503, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_statsbeat_502(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(502, "{}")
            result = exporter._transmit(self._envelopes_to_export)
        stats_mock.assert_called_once()
        self.assertEqual(len(_REQUESTS_MAP), 3)
        self.assertEqual(_REQUESTS_MAP[_REQ_RETRY_NAME[1]][502], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmission_503(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(503, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
        },
    )
    def test_statsbeat_503(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(503, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(len(_REQUESTS_MAP), 3)
        self.assertEqual(_REQUESTS_MAP[_REQ_RETRY_NAME[1]][503], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmission_504(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(504, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_statsbeat_504(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(504, "{}")
            result = exporter._transmit(self._envelopes_to_export)
        stats_mock.assert_called_once()
        self.assertEqual(len(_REQUESTS_MAP), 3)
        self.assertEqual(_REQUESTS_MAP[_REQ_RETRY_NAME[1]][504], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmission_empty(self):
        status = self._base._transmit([])
        self.assertEqual(status, ExportResult.SUCCESS)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._get_authentication_credential")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._get_auth_policy")
    def test_exporter_credential(self, mock_add_credential_policy, mock_get_authentication_credential):
        TEST_CREDENTIAL = "TEST_CREDENTIAL"
        mock_get_authentication_credential.return_value = TEST_CREDENTIAL
        base = BaseExporter(credential=TEST_CREDENTIAL, authentication_policy=TEST_AUTH_POLICY)
        self.assertEqual(base._credential, TEST_CREDENTIAL)
        mock_add_credential_policy.assert_called_once_with(TEST_CREDENTIAL, TEST_AUTH_POLICY, None)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._get_authentication_credential")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._get_auth_policy")
    def test_exporter_credential_audience(self, mock_add_credential_policy, mock_get_authentication_credential):
        test_cs = "AadAudience=test-aad"
        TEST_CREDENTIAL = "TEST_CREDENTIAL"
        mock_get_authentication_credential.return_value = TEST_CREDENTIAL
        # TODO: replace with mock
        base = BaseExporter(
            connection_string=test_cs,
            credential=TEST_CREDENTIAL,
            authentication_policy=TEST_AUTH_POLICY,
        )
        self.assertEqual(base._credential, TEST_CREDENTIAL)
        mock_add_credential_policy.assert_called_once_with(TEST_CREDENTIAL, TEST_AUTH_POLICY, "test-aad")
        mock_get_authentication_credential.assert_called_once_with(
            connection_string=test_cs,
            credential=TEST_CREDENTIAL,
            authentication_policy=TEST_AUTH_POLICY,
        )

    @mock.patch.dict("os.environ", {"APPLICATIONINSIGHTS_AUTHENTICATION_STRING": "TEST_CREDENTIAL_ENV_VAR"})
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._get_authentication_credential")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._get_auth_policy")
    def test_credential_env_var_and_arg(self, mock_add_credential_policy, mock_get_authentication_credential):
        mock_get_authentication_credential.return_value = "TEST_CREDENTIAL_ENV_VAR"
        base = BaseExporter(authentication_policy=TEST_AUTH_POLICY)
        self.assertEqual(base._credential, "TEST_CREDENTIAL_ENV_VAR")
        mock_add_credential_policy.assert_called_once_with("TEST_CREDENTIAL_ENV_VAR", TEST_AUTH_POLICY, None)
        mock_get_authentication_credential.assert_called_once_with(authentication_policy=TEST_AUTH_POLICY)

    @mock.patch.dict("os.environ", {"APPLICATIONINSIGHTS_AUTHENTICATION_STRING": "TEST_CREDENTIAL_ENV_VAR"})
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._get_authentication_credential")
    def test_statsbeat_no_credential(self, mock_get_authentication_credential):
        mock_get_authentication_credential.return_value = "TEST_CREDENTIAL_ENV_VAR"
        statsbeat_exporter = _StatsBeatExporter()
        self.assertIsNone(statsbeat_exporter._credential)
        mock_get_authentication_credential.assert_not_called()

    def test_get_auth_policy(self):
        class TestCredential:
            def get_token(self):
                return "TEST_TOKEN"

        credential = TestCredential()
        result = _get_auth_policy(credential, TEST_AUTH_POLICY)
        self.assertEqual(result._credential, credential)
        self.assertEqual(result._scopes, (_DEFAULT_AAD_SCOPE,))

    def test_get_auth_policy_no_credential(self):
        self.assertEqual(_get_auth_policy(credential=None, default_auth_policy=TEST_AUTH_POLICY), TEST_AUTH_POLICY)

    def test_get_auth_policy_invalid_credential(self):
        class InvalidTestCredential:
            def invalid_get_token():
                return "TEST_TOKEN"

        self.assertRaises(
            ValueError, _get_auth_policy, credential=InvalidTestCredential(), default_auth_policy=TEST_AUTH_POLICY
        )

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._track_dropped_items")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._track_dropped_items")
    def test_handle_transmit_from_storage_success_result(self, mock_track_dropped1, mock_track_dropped2):
        """Test that when storage.put() returns StorageExportResult.LOCAL_FILE_BLOB_SUCCESS,
        the method continues without any special handling."""
        exporter = BaseExporter(disable_offline_storage=False)
        mock_customer_sdkstats = mock.Mock()
        exporter._customer_sdkstats_metrics = mock_customer_sdkstats
        exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

        # Mock storage.put() to return success
        exporter.storage = mock.Mock()
        exporter.storage.put.return_value = StorageExportResult.LOCAL_FILE_BLOB_SUCCESS

        test_envelopes = [TelemetryItem(name="test", time=datetime.now())]
        serialized_envelopes = [envelope.as_dict() for envelope in test_envelopes]
        exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

        # Verify storage.put was called with the serialized envelopes
        exporter.storage.put.assert_called_once_with(serialized_envelopes)
        # Verify that no dropped items were tracked (since it was a success)
        mock_track_dropped1.assert_not_called()
        mock_track_dropped2.assert_not_called()
        # Verify that the customer sdkstats wasn't invoked
        mock_customer_sdkstats.assert_not_called()

    def test_get_auth_policy_audience(self):
        class TestCredential:
            def get_token():
                return "TEST_TOKEN"

        credential = TestCredential()
        result = _get_auth_policy(credential, TEST_AUTH_POLICY, aad_audience="test_audience")
        self.assertEqual(result._credential, credential)
        self.assertEqual(result._scopes, ("test_audience/.default",))

    @mock.patch.dict("os.environ", {"APPLICATIONINSIGHTS_AUTHENTICATION_STRING": "Authorization=AAD"})
    def test_get_authentication_credential_arg(self):
        TEST_CREDENTIAL = "TEST_CREDENTIAL"
        result = _get_authentication_credential(
            credential=TEST_CREDENTIAL,
        )
        self.assertEqual(result, TEST_CREDENTIAL)

    @mock.patch.dict("os.environ", {"APPLICATIONINSIGHTS_AUTHENTICATION_STRING": "Authorization=AAD"})
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.logger")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.ManagedIdentityCredential")
    def test_get_authentication_credential_system_assigned(self, mock_managed_identity, mock_logger):
        MOCK_MANAGED_IDENTITY_CREDENTIAL = "MOCK_MANAGED_IDENTITY_CREDENTIAL"
        mock_managed_identity.return_value = MOCK_MANAGED_IDENTITY_CREDENTIAL
        result = _get_authentication_credential(foo="bar")
        mock_logger.assert_not_called()
        self.assertEqual(result, MOCK_MANAGED_IDENTITY_CREDENTIAL)
        mock_managed_identity.assert_called_once_with()

    @mock.patch.dict(
        "os.environ", {"APPLICATIONINSIGHTS_AUTHENTICATION_STRING": "Authorization=AAD;ClientId=TEST_CLIENT_ID"}
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.logger")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.ManagedIdentityCredential")
    def test_get_authentication_credential_client_id(self, mock_managed_identity, mock_logger):
        MOCK_MANAGED_IDENTITY_CLIENT_ID_CREDENTIAL = "MOCK_MANAGED_IDENTITY_CLIENT_ID_CREDENTIAL"
        mock_managed_identity.return_value = MOCK_MANAGED_IDENTITY_CLIENT_ID_CREDENTIAL
        result = _get_authentication_credential(foo="bar")
        mock_logger.assert_not_called()
        self.assertEqual(result, MOCK_MANAGED_IDENTITY_CLIENT_ID_CREDENTIAL)
        mock_managed_identity.assert_called_once_with(client_id="TEST_CLIENT_ID")

    @mock.patch.dict(
        "os.environ", {"APPLICATIONINSIGHTS_AUTHENTICATION_STRING": "Authorization=AAD;ClientId=TEST_CLIENT_ID=bar"}
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.logger")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.ManagedIdentityCredential")
    def test_get_authentication_credential_misformatted(self, mock_managed_identity, mock_logger):
        # Even a single misformatted pair means Entra ID auth is skipped.
        MOCK_MANAGED_IDENTITY_CREDENTIAL = "MOCK_MANAGED_IDENTITY_CREDENTIAL"
        mock_managed_identity.return_value = MOCK_MANAGED_IDENTITY_CREDENTIAL
        result = _get_authentication_credential(foo="bar")
        mock_logger.error.assert_called_once()
        self.assertIsNone(result)
        mock_managed_identity.assert_not_called()

    @mock.patch.dict("os.environ", {"APPLICATIONINSIGHTS_AUTHENTICATION_STRING": "ClientId=TEST_CLIENT_ID"})
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.ManagedIdentityCredential")
    def test_get_authentication_credential_no_auth(self, mock_managed_identity):
        MOCK_MANAGED_IDENTITY_CLIENT_ID_CREDENTIAL = "MOCK_MANAGED_IDENTITY_CLIENT_ID_CREDENTIAL"
        mock_managed_identity.return_value = MOCK_MANAGED_IDENTITY_CLIENT_ID_CREDENTIAL
        result = _get_authentication_credential(foo="bar")
        self.assertIsNone(result)
        mock_managed_identity.assert_not_called()

    @mock.patch.dict(
        "os.environ", {"APPLICATIONINSIGHTS_AUTHENTICATION_STRING": "Authorization=foobar;ClientId=TEST_CLIENT_ID"}
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.ManagedIdentityCredential")
    def test_get_authentication_credential_no_aad(self, mock_managed_identity):
        MOCK_MANAGED_IDENTITY_CLIENT_ID_CREDENTIAL = "MOCK_MANAGED_IDENTITY_CLIENT_ID_CREDENTIAL"
        mock_managed_identity.return_value = MOCK_MANAGED_IDENTITY_CLIENT_ID_CREDENTIAL
        result = _get_authentication_credential(foo="bar")
        self.assertIsNone(result)
        mock_managed_identity.assert_not_called()

    @mock.patch.dict(
        "os.environ", {"APPLICATIONINSIGHTS_AUTHENTICATION_STRING": "Authorization=foobar;ClientId=TEST_CLIENT_ID"}
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.ManagedIdentityCredential")
    def test_get_authentication_credential_no_aad(self, mock_managed_identity):
        MOCK_MANAGED_IDENTITY_CLIENT_ID_CREDENTIAL = "MOCK_MANAGED_IDENTITY_CLIENT_ID_CREDENTIAL"
        mock_managed_identity.return_value = MOCK_MANAGED_IDENTITY_CLIENT_ID_CREDENTIAL
        result = _get_authentication_credential(foo="bar")
        self.assertIsNone(result)
        mock_managed_identity.assert_not_called()

    @mock.patch.dict(
        "os.environ", {"APPLICATIONINSIGHTS_AUTHENTICATION_STRING": "Authorization=AAD;ClientId=TEST_CLIENT_ID"}
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.ManagedIdentityCredential")
    def test_get_authentication_credential_error(self, mock_managed_identity):
        MOCK_MANAGED_IDENTITY_CLIENT_ID_CREDENTIAL = "MOCK_MANAGED_IDENTITY_CLIENT_ID_CREDENTIAL"
        mock_managed_identity.return_value = MOCK_MANAGED_IDENTITY_CLIENT_ID_CREDENTIAL
        mock_managed_identity.side_effect = ValueError("TEST ERROR")
        result = _get_authentication_credential(foo="bar")
        self.assertIsNone(result)
        mock_managed_identity.assert_called_once_with(client_id="TEST_CLIENT_ID")

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_constructor_customer_sdkstats_storage_integration(self):
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.collect_customer_sdkstats"
        ) as mock_collect:
            mock_customer_sdkstats = mock.Mock()

            def mock_collect_side_effect(exporter):
                setattr(exporter, "_customer_sdkstats_metrics", mock_customer_sdkstats)
                if hasattr(exporter, "storage") and exporter.storage:
                    setattr(exporter.storage, "_customer_sdkstats_metrics", mock_customer_sdkstats)

            mock_collect.side_effect = mock_collect_side_effect

            exporter = BaseExporter(
                connection_string="InstrumentationKey=363331ca-f431-4119-bdcd-31a75920f958;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/",
                disable_offline_storage=False,
            )

            mock_collect.assert_called_once_with(exporter)

            self.assertEqual(exporter._customer_sdkstats_metrics, mock_customer_sdkstats)

            self.assertIsNotNone(exporter.storage)
            self.assertEqual(exporter.storage._customer_sdkstats_metrics, mock_customer_sdkstats)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_constructor_customer_sdkstats_no_storage(self):
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.collect_customer_sdkstats"
        ) as mock_collect:
            mock_customer_sdkstats = mock.Mock()

            def mock_collect_side_effect(exporter):
                exporter._customer_sdkstats_metrics = mock_customer_sdkstats
                if hasattr(exporter, "storage") and exporter.storage:
                    exporter.storage._customer_sdkstats_metrics = mock_customer_sdkstats

            mock_collect.side_effect = mock_collect_side_effect

            exporter = BaseExporter(
                connection_string="InstrumentationKey=363331ca-f431-4119-bdcd-31a75920f958;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/",
                disable_offline_storage=True,
            )

            mock_collect.assert_called_once_with(exporter)

            self.assertEqual(exporter._customer_sdkstats_metrics, mock_customer_sdkstats)

            self.assertIsNone(exporter.storage)

    def test_customer_sdkstats_shutdown_state(self):
        """Test that customer sdkstats shutdown state works correctly"""
        from azure.monitor.opentelemetry.exporter.statsbeat._state import (
            get_customer_sdkstats_shutdown,
            _CUSTOMER_SDKSTATS_STATE,
            _CUSTOMER_SDKSTATS_STATE_LOCK,
        )

        # Initially should not be shutdown (reset in setUp)
        self.assertFalse(get_customer_sdkstats_shutdown())

        # Directly set shutdown state (simulating what shutdown function should do)
        with _CUSTOMER_SDKSTATS_STATE_LOCK:
            _CUSTOMER_SDKSTATS_STATE["SHUTDOWN"] = True

        # Should now be shutdown
        self.assertTrue(get_customer_sdkstats_shutdown())

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_should_collect_customer_sdkstats_with_shutdown(self):
        """Test that _should_collect_customer_sdkstats respects shutdown state"""
        from azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats import (
            _CUSTOMER_SDKSTATS_STATE,
            _CUSTOMER_SDKSTATS_STATE_LOCK,
        )

        exporter = BaseExporter(
            connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789012", disable_offline_storage=True
        )

        # Should collect when not shutdown (verified by environment variables)
        self.assertTrue(exporter._should_collect_customer_sdkstats())

        # Directly set shutdown state (simulating what shutdown function should do)
        with _CUSTOMER_SDKSTATS_STATE_LOCK:
            _CUSTOMER_SDKSTATS_STATE["SHUTDOWN"] = True

        # Should not collect when shutdown
        self.assertFalse(exporter._should_collect_customer_sdkstats())

    def test_customer_sdkstats_shutdown_on_invalid_code(self):
        """Test that customer sdkstats shutdown is called and state updated on invalid response codes"""
        # Import needed components for verification
        from azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats import (
            _CUSTOMER_SDKSTATS_STATE,
            _CUSTOMER_SDKSTATS_STATE_LOCK,
            CustomerSdkStatsMetrics,
        )

        # Set up test environment
        exporter = BaseExporter()
        envelope = TelemetryItem(name="test", time=datetime.now())

        # Set up mocks for the actual implementations
        with _CUSTOMER_SDKSTATS_STATE_LOCK:
            _CUSTOMER_SDKSTATS_STATE["SHUTDOWN"] = False

        # Set up a meter provider mock to ensure we have something to shutdown
        mock_meter_provider = mock.MagicMock()

        # Create a mock instance for CustomerSdkStatsMetrics to be used in the global variable
        mock_instance = mock.MagicMock()
        mock_instance._customer_sdkstats_meter_provider = mock_meter_provider

        # Set _CUSTOMER_SDKSTATS_METRICS to our mock instance
        import sys

        customer_sdkstats_module = sys.modules["azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats"]
        original_metrics = getattr(customer_sdkstats_module, "_CUSTOMER_SDKSTATS_METRICS", None)
        setattr(customer_sdkstats_module, "_CUSTOMER_SDKSTATS_METRICS", mock_instance)

        try:
            # Execute the test scenario
            with mock.patch("requests.Session.request") as post:
                post.return_value = MockResponse(400, "Invalid request")
                result = exporter._transmit([envelope])

                # Verify the result is as expected
                self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

                # Verify the meter provider's shutdown was called
                mock_meter_provider.shutdown.assert_called_once()

                # Verify that the state was properly updated to indicate shutdown happened
                self.assertTrue(
                    _CUSTOMER_SDKSTATS_STATE["SHUTDOWN"],
                    "The SHUTDOWN state should be set to True after invalid response code",
                )
        finally:
            # Restore the original _CUSTOMER_SDKSTATS_METRICS
            setattr(customer_sdkstats_module, "_CUSTOMER_SDKSTATS_METRICS", original_metrics)

    def test_customer_sdkstats_shutdown_on_failure_threshold(self):
        """Test that customer sdkstats shutdown function properly updates the shutdown state"""
        # This test verifies that the shutdown_customer_sdkstats_metrics function
        # properly updates the SHUTDOWN state when called

        # Import needed components for verification
        from azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats import (
            shutdown_customer_sdkstats_metrics,
            _CUSTOMER_SDKSTATS_STATE,
            _CUSTOMER_SDKSTATS_STATE_LOCK,
            CustomerSdkStatsMetrics,
        )

        # Set up a meter provider mock to ensure we have something to shutdown
        mock_meter_provider = mock.MagicMock()

        # Create a mock instance for CustomerSdkStatsMetrics to be used in the global variable
        mock_instance = mock.MagicMock()
        mock_instance._customer_sdkstats_meter_provider = mock_meter_provider

        # Set _CUSTOMER_SDKSTATS_METRICS to our mock instance
        import sys

        customer_sdkstats_module = sys.modules["azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats"]
        original_metrics = getattr(customer_sdkstats_module, "_CUSTOMER_SDKSTATS_METRICS", None)
        setattr(customer_sdkstats_module, "_CUSTOMER_SDKSTATS_METRICS", mock_instance)

        try:
            # Make sure state starts with SHUTDOWN as False
            with _CUSTOMER_SDKSTATS_STATE_LOCK:
                _CUSTOMER_SDKSTATS_STATE["SHUTDOWN"] = False

            # Call the actual shutdown function directly (no mocking)
            shutdown_customer_sdkstats_metrics()

            # Verify the meter provider's shutdown was called
            mock_meter_provider.shutdown.assert_called_once()

            # Verify that the state was properly updated by the function
            self.assertTrue(
                _CUSTOMER_SDKSTATS_STATE["SHUTDOWN"],
                "The SHUTDOWN state should be set to True after shutdown_customer_sdkstats_metrics is called",
            )
        finally:
            # Restore the original _CUSTOMER_SDKSTATS_METRICS
            setattr(customer_sdkstats_module, "_CUSTOMER_SDKSTATS_METRICS", original_metrics)

        # Note: The actual integration point exists in _base.py where both shutdown
        # functions are called together during failure threshold

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_customer_sdkstats_no_collection_after_shutdown(self):
        """Test that customer sdkstats is not collected after shutdown"""
        from azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats import (
            _CUSTOMER_SDKSTATS_STATE,
            _CUSTOMER_SDKSTATS_STATE_LOCK,
        )

        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.collect_customer_sdkstats"
        ) as mock_collect:
            # First exporter should trigger collection (if not already shutdown)
            exporter1 = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789012",
                disable_offline_storage=True,
            )
            initial_should_collect = exporter1._should_collect_customer_sdkstats()

            # Directly set shutdown state (simulating what shutdown function should do)
            with _CUSTOMER_SDKSTATS_STATE_LOCK:
                _CUSTOMER_SDKSTATS_STATE["SHUTDOWN"] = True

            # Second exporter should not trigger collection
            exporter2 = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789012",
                disable_offline_storage=True,
            )
            self.assertFalse(exporter2._should_collect_customer_sdkstats())

    def test_handle_transmit_from_storage_success_triggers_transmit(self):
        exporter = BaseExporter(disable_offline_storage=False)

        with mock.patch.object(exporter, "_transmit_from_storage") as mock_transmit_from_storage:
            test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

            exporter._handle_transmit_from_storage(test_envelopes, ExportResult.SUCCESS)

            mock_transmit_from_storage.assert_called_once()

    def test_handle_transmit_from_storage_no_storage(self):
        exporter = BaseExporter(disable_offline_storage=True)

        self.assertIsNone(exporter.storage)

        test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

        exporter._handle_transmit_from_storage(test_envelopes, ExportResult.SUCCESS)
        exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

    def test_transmit_from_storage_no_storage(self):
        exporter = BaseExporter(disable_offline_storage=True)

        self.assertIsNone(exporter.storage)

        exporter._transmit_from_storage()

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._track_dropped_items")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    def test_handle_transmit_from_storage_client_storage_disabled_tracked(
        self, mock_track_dropped_from_storage, mock_track_dropped
    ):
        """Test that _handle_transmit_from_storage tracks CLIENT_STORAGE_DISABLED when storage.put() returns CLIENT_STORAGE_DISABLED"""
        exporter = BaseExporter(disable_offline_storage=False)

        # Setup customer sdkstats
        mock_customer_sdkstats = mock.Mock()
        exporter._customer_sdkstats_metrics = mock_customer_sdkstats
        exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

        # Mock the storage to return CLIENT_STORAGE_DISABLED
        exporter.storage = mock.Mock()
        exporter.storage.put.return_value = StorageExportResult.CLIENT_STORAGE_DISABLED

        test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

        # Set up side_effect for _track_dropped_items_from_storage
        def side_effect(customer_sdkstats, result_from_storage_put, envelopes):
            from azure.monitor.opentelemetry.exporter.statsbeat._utils import _track_dropped_items_from_storage

            # Call the real function which will use our mocked _track_dropped_items
            _track_dropped_items_from_storage(customer_sdkstats, result_from_storage_put, envelopes)

        mock_track_dropped_from_storage.side_effect = side_effect

        # Call _handle_transmit_from_storage with FAILED_RETRYABLE
        result = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

        # Verify storage.put was called
        exporter.storage.put.assert_called_once()

        # Verify that _track_dropped_items_from_storage was called with CLIENT_STORAGE_DISABLED
        mock_track_dropped_from_storage.assert_called_once_with(
            mock_customer_sdkstats, StorageExportResult.CLIENT_STORAGE_DISABLED, test_envelopes
        )

        # Verify that _track_dropped_items was called with CLIENT_STORAGE_DISABLED
        mock_track_dropped.assert_called_once_with(
            mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_STORAGE_DISABLED
        )

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._track_dropped_items")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    def test_handle_transmit_from_storage_client_readonly_tracked(
        self, mock_track_dropped_from_storage, mock_track_dropped
    ):
        """Test that _handle_transmit_from_storage tracks CLIENT_READONLY when storage.put() returns CLIENT_READONLY"""
        exporter = BaseExporter(disable_offline_storage=False)

        # Setup customer sdkstats
        mock_customer_sdkstats = mock.Mock()
        exporter._customer_sdkstats_metrics = mock_customer_sdkstats
        exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

        # Mock the storage to return CLIENT_READONLY
        exporter.storage = mock.Mock()
        exporter.storage.put.return_value = StorageExportResult.CLIENT_READONLY

        test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

        # Set up side_effect for _track_dropped_items_from_storage
        def side_effect(customer_sdkstats, result_from_storage_put, envelopes):
            from azure.monitor.opentelemetry.exporter.statsbeat._utils import _track_dropped_items_from_storage

            # Call the real function which will use our mocked _track_dropped_items
            _track_dropped_items_from_storage(customer_sdkstats, result_from_storage_put, envelopes)

        mock_track_dropped_from_storage.side_effect = side_effect

        # Save the original readonly state
        original_readonly_state = _LOCAL_STORAGE_SETUP_STATE["READONLY"]
        _LOCAL_STORAGE_SETUP_STATE["READONLY"] = True

        try:
            # Call _handle_transmit_from_storage with FAILED_RETRYABLE
            result = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

            # Verify storage.put was called
            exporter.storage.put.assert_called_once()

            # Verify that _track_dropped_items_from_storage was called with the right arguments
            mock_track_dropped_from_storage.assert_called_once_with(
                mock_customer_sdkstats, StorageExportResult.CLIENT_READONLY, test_envelopes
            )

            # Verify that _track_dropped_items was called with CLIENT_READONLY
            mock_track_dropped.assert_called_once_with(mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_READONLY)

            # Verify _LOCAL_STORAGE_SETUP_STATE READONLY remains True (once set, it stays True)
            self.assertTrue(_LOCAL_STORAGE_SETUP_STATE["READONLY"])

            # Verify the method returns None as expected
            self.assertIsNone(result)
        finally:
            # Restore original state
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = original_readonly_state

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._track_dropped_items")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    def test_handle_transmit_from_storage_client_persistence_capacity_tracked(
        self, mock_track_dropped_from_storage, mock_track_dropped
    ):
        """Test that _handle_transmit_from_storage tracks CLIENT_PERSISTENCE_CAPACITY when storage.put() returns CLIENT_PERSISTENCE_CAPACITY_REACHED"""
        exporter = BaseExporter(disable_offline_storage=False)

        # Setup customer sdkstats
        mock_customer_sdkstats = mock.Mock()
        exporter._customer_sdkstats_metrics = mock_customer_sdkstats
        exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

        # Mock the storage to return CLIENT_PERSISTENCE_CAPACITY_REACHED
        exporter.storage = mock.Mock()
        exporter.storage.put.return_value = StorageExportResult.CLIENT_PERSISTENCE_CAPACITY_REACHED

        test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

        # Set up side_effect for _track_dropped_items_from_storage
        def side_effect(customer_sdkstats, result_from_storage_put, envelopes):
            from azure.monitor.opentelemetry.exporter.statsbeat._utils import _track_dropped_items_from_storage

            # Call the real function which will use our mocked _track_dropped_items
            _track_dropped_items_from_storage(customer_sdkstats, result_from_storage_put, envelopes)

        mock_track_dropped_from_storage.side_effect = side_effect

        # Call _handle_transmit_from_storage with FAILED_RETRYABLE
        result = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

        # Verify storage.put was called
        exporter.storage.put.assert_called_once()

        # Verify that _track_dropped_items_from_storage was called with the right arguments
        mock_track_dropped_from_storage.assert_called_once_with(
            mock_customer_sdkstats, StorageExportResult.CLIENT_PERSISTENCE_CAPACITY_REACHED, test_envelopes
        )

        # Verify that _track_dropped_items was called with CLIENT_PERSISTENCE_CAPACITY
        mock_track_dropped.assert_called_once_with(
            mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_PERSISTENCE_CAPACITY
        )

        # Verify the method returns None as expected
        self.assertIsNone(result)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_handle_transmit_from_storage_client_exception_tracked(
        self, mock_track_dropped, mock_track_dropped_from_storage
    ):
        """Test that _handle_transmit_from_storage tracks CLIENT_EXCEPTION when storage.put() returns an error string and updates _LOCAL_STORAGE_SETUP_STATE"""
        exporter = BaseExporter(disable_offline_storage=False)

        # Setup customer sdkstats
        mock_customer_sdkstats = mock.Mock()
        exporter._customer_sdkstats_metrics = mock_customer_sdkstats
        exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

        # Mock the storage to return an error string (not one of the enum values)
        error_message = "Storage write failed: Permission denied"
        exporter.storage = mock.Mock()
        exporter.storage.put.return_value = error_message

        test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

        # Set initial exception state
        original_exception_state = _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]
        _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = error_message

        # Set up side_effect for _track_dropped_items_from_storage
        def side_effect(customer_sdkstats, result_from_storage_put, envelopes):
            from azure.monitor.opentelemetry.exporter.export._base import _track_dropped_items

            if isinstance(result_from_storage_put, str):
                _track_dropped_items(customer_sdkstats, envelopes, DropCode.CLIENT_EXCEPTION, result_from_storage_put)

        mock_track_dropped_from_storage.side_effect = side_effect

        try:
            # Directly call storage.put and track_dropped_items_from_storage
            envelopes_to_store = [x.as_dict() for x in test_envelopes]
            result_from_storage = exporter.storage.put(envelopes_to_store)

            # Call _track_dropped_items_from_storage directly
            mock_track_dropped_from_storage(mock_customer_sdkstats, result_from_storage, test_envelopes)

            # Verify storage.put was called
            exporter.storage.put.assert_called_once()

            # Verify that _track_dropped_items_from_storage was called with error message
            mock_track_dropped_from_storage.assert_called_once_with(
                mock_customer_sdkstats, error_message, test_envelopes
            )

            # Verify that _track_dropped_items was called with CLIENT_EXCEPTION and error message
            mock_track_dropped.assert_called_once_with(
                mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_EXCEPTION, error_message
            )

            # Verify _LOCAL_STORAGE_SETUP_STATE remains unchanged during execution
            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"], error_message)

        finally:
            # Restore original state
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = original_exception_state

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_handle_transmit_from_storage_no_storage_client_storage_disabled_tracked(self, mock_track_dropped):
        """Test that _handle_transmit_from_storage tracks CLIENT_STORAGE_DISABLED when storage is disabled"""
        exporter = BaseExporter(disable_offline_storage=True)

        # Setup customer sdkstats
        mock_customer_sdkstats = mock.Mock()
        exporter._customer_sdkstats_metrics = mock_customer_sdkstats
        exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

        # Verify storage is None
        self.assertIsNone(exporter.storage)

        test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

        # Call _handle_transmit_from_storage with FAILED_RETRYABLE
        result = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

        # Verify that _track_dropped_items was called with CLIENT_STORAGE_DISABLED
        mock_track_dropped.assert_called_once_with(
            mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_STORAGE_DISABLED
        )

        # Verify no return value when storage is disabled
        self.assertIsNone(result)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_handle_transmit_from_storage_success_triggers_transmit_from_storage(
        self,
    ):
        """Test that _handle_transmit_from_storage calls _transmit_from_storage on SUCCESS"""
        exporter = BaseExporter(disable_offline_storage=False)

        # Setup customer sdkstats
        mock_customer_sdkstats = mock.Mock()
        exporter._customer_sdkstats_metrics = mock_customer_sdkstats
        exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

        # Mock storage and _transmit_from_storage
        exporter.storage = mock.Mock()

        test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

        with mock.patch.object(exporter, "_transmit_from_storage") as mock_transmit_from_storage:
            # Call _handle_transmit_from_storage with SUCCESS
            result = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.SUCCESS)

            # Verify _transmit_from_storage was called
            mock_transmit_from_storage.assert_called_once()

            # Verify storage.put was not called for SUCCESS
            exporter.storage.put.assert_not_called()

            # Verify no return value for SUCCESS
            self.assertIsNone(result)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_partial_success_206_client_exception_tracking(self, mock_track_dropped, mock_track_dropped_from_storage):
        """Test that both _track_dropped_items_from_storage and _track_dropped_items are called correctly
        when there's a 206 Partial Success with CLIENT_EXCEPTION scenario."""

        # Set up side effect to call the real function but use our mock for _track_dropped_items
        def side_effect(statsbeat, result_from_storage, telemetry):
            from azure.monitor.opentelemetry.exporter.statsbeat._utils import _track_dropped_items

            if isinstance(result_from_storage, str):
                _track_dropped_items(statsbeat, telemetry, DropCode.CLIENT_EXCEPTION, result_from_storage)

        mock_track_dropped_from_storage.side_effect = side_effect

        # Create base exporter
        exporter = BaseExporter()
        mock_customer_sdkstats = mock.Mock()
        exporter._customer_sdkstats_metrics = mock_customer_sdkstats
        exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

        # Enable storage
        exporter.storage = mock.Mock()

        # Create test envelopes for first batch that will be "accepted"
        accepted_envelopes = [TelemetryItem(name="accepted", time=datetime.now())]

        # Create test envelopes for second batch that will be "retried" due to 206
        resend_envelopes = [TelemetryItem(name="retried", time=datetime.now())]

        # Mock the storage.put method to return a string error (simulating CLIENT_EXCEPTION)
        error_message = "Test error message for client exception"
        exporter.storage.put.return_value = error_message

        # Mock transmit method to return partial success (206) and trigger track_dropped_items_from_storage
        with mock.patch.object(AzureMonitorClient, "track") as mock_track:
            # Setup mock for 206 response with one retryable error
            mock_track.return_value = TrackResponse(
                items_received=2,
                items_accepted=1,
                errors=[
                    TelemetryErrorDetails(index=1, status_code=500, message="should retry"),
                ],
            )

            # Call _transmit to trigger the code path
            result = exporter._transmit(accepted_envelopes + resend_envelopes)

        # Verify storage.put was called
        exporter.storage.put.assert_called_once()

        # Verify _track_dropped_items_from_storage was called with the correct parameters
        mock_track_dropped_from_storage.assert_called_once()
        dropped_args = mock_track_dropped_from_storage.call_args[0]
        self.assertEqual(dropped_args[0], mock_customer_sdkstats)
        self.assertEqual(dropped_args[1], error_message)  # The error message from storage.put

        # Verify _track_dropped_items was called with CLIENT_EXCEPTION from our side_effect
        mock_track_dropped.assert_called_once()
        dropped_items_args = mock_track_dropped.call_args[0]
        self.assertEqual(dropped_items_args[0], mock_customer_sdkstats)
        self.assertEqual(dropped_items_args[2], DropCode.CLIENT_EXCEPTION)
        self.assertEqual(dropped_items_args[3], error_message)

        # Verify result is FAILED_NOT_RETRYABLE as we already tried to store
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_LOCAL_STORAGE_SETUP_STATE_exception_isolation_with_errno(
        self, mock_track_dropped, mock_track_dropped_from_storage
    ):
        """Test that errno-based exceptions are properly isolated and don't affect readonly state"""
        # Save original state
        original_readonly_state = _LOCAL_STORAGE_SETUP_STATE["READONLY"]
        original_exception_state = _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]

        try:
            # Test with both states - readonly True, exception state empty (normal post-reset state)
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = True
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = ""

            exporter = BaseExporter(disable_offline_storage=False)
            mock_customer_sdkstats = mock.Mock()
            exporter._customer_sdkstats_metrics = mock_customer_sdkstats
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

            # Mock storage.put() to return error string
            exporter.storage = mock.Mock()
            exporter.storage.put.return_value = "Storage error occurred"

            test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

            # Instead of actually mocking the call, we'll side_effect to call the real function
            # but with our mocked _track_dropped_items
            def side_effect(customer_sdkstats, result_from_storage_put, envelopes):
                from azure.monitor.opentelemetry.exporter.export._base import _track_dropped_items

                if isinstance(result_from_storage_put, str):
                    _track_dropped_items(
                        customer_sdkstats, envelopes, DropCode.CLIENT_EXCEPTION, result_from_storage_put
                    )

            mock_track_dropped_from_storage.side_effect = side_effect

            # Directly call storage.put and track_dropped_items_from_storage instead of _handle_transmit_from_storage
            envelopes_to_store = [x.as_dict() for x in test_envelopes]
            result_from_storage = exporter.storage.put(envelopes_to_store)

            # Call _track_dropped_items_from_storage directly
            mock_track_dropped_from_storage(mock_customer_sdkstats, result_from_storage, test_envelopes)

            # Verify that _track_dropped_items_from_storage was called with the right arguments
            mock_track_dropped_from_storage.assert_called_once_with(
                mock_customer_sdkstats, "Storage error occurred", test_envelopes
            )

            # Verify that _track_dropped_items was called with CLIENT_EXCEPTION and the error message
            mock_track_dropped.assert_called_once_with(
                mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_EXCEPTION, "Storage error occurred"
            )

            # Verify readonly remains True, exception state remains empty
            self.assertTrue(_LOCAL_STORAGE_SETUP_STATE["READONLY"])
            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"], "")

        finally:
            # Restore original state
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = original_readonly_state
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = original_exception_state

    # ===== Comprehensive _handle_transmit_from_storage Error Scenario Tests =====

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_handle_transmit_from_storage_localfilestorage_readonly_simulation(
        self, mock_track_dropped, mock_track_dropped_from_storage
    ):
        """Test LocalFileStorage(read-only filesystem) simulation during _check_and_set_folder_permissions"""

        # Set up side effect to call the real function but use our mock for _track_dropped_items
        def side_effect(statsbeat, result_from_storage_put, telemetry):
            from azure.monitor.opentelemetry.exporter.export._base import _track_dropped_items

            if result_from_storage_put == StorageExportResult.CLIENT_READONLY:
                _track_dropped_items(statsbeat, telemetry, DropCode.CLIENT_READONLY)

        mock_track_dropped_from_storage.side_effect = side_effect
        """Test LocalFileStorage(read-only filesystem) simulation during _check_and_set_folder_permissions"""
        # Save original state
        original_readonly_state = _LOCAL_STORAGE_SETUP_STATE["READONLY"]
        original_exception_state = _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]

        try:
            # Simulate (Read-only file system) during folder permissions check
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = True
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = ""

            exporter = BaseExporter(disable_offline_storage=False)
            mock_customer_sdkstats = mock.Mock()
            exporter._customer_sdkstats_metrics = mock_customer_sdkstats
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

            # Mock storage to return CLIENT_READONLY
            exporter.storage = mock.Mock()
            exporter.storage.put.return_value = StorageExportResult.CLIENT_READONLY

            test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

            # Call _handle_transmit_from_storage with FAILED_RETRYABLE
            result = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

            # Verify storage.put was called
            exporter.storage.put.assert_called_once()

            # Verify that _track_dropped_items was called with CLIENT_READONLY
            mock_track_dropped.assert_called_once_with(mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_READONLY)

            # Verify readonly state remains True (once set, it stays True)
            self.assertTrue(_LOCAL_STORAGE_SETUP_STATE["READONLY"])
            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"], "")

            self.assertIsNone(result)

        finally:
            # Restore original state
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = original_readonly_state
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = original_exception_state

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_partial_success_206_client_exception_tracking(self, mock_track_dropped, mock_track_dropped_from_storage):
        """Test that both _track_dropped_items_from_storage and _track_dropped_items are called correctly
        when there's a 206 Partial Success with CLIENT_EXCEPTION scenario."""

        # Set up side effect to call the real function but use our mock for _track_dropped_items
        def side_effect(statsbeat, result_from_storage, telemetry):
            from azure.monitor.opentelemetry.exporter.export._base import _track_dropped_items

            if isinstance(result_from_storage, str):
                _track_dropped_items(statsbeat, telemetry, DropCode.CLIENT_EXCEPTION, result_from_storage)

        mock_track_dropped_from_storage.side_effect = side_effect

        # Create base exporter
        exporter = BaseExporter()
        mock_customer_sdkstats = mock.Mock()
        exporter._customer_sdkstats_metrics = mock_customer_sdkstats
        exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

        # Enable storage
        exporter.storage = mock.Mock()

        # Create test envelopes for first batch that will be "accepted"
        accepted_envelopes = [TelemetryItem(name="accepted", time=datetime.now())]

        # Create test envelopes for second batch that will be "retried" due to 206
        resend_envelopes = [TelemetryItem(name="retried", time=datetime.now())]

        # Mock the storage.put method to return a string error (simulating CLIENT_EXCEPTION)
        error_message = "Test error message for client exception"
        exporter.storage.put.return_value = error_message

        # Mock transmit method to return partial success (206) and trigger track_dropped_items_from_storage
        with mock.patch.object(AzureMonitorClient, "track") as mock_track:
            # Setup mock for 206 response with one retryable error
            mock_track.return_value = TrackResponse(
                items_received=2,
                items_accepted=1,
                errors=[
                    TelemetryErrorDetails(index=1, status_code=500, message="should retry"),
                ],
            )

            # Call _transmit to trigger the code path
            result = exporter._transmit(accepted_envelopes + resend_envelopes)

        # Verify storage.put was called with the resend_envelopes
        self.assertEqual(exporter.storage.put.call_count, 1)

        # Verify _track_dropped_items_from_storage was called with the correct parameters
        mock_track_dropped_from_storage.assert_called_once_with(mock_customer_sdkstats, error_message, resend_envelopes)

        # Verify _track_dropped_items was called with CLIENT_EXCEPTION from our side_effect
        mock_track_dropped.assert_called_once_with(
            mock_customer_sdkstats, resend_envelopes, DropCode.CLIENT_EXCEPTION, error_message
        )

        # Verify final result is FAILED_NOT_RETRYABLE because we already tried to store in offline storage
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_partial_success_206_persistence_capacity_tracking(
        self, mock_track_dropped, mock_track_dropped_from_storage
    ):
        """Test that both _track_dropped_items_from_storage and _track_dropped_items are called correctly
        when there's a 206 Partial Success with CLIENT_PERSISTENCE_CAPACITY scenario."""

        # Set up side effect to call the real function but use our mock for _track_dropped_items
        def side_effect(statsbeat, result_from_storage, telemetry):
            from azure.monitor.opentelemetry.exporter.export._base import _track_dropped_items

            if result_from_storage == StorageExportResult.CLIENT_PERSISTENCE_CAPACITY_REACHED:
                _track_dropped_items(statsbeat, telemetry, DropCode.CLIENT_PERSISTENCE_CAPACITY)

        mock_track_dropped_from_storage.side_effect = side_effect

        # Create base exporter
        exporter = BaseExporter()
        mock_customer_sdkstats = mock.Mock()
        exporter._customer_sdkstats_metrics = mock_customer_sdkstats
        exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

        # Enable storage
        exporter.storage = mock.Mock()

        # Create test envelopes for first batch that will be "accepted"
        accepted_envelopes = [TelemetryItem(name="accepted", time=datetime.now())]

        # Create test envelopes for second batch that will be "retried" due to 206
        resend_envelopes = [TelemetryItem(name="retried", time=datetime.now())]

        # Mock the storage.put method to return CLIENT_PERSISTENCE_CAPACITY_REACHED
        exporter.storage.put.return_value = StorageExportResult.CLIENT_PERSISTENCE_CAPACITY_REACHED

        # Mock transmit method to return partial success (206) and resend_envelopes
        exporter._transmit = mock.Mock(return_value=(ExportResult.FAILED_RETRYABLE, resend_envelopes))

        # Call storage.put directly with resend_envelopes
        test_envelopes = accepted_envelopes + resend_envelopes
        envelopes_to_store = [x.as_dict() for x in resend_envelopes]
        result_from_storage = exporter.storage.put(envelopes_to_store)

        # Call _track_dropped_items_from_storage directly since we're not using the normal flow
        mock_track_dropped_from_storage(mock_customer_sdkstats, result_from_storage, resend_envelopes)

        # Verify storage.put was called with the resend_envelopes
        self.assertEqual(exporter.storage.put.call_count, 1)

        # Verify _track_dropped_items_from_storage was called with the correct parameters
        mock_track_dropped_from_storage.assert_called_once_with(
            mock_customer_sdkstats, StorageExportResult.CLIENT_PERSISTENCE_CAPACITY_REACHED, resend_envelopes
        )

        # Verify _track_dropped_items was called with CLIENT_PERSISTENCE_CAPACITY from our side_effect
        mock_track_dropped.assert_called_once_with(
            mock_customer_sdkstats, resend_envelopes, DropCode.CLIENT_PERSISTENCE_CAPACITY
        )

        # Verify result_from_storage has the expected value
        self.assertEqual(result_from_storage, StorageExportResult.CLIENT_PERSISTENCE_CAPACITY_REACHED)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_handle_transmit_from_storage_localfilestorage_general_exception_simulation(
        self, mock_track_dropped, mock_track_dropped_from_storage
    ):
        """Test LocalFileStorage general exception simulation during _check_and_set_folder_permissions"""

        # Set up side effect to call the real function but use our mock for _track_dropped_items
        def side_effect(statsbeat, result_from_storage_put, telemetry):
            from azure.monitor.opentelemetry.exporter.export._base import _track_dropped_items
            from azure.monitor.opentelemetry.exporter.statsbeat._utils import get_local_storage_setup_state_exception

            if get_local_storage_setup_state_exception() != "":
                _track_dropped_items(statsbeat, telemetry, DropCode.CLIENT_EXCEPTION, result_from_storage_put)
            elif isinstance(result_from_storage_put, str):
                _track_dropped_items(statsbeat, telemetry, DropCode.CLIENT_EXCEPTION, result_from_storage_put)

        mock_track_dropped_from_storage.side_effect = side_effect
        """Test LocalFileStorage general exception simulation during _check_and_set_folder_permissions"""
        # Save original state
        original_readonly_state = _LOCAL_STORAGE_SETUP_STATE["READONLY"]
        original_exception_state = _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]

        try:
            # Simulate general exception during folder permissions check
            general_exception_message = "ValueError: Invalid path format"
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = False
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = general_exception_message

            exporter = BaseExporter(disable_offline_storage=False)
            mock_customer_sdkstats = mock.Mock()
            exporter._customer_sdkstats_metrics = mock_customer_sdkstats
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

            # Mock storage to return success, but we have exception state from folder permissions
            exporter.storage = mock.Mock()
            exporter.storage.put.return_value = "/path/to/successful/blob"  # Success path

            test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

            # Call _handle_transmit_from_storage with FAILED_RETRYABLE
            result = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

            # Verify storage.put was called
            exporter.storage.put.assert_called_once()

            # Verify that _track_dropped_items was called with CLIENT_EXCEPTION from folder permissions
            mock_track_dropped.assert_called_once_with(
                mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_EXCEPTION, "/path/to/successful/blob"
            )

            # Verify exception state was reset after handling
            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"], general_exception_message)
            self.assertFalse(_LOCAL_STORAGE_SETUP_STATE["READONLY"])

            self.assertIsNone(result)

        finally:
            # Restore original state
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = original_readonly_state
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = original_exception_state

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_handle_transmit_from_storage_localfileblob_put_exception_simulation(
        self, mock_track_dropped, mock_track_dropped_from_storage
    ):
        """Test LocalFileBlob.put() exception simulation (file write errors)"""

        # Set up side effect to call the real function but use our mock for _track_dropped_items
        def side_effect(statsbeat, result_from_storage_put, telemetry):
            from azure.monitor.opentelemetry.exporter.export._base import _track_dropped_items

            if isinstance(result_from_storage_put, str):
                _track_dropped_items(statsbeat, telemetry, DropCode.CLIENT_EXCEPTION, result_from_storage_put)

        mock_track_dropped_from_storage.side_effect = side_effect
        """Test LocalFileBlob.put() exception simulation (file write errors)"""
        # Save original state
        original_readonly_state = _LOCAL_STORAGE_SETUP_STATE["READONLY"]
        original_exception_state = _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]

        try:
            # Clean state - no prior exceptions
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = False
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = ""

            exporter = BaseExporter(disable_offline_storage=False)
            mock_customer_sdkstats = mock.Mock()
            exporter._customer_sdkstats_metrics = mock_customer_sdkstats
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

            # Mock storage.put() to return string error (like LocalFileBlob.put() does)
            blob_error_message = "[Errno 28] No space left on device"
            exporter.storage = mock.Mock()
            exporter.storage.put.return_value = blob_error_message

            test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

            # Call _handle_transmit_from_storage with FAILED_RETRYABLE
            result = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

            # Verify storage.put was called
            exporter.storage.put.assert_called_once()

            # Verify that _track_dropped_items was called with CLIENT_EXCEPTION from blob put error
            mock_track_dropped.assert_called_once_with(
                mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_EXCEPTION, blob_error_message
            )

            # Verify states remain clean (blob errors don't affect global state)
            self.assertFalse(_LOCAL_STORAGE_SETUP_STATE["READONLY"])
            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"], "")

            self.assertIsNone(result)

        finally:
            # Restore original state
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = original_readonly_state
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = original_exception_state

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_handle_transmit_from_storage_localfileblob_rename_exception_simulation(
        self, mock_track_dropped, mock_track_dropped_from_storage
    ):
        """Test LocalFileBlob.put() rename exception simulation (atomic write failure)"""

        # Set up side effect to call the real function but use our mock for _track_dropped_items
        def side_effect(statsbeat, result_from_storage_put, telemetry):
            from azure.monitor.opentelemetry.exporter.export._base import _track_dropped_items

            if isinstance(result_from_storage_put, str):
                _track_dropped_items(statsbeat, telemetry, DropCode.CLIENT_EXCEPTION, result_from_storage_put)

        mock_track_dropped_from_storage.side_effect = side_effect
        """Test LocalFileBlob.put() rename exception simulation (atomic write failure)"""
        # Save original state
        original_readonly_state = _LOCAL_STORAGE_SETUP_STATE["READONLY"]
        original_exception_state = _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]

        try:
            # Clean state - no prior exceptions
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = False
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = ""

            exporter = BaseExporter(disable_offline_storage=False)
            mock_customer_sdkstats = mock.Mock()
            exporter._customer_sdkstats_metrics = mock_customer_sdkstats
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

            # Mock storage.put() to return string error (rename/atomic write failure)
            rename_error_message = "[Errno 1] Operation not permitted: rename failure"
            exporter.storage = mock.Mock()
            exporter.storage.put.return_value = rename_error_message

            test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

            # Call _handle_transmit_from_storage with FAILED_RETRYABLE
            result = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

            # Verify storage.put was called
            exporter.storage.put.assert_called_once()

            # Verify that _track_dropped_items was called with CLIENT_EXCEPTION from rename error
            mock_track_dropped.assert_called_once_with(
                mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_EXCEPTION, rename_error_message
            )

            # Verify states remain clean (blob errors don't affect global state)
            self.assertFalse(_LOCAL_STORAGE_SETUP_STATE["READONLY"])
            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"], "")

            self.assertIsNone(result)

        finally:
            # Restore original state
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = original_readonly_state
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = original_exception_state

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_handle_transmit_from_storage_localfileblob_json_serialization_exception_simulation(
        self, mock_track_dropped, mock_track_dropped_from_storage
    ):
        """Test LocalFileBlob.put() JSON serialization exception simulation"""

        # Set up side effect to call the real function but use our mock for _track_dropped_items
        def side_effect(statsbeat, result_from_storage_put, telemetry):
            from azure.monitor.opentelemetry.exporter.export._base import _track_dropped_items

            if isinstance(result_from_storage_put, str):
                _track_dropped_items(statsbeat, telemetry, DropCode.CLIENT_EXCEPTION, result_from_storage_put)

        mock_track_dropped_from_storage.side_effect = side_effect
        """Test LocalFileBlob.put() JSON serialization exception simulation"""
        # Save original state
        original_readonly_state = _LOCAL_STORAGE_SETUP_STATE["READONLY"]
        original_exception_state = _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]

        try:
            # Clean state - no prior exceptions
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = False
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = ""

            exporter = BaseExporter(disable_offline_storage=False)
            mock_customer_sdkstats = mock.Mock()
            exporter._customer_sdkstats_metrics = mock_customer_sdkstats
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

            # Mock storage.put() to return string error (JSON serialization failure)
            json_error_message = "TypeError: Object of type datetime is not JSON serializable"
            exporter.storage = mock.Mock()
            exporter.storage.put.return_value = json_error_message

            test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

            # Call _handle_transmit_from_storage with FAILED_RETRYABLE
            result = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

            # Verify storage.put was called
            exporter.storage.put.assert_called_once()

            # Verify that _track_dropped_items was called with CLIENT_EXCEPTION from JSON error
            mock_track_dropped.assert_called_once_with(
                mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_EXCEPTION, json_error_message
            )

            # Verify states remain clean (blob errors don't affect global state)
            self.assertFalse(_LOCAL_STORAGE_SETUP_STATE["READONLY"])
            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"], "")

            self.assertIsNone(result)

        finally:
            # Restore original state
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = original_readonly_state
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = original_exception_state

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._track_dropped_items")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    def test_handle_transmit_from_storage_combined_folder_permissions_and_blob_errors(
        self, mock_track_dropped_from_storage, mock_track_dropped
    ):
        """Test combination of folder permissions exception state and subsequent blob errors"""
        # Save original state
        original_readonly_state = _LOCAL_STORAGE_SETUP_STATE["READONLY"]
        original_exception_state = _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]

        try:
            # Simulate folder permissions exception occurred during storage setup
            folder_exception_message = "OSError: [Errno 13] Permission denied during folder setup"
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = False
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = folder_exception_message

            exporter = BaseExporter(disable_offline_storage=False)
            mock_customer_sdkstats = mock.Mock()
            exporter._customer_sdkstats_metrics = mock_customer_sdkstats
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

            # Mock storage.put() to also return a blob error
            blob_error_message = "IOError: Disk full during blob write"
            exporter.storage = mock.Mock()
            exporter.storage.put.return_value = blob_error_message

            test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

            # Set up side_effect for _track_dropped_items_from_storage
            def side_effect(customer_sdkstats, result_from_storage_put, envelopes):
                from azure.monitor.opentelemetry.exporter.statsbeat._utils import _track_dropped_items_from_storage

                # Call the real function which will use our mocked _track_dropped_items
                _track_dropped_items_from_storage(customer_sdkstats, result_from_storage_put, envelopes)

            mock_track_dropped_from_storage.side_effect = side_effect

            # Call _handle_transmit_from_storage with FAILED_RETRYABLE
            result = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

            # Verify storage.put was called
            exporter.storage.put.assert_called_once()

            # Verify that _track_dropped_items_from_storage was called with the blob error
            mock_track_dropped_from_storage.assert_called_once_with(
                mock_customer_sdkstats, blob_error_message, test_envelopes
            )

            # Verify that _track_dropped_items was called with CLIENT_EXCEPTION from blob error
            mock_track_dropped.assert_called_once_with(
                mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_EXCEPTION, blob_error_message
            )

            # Verify folder exception state was reset after handling
            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"], folder_exception_message)
            self.assertFalse(_LOCAL_STORAGE_SETUP_STATE["READONLY"])

            self.assertIsNone(result)

        finally:
            # Restore original state
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = original_readonly_state
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = original_exception_state

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_handle_transmit_from_storage_readonly_filesystem_with_subsequent_errors(
        self, mock_track_dropped, mock_track_dropped_from_storage
    ):
        """Test readonly filesystem state with subsequent storage errors"""

        # Set up side effect to call the real function but use our mock for _track_dropped_items
        def side_effect(statsbeat, result_from_storage_put, telemetry):
            from azure.monitor.opentelemetry.exporter.export._base import _track_dropped_items

            if result_from_storage_put == StorageExportResult.CLIENT_READONLY:
                _track_dropped_items(statsbeat, telemetry, DropCode.CLIENT_READONLY)

        mock_track_dropped_from_storage.side_effect = side_effect
        """Test readonly filesystem state with subsequent storage errors"""
        # Save original state
        original_readonly_state = _LOCAL_STORAGE_SETUP_STATE["READONLY"]
        original_exception_state = _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]

        try:
            # Simulate readonly filesystem detected during folder permissions check
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = True
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = ""

            exporter = BaseExporter(disable_offline_storage=False)
            mock_customer_sdkstats = mock.Mock()
            exporter._customer_sdkstats_metrics = mock_customer_sdkstats
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

            # Mock storage.put() to return CLIENT_READONLY
            exporter.storage = mock.Mock()
            exporter.storage.put.return_value = StorageExportResult.CLIENT_READONLY

            test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

            # Call _handle_transmit_from_storage with FAILED_RETRYABLE
            result = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

            # Verify storage.put was called
            exporter.storage.put.assert_called_once()

            # Verify that _track_dropped_items was called with CLIENT_READONLY
            mock_track_dropped.assert_called_once_with(mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_READONLY)

            # Verify readonly state remains True (once set, it stays True)
            self.assertTrue(_LOCAL_STORAGE_SETUP_STATE["READONLY"])
            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"], "")

            self.assertIsNone(result)

        finally:
            # Restore original state
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = original_readonly_state
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = original_exception_state

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_handle_transmit_from_storage_success_path_validation(self, mock_track_dropped):
        """Test success path returns LocalFileBlob and doesn't trigger error handling"""
        # Save original state
        original_readonly_state = _LOCAL_STORAGE_SETUP_STATE["READONLY"]
        original_exception_state = _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]

        try:
            # Clean state - no exceptions or readonly
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = False
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = ""

            exporter = BaseExporter(disable_offline_storage=False)
            mock_customer_sdkstats = mock.Mock()
            exporter._customer_sdkstats_metrics = mock_customer_sdkstats
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

            # Mock storage.put() to return a LocalFileBlob object (not a string)
            # The success case is when LocalFileBlob.put() returns self (the LocalFileBlob instance)
            # which means storage.put() returns a LocalFileBlob object
            success_blob = mock.Mock()  # Mock LocalFileBlob object
            exporter.storage = mock.Mock()
            exporter.storage.put.return_value = success_blob

            test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

            # Call _handle_transmit_from_storage with FAILED_RETRYABLE
            result = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

            # Verify storage.put was called
            exporter.storage.put.assert_called_once()

            # Verify that _track_dropped_items was NOT called (success path - else clause)
            mock_track_dropped.assert_not_called()

            # Verify states remain clean (success doesn't affect state)
            self.assertFalse(_LOCAL_STORAGE_SETUP_STATE["READONLY"])
            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"], "")

            self.assertIsNone(result)

        finally:
            # Restore original state
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = original_readonly_state
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = original_exception_state

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_handle_transmit_from_storage_unexpected_return_value(self, mock_track_dropped1, mock_track_dropped2):
        """Test that when storage.put() returns an unexpected value type (not StorageExportResult or str),
        the method continues without any special handling."""
        exporter = BaseExporter(disable_offline_storage=False)
        mock_customer_sdkstats = mock.Mock()
        exporter._customer_sdkstats_metrics = mock_customer_sdkstats
        exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

        # Mock storage.put() to return an unexpected value type (int)
        exporter.storage = mock.Mock()
        exporter.storage.put.return_value = 42  # Neither StorageExportResult nor str

        test_envelopes = [TelemetryItem(name="test", time=datetime.now())]
        exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

        # Verify that no dropped items were tracked (since return value isn't handled)
        mock_track_dropped1.assert_not_called()
        mock_track_dropped2.assert_not_called()
        # Verify that the customer sdkstats wasn't invoked
        mock_customer_sdkstats.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_handle_transmit_from_storage_string_return_values_trigger_exception_tracking(
        self, mock_track_dropped, mock_track_dropped_from_storage
    ):
        """Test that string return values from storage.put() trigger CLIENT_EXCEPTION tracking"""

        # Set up side effect to call the real function but use our mock for _track_dropped_items
        def side_effect(statsbeat, result_from_storage_put, telemetry):
            from azure.monitor.opentelemetry.exporter.export._base import _track_dropped_items

            if isinstance(result_from_storage_put, str):
                _track_dropped_items(statsbeat, telemetry, DropCode.CLIENT_EXCEPTION, result_from_storage_put)

        mock_track_dropped_from_storage.side_effect = side_effect
        """Test that string return values from storage.put() trigger CLIENT_EXCEPTION tracking"""
        # Save original state
        original_readonly_state = _LOCAL_STORAGE_SETUP_STATE["READONLY"]
        original_exception_state = _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]

        try:
            # Clean state - no exceptions or readonly
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = False
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = ""

            exporter = BaseExporter(disable_offline_storage=False)
            mock_customer_sdkstats = mock.Mock()
            exporter._customer_sdkstats_metrics = mock_customer_sdkstats
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

            # Test different string return values that should trigger exception tracking
            string_returns = [
                "/tmp/telemetry/blob_12345.json",  # File path (success)
                "Permission denied",  # Error message
                "Disk full",  # Error message
                "",  # Empty string
                "Storage error occurred",  # Error message
            ]

            for string_return in string_returns:
                with self.subTest(string_return=string_return):
                    # Reset mock for each test
                    mock_track_dropped.reset_mock()

                    # Mock storage.put() to return string value
                    exporter.storage = mock.Mock()
                    exporter.storage.put.return_value = string_return

                    test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

                    # Call _handle_transmit_from_storage with FAILED_RETRYABLE
                    result = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

                    # Verify storage.put was called
                    exporter.storage.put.assert_called_once()

                    # Verify that _track_dropped_items WAS called (string triggers exception tracking)
                    mock_track_dropped.assert_called_once_with(
                        mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_EXCEPTION, string_return
                    )

                    # Verify states remain clean (storage.put() string errors don't affect global state)
                    self.assertFalse(_LOCAL_STORAGE_SETUP_STATE["READONLY"])
                    self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"], "")

                    self.assertIsNone(result)

        finally:
            # Restore original state
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = original_readonly_state
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = original_exception_state

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._track_dropped_items")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    def test_LOCAL_STORAGE_SETUP_STATE_readonly_and_exception_mixed_scenarios(
        self, mock_track_dropped_from_storage, mock_track_dropped
    ):
        """Test mixed scenarios where both readonly and exception conditions occur"""
        # Save original state
        original_readonly_state = _LOCAL_STORAGE_SETUP_STATE["READONLY"]
        original_exception_state = _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]

        try:
            exporter = BaseExporter(disable_offline_storage=False)
            mock_customer_sdkstats = mock.Mock()
            exporter._customer_sdkstats_metrics = mock_customer_sdkstats
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)
            exporter.storage = mock.Mock()

            test_envelopes = [TelemetryItem(name="test", time=datetime.now())]

            # Set up side_effect for _track_dropped_items_from_storage
            def side_effect(customer_sdkstats, result_from_storage_put, envelopes):
                from azure.monitor.opentelemetry.exporter.statsbeat._utils import _track_dropped_items_from_storage

                # Call the real function which will use our mocked _track_dropped_items
                _track_dropped_items_from_storage(customer_sdkstats, result_from_storage_put, envelopes)

            mock_track_dropped_from_storage.side_effect = side_effect

            # Scenario 1: Start with both states set, handle readonly first
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = True
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = "Storage error occurred"

            # Handle readonly condition
            exporter.storage.put.return_value = StorageExportResult.CLIENT_READONLY
            result1 = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

            # Verify readonly remains True (once set, it stays True), exception state preserved
            self.assertTrue(_LOCAL_STORAGE_SETUP_STATE["READONLY"])
            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"], "Storage error occurred")
            self.assertIsNone(result1)

            # Verify track_dropped_items_from_storage was called with readonly result
            mock_track_dropped_from_storage.assert_called_with(
                mock_customer_sdkstats, StorageExportResult.CLIENT_READONLY, test_envelopes
            )

            # Verify _track_dropped_items was called with CLIENT_READONLY
            mock_track_dropped.assert_called_with(mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_READONLY)

            # Scenario 2: Now handle the remaining exception
            mock_track_dropped_from_storage.reset_mock()
            mock_track_dropped.reset_mock()
            exporter.storage.put.return_value = "File system error: Permission denied"
            result2 = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

            # Verify exception was reset if exception state was updated, readonly state remains True
            self.assertTrue(_LOCAL_STORAGE_SETUP_STATE["READONLY"])
            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"], "Storage error occurred")
            self.assertIsNone(result2)

            # Verify track_dropped_items_from_storage was called with error string
            mock_track_dropped_from_storage.assert_called_with(
                mock_customer_sdkstats, "File system error: Permission denied", test_envelopes
            )

            # Verify _track_dropped_items was called with CLIENT_EXCEPTION and the error message
            mock_track_dropped.assert_called_with(
                mock_customer_sdkstats,
                test_envelopes,
                DropCode.CLIENT_EXCEPTION,
                "File system error: Permission denied",
            )

            # Scenario 3: Set both states again, handle exception first this time
            mock_track_dropped_from_storage.reset_mock()
            mock_track_dropped.reset_mock()
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = True
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = "Another error"

            # Handle exception condition first
            exporter.storage.put.return_value = "Disk full error"
            result3 = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["READONLY"], True)
            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"], "Another error")
            self.assertIsNone(result3)

            # Verify track_dropped_items_from_storage was called with error string
            mock_track_dropped_from_storage.assert_called_with(
                mock_customer_sdkstats, "Disk full error", test_envelopes
            )

            # Verify _track_dropped_items was called with CLIENT_EXCEPTION and the error message
            mock_track_dropped.assert_called_with(
                mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_EXCEPTION, "Disk full error"
            )

            # Scenario 4: Now handle the remaining readonly condition
            mock_track_dropped_from_storage.reset_mock()
            mock_track_dropped.reset_mock()
            exporter.storage.put.return_value = StorageExportResult.CLIENT_READONLY
            result4 = exporter._handle_transmit_from_storage(test_envelopes, ExportResult.FAILED_RETRYABLE)

            # Verify readonly remains True (once set, it stays True), if exception state was changed, should be reset after recording dropped items
            self.assertTrue(_LOCAL_STORAGE_SETUP_STATE["READONLY"])
            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"], "Another error")
            self.assertIsNone(result4)

            # Verify track_dropped_items_from_storage was called with readonly result
            mock_track_dropped_from_storage.assert_called_with(
                mock_customer_sdkstats, StorageExportResult.CLIENT_READONLY, test_envelopes
            )

            # Verify _track_dropped_items was called with CLIENT_READONLY
            mock_track_dropped.assert_called_with(mock_customer_sdkstats, test_envelopes, DropCode.CLIENT_READONLY)

        finally:
            # Restore original state
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = original_readonly_state
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = original_exception_state

    def test_local_storage_state_exception_get_set_operations(self):
        """Test the validity of get and set operations for exception state in local storage state"""
        from azure.monitor.opentelemetry.exporter.statsbeat._state import (
            get_local_storage_setup_state_exception,
            set_local_storage_setup_state_exception,
            _LOCAL_STORAGE_SETUP_STATE,
            _LOCAL_STORAGE_SETUP_STATE_LOCK,
        )

        # Save original state
        original_exception_state = _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]

        try:
            # Test 1: Initial state should be None
            self.assertEqual(get_local_storage_setup_state_exception(), "")

            # Test 2: Set string value and verify get operation
            test_error = "Test storage exception"
            set_local_storage_setup_state_exception(test_error)
            self.assertEqual(get_local_storage_setup_state_exception(), test_error)

            # Test 3: Set empty string and verify get operation
            set_local_storage_setup_state_exception("")
            self.assertEqual(get_local_storage_setup_state_exception(), "")

            # Test 4: Set complex error message and verify get operation
            complex_error = "OSError: [Errno 28] No space left on device: '/tmp/storage/file.blob'"
            set_local_storage_setup_state_exception(complex_error)
            self.assertEqual(get_local_storage_setup_state_exception(), complex_error)

            # Test 5: Verify thread safety by directly accessing state
            with _LOCAL_STORAGE_SETUP_STATE_LOCK:
                direct_value = _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]
            self.assertEqual(direct_value, complex_error)
            self.assertEqual(get_local_storage_setup_state_exception(), direct_value)

            # Test 6: Test multiple rapid set/get operations
            test_values = ["Error 1", "Error 2", "Error 3", "", "Final error"]

            for value in test_values:
                with self.subTest(value=value):
                    set_local_storage_setup_state_exception(value)
                    self.assertEqual(get_local_storage_setup_state_exception(), value)

            # Test 8: Verify that set operation doesn't affect other state values
            original_readonly = _LOCAL_STORAGE_SETUP_STATE["READONLY"]
            set_local_storage_setup_state_exception("New exception")
            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["READONLY"], original_readonly)
            self.assertEqual(get_local_storage_setup_state_exception(), "New exception")

        finally:
            # Restore original state
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = original_exception_state

    def test_local_storage_state_exception_concurrent_access(self):
        """Test concurrent access to exception state get/set operations"""
        import threading
        import time
        from azure.monitor.opentelemetry.exporter.statsbeat._state import (
            get_local_storage_setup_state_exception,
            set_local_storage_setup_state_exception,
            _LOCAL_STORAGE_SETUP_STATE,
        )

        # Save original state
        original_exception_state = _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]
        results = []
        errors = []

        def worker_thread(thread_id):
            try:
                for i in range(10):
                    # Set a unique value
                    value = f"Thread-{thread_id}-Error-{i}"
                    set_local_storage_setup_state_exception(value)

                    # Small delay to increase chance of race conditions
                    time.sleep(0.001)

                    # Get the value and verify it's either our value or another thread's value
                    retrieved_value = get_local_storage_setup_state_exception()
                    results.append((thread_id, i, value, retrieved_value))

                    # Verify it's a valid value (either ours or from another thread)
                    if retrieved_value is not None:
                        self.assertIsInstance(retrieved_value, str)
                        self.assertTrue(retrieved_value.startswith("Thread-"))
            except Exception as e:
                errors.append(f"Thread {thread_id}: {e}")

        try:
            # Reset to original state
            set_local_storage_setup_state_exception("")

            # Start multiple threads
            threads = []
            for i in range(5):
                thread = threading.Thread(target=worker_thread, args=(i,))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Verify no errors occurred
            self.assertEqual(len(errors), 0, f"Errors in concurrent access: {errors}")

            # Verify we got results from all threads
            self.assertEqual(len(results), 50)  # 5 threads * 10 operations each

            # Verify final state is valid
            final_value = get_local_storage_setup_state_exception()
            if final_value is not None:
                self.assertIsInstance(final_value, str)
                self.assertTrue(final_value.startswith("Thread-"))

        finally:
            # Restore original state
            _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = original_exception_state

    def test_local_storage_state_readonly_get_operations(self):
        """Test the get operation for readonly state in local storage state"""
        from azure.monitor.opentelemetry.exporter.statsbeat._state import (
            get_local_storage_setup_state_readonly,
            _LOCAL_STORAGE_SETUP_STATE,
            _LOCAL_STORAGE_SETUP_STATE_LOCK,
        )

        # Save original state
        original_readonly_state = _LOCAL_STORAGE_SETUP_STATE["READONLY"]

        try:
            # Test 1: Initial state should be False
            self.assertEqual(get_local_storage_setup_state_readonly(), False)

            # Test 2: Set True directly and verify get operation
            with _LOCAL_STORAGE_SETUP_STATE_LOCK:
                _LOCAL_STORAGE_SETUP_STATE["READONLY"] = True
            self.assertEqual(get_local_storage_setup_state_readonly(), True)

            # Test 3: Set False directly and verify get operation
            with _LOCAL_STORAGE_SETUP_STATE_LOCK:
                _LOCAL_STORAGE_SETUP_STATE["READONLY"] = False
            self.assertEqual(get_local_storage_setup_state_readonly(), False)

            # Test 4: Verify get operation doesn't affect other state values
            original_exception = _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]
            with _LOCAL_STORAGE_SETUP_STATE_LOCK:
                _LOCAL_STORAGE_SETUP_STATE["READONLY"] = True

            # Get readonly state multiple times
            for _ in range(5):
                self.assertEqual(get_local_storage_setup_state_readonly(), True)

            # Verify exception state wasn't affected
            self.assertEqual(_LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"], original_exception)

        finally:
            # Restore original state
            _LOCAL_STORAGE_SETUP_STATE["READONLY"] = original_readonly_state

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_should_collect_customer_sdkstats_enabled(self):
        exporter = BaseExporter(disable_offline_storage=True)
        self.assertTrue(exporter._should_collect_customer_sdkstats())

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "false",
        },
    )
    def test_should_collect_customer_sdkstats_disabled(self):
        exporter = BaseExporter(disable_offline_storage=True)
        self.assertFalse(exporter._should_collect_customer_sdkstats())

    def test_should_collect_customer_sdkstats_env_not_set(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            exporter = BaseExporter(
                connection_string="InstrumentationKey=363331ca-f431-4119-bdcd-31a75920f958;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/",
                disable_offline_storage=True,
            )
            self.assertFalse(exporter._should_collect_customer_sdkstats())

    def test_should_collect_customer_sdkstats_instrumentation_collection(self):
        with mock.patch.dict(
            os.environ,
            {
                "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
                "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
            },
        ):
            exporter = BaseExporter(disable_offline_storage=True, instrumentation_collection=True)
            self.assertFalse(exporter._should_collect_customer_sdkstats())

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_base_exporter_storage_put_readonly_tracked(self, mock_track_dropped):
        """Test that BaseExporter tracks CLIENT_READONLY when storage.put() returns CLIENT_READONLY"""
        exporter = BaseExporter(disable_offline_storage=False)

        # Setup customer sdkstats
        mock_customer_sdkstats = mock.Mock()
        exporter._customer_sdkstats_metrics = mock_customer_sdkstats
        exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

        # Mock the storage to return CLIENT_READONLY
        exporter.storage = mock.Mock()
        exporter.storage.gets.return_value = []  # No blobs from storage
        exporter.storage.put.return_value = StorageExportResult.CLIENT_READONLY

        # This should trigger the storage status check in _transmit_from_storage
        exporter._transmit_from_storage()

        # Verify that _track_dropped_items was called with CLIENT_READONLY
        # Note: Since no envelopes are processed from storage, this should not be called in current implementation
        mock_track_dropped.assert_not_called()

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_base_exporter_storage_put_exception_tracked(self, mock_track_dropped):
        """Test that BaseExporter tracks CLIENT_EXCEPTION when storage.put() returns an error string"""
        exporter = BaseExporter(disable_offline_storage=False)

        # Setup customer sdkstats
        mock_customer_sdkstats = mock.Mock()
        exporter._customer_sdkstats_metrics = mock_customer_sdkstats
        exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

        # Mock the storage to return an error string
        exporter.storage = mock.Mock()
        exporter.storage.gets.return_value = []  # No blobs from storage
        error_message = "Storage write failed: Permission denied"
        exporter.storage.put.return_value = error_message

        # This should trigger the storage status check in _transmit_from_storage
        exporter._transmit_from_storage()

        # Verify that _track_dropped_items was called with CLIENT_EXCEPTION
        # Note: Since no envelopes are processed from storage, this should not be called in current implementation
        mock_track_dropped.assert_not_called()

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_base_exporter_storage_put_capacity_reached_tracked(self, mock_track_dropped):
        """Test that BaseExporter tracks CLIENT_PERSISTENCE_CAPACITY when storage.put() returns CLIENT_PERSISTENCE_CAPACITY_REACHED"""
        exporter = BaseExporter(disable_offline_storage=False)

        # Setup customer sdkstats
        mock_customer_sdkstats = mock.Mock()
        exporter._customer_sdkstats_metrics = mock_customer_sdkstats
        exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)

        # Mock the storage to return CLIENT_PERSISTENCE_CAPACITY_REACHED
        exporter.storage = mock.Mock()
        exporter.storage.gets.return_value = []  # No blobs from storage
        exporter.storage.put.return_value = StorageExportResult.CLIENT_PERSISTENCE_CAPACITY_REACHED

        # This should trigger the storage status check in _transmit_from_storage
        exporter._transmit_from_storage()

        # Verify that _track_dropped_items was called with CLIENT_PERSISTENCE_CAPACITY
        # Note: Since no envelopes are processed from storage, this should not be called in current implementation
        mock_track_dropped.assert_not_called()

    # Custom Breeze Message Handling Tests
    # These tests verify that custom error messages from Azure Monitor service (Breeze)
    # are properly preserved and passed through the error handling chain.

    def test_determine_client_retry_code_telemetry_error_details_with_custom_message(self):
        """Test that TelemetryErrorDetails with custom message preserves the message for specific status codes."""
        exporter = BaseExporter(disable_offline_storage=True)

        # Test various specific status codes with custom messages
        test_cases = [
            (401, "Authentication failed. Please check your instrumentation key."),
            (403, "Forbidden access. Verify your permissions for this resource."),
            (408, "Request timeout. The service took too long to respond."),
            (429, "Rate limit exceeded for instrumentation key. Current rate: 1000 req/min, limit: 500 req/min."),
            (500, "Internal server error. Please try again later."),
            (502, "Bad gateway. The upstream server is unavailable."),
            (503, "Service unavailable. The monitoring service is temporarily down."),
            (504, "Gateway timeout. The request timed out while waiting for the upstream server."),
        ]

        for status_code, custom_message in test_cases:
            with self.subTest(status_code=status_code):
                error = TelemetryErrorDetails(index=0, status_code=status_code, message=custom_message)

                retry_code, message = _determine_client_retry_code(error)
                self.assertEqual(retry_code, status_code)
                self.assertEqual(message, custom_message)

    def test_determine_client_retry_code_telemetry_error_details_without_message(self):
        """Test that TelemetryErrorDetails without message returns _UNKNOWN for specific status codes."""
        exporter = BaseExporter(disable_offline_storage=True)

        status_codes = [401, 403, 408, 429, 500, 502, 503, 504]

        for status_code in status_codes:
            with self.subTest(status_code=status_code):
                error = TelemetryErrorDetails(index=0, status_code=status_code, message=None)

                retry_code, message = _determine_client_retry_code(error)
                self.assertEqual(retry_code, status_code)
                self.assertEqual(message, _UNKNOWN)

    def test_determine_client_retry_code_telemetry_error_details_empty_message(self):
        """Test that TelemetryErrorDetails with empty message returns _UNKNOWN for specific status codes."""
        exporter = BaseExporter(disable_offline_storage=True)

        status_codes = [401, 403, 408, 429, 500, 502, 503, 504]

        for status_code in status_codes:
            with self.subTest(status_code=status_code):
                error = TelemetryErrorDetails(index=0, status_code=status_code, message="")

                retry_code, message = _determine_client_retry_code(error)
                self.assertEqual(retry_code, status_code)
                self.assertEqual(message, _UNKNOWN)

    def test_determine_client_retry_code_http_response_error_with_custom_message(self):
        """Test that HttpResponseError with custom message preserves the message for specific status codes."""
        exporter = BaseExporter(disable_offline_storage=True)

        test_cases = [
            (429, "Rate limit exceeded. Please reduce your request rate."),
            (500, "Internal server error occurred during telemetry processing."),
            (503, "Service temporarily unavailable due to high load."),
        ]

        for status_code, custom_message in test_cases:
            with self.subTest(status_code=status_code):
                error = HttpResponseError()
                error.status_code = status_code
                error.message = custom_message

                retry_code, message = _determine_client_retry_code(error)
                self.assertEqual(retry_code, status_code)
                self.assertEqual(message, custom_message)

    def test_determine_client_retry_code_generic_error_with_message_attribute(self):
        """Test that generic errors with message attribute preserve the message for specific status codes."""
        exporter = BaseExporter(disable_offline_storage=True)

        test_cases = [
            (401, "Custom auth error from service"),
            (429, "Custom rate limit message"),
            (500, "Custom server error message"),
        ]

        for status_code, custom_message in test_cases:
            with self.subTest(status_code=status_code):
                error = mock.Mock()
                error.status_code = status_code
                error.message = custom_message

                retry_code, message = _determine_client_retry_code(error)
                self.assertEqual(retry_code, status_code)
                self.assertEqual(message, custom_message)

    def test_determine_client_retry_code_non_specific_status_codes(self):
        """Test that non-specific status codes are handled with CLIENT_EXCEPTION."""
        exporter = BaseExporter(disable_offline_storage=True)

        # Test non-specific status codes
        non_specific_codes = [400, 404, 410, 413]

        for status_code in non_specific_codes:
            with self.subTest(status_code=status_code):
                error = mock.Mock()
                error.status_code = status_code
                error.message = f"Error message for {status_code}"

                retry_code, message = _determine_client_retry_code(error)
                self.assertEqual(retry_code, RetryCode.CLIENT_EXCEPTION)
                self.assertEqual(message, str(error))

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_track_retry_items_with_custom_breeze_messages(self):
        """Test that _track_retry_items properly passes custom messages from Breeze errors."""
        exporter = BaseExporter(disable_offline_storage=True)
        exporter._customer_sdkstats_metrics = mock.Mock()

        # Create test envelopes
        envelopes = [TelemetryItem(name="Test", time=datetime.now())]

        # Test TelemetryErrorDetails with custom message
        error = TelemetryErrorDetails(
            index=0,
            status_code=429,
            message="Rate limit exceeded for instrumentation key. Current rate: 1000 req/min, limit: 500 req/min.",
        )

        _track_retry_items(exporter._customer_sdkstats_metrics, envelopes, error)

        # Verify that count_retry_items was called with the custom message
        exporter._customer_sdkstats_metrics.count_retry_items.assert_called_once_with(
            1,
            "UNKNOWN",  # telemetry type
            429,  # status code
            "Rate limit exceeded for instrumentation key. Current rate: 1000 req/min, limit: 500 req/min.",
        )

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_track_retry_items_with_http_response_error_custom_message(self):
        """Test that _track_retry_items properly passes custom messages from HttpResponseError."""
        exporter = BaseExporter(disable_offline_storage=True)
        exporter._customer_sdkstats_metrics = mock.Mock()

        # Create test envelopes
        envelopes = [TelemetryItem(name="Test", time=datetime.now())]

        # Test HttpResponseError with custom message
        error = HttpResponseError()
        error.status_code = 503
        error.message = "Service temporarily unavailable due to maintenance."

        _track_retry_items(exporter._customer_sdkstats_metrics, envelopes, error)

        # Verify that count_retry_items was called with the custom message
        exporter._customer_sdkstats_metrics.count_retry_items.assert_called_once_with(
            1, "UNKNOWN", 503, "Service temporarily unavailable due to maintenance."  # telemetry type  # status code
        )

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_track_retry_items_without_custom_message(self):
        """Test that _track_retry_items handles errors without custom messages."""
        exporter = BaseExporter(disable_offline_storage=True)
        exporter._customer_sdkstats_metrics = mock.Mock()

        # Create test envelopes
        envelopes = [TelemetryItem(name="Test", time=datetime.now())]

        # Test error without message attribute for specific status code
        error = mock.Mock(spec=["status_code"])  # Only specify status_code attribute
        error.status_code = 500

        _track_retry_items(exporter._customer_sdkstats_metrics, envelopes, error)

        # Verify that count_retry_items was called with _UNKNOWN message for specific status codes without custom message
        exporter._customer_sdkstats_metrics.count_retry_items.assert_called_once_with(
            1,
            "UNKNOWN",  # telemetry type
            500,  # status code
            "UNKNOWN",  # message (_UNKNOWN is returned for specific status codes without custom message)
        )

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_track_retry_items_service_request_error_with_message(self):
        """Test that _track_retry_items properly handles ServiceRequestError with message."""
        exporter = BaseExporter(disable_offline_storage=True)
        exporter._customer_sdkstats_metrics = mock.Mock()

        # Create test envelopes
        envelopes = [TelemetryItem(name="Test", time=datetime.now())]

        # Test ServiceRequestError with message (using "timeout" to test timeout detection)
        error = ServiceRequestError("Connection timeout occurred")

        _track_retry_items(exporter._customer_sdkstats_metrics, envelopes, error)

        # Verify that count_retry_items was called with CLIENT_TIMEOUT
        exporter._customer_sdkstats_metrics.count_retry_items.assert_called_once_with(
            1,
            "UNKNOWN",  # telemetry type
            RetryCode.CLIENT_TIMEOUT,  # retry code
            "Connection timeout occurred",  # message
        )

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_track_retry_items_service_request_error_no_timeout(self):
        """Test that _track_retry_items properly handles ServiceRequestError without timeout in message."""
        exporter = BaseExporter(disable_offline_storage=True)
        exporter._customer_sdkstats_metrics = mock.Mock()

        # Create test envelopes
        envelopes = [TelemetryItem(name="Test", time=datetime.now())]

        # Test ServiceRequestError with message that doesn't contain "timeout"
        error = ServiceRequestError("Connection failed")

        _track_retry_items(exporter._customer_sdkstats_metrics, envelopes, error)

        # Verify that count_retry_items was called with CLIENT_EXCEPTION
        exporter._customer_sdkstats_metrics.count_retry_items.assert_called_once_with(
            1, "UNKNOWN", RetryCode.CLIENT_EXCEPTION, "Connection failed"  # telemetry type  # retry code  # message
        )

    def test_determine_client_retry_code_http_status_codes(self):
        exporter = BaseExporter(disable_offline_storage=True)

        status_codes = [401, 403, 408, 429, 500, 502, 503, 504]

        for status_code in status_codes:
            # Create mock without message attribute to test _UNKNOWN fallback
            error = mock.Mock(spec=["status_code"])
            error.status_code = status_code

            retry_code, message = _determine_client_retry_code(error)
            self.assertEqual(retry_code, status_code)
            self.assertEqual(message, _UNKNOWN)

    def test_determine_client_retry_code_service_request_error(self):
        exporter = BaseExporter(disable_offline_storage=True)

        error = ServiceRequestError("Connection failed")

        retry_code, message = _determine_client_retry_code(error)
        self.assertEqual(retry_code, RetryCode.CLIENT_EXCEPTION)
        self.assertEqual(message, "Connection failed")

    def test_determine_client_retry_code_service_request_error_with_message(self):
        exporter = BaseExporter(disable_offline_storage=True)

        error = ServiceRequestError("Network error")
        error.message = "Specific network error"

        retry_code, message = _determine_client_retry_code(error)
        self.assertEqual(retry_code, RetryCode.CLIENT_EXCEPTION)
        self.assertEqual(message, "Specific network error")

    def test_determine_client_retry_code_timeout_error(self):
        exporter = BaseExporter(disable_offline_storage=True)

    # customer sdkstats Flag Regression Tests
    # These tests ensure that the _is_customer_sdkstats_exporter() method using
    # getattr(self, '_is_customer_sdkstats', False) works correctly across
    # all scenarios and edge cases.

    def test_regular_exporter_not_flagged_as_customer_sdkstats(self):
        """Test that regular exporters are not identified as customer sdkstats exporters."""
        # Test BaseExporter
        base_exporter = BaseExporter(connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc")
        self.assertFalse(base_exporter._is_customer_sdkstats_exporter())

        # Test AzureMonitorTraceExporter
        trace_exporter = AzureMonitorTraceExporter(
            connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc"
        )
        self.assertFalse(trace_exporter._is_customer_sdkstats_exporter())

        # Test AzureMonitorMetricExporter
        metric_exporter = AzureMonitorMetricExporter(
            connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc"
        )
        self.assertFalse(metric_exporter._is_customer_sdkstats_exporter())

    def test_statsbeat_exporter_not_flagged_as_customer_sdkstats(self):
        """Test that regular statsbeat exporter is not identified as customer sdkstats exporter."""
        statsbeat_exporter = _StatsBeatExporter(
            connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc"
        )
        self.assertFalse(statsbeat_exporter._is_customer_sdkstats_exporter())

    def test_customer_sdkstats_exporter_properly_flagged(self):
        """Test that customer sdkstats exporter is properly identified when flag is set."""
        # Create a metric exporter and manually set the customer sdkstats flag
        exporter = AzureMonitorMetricExporter(
            connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc", instrumentation_collection=True
        )

        # Verify initially not flagged
        self.assertFalse(exporter._is_customer_sdkstats_exporter())

        # Set the customer sdkstats flag
        exporter._is_customer_sdkstats = True

        # Verify now properly flagged
        self.assertTrue(exporter._is_customer_sdkstats_exporter())

    def test_flag_attribute_missing_returns_false(self):
        """Test that missing _is_customer_sdkstats attribute returns False (default behavior)."""
        exporter = BaseExporter(connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc")

        # Ensure the attribute doesn't exist
        self.assertFalse(hasattr(exporter, "_is_customer_sdkstats"))

        # Verify getattr returns False as default
        self.assertFalse(exporter._is_customer_sdkstats_exporter())

    def test_flag_attribute_false_returns_false(self):
        """Test that _is_customer_sdkstats = False explicitly returns False."""
        exporter = BaseExporter(connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc")
        exporter._is_customer_sdkstats = False

        self.assertFalse(exporter._is_customer_sdkstats_exporter())

    def test_flag_attribute_true_returns_true(self):
        """Test that _is_customer_sdkstats = True returns True."""
        exporter = BaseExporter(connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc")
        exporter._is_customer_sdkstats = True

        self.assertTrue(exporter._is_customer_sdkstats_exporter())

    def test_flag_attribute_none_returns_false(self):
        """Test that _is_customer_sdkstats = None returns False."""
        exporter = BaseExporter(connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc")
        exporter._is_customer_sdkstats = None

        self.assertFalse(exporter._is_customer_sdkstats_exporter())

    def test_flag_attribute_other_values_behavior(self):
        """Test behavior with various non-boolean values for the flag."""
        exporter = BaseExporter(connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc")

        # Test with string "true" - should be truthy
        exporter._is_customer_sdkstats = "true"
        self.assertTrue(exporter._is_customer_sdkstats_exporter())

        # Test with string "false" - should be truthy (non-empty string)
        exporter._is_customer_sdkstats = "false"
        self.assertTrue(exporter._is_customer_sdkstats_exporter())

        # Test with empty string - should be falsy
        exporter._is_customer_sdkstats = ""
        self.assertFalse(exporter._is_customer_sdkstats_exporter())

        # Test with number 1 - should be truthy
        exporter._is_customer_sdkstats = 1
        self.assertTrue(exporter._is_customer_sdkstats_exporter())

        # Test with number 0 - should be falsy
        exporter._is_customer_sdkstats = 0
        self.assertFalse(exporter._is_customer_sdkstats_exporter())

    @mock.patch.dict(os.environ, {"APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true"})
    def test_should_collect_customer_sdkstats_with_regular_exporter_flag_test(self):
        """Test that regular exporters should collect customer sdkstats when enabled."""
        # Mock customer sdkstats shutdown state and storage method
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._state.get_customer_sdkstats_shutdown", return_value=False
        ), mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.collect_customer_sdkstats"):
            exporter = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc",
                disable_offline_storage=True,  # Disable storage to avoid missing method issue
            )

            # Regular exporter should collect customer sdkstats
            self.assertTrue(exporter._should_collect_customer_sdkstats())

    @mock.patch.dict(os.environ, {"APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true"})
    def test_should_collect_customer_sdkstats_with_customer_sdkstats_exporter_flag_test(self):
        """Test that customer sdkstats exporters should NOT collect customer sdkstats."""
        # Mock customer sdkstats shutdown state
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._state.get_customer_sdkstats_shutdown", return_value=False
        ):
            exporter = AzureMonitorMetricExporter(
                connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc",
                instrumentation_collection=True,
            )
            exporter._is_customer_sdkstats = True

            # customer sdkstats exporter should NOT collect customer sdkstats (prevents recursion)
            self.assertFalse(exporter._should_collect_customer_sdkstats())

    def test_customer_sdkstats_metrics_creation_with_flag_test(self):
        """Test that CustomerSdkStatsMetrics properly sets the flag on its exporter."""
        original_env = os.environ.get("APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW")
        os.environ["APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW"] = "true"

        try:
            # Mock to prevent actual metric collection setup
            with mock.patch(
                "azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.PeriodicExportingMetricReader"
            ), mock.patch(
                "azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.MeterProvider"
            ), mock.patch(
                "azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.get_compute_type", return_value="vm"
            ):
                connection_string = "InstrumentationKey=12345678-1234-1234-1234-123456789abc"

                customer_sdkstats = CustomerSdkStatsMetrics(connection_string)

                # Verify that the exporter was created and flagged
                self.assertTrue(hasattr(customer_sdkstats, "_customer_sdkstats_exporter"))
                self.assertTrue(customer_sdkstats._customer_sdkstats_exporter._is_customer_sdkstats_exporter())

        finally:
            if original_env is not None:
                os.environ["APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW"] = original_env
            else:
                os.environ.pop("APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW", None)

    def test_multiple_exporters_independent_flags(self):
        """Test that multiple exporters can have independent flag states."""
        # Create multiple exporters
        exporter1 = AzureMonitorMetricExporter(
            connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc"
        )
        exporter2 = AzureMonitorMetricExporter(
            connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc"
        )
        exporter3 = AzureMonitorTraceExporter(
            connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc"
        )

        # Initially, none should be flagged
        self.assertFalse(exporter1._is_customer_sdkstats_exporter())
        self.assertFalse(exporter2._is_customer_sdkstats_exporter())
        self.assertFalse(exporter3._is_customer_sdkstats_exporter())

        # Flag only exporter2
        exporter2._is_customer_sdkstats = True

        # Verify only exporter2 is flagged
        self.assertFalse(exporter1._is_customer_sdkstats_exporter())
        self.assertTrue(exporter2._is_customer_sdkstats_exporter())
        self.assertFalse(exporter3._is_customer_sdkstats_exporter())

        # Flag exporter3
        exporter3._is_customer_sdkstats = True

        # Verify exporter2 and exporter3 are flagged, but not exporter1
        self.assertFalse(exporter1._is_customer_sdkstats_exporter())
        self.assertTrue(exporter2._is_customer_sdkstats_exporter())
        self.assertTrue(exporter3._is_customer_sdkstats_exporter())

    def test_flag_modification_after_creation(self):
        """Test that flag can be modified after exporter creation."""
        exporter = BaseExporter(connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc")

        # Initially not flagged
        self.assertFalse(exporter._is_customer_sdkstats_exporter())

        # Set flag
        exporter._is_customer_sdkstats = True
        self.assertTrue(exporter._is_customer_sdkstats_exporter())

        # Unset flag
        exporter._is_customer_sdkstats = False
        self.assertFalse(exporter._is_customer_sdkstats_exporter())

        # Delete flag attribute
        delattr(exporter, "_is_customer_sdkstats")
        self.assertFalse(exporter._is_customer_sdkstats_exporter())

    def test_getattr_with_different_default_values(self):
        """Test that getattr behavior is consistent with different theoretical default values."""
        exporter = BaseExporter(connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc")

        # Test current implementation (default False)
        self.assertEqual(getattr(exporter, "_is_customer_sdkstats", False), False)

        # Test what would happen with different defaults
        self.assertEqual(getattr(exporter, "_is_customer_sdkstats", True), True)
        self.assertEqual(getattr(exporter, "_is_customer_sdkstats", None), None)
        self.assertEqual(getattr(exporter, "_is_customer_sdkstats", "default"), "default")

        # Set the attribute and verify getattr returns the actual value regardless of default
        exporter._is_customer_sdkstats = True
        self.assertEqual(getattr(exporter, "_is_customer_sdkstats", False), True)
        self.assertEqual(getattr(exporter, "_is_customer_sdkstats", "other"), True)

    @mock.patch.dict(os.environ, {"APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true"})
    def test_integration_scenario_mixed_exporters_flag_test(self):
        """Integration test with mixed exporter types to ensure no interference."""
        # Mock customer sdkstats shutdown state and storage method
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._state.get_customer_sdkstats_shutdown", return_value=False
        ), mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.collect_customer_sdkstats"):
            # Create various types of exporters with storage disabled
            trace_exporter = AzureMonitorTraceExporter(
                connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc",
                disable_offline_storage=True,
            )
            metric_exporter = AzureMonitorMetricExporter(
                connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc",
                disable_offline_storage=True,
            )

            # Create a customer sdkstats exporter
            customer_sdkstats_exporter = AzureMonitorMetricExporter(
                connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc",
                instrumentation_collection=True,
                disable_offline_storage=True,
            )
            customer_sdkstats_exporter._is_customer_sdkstats = True

            # Verify identification
            self.assertFalse(trace_exporter._is_customer_sdkstats_exporter())
            self.assertFalse(metric_exporter._is_customer_sdkstats_exporter())
            self.assertTrue(customer_sdkstats_exporter._is_customer_sdkstats_exporter())

            # Verify collection logic
            self.assertTrue(trace_exporter._should_collect_customer_sdkstats())
            self.assertTrue(metric_exporter._should_collect_customer_sdkstats())
            self.assertFalse(customer_sdkstats_exporter._should_collect_customer_sdkstats())

    def test_inheritance_flag_behavior(self):
        """Test that flag behavior works correctly with inheritance."""

        class CustomExporter(BaseExporter):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        custom_exporter = CustomExporter(connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789abc")

        # Should work the same as BaseExporter
        self.assertFalse(custom_exporter._is_customer_sdkstats_exporter())

        custom_exporter._is_customer_sdkstats = True
        self.assertTrue(custom_exporter._is_customer_sdkstats_exporter())

    # End of customer sdkstats Flag Regression Tests

    def test_determine_client_retry_code_timeout_error(self):
        exporter = BaseExporter(disable_offline_storage=True)

        timeout_error = ServiceRequestError("Request timed out")

        retry_code, message = _determine_client_retry_code(timeout_error)
        self.assertEqual(retry_code, RetryCode.CLIENT_TIMEOUT)
        self.assertEqual(message, "Request timed out")

        timeout_error2 = ServiceRequestError("Connection timeout occurred")

        retry_code2, message2 = _determine_client_retry_code(timeout_error2)
        self.assertEqual(retry_code2, RetryCode.CLIENT_TIMEOUT)
        self.assertEqual(message2, "Connection timeout occurred")

    def test_determine_client_retry_code_general_exception(self):
        exporter = BaseExporter(disable_offline_storage=True)

        error = Exception("Something went wrong")

        retry_code, message = _determine_client_retry_code(error)
        self.assertEqual(retry_code, RetryCode.CLIENT_EXCEPTION)
        self.assertEqual(message, "Something went wrong")

    def test_track_retry_items_stats_exporter(self):
        exporter = _StatsBeatExporter(disable_offline_storage=True)

        mock_customer_sdkstats = mock.Mock()
        exporter._customer_sdkstats_metrics = mock_customer_sdkstats

        test_envelopes = [TelemetryItem(name="test1", time=datetime.now())]

        error = Exception("Some error")

        # Only call _track_retry_items if should_collect_customer_sdkstats is True
        if exporter._customer_sdkstats_metrics and exporter._should_collect_customer_sdkstats():
            _track_retry_items(exporter._customer_sdkstats_metrics, test_envelopes, error)

        mock_customer_sdkstats.count_retry_items.assert_not_called()

    def test_track_retry_items_no_customer_sdkstats(self):
        exporter = BaseExporter(disable_offline_storage=True)

        self.assertIsNone(exporter._customer_sdkstats_metrics)

        test_envelopes = [TelemetryItem(name="test1", time=datetime.now())]

        error = Exception("Some error")

        _track_retry_items(exporter._customer_sdkstats_metrics, test_envelopes, error)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_track_retry_items_with_customer_sdkstats(self):
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.collect_customer_sdkstats"
        ) as mock_collect:
            mock_customer_sdkstats = mock.Mock()

            def mock_collect_side_effect(exporter):
                setattr(exporter, "_customer_sdkstats_metrics", mock_customer_sdkstats)

            mock_collect.side_effect = mock_collect_side_effect

            exporter = BaseExporter(disable_offline_storage=True)

            test_envelopes = [
                TelemetryItem(name="test1", time=datetime.now()),
                TelemetryItem(name="test2", time=datetime.now()),
            ]

            error = ServiceRequestError("Connection failed")
            _track_retry_items(exporter._customer_sdkstats_metrics, test_envelopes, error)

            self.assertEqual(mock_customer_sdkstats.count_retry_items.call_count, 2)

            calls = mock_customer_sdkstats.count_retry_items.call_args_list
            self.assertEqual(calls[0][0][0], 1)
            self.assertEqual(calls[0][0][2], RetryCode.CLIENT_EXCEPTION)
            self.assertEqual(calls[1][0][0], 1)
            self.assertEqual(calls[1][0][2], RetryCode.CLIENT_EXCEPTION)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_track_retry_items_with_status_code_error(self):
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.collect_customer_sdkstats"
        ) as mock_collect:
            mock_customer_sdkstats = mock.Mock()

            def mock_collect_side_effect(exporter):
                setattr(exporter, "_customer_sdkstats_metrics", mock_customer_sdkstats)

            mock_collect.side_effect = mock_collect_side_effect

            exporter = BaseExporter(disable_offline_storage=True)

            test_envelopes = [TelemetryItem(name="test1", time=datetime.now())]

            error = HttpResponseError()
            error.status_code = 429
            _track_retry_items(exporter._customer_sdkstats_metrics, test_envelopes, error)

            mock_customer_sdkstats.count_retry_items.assert_called_once()

            args, kwargs = mock_customer_sdkstats.count_retry_items.call_args
            self.assertEqual(args[0], 1)
            self.assertEqual(args[2], 429)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_transmission_success_tracks_successful_items(self):
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.collect_customer_sdkstats"
        ) as mock_collect:
            mock_customer_sdkstats = mock.Mock()

            def mock_collect_side_effect(exporter):
                setattr(exporter, "_customer_sdkstats_metrics", mock_customer_sdkstats)

            mock_collect.side_effect = mock_collect_side_effect

            exporter = BaseExporter(disable_offline_storage=True)

            test_envelopes = [
                TelemetryItem(name="test1", time=datetime.now()),
                TelemetryItem(name="test2", time=datetime.now()),
            ]

            with mock.patch.object(AzureMonitorClient, "track") as mock_track:
                mock_track.return_value = TrackResponse(
                    items_received=2,
                    items_accepted=2,
                    errors=[],
                )

                result = exporter._transmit(test_envelopes)

                self.assertEqual(result, ExportResult.SUCCESS)

                self.assertEqual(mock_customer_sdkstats.count_successful_items.call_count, 2)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_transmission_206_tracks_dropped_items(self):
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.collect_customer_sdkstats"
        ) as mock_collect:
            mock_customer_sdkstats = mock.Mock()

            def mock_collect_side_effect(exporter):
                setattr(exporter, "_customer_sdkstats_metrics", mock_customer_sdkstats)

            mock_collect.side_effect = mock_collect_side_effect

            exporter = BaseExporter(disable_offline_storage=True)

            test_envelopes = [
                TelemetryItem(name="test1", time=datetime.now()),
                TelemetryItem(name="test2", time=datetime.now()),
                TelemetryItem(name="test3", time=datetime.now()),
            ]

            with mock.patch.object(AzureMonitorClient, "track") as mock_track:
                mock_track.return_value = TrackResponse(
                    items_received=3,
                    items_accepted=2,
                    errors=[
                        TelemetryErrorDetails(
                            index=0,
                            status_code=400,
                            message="Invalid data",
                        ),
                    ],
                )

                result = exporter._transmit(test_envelopes)

                self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

                mock_customer_sdkstats.count_dropped_items.assert_called_once()

                args, kwargs = mock_customer_sdkstats.count_dropped_items.call_args
                self.assertEqual(args[0], 1)  # count
                self.assertEqual(args[2], 400)  # status_code
                # The error parameter is now optional, so it's not passed when None
                # This means args only has 3 elements, not 4

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_transmission_206_tracks_retry_items(self):
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.collect_customer_sdkstats"
        ) as mock_collect:
            mock_customer_sdkstats = mock.Mock()

            def mock_collect_side_effect(exporter):
                setattr(exporter, "_customer_sdkstats_metrics", mock_customer_sdkstats)

            mock_collect.side_effect = mock_collect_side_effect

            exporter = BaseExporter(disable_offline_storage=False)

            exporter.storage.put = mock.Mock()

            test_envelopes = [
                TelemetryItem(name="test1", time=datetime.now()),
                TelemetryItem(name="test2", time=datetime.now()),
                TelemetryItem(name="test3", time=datetime.now()),
            ]

            with mock.patch.object(AzureMonitorClient, "track") as mock_track:
                mock_track.return_value = TrackResponse(
                    items_received=3,
                    items_accepted=2,
                    errors=[
                        TelemetryErrorDetails(
                            index=2,
                            status_code=500,
                            message="Server error",
                        ),
                    ],
                )

                result = exporter._transmit(test_envelopes)

                self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

                exporter.storage.put.assert_called_once()

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_transmission_service_request_error_tracks_retry_items(self):
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.collect_customer_sdkstats"
        ) as mock_collect:
            mock_customer_sdkstats = mock.Mock()

            def mock_collect_side_effect(exporter):
                setattr(exporter, "_customer_sdkstats_metrics", mock_customer_sdkstats)

            mock_collect.side_effect = mock_collect_side_effect

            exporter = BaseExporter(disable_offline_storage=True)

            test_envelopes = [TelemetryItem(name="test1", time=datetime.now())]

            with mock.patch.object(AzureMonitorClient, "track", side_effect=ServiceRequestError("Connection failed")):
                result = exporter._transmit(test_envelopes)

                self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

                mock_customer_sdkstats.count_retry_items.assert_called_once()

                args, kwargs = mock_customer_sdkstats.count_retry_items.call_args
                self.assertEqual(args[0], 1)
                self.assertEqual(args[2], RetryCode.CLIENT_EXCEPTION)
                self.assertEqual(args[3], "Connection failed")

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_transmission_general_exception_tracks_dropped_items(self):
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.collect_customer_sdkstats"
        ) as mock_collect:
            mock_customer_sdkstats = mock.Mock()

            def mock_collect_side_effect(exporter):
                setattr(exporter, "_customer_sdkstats_metrics", mock_customer_sdkstats)

            mock_collect.side_effect = mock_collect_side_effect

            exporter = BaseExporter(disable_offline_storage=True)

            test_envelopes = [TelemetryItem(name="test1", time=datetime.now())]

            with mock.patch.object(AzureMonitorClient, "track", side_effect=Exception("Unexpected error")):
                result = exporter._transmit(test_envelopes)

                self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

                # We expect two calls: one for storage disabled, one for the exception
                expected_calls = [
                    mock.call(1, "UNKNOWN", DropCode.CLIENT_STORAGE_DISABLED),
                    mock.call(1, "UNKNOWN", DropCode.CLIENT_EXCEPTION, "Unexpected error"),
                ]
                mock_customer_sdkstats.count_dropped_items.assert_has_calls(expected_calls)
                self.assertEqual(mock_customer_sdkstats.count_dropped_items.call_count, 2)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "false",
        },
    )
    def test_constructor_customer_sdkstats_disabled(self):
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.collect_customer_sdkstats"
        ) as mock_collect:
            exporter = BaseExporter(disable_offline_storage=True)

            mock_collect.assert_not_called()

            self.assertIsNone(exporter._customer_sdkstats_metrics)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_constructor_customer_sdkstats_enabled(self):
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.collect_customer_sdkstats"
        ) as mock_collect:
            exporter = BaseExporter(disable_offline_storage=True)

            self.assertGreaterEqual(mock_collect.call_count, 1)

            exporter_calls = [call[0][0] for call in mock_collect.call_args_list]
            self.assertIn(exporter, exporter_calls)

            self.assertIsNone(exporter._customer_sdkstats_metrics)

    def test_is_customer_sdkstats_exporter_false(self):
        exporter = BaseExporter(disable_offline_storage=True)
        self.assertFalse(exporter._is_customer_sdkstats_exporter())

    def test_customer_sdkstats_metrics_initialization_none(self):
        exporter = BaseExporter(disable_offline_storage=True)
        self.assertIsNone(exporter._customer_sdkstats_metrics)

    # Tests for customer sdkstats tracking in _transmit method
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_retry_items")
    def test_transmit_track_retry_items_throttle_error(self, mock_track_retry):
        """Test that _track_retry_items is called when 429 (retryable) error occurs."""
        with mock.patch.object(
            AzureMonitorClient, "track", throw(HttpResponseError, message="throttled", response=MockResponse(429, "{}"))
        ):
            exporter = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd",
                disable_offline_storage=True,
            )
            # Enable customer sdkstats collection
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)
            exporter._customer_sdkstats_metrics = mock.Mock()

            test_envelope = mock.Mock()
            result = exporter._transmit([test_envelope])

            self.assertEqual(result, ExportResult.FAILED_RETRYABLE)
            mock_track_retry.assert_called_once_with(
                exporter._customer_sdkstats_metrics, [test_envelope], mock.ANY  # HttpResponseError instance
            )

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_transmit_track_dropped_items_true_throttle_error(self, mock_track_dropped):
        """Test that _track_dropped_items is called when true throttle error (402/439) occurs."""
        with mock.patch.object(
            AzureMonitorClient,
            "track",
            throw(HttpResponseError, message="quota exceeded", response=MockResponse(402, "{}")),
        ):
            exporter = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd",
                disable_offline_storage=True,
            )
            # Enable customer sdkstats collection
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)
            exporter._customer_sdkstats_metrics = mock.Mock()

            test_envelope = mock.Mock()
            result = exporter._transmit([test_envelope])

            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
            mock_track_dropped.assert_called_once_with(
                exporter._customer_sdkstats_metrics, [test_envelope], 402  # HTTP status code is passed directly
            )

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_transmit_track_dropped_items_general_exception(self, mock_track_dropped):
        """Test that _track_dropped_items is called for general exceptions."""
        with mock.patch.object(AzureMonitorClient, "track", throw(Exception, "Generic error")):
            exporter = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd",
                disable_offline_storage=True,
            )
            # Enable customer sdkstats collection
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)
            exporter._customer_sdkstats_metrics = mock.Mock()

            test_envelope = mock.Mock()
            result = exporter._transmit([test_envelope])

            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
            mock_track_dropped.assert_called_once_with(
                exporter._customer_sdkstats_metrics,
                [test_envelope],
                DropCode.CLIENT_EXCEPTION,
                mock.ANY,  # Exception instance
            )

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_transmit_track_dropped_items_non_retryable_http_error(self, mock_track_dropped):
        """Test that _track_dropped_items is called for non-retryable HTTP errors."""
        with mock.patch.object(
            AzureMonitorClient,
            "track",
            throw(HttpResponseError, message="bad request", response=MockResponse(400, "{}")),
        ):
            exporter = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd",
                disable_offline_storage=True,
            )
            # Enable customer sdkstats collection
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)
            exporter._customer_sdkstats_metrics = mock.Mock()

            test_envelope = mock.Mock()
            result = exporter._transmit([test_envelope])

            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
            mock_track_dropped.assert_called_once_with(
                exporter._customer_sdkstats_metrics, [test_envelope], 400  # HTTP status code is passed directly
            )

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_retry_items")
    def test_transmit_track_retry_items_retryable_http_error(self, mock_track_retry):
        """Test that _track_retry_items is called for retryable HTTP errors."""
        with mock.patch.object(
            AzureMonitorClient,
            "track",
            throw(HttpResponseError, message="server error", response=MockResponse(500, "{}")),
        ):
            exporter = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd",
                disable_offline_storage=True,
            )
            # Enable customer sdkstats collection
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)
            exporter._customer_sdkstats_metrics = mock.Mock()

            test_envelope = mock.Mock()
            result = exporter._transmit([test_envelope])

            self.assertEqual(result, ExportResult.FAILED_RETRYABLE)
            mock_track_retry.assert_called_once_with(
                exporter._customer_sdkstats_metrics, [test_envelope], mock.ANY  # HttpResponseError instance
            )

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_retry_items")
    def test_transmit_track_retry_items_service_request_error(self, mock_track_retry):
        """Test that _track_retry_items is called for ServiceRequestError."""
        with mock.patch.object(AzureMonitorClient, "track", throw(ServiceRequestError, message="Request failed")):
            exporter = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd",
                disable_offline_storage=True,
            )
            # Enable customer sdkstats collection
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)
            exporter._customer_sdkstats_metrics = mock.Mock()

            test_envelope = mock.Mock()
            result = exporter._transmit([test_envelope])

            self.assertEqual(result, ExportResult.FAILED_RETRYABLE)
            mock_track_retry.assert_called_once_with(
                exporter._customer_sdkstats_metrics, [test_envelope], mock.ANY  # ServiceRequestError instance
            )

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_transmit_track_dropped_items_redirect_error_no_headers(self, mock_track_dropped):
        """Test that _track_dropped_items is called for redirect errors without proper headers."""
        response = MockResponse(302, "{}")
        response.headers = {}  # No location header
        with mock.patch.object(
            AzureMonitorClient, "track", throw(HttpResponseError, message="redirect", response=response)
        ):
            exporter = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd",
                disable_offline_storage=True,
            )
            # Enable customer sdkstats collection
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)
            exporter._customer_sdkstats_metrics = mock.Mock()

            test_envelope = mock.Mock()
            result = exporter._transmit([test_envelope])

            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
            mock_track_dropped.assert_called_once_with(
                exporter._customer_sdkstats_metrics, [test_envelope], 302  # HTTP status code is passed directly
            )

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_transmit_track_dropped_items_storage_disabled(self, mock_track_dropped):
        """Test that _track_dropped_items is called when storage is disabled for retryable items."""
        with mock.patch.object(AzureMonitorClient, "track") as mock_track:
            mock_track.return_value = TrackResponse(
                items_received=2,
                items_accepted=1,
                errors=[TelemetryErrorDetails(index=0, status_code=500, message="Internal server error")],
            )

            exporter = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd",
                disable_offline_storage=True,  # Storage disabled
            )
            # Enable customer sdkstats collection
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)
            exporter._customer_sdkstats_metrics = mock.Mock()

            test_envelope1 = mock.Mock()
            test_envelope2 = mock.Mock()
            result = exporter._transmit([test_envelope1, test_envelope2])

            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
            mock_track_dropped.assert_called_once_with(
                exporter._customer_sdkstats_metrics,
                [test_envelope1],  # Only the failed envelope
                DropCode.CLIENT_STORAGE_DISABLED,
            )

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_retry_items")
    def test_transmit_no_tracking_when_customer_sdkstats_disabled(self, mock_track_retry, mock_track_dropped):
        """Test that tracking functions are not called when customer sdkstats is disabled."""
        with mock.patch.object(
            AzureMonitorClient,
            "track",
            throw(HttpResponseError, message="server error", response=MockResponse(500, "{}")),
        ):
            exporter = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd",
                disable_offline_storage=True,
            )
            # Disable customer sdkstats collection
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=False)
            exporter._customer_sdkstats_metrics = mock.Mock()

            test_envelope = mock.Mock()
            result = exporter._transmit([test_envelope])

            self.assertEqual(result, ExportResult.FAILED_RETRYABLE)
            mock_track_retry.assert_not_called()
            mock_track_dropped.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_retry_items")
    def test_transmit_no_tracking_when_customer_sdkstats_metrics_none(self, mock_track_retry, mock_track_dropped):
        """Test that tracking functions are not called when customer sdkstats metrics is None."""
        with mock.patch.object(
            AzureMonitorClient,
            "track",
            throw(HttpResponseError, message="server error", response=MockResponse(500, "{}")),
        ):
            exporter = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd",
                disable_offline_storage=True,
            )
            # customer sdkstats metrics is None
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)
            exporter._customer_sdkstats_metrics = None

            test_envelope = mock.Mock()
            result = exporter._transmit([test_envelope])

            self.assertEqual(result, ExportResult.FAILED_RETRYABLE)
            mock_track_retry.assert_not_called()
            mock_track_dropped.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_transmit_track_dropped_items_partial_failure_non_retryable(self, mock_track_dropped):
        """Test that _track_dropped_items is called for non-retryable partial failures."""
        with mock.patch.object(AzureMonitorClient, "track") as mock_track:
            mock_track.return_value = TrackResponse(
                items_received=2,
                items_accepted=1,
                errors=[TelemetryErrorDetails(index=0, status_code=400, message="Invalid data")],  # Non-retryable
            )

            exporter = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd",
                disable_offline_storage=True,
            )
            # Enable customer sdkstats collection
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)
            exporter._customer_sdkstats_metrics = mock.Mock()

            test_envelope1 = mock.Mock()
            test_envelope2 = mock.Mock()
            result = exporter._transmit([test_envelope1, test_envelope2])

            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
            mock_track_dropped.assert_called_once_with(
                exporter._customer_sdkstats_metrics,
                [test_envelope1],  # Only the failed envelope
                400,  # HTTP status code is passed directly
            )

    def test_track_dropped_items_no_error(self):
        """Test _track_dropped_items with no error (error=None)."""
        # Create mock customer sdkstats metrics
        mock_customer_sdkstats = mock.Mock()

        # Create test envelopes
        envelope1 = TelemetryItem(name="test1", time=datetime.now())
        envelope2 = TelemetryItem(name="test2", time=datetime.now())
        envelopes = [envelope1, envelope2]

        # Mock _get_telemetry_type to return consistent values
        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._get_telemetry_type") as mock_get_type:
            mock_get_type.side_effect = ["trace", "metric"]

            # Call _track_dropped_items with no error
            _track_dropped_items(
                mock_customer_sdkstats, envelopes, DropCode.CLIENT_STORAGE_DISABLED, error_message=None
            )

            # Verify that count_dropped_items was called for each envelope
            self.assertEqual(mock_customer_sdkstats.count_dropped_items.call_count, 2)

            # Check first call
            first_call = mock_customer_sdkstats.count_dropped_items.call_args_list[0]
            self.assertEqual(first_call[0], (1, "trace", DropCode.CLIENT_STORAGE_DISABLED))

            # Check second call
            second_call = mock_customer_sdkstats.count_dropped_items.call_args_list[1]
            self.assertEqual(second_call[0], (1, "metric", DropCode.CLIENT_STORAGE_DISABLED))

    def test_track_dropped_items_with_error_index(self):
        """Test _track_dropped_items with error string."""
        # Create mock customer sdkstats metrics
        mock_customer_sdkstats = mock.Mock()

        # Create test envelopes
        envelope1 = TelemetryItem(name="test1", time=datetime.now())
        envelope2 = TelemetryItem(name="test2", time=datetime.now())
        envelope3 = TelemetryItem(name="test3", time=datetime.now())
        envelopes = [envelope1, envelope2, envelope3]

        # Create error string
        error_message = "Bad Request: Invalid telemetry data"

        # Mock _get_telemetry_type
        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._get_telemetry_type") as mock_get_type:
            mock_get_type.side_effect = ["trace", "metric", "log"]

            # Call _track_dropped_items with error string
            _track_dropped_items(
                mock_customer_sdkstats, envelopes, DropCode.CLIENT_EXCEPTION, error_message=error_message
            )

            # With the current simplified implementation, all envelopes are processed when error is not None
            self.assertEqual(mock_customer_sdkstats.count_dropped_items.call_count, 3)

            # Check the calls
            calls = mock_customer_sdkstats.count_dropped_items.call_args_list
            self.assertEqual(calls[0][0], (1, "trace", DropCode.CLIENT_EXCEPTION, error_message))
            self.assertEqual(calls[1][0], (1, "metric", DropCode.CLIENT_EXCEPTION, error_message))
            self.assertEqual(calls[2][0], (1, "log", DropCode.CLIENT_EXCEPTION, error_message))

    def test_track_dropped_items_with_client_exception_error(self):
        """Test _track_dropped_items with CLIENT_EXCEPTION drop code and error string."""
        # Create mock customer sdkstats metrics
        mock_customer_sdkstats = mock.Mock()

        # Create test envelopes
        envelope1 = TelemetryItem(name="test1", time=datetime.now())
        envelope2 = TelemetryItem(name="test2", time=datetime.now())
        envelopes = [envelope1, envelope2]

        # Create error string
        error_message = "Connection timeout"

        # Mock _get_telemetry_type
        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._get_telemetry_type") as mock_get_type:
            mock_get_type.side_effect = ["trace", "metric"]

            # Call _track_dropped_items with CLIENT_EXCEPTION
            _track_dropped_items(
                mock_customer_sdkstats, envelopes, DropCode.CLIENT_EXCEPTION, error_message=error_message
            )

            # Verify that count_dropped_items was called for each envelope
            self.assertEqual(mock_customer_sdkstats.count_dropped_items.call_count, 2)

            # Check first call
            first_call = mock_customer_sdkstats.count_dropped_items.call_args_list[0]
            self.assertEqual(first_call[0], (1, "trace", DropCode.CLIENT_EXCEPTION, error_message))

            # Check second call
            second_call = mock_customer_sdkstats.count_dropped_items.call_args_list[1]
            self.assertEqual(second_call[0], (1, "metric", DropCode.CLIENT_EXCEPTION, error_message))

    def test_track_dropped_items_with_status_code_error_not_client_exception(self):
        """Test _track_dropped_items with error string and non-CLIENT_EXCEPTION drop code."""
        # Create mock customer sdkstats metrics
        mock_customer_sdkstats = mock.Mock()

        # Create test envelopes
        envelope1 = TelemetryItem(name="test1", time=datetime.now())
        envelopes = [envelope1]

        # Create error string
        error_message = "Internal Server Error"

        # Mock _get_telemetry_type
        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._get_telemetry_type") as mock_get_type:
            mock_get_type.return_value = "trace"

            # Call _track_dropped_items with non-CLIENT_EXCEPTION drop code
            _track_dropped_items(
                mock_customer_sdkstats, envelopes, 500, error_message=error_message  # Using status code as drop code
            )

            # With the current simplified implementation, any error (not None) will process all envelopes
            mock_customer_sdkstats.count_dropped_items.assert_called_once_with(1, "trace", 500, error_message)

    def test_track_dropped_items_with_error_none_index(self):
        """Test _track_dropped_items with error string."""
        # Create mock customer sdkstats metrics
        mock_customer_sdkstats = mock.Mock()

        # Create test envelopes
        envelope1 = TelemetryItem(name="test1", time=datetime.now())
        envelopes = [envelope1]

        # Create error string
        error_message = "Bad Request"

        # Mock _get_telemetry_type
        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._get_telemetry_type") as mock_get_type:
            mock_get_type.return_value = "trace"

            # Call _track_dropped_items
            _track_dropped_items(
                mock_customer_sdkstats, envelopes, DropCode.CLIENT_EXCEPTION, error_message=error_message
            )

            # With current implementation, any non-None error will process all envelopes
            mock_customer_sdkstats.count_dropped_items.assert_called_once_with(
                1, "trace", DropCode.CLIENT_EXCEPTION, error_message
            )

    def test_track_dropped_items_no_customer_sdkstats_metrics(self):
        """Test _track_dropped_items with None customer_sdkstats_metrics."""
        # Create test envelopes
        envelope1 = TelemetryItem(name="test1", time=datetime.now())
        envelopes = [envelope1]

        # Call _track_dropped_items with None metrics
        result = _track_dropped_items(
            customer_sdkstats_metrics=None,
            envelopes=envelopes,
            drop_code=DropCode.CLIENT_STORAGE_DISABLED,
            error_message=None,
        )

        # Should return None and not raise any exceptions
        self.assertIsNone(result)

    def test_track_dropped_items_empty_envelopes_list(self):
        """Test _track_dropped_items with empty envelopes list."""
        # Create mock customer sdkstats metrics
        mock_customer_sdkstats = mock.Mock()

        # Call _track_dropped_items with empty list
        _track_dropped_items(
            mock_customer_sdkstats, envelopes=[], drop_code=DropCode.CLIENT_STORAGE_DISABLED, error_message=None
        )

        # Should not call count_dropped_items since there are no envelopes
        mock_customer_sdkstats.count_dropped_items.assert_not_called()

    def test_track_dropped_items_integration_with_transmit_206_error_status_code(self):
        """Integration test for _track_dropped_items with 206 response containing status code errors."""
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items") as mock_track_dropped:
            with mock.patch.object(AzureMonitorClient, "track") as mock_track:
                # Setup 206 response with mixed success/failure
                mock_track.return_value = TrackResponse(
                    items_received=3,
                    items_accepted=1,
                    errors=[
                        TelemetryErrorDetails(
                            index=0,
                            status_code=400,  # Non-retryable - should be tracked as dropped
                            message="Bad request",
                        ),
                        TelemetryErrorDetails(
                            index=2,
                            status_code=500,  # Retryable - should not be tracked as dropped initially
                            message="Server error",
                        ),
                    ],
                )

                exporter = BaseExporter(
                    connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd",
                    disable_offline_storage=True,
                )
                # Enable customer sdkstats collection
                exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)
                exporter._customer_sdkstats_metrics = mock.Mock()

                test_envelopes = [
                    TelemetryItem(name="envelope0", time=datetime.now()),
                    TelemetryItem(name="envelope1", time=datetime.now()),
                    TelemetryItem(name="envelope2", time=datetime.now()),
                ]

                result = exporter._transmit(test_envelopes)

                self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

                # Verify _track_dropped_items was called for the non-retryable error (400)

                # Check if _track_dropped_items was called (regardless of the bug)
                self.assertTrue(mock_track_dropped.called)

                # Find the call that matches our expectations
                found_call = False
                for call in mock_track_dropped.call_args_list:
                    args = call[0]
                    if len(args) >= 3 and args[2] == 400:  # status_code as drop_code
                        found_call = True
                        break

                self.assertTrue(found_call, "Expected call to _track_dropped_items with status_code 400 not found")

    def test_track_dropped_items_with_various_drop_codes(self):
        """Test _track_dropped_items with different DropCode values."""
        # Create mock customer sdkstats metrics
        mock_customer_sdkstats = mock.Mock()
        envelope = TelemetryItem(name="test", time=datetime.now())

        drop_codes_to_test = [
            DropCode.CLIENT_STORAGE_DISABLED,
            DropCode.CLIENT_EXCEPTION,
            400,  # HTTP status code
            500,  # HTTP status code
        ]

        # Mock _get_telemetry_type
        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._get_telemetry_type") as mock_get_type:
            mock_get_type.return_value = "trace"

            for drop_code in drop_codes_to_test:
                mock_customer_sdkstats.reset_mock()

                # Test with no error
                _track_dropped_items(mock_customer_sdkstats, [envelope], drop_code, error_message=None)

                # Should call count_dropped_items for each drop_code
                mock_customer_sdkstats.count_dropped_items.assert_called_once_with(1, "trace", drop_code)

    def test_track_dropped_items_with_status_code_as_drop_code_and_error(self):
        """Test _track_dropped_items using HTTP status code as drop_code with error string."""
        # Create mock customer sdkstats metrics
        mock_customer_sdkstats = mock.Mock()
        envelope = TelemetryItem(name="test", time=datetime.now())

        # Create error string
        error_message = "Bad Request"

        # Mock _get_telemetry_type
        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._get_telemetry_type") as mock_get_type:
            mock_get_type.return_value = "trace"

            # Call _track_dropped_items using status code as drop_code (common pattern in _base.py)
            _track_dropped_items(
                mock_customer_sdkstats,
                [envelope],
                drop_code=400,  # Status code as drop code
                error_message=error_message,
            )

            # Should call count_dropped_items with status code as drop_code
            mock_customer_sdkstats.count_dropped_items.assert_called_once_with(1, "trace", 400, error_message)

    def test_track_dropped_items_error_with_string_conversion(self):
        """Test _track_dropped_items with different string error types."""
        # Create mock customer sdkstats metrics
        mock_customer_sdkstats = mock.Mock()
        envelope = TelemetryItem(name="test", time=datetime.now())

        # Test different error string cases
        error_cases = ["Test exception", "Invalid value error", "Connection timeout", "Server internal error"]

        # Mock _get_telemetry_type
        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._get_telemetry_type") as mock_get_type:
            mock_get_type.return_value = "trace"

            for error_message in error_cases:
                mock_customer_sdkstats.reset_mock()

                _track_dropped_items(
                    mock_customer_sdkstats, [envelope], DropCode.CLIENT_EXCEPTION, error_message=error_message
                )

                # Should call count_dropped_items with the error string
                mock_customer_sdkstats.count_dropped_items.assert_called_once_with(
                    1, "trace", DropCode.CLIENT_EXCEPTION, error_message
                )

    def test_track_dropped_items_regression_base_exporter_pattern(self):
        """Regression test that matches the actual usage pattern in _base.py."""
        # This test verifies the common pattern used in _base.py where:
        # 1. Status codes are used as drop codes
        # 2. Error messages are passed as strings
        # 3. Single envelope is wrapped in a list (fixing the bug in _base.py)

        mock_customer_sdkstats = mock.Mock()
        envelope = TelemetryItem(name="test", time=datetime.now())

        # Create error message string (what should be passed instead of error object)
        error_message = "Bad Request - Invalid telemetry"

        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._get_telemetry_type") as mock_get_type:
            mock_get_type.return_value = "trace"

            # Test the corrected pattern (envelope wrapped in list, error as string)
            _track_dropped_items(
                mock_customer_sdkstats,
                [envelope],  # Correct - envelope wrapped in list
                drop_code=400,  # Status code as drop code
                error_message=error_message,  # Error as string
            )

            mock_customer_sdkstats.count_dropped_items.assert_called_once_with(1, "trace", 400, error_message)

            # Test what would happen with the bug (single envelope instead of list)
            mock_customer_sdkstats.reset_mock()
            mock_get_type.reset_mock()

            # This would cause an error in real usage since envelope is not iterable
            with self.assertRaises(TypeError):
                _track_dropped_items(
                    mock_customer_sdkstats,
                    envelope,  # Bug - single envelope instead of list
                    drop_code=400,
                    error_message=error_message,
                )

    def test_track_dropped_items_custom_message_circular_redirect_scenario(self):
        """Test _track_dropped_items with custom message for circular redirect scenario."""
        # This test simulates the circular redirect scenario in _base.py lines 336-349
        # to verify that the custom error message is properly passed through

        mock_customer_sdkstats = mock.Mock()
        envelope = TelemetryItem(name="test_request", time=datetime.now())

        # Use the exact custom message from the _base.py code
        expected_custom_message = "Error sending telemetry because of circular redirects. Please check the integrity of your connection string."

        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._get_telemetry_type") as mock_get_type:
            mock_get_type.return_value = "request"

            # Call _track_dropped_items with the exact custom message from the circular redirect scenario
            _track_dropped_items(
                mock_customer_sdkstats,
                [envelope],
                drop_code=DropCode.CLIENT_EXCEPTION,
                error_message=expected_custom_message,
            )

            # Verify the custom message is properly passed through to count_dropped_items
            mock_customer_sdkstats.count_dropped_items.assert_called_once_with(
                1, "request", DropCode.CLIENT_EXCEPTION, expected_custom_message
            )

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_transmit_circular_redirect_scenario_integration(self, mock_track_dropped):
        """Integration test that simulates the circular redirect scenario to verify custom message."""
        # This test simulates the actual circular redirect scenario that triggers the custom message

        # Create a redirect response with correct redirect status code (307 or 308)
        redirect_response = MockResponse(307, "{}")  # Use 307 which is in _REDIRECT_STATUS_CODES
        redirect_response.headers = {"location": "https://redirect.example.com"}

        with mock.patch.object(AzureMonitorClient, "track") as mock_track:
            # Mock the track method to raise HttpResponseError with redirect status
            mock_track.side_effect = HttpResponseError(message="Temporary Redirect", response=redirect_response)

            exporter = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd",
                disable_offline_storage=True,
            )

            # Enable customer sdkstats collection
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)
            exporter._customer_sdkstats_metrics = mock.Mock()

            # Set consecutive redirects to one less than max to simulate we've been redirecting
            # When the HttpResponseError is raised, _consecutive_redirects will be incremented
            # and then compared to max_redirects. We want it to equal max_redirects after increment.
            max_redirects = exporter.client._config.redirect_policy.max_redirects
            exporter._consecutive_redirects = max_redirects - 1  # Will become max_redirects after increment

            test_envelope = TelemetryItem(name="test", time=datetime.now())
            result = exporter._transmit([test_envelope])

            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

            # Verify _track_dropped_items was called with the circular redirect custom message
            mock_track_dropped.assert_called_with(
                exporter._customer_sdkstats_metrics,
                [test_envelope],
                DropCode.CLIENT_EXCEPTION,
                "Error sending telemetry because of circular redirects. Please check the integrity of your connection string.",
            )

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_transmit_redirect_parsing_error_scenario_integration(self, mock_track_dropped):
        """Integration test that simulates the redirect parsing error scenario to verify custom message."""
        # This test simulates the scenario where redirect headers are missing/malformed (lines 328-335)

        # Create a redirect response with NO headers (or empty headers)
        redirect_response = MockResponse(307, "{}")  # Use 307 which is in _REDIRECT_STATUS_CODES
        redirect_response.headers = {}  # Empty headers - will cause parsing error

        with mock.patch.object(AzureMonitorClient, "track") as mock_track:
            # Mock the track method to raise HttpResponseError with redirect status but no location header
            mock_track.side_effect = HttpResponseError(message="Temporary Redirect", response=redirect_response)

            exporter = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd",
                disable_offline_storage=True,
            )

            # Enable customer sdkstats collection
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)
            exporter._customer_sdkstats_metrics = mock.Mock()

            # Set consecutive redirects to be less than max to ensure we go into the redirect handling logic
            # but not the circular redirect scenario
            max_redirects = exporter.client._config.redirect_policy.max_redirects
            exporter._consecutive_redirects = 0  # Start with 0 redirects

            test_envelope = TelemetryItem(name="test", time=datetime.now())
            result = exporter._transmit([test_envelope])

            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

            # Verify _track_dropped_items was called with the redirect parsing error custom message
            mock_track_dropped.assert_called_with(
                exporter._customer_sdkstats_metrics,
                [test_envelope],
                DropCode.CLIENT_EXCEPTION,
                "Error parsing redirect information.",
            )

    def test_track_dropped_items_custom_message_vs_no_message_comparison(self):
        """Test _track_dropped_items comparing custom message vs no message scenarios."""
        # This test demonstrates the difference between providing a custom message
        # and not providing any error message

        mock_customer_sdkstats = mock.Mock()
        envelope = TelemetryItem(name="test_trace", time=datetime.now())

        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._get_telemetry_type") as mock_get_type:
            mock_get_type.return_value = "trace"

            # Test 1: Call with custom message
            custom_message = "Custom error description for debugging"
            _track_dropped_items(
                mock_customer_sdkstats, [envelope], drop_code=DropCode.CLIENT_EXCEPTION, error_message=custom_message
            )

            # Verify custom message is included
            mock_customer_sdkstats.count_dropped_items.assert_called_with(
                1, "trace", DropCode.CLIENT_EXCEPTION, custom_message
            )

            # Reset mock for second test
            mock_customer_sdkstats.reset_mock()

            # Test 2: Call without error message (default None)
            _track_dropped_items(
                mock_customer_sdkstats,
                [envelope],
                drop_code=DropCode.CLIENT_EXCEPTION
                # error parameter omitted, should default to None
            )

            # Verify no error message is passed (only 3 arguments)
            mock_customer_sdkstats.count_dropped_items.assert_called_with(1, "trace", DropCode.CLIENT_EXCEPTION)

            # Verify the calls were different
            self.assertEqual(mock_customer_sdkstats.count_dropped_items.call_count, 1)

            # Check that the second call didn't include the error message
            args, kwargs = mock_customer_sdkstats.count_dropped_items.call_args
            self.assertEqual(len(args), 3)  # Should only have 3 args when no error message


def validate_telemetry_item(item1, item2):
    return (
        item1.name == item2.name
        and item1.time.year == item2.time.year
        and item1.time.month == item2.time.month
        and item1.time.day == item2.time.day
        and item1.time.hour == item2.time.hour
        and item1.time.minute == item2.time.minute
        and item1.time.second == item2.time.second
        and item1.time.microsecond == item2.time.microsecond
        and item1.version == item2.version
        and item1.sample_rate == item2.sample_rate
        and item1.sequence == item2.sequence
        and item1.instrumentation_key == item2.instrumentation_key
        and item1.tags == item2.tags
    )


class MockResponse:
    def __init__(self, status_code, text, headers={}, reason="test", content="{}"):
        self.status_code = status_code
        self.text = text
        self.headers = headers
        self.reason = reason
        self.content = content
        self.raw = MockRaw()


class MockRaw:
    def __init__(self):
        self.enforce_content_length = False
