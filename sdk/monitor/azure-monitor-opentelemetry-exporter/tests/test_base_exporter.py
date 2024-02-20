# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import shutil
import unittest
from unittest import mock
from datetime import datetime

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.core.pipeline.transport import HttpResponse
from azure.monitor.opentelemetry.exporter.export._base import (
    _MONITOR_DOMAIN_MAPPING,
    _format_storage_telemetry_item,
    _get_auth_policy,
    BaseExporter,
    ExportResult,
)
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _REQUESTS_MAP,
    _STATSBEAT_STATE,
)
from azure.monitor.opentelemetry.exporter._constants import (
    _REQ_DURATION_NAME,
    _REQ_EXCEPTION_NAME,
    _REQ_FAILURE_NAME,
    _REQ_RETRY_NAME,
    _REQ_SUCCESS_NAME,
    _REQ_THROTTLE_NAME,
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
                print('Failed to delete %s. Reason: %s' % (file_path, e))


# pylint: disable=W0212
# pylint: disable=R0904
class TestBaseExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ[
            "APPINSIGHTS_INSTRUMENTATIONKEY"
        ] = "1234abcd-5678-4efa-8abc-1234567890ab"
        os.environ["APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL"] = "true"
        cls._base = BaseExporter()
        cls._envelopes_to_export = [TelemetryItem(name="Test", time=datetime.now())]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._base.storage._path, True)

    def setUp(self) -> None:
        _REQUESTS_MAP.clear()
        _STATSBEAT_STATE = {
            "INITIAL_FAILURE_COUNT": 0,
            "INITIAL_SUCCESS": False,
            "SHUTDOWN": False,
        }

    def tearDown(self):
        clean_folder(self._base.storage._path)

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
                TEST_TEMP_DIR, "Microsoft/AzureMonitor", "opentelemetry-python-" + "4321abcd-5678-4efa-8abc-1234567890ab"
            )
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
        envelope_mock = {"name":"test","time":"time"}
        blob_mock.get.return_value = [envelope_mock]
        dict_patch.return_value = {"name":"test","time":"time"}
        format_patch.return_value = envelope_mock
        exporter.storage.gets.return_value = [blob_mock]
        with mock.patch.object(AzureMonitorClient, 'track') as post:
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
        envelope_mock = {"name":"test","time":"time"}
        blob_mock.get.return_value = [envelope_mock]
        dict_patch.return_value = {"name":"test","time":"time"}
        format_patch.return_value = envelope_mock
        exporter.storage.gets.return_value = [blob_mock]
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code"):
            with mock.patch.object(AzureMonitorClient, 'track', throw(HttpResponseError)):
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
        time=datetime.now()
        base = MonitorBase(
            base_type="",
            base_data=None
        )
        ti = TelemetryItem(
            name="test_telemetry_item",
            time=time,
            version=1,
            sample_rate=50.0,
            sequence="test_sequence",
            instrumentation_key="4321abcd-5678-4efa-8abc-1234567890ab",
            tags={"tag1": "val1", "tag2": "val2"},
            data=base
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
            version=2,
            properties={"key1": "val1"},
            severity_level="3",
            exceptions=[exc_data_details]
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
            with mock.patch.object(AzureMonitorClient, 'track', throw(HttpResponseError)):
                result = self._base._transmit(self._envelopes_to_export)
            self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmit_http_error_not_retryable(self):
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code") as m:
            m.return_value = False
            with mock.patch.object(AzureMonitorClient, 'track', throw(HttpResponseError)):
                result = self._base._transmit(self._envelopes_to_export)
            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmit_http_error_redirect(self):
        response = HttpResponse(None, None)
        response.status_code = 307
        response.headers = {"location":"https://example.com"}
        prev_redirects = self._base.client._config.redirect_policy.max_redirects
        self._base.client._config.redirect_policy.max_redirects = 2
        prev_host = self._base.client._config.host
        error = HttpResponseError(response=response)
        with mock.patch.object(AzureMonitorClient, 'track') as post:
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
        with mock.patch.object(AzureMonitorClient, 'track') as post:
            post.side_effect = error
            result = self._base._transmit(self._envelopes_to_export)
            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
            self.assertEqual(post.call_count, 1)
            self.assertEqual(self._base.client._config.host, prev_host)

    def test_transmit_http_error_redirect_invalid_location_header(self):
        response = HttpResponse(None, None)
        response.status_code = 307
        response.headers = {"location":"123"}
        error = HttpResponseError(response=response)
        prev_host = self._base.client._config.host
        with mock.patch.object(AzureMonitorClient, 'track') as post:
            post.side_effect = error
            result = self._base._transmit(self._envelopes_to_export)
            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
            self.assertEqual(post.call_count, 1)
            self.assertEqual(self._base.client._config.host, prev_host)

    def test_transmit_request_error(self):
        with mock.patch.object(AzureMonitorClient, 'track', throw(ServiceRequestError, message="error")):
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
        "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
        }
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_transmit_request_error_statsbeat(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        with mock.patch.object(AzureMonitorClient, 'track', throw(ServiceRequestError, message="error")):
            result = exporter._transmit(self._envelopes_to_export)
        stats_mock.assert_called_once()
        self.assertEqual(len(_REQUESTS_MAP), 3)
        self.assertEqual(_REQUESTS_MAP[_REQ_EXCEPTION_NAME[1]]["ServiceRequestError"], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmit_request_exception(self):
        with mock.patch.object(AzureMonitorClient, 'track', throw(Exception)):
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
        "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
        }
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_transmit_request_exception_statsbeat(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        with mock.patch.object(AzureMonitorClient, 'track', throw(Exception)):
            result = exporter._transmit(self._envelopes_to_export)
        stats_mock.assert_called_once()
        self.assertEqual(len(_REQUESTS_MAP), 3)
        self.assertEqual(_REQUESTS_MAP[_REQ_EXCEPTION_NAME[1]]["Exception"], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmission_200(self):
        with mock.patch.object(AzureMonitorClient, 'track') as post:
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
        }
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_statsbeat_200(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        with mock.patch.object(AzureMonitorClient, 'track') as post:
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
        custom_envelopes_to_export = [TelemetryItem(name="Test", time=datetime.now(
        )), TelemetryItem(name="Test", time=datetime.now()), test_envelope]
        with mock.patch.object(AzureMonitorClient, 'track') as post:
            post.return_value = TrackResponse(
                items_received=3,
                items_accepted=1,
                errors=[
                    TelemetryErrorDetails(
                        index=0,
                        status_code=400,
                        message="should drop",
                    ),
                    TelemetryErrorDetails(
                        index=2,
                        status_code=500,
                        message="should retry"
                    )
                ],
            )
            result = exporter._transmit(custom_envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
        exporter.storage.put.assert_called_once()

    @mock.patch.dict(
        os.environ,
        {
        "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "false",
        }
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_statsbeat_206_retry(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        exporter.storage = mock.Mock()
        test_envelope = TelemetryItem(name="testEnvelope", time=datetime.now())
        custom_envelopes_to_export = [TelemetryItem(name="Test", time=datetime.now(
        )), TelemetryItem(name="Test", time=datetime.now()), test_envelope]
        with mock.patch.object(AzureMonitorClient, 'track') as post:
            post.return_value = TrackResponse(
                items_received=3,
                items_accepted=1,
                errors=[
                    TelemetryErrorDetails(
                        index=0,
                        status_code=400,
                        message="should drop",
                    ),
                    TelemetryErrorDetails(
                        index=2,
                        status_code=500,
                        message="should retry"
                    )
                ],
            )
            result = exporter._transmit(custom_envelopes_to_export)
        stats_mock.assert_called_once()
        self.assertEqual(len(_REQUESTS_MAP), 3)
        self.assertEqual(_REQUESTS_MAP[_REQ_RETRY_NAME[1]][500], 1)
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertIsNotNone(_REQUESTS_MAP[_REQ_DURATION_NAME[1]])
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmission_206_no_retry(self):
        exporter = BaseExporter(disable_offline_storage=True)
        exporter.storage = mock.Mock()
        test_envelope = TelemetryItem(name="testEnvelope", time=datetime.now())
        custom_envelopes_to_export = [TelemetryItem(name="Test", time=datetime.now(
        )), TelemetryItem(name="Test", time=datetime.now()), test_envelope]
        with mock.patch.object(AzureMonitorClient, 'track') as post:
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
        }
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_statsbeat_206_no_retry(self, stats_mock):
        exporter = BaseExporter(disable_offline_storage=True)
        exporter.storage = mock.Mock()
        test_envelope = TelemetryItem(name="testEnvelope", time=datetime.now())
        custom_envelopes_to_export = [TelemetryItem(name="Test", time=datetime.now(
        )), TelemetryItem(name="Test", time=datetime.now()), test_envelope]
        with mock.patch.object(AzureMonitorClient, 'track') as post:
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
        }
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
        }
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
        }
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
        }
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
        }
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
        }
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
        }
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
        }
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
        }
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

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._get_auth_policy")
    def test_exporter_credential(self, mock_add_credential_policy):
        TEST_CREDENTIAL = "TEST_CREDENTIAL"
        base = BaseExporter(credential=TEST_CREDENTIAL, authentication_policy=TEST_AUTH_POLICY)
        self.assertEqual(base._credential, TEST_CREDENTIAL)
        mock_add_credential_policy.assert_called_once_with(TEST_CREDENTIAL, TEST_AUTH_POLICY)

    def test_get_auth_policy(self):
        class TestCredential():
            def get_token():
                return "TEST_TOKEN"
        credential = TestCredential()
        result = _get_auth_policy(credential, TEST_AUTH_POLICY)
        self.assertEqual(result._credential, credential)
        

    def test_get_auth_policy_no_credential(self):
        self.assertEqual(_get_auth_policy(credential=None, default_auth_policy=TEST_AUTH_POLICY), TEST_AUTH_POLICY)
        

    def test_get_auth_policy_invalid_credential(self):
        class InvalidTestCredential():
            def invalid_get_token():
                return "TEST_TOKEN"
        self.assertRaises(ValueError, _get_auth_policy, credential=InvalidTestCredential(), default_auth_policy=TEST_AUTH_POLICY)


def validate_telemetry_item(item1, item2):
    return item1.name == item2.name and \
        item1.time.year == item2.time.year and \
        item1.time.month == item2.time.month and \
        item1.time.day == item2.time.day and \
        item1.time.hour == item2.time.hour and \
        item1.time.minute == item2.time.minute and \
        item1.time.second == item2.time.second and \
        item1.time.microsecond == item2.time.microsecond and \
        item1.version == item2.version and \
        item1.sample_rate == item2.sample_rate and \
        item1.sequence == item2.sequence and \
        item1.instrumentation_key == item2.instrumentation_key and \
        item1.tags == item2.tags


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
