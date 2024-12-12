# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from datetime import datetime
import json
import unittest
from unittest import mock

from opentelemetry.sdk.metrics.export import HistogramDataPoint, NumberDataPoint
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind

from azure.monitor.opentelemetry.exporter._quickpulse._constants import (
    _COMMITTED_BYTES_NAME,
    _QUICKPULSE_PROJECTION_MAX_VALUE,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import (
    AggregationType,
    DocumentType,
    Exception,
    MetricPoint,
    MonitoringDataPoint,
    RemoteDependency,
    Request,
    TelemetryType,
    Trace,
)
from azure.monitor.opentelemetry.exporter._quickpulse._types import (
    _DependencyData,
    _RequestData,
)
from azure.monitor.opentelemetry.exporter._quickpulse._utils import (
    _calculate_aggregation,
    _check_filters,
    _check_metric_filters,
    _create_projections,
    _derive_metrics_from_telemetry_data,
    _get_metrics_from_projections,
    _get_span_document,
    _get_log_record_document,
    _filter_time_stamp_to_ms,
    _init_derived_metric_projection,
    _metric_to_quick_pulse_data_points,
    _validate_derived_metric_info,
    _update_filter_configuration,
)


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_mdp = MonitoringDataPoint(
            version=1.0,
            invariant_version=1,
            instance="test_instance",
            role_name="test_role_name",
            machine_name="test_machine_name",
            stream_id="test_stream_id",
            is_web_app=False,
            performance_collection_supported=True,
        )

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils.datetime")
    def test_metric_to_qp_data_point_hist(self, datetime_mock):
        point = HistogramDataPoint(
            {},
            0,
            0,
            2,
            10,
            [1, 1, 0],
            [0, 10, 20],
            0,
            5,
        )
        metric = mock.Mock()
        metric.name = _COMMITTED_BYTES_NAME[0]
        metric.data.data_points = [point]
        scope_metric = mock.Mock()
        scope_metric.metrics = [metric]
        resource_metric = mock.Mock()
        resource_metric.scope_metrics = [scope_metric]
        metric_data = mock.Mock()
        metric_data.resource_metrics = [resource_metric]
        metric_point = MetricPoint(name=_COMMITTED_BYTES_NAME[1], weight=1, value=5)
        documents = [mock.Mock()]
        date_now = datetime.now()
        datetime_mock.now.return_value = date_now
        mdp = _metric_to_quick_pulse_data_points(metric_data, self.base_mdp, documents)[0]
        self.assertEqual(mdp.version, self.base_mdp.version)
        self.assertEqual(mdp.instance, self.base_mdp.instance)
        self.assertEqual(mdp.role_name, self.base_mdp.role_name)
        self.assertEqual(mdp.machine_name, self.base_mdp.machine_name)
        self.assertEqual(mdp.stream_id, self.base_mdp.stream_id)
        self.assertEqual(mdp.timestamp, date_now)
        self.assertEqual(mdp.metrics, [metric_point])
        self.assertEqual(mdp.documents, documents)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils.datetime")
    def test_metric_to_qp_data_point_num(self, datetime_mock):
        point = NumberDataPoint(
            {},
            0,
            0,
            7,
        )
        metric = mock.Mock()
        metric.name = _COMMITTED_BYTES_NAME[0]
        metric.data.data_points = [point]
        scope_metric = mock.Mock()
        scope_metric.metrics = [metric]
        resource_metric = mock.Mock()
        resource_metric.scope_metrics = [scope_metric]
        metric_data = mock.Mock()
        metric_data.resource_metrics = [resource_metric]
        metric_point = MetricPoint(name=_COMMITTED_BYTES_NAME[1], weight=1, value=7)
        documents = [mock.Mock()]
        date_now = datetime.now()
        datetime_mock.now.return_value = date_now
        mdp = _metric_to_quick_pulse_data_points(metric_data, self.base_mdp, documents)[0]
        self.assertEqual(mdp.version, self.base_mdp.version)
        self.assertEqual(mdp.instance, self.base_mdp.instance)
        self.assertEqual(mdp.role_name, self.base_mdp.role_name)
        self.assertEqual(mdp.machine_name, self.base_mdp.machine_name)
        self.assertEqual(mdp.stream_id, self.base_mdp.stream_id)
        self.assertEqual(mdp.timestamp, date_now)
        self.assertEqual(mdp.metrics, [metric_point])
        self.assertEqual(mdp.documents, documents)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_metrics_from_projections")
    def test_metric_to_qp_data_point_process_filtered_metrics(self, projection_mock):
        metric_data = mock.Mock()
        metric_data.resource_metrics = []
        projections = [("ID:1234", 5.0)]
        projection_mock.return_value = projections
        mdp = _metric_to_quick_pulse_data_points(metric_data, self.base_mdp, [])[0]
        self.assertEqual(mdp.metrics[0].name, "ID:1234")
        self.assertEqual(mdp.metrics[0].value, 5.0)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._ns_to_iso8601_string")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_url_for_http_dependency")
    def test_get_span_document_client(self, url_mock, iso_mock):
        span_mock = mock.Mock()
        span_mock.name = "test_span"
        span_mock.end_time = 10
        span_mock.start_time = 4
        span_mock.attributes = {
            SpanAttributes.HTTP_STATUS_CODE: "200",
            SpanAttributes.RPC_GRPC_STATUS_CODE: "400",
        }
        span_mock.kind = SpanKind.CLIENT
        url_mock.return_value = "test_url"
        iso_mock.return_value = "1000"
        doc = _get_span_document(span_mock)
        self.assertTrue(isinstance(doc, RemoteDependency))
        self.assertEqual(doc.document_type, DocumentType.REMOTE_DEPENDENCY)
        self.assertEqual(doc.name, "test_span")
        self.assertEqual(doc.command_name, "test_url")
        self.assertEqual(doc.result_code, "200")
        self.assertEqual(doc.duration, "1000")

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._ns_to_iso8601_string")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_url_for_http_request")
    def test_get_span_document_server(self, url_mock, iso_mock):
        span_mock = mock.Mock()
        span_mock.name = "test_span"
        span_mock.end_time = 10
        span_mock.start_time = 4
        span_mock.attributes = {
            SpanAttributes.HTTP_STATUS_CODE: "200",
            SpanAttributes.RPC_GRPC_STATUS_CODE: "400",
        }
        span_mock.kind = SpanKind.SERVER
        url_mock.return_value = "test_url"
        iso_mock.return_value = "1000"
        doc = _get_span_document(span_mock)
        self.assertTrue(isinstance(doc, Request))
        self.assertEqual(doc.document_type, DocumentType.REQUEST)
        self.assertEqual(doc.name, "test_span")
        self.assertEqual(doc.url, "test_url")
        self.assertEqual(doc.response_code, "200")
        self.assertEqual(doc.duration, "1000")

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._ns_to_iso8601_string")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_url_for_http_request")
    def test_get_span_document_server_grpc_status(self, url_mock, iso_mock):
        span_mock = mock.Mock()
        span_mock.name = "test_span"
        span_mock.end_time = 10
        span_mock.start_time = 4
        span_mock.attributes = {
            SpanAttributes.RPC_GRPC_STATUS_CODE: "400",
        }
        span_mock.kind = SpanKind.SERVER
        url_mock.return_value = "test_url"
        iso_mock.return_value = "1000"
        doc = _get_span_document(span_mock)
        self.assertTrue(isinstance(doc, Request))
        self.assertEqual(doc.document_type, DocumentType.REQUEST)
        self.assertEqual(doc.name, "test_span")
        self.assertEqual(doc.url, "test_url")
        self.assertEqual(doc.response_code, "400")
        self.assertEqual(doc.duration, "1000")

    def test_get_log_record_document_server_exc(self):
        log_record = mock.Mock()
        log_record.attributes = {
            SpanAttributes.EXCEPTION_TYPE: "exc_type",
            SpanAttributes.EXCEPTION_MESSAGE: "exc_message",
        }
        log_data = mock.Mock()
        log_data.log_record = log_record
        doc = _get_log_record_document(log_data)
        self.assertTrue(isinstance(doc, Exception))
        self.assertEqual(doc.document_type, DocumentType.EXCEPTION)
        self.assertEqual(doc.exception_type, "exc_type")
        self.assertEqual(doc.exception_message, "exc_message")

    def test_get_log_record_document_server_exc(self):
        log_record = mock.Mock()
        log_record.attributes = {}
        log_record.body = "body"
        log_data = mock.Mock()
        log_data.log_record = log_record
        doc = _get_log_record_document(log_data)
        self.assertTrue(isinstance(doc, Trace))
        self.assertEqual(doc.document_type, DocumentType.TRACE)
        self.assertEqual(doc.message, "body")

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._set_quickpulse_etag")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._set_quickpulse_derived_metric_infos")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._init_derived_metric_projection")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._rename_exception_fields_for_filtering")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._validate_derived_metric_info")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils.DerivedMetricInfo")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._clear_quickpulse_projection_map")
    def test_update_filter_configuration(
        self, clear_mock, dict_mock, validate_mock, rename_mock, init_projection_mock, set_metric_info_mock, etag_mock
    ):
        etag = "new-etag"
        test_config_bytes = '{"Metrics":[{"Id":"94.e4b85108","TelemetryType":"Request","FilterGroups":[{"Filters":[]}],"Projection":"Count()","Aggregation":"Sum","BackEndAggregation":"Sum"}]}'.encode()
        test_config_dict = json.loads(test_config_bytes.decode()).get("Metrics")[0]
        metric_info_mock = mock.Mock()
        metric_info_mock.telemetry_type = TelemetryType.REQUEST
        dict_mock.from_dict.return_value = metric_info_mock
        validate_mock.return_value = True
        rename_mock.return_value = None
        _update_filter_configuration(etag, test_config_bytes)
        clear_mock.assert_called_once()
        dict_mock.from_dict.assert_called_once_with(test_config_dict)
        init_projection_mock.assert_called_once_with(metric_info_mock)
        metric_infos = {}
        metric_infos[TelemetryType.REQUEST] = [metric_info_mock]
        set_metric_info_mock.assert_called_once_with(metric_infos)
        etag_mock.assert_called_once_with(etag)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._set_quickpulse_etag")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._set_quickpulse_derived_metric_infos")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._init_derived_metric_projection")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._validate_derived_metric_info")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils.DerivedMetricInfo")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._clear_quickpulse_projection_map")
    def test_update_filter_configuration_invalid(
        self, clear_mock, dict_mock, validate_mock, init_projection_mock, set_metric_info_mock, etag_mock
    ):
        etag = "new-etag"
        test_config_bytes = '{"Metrics":[{"Id":"94.e4b85108","TelemetryType":"Request","FilterGroups":[{"Filters":[]}],"Projection":"Count()","Aggregation":"Sum","BackEndAggregation":"Sum"}]}'.encode()
        test_config_dict = json.loads(test_config_bytes.decode()).get("Metrics")[0]
        metric_info_mock = mock.Mock()
        metric_info_mock.telemetry_type = TelemetryType.REQUEST
        dict_mock.from_dict.return_value = metric_info_mock
        validate_mock.return_value = False
        _update_filter_configuration(etag, test_config_bytes)
        clear_mock.assert_called_once()
        dict_mock.from_dict.assert_called_once_with(test_config_dict)
        init_projection_mock.assert_not_called()
        metric_infos = {}
        set_metric_info_mock.assert_called_once_with(metric_infos)
        etag_mock.assert_called_once_with(etag)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._create_projections")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._check_metric_filters")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_quickpulse_derived_metric_infos")
    def test_derive_metrics_from_telemetry_data(self, get_derived_mock, filter_mock, projection_mock):
        metric_infos = [mock.Mock]
        get_derived_mock.return_value = {
            TelemetryType.DEPENDENCY: metric_infos,
        }
        data = _DependencyData(
            duration=0,
            success=True,
            name="test",
            result_code=200,
            target="",
            type="",
            data="",
            custom_dimensions={},
        )
        filter_mock.return_value = True
        _derive_metrics_from_telemetry_data(data)
        get_derived_mock.assert_called_once()
        filter_mock.assert_called_once_with(metric_infos, data)
        projection_mock.assert_called_once_with(metric_infos, data)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._create_projections")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._check_metric_filters")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_quickpulse_derived_metric_infos")
    def test_derive_metrics_from_telemetry_data_filter_false(self, get_derived_mock, filter_mock, projection_mock):
        metric_infos = [mock.Mock]
        get_derived_mock.return_value = {
            TelemetryType.DEPENDENCY: metric_infos,
        }
        data = _DependencyData(
            duration=0,
            success=True,
            name="test",
            result_code=200,
            target="",
            type="",
            data="",
            custom_dimensions={},
        )
        filter_mock.return_value = False
        _derive_metrics_from_telemetry_data(data)
        get_derived_mock.assert_called_once()
        filter_mock.assert_called_once_with(metric_infos, data)
        projection_mock.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._check_filters")
    def test_check_metric_filters(self, filter_mock):
        metric_info = mock.Mock()
        group_mock = mock.Mock()
        filters_mock = mock.Mock()
        group_mock.filters = filters_mock
        metric_info.filter_groups = [group_mock]
        filter_mock.return_value = True
        data = mock.Mock()
        match = _check_metric_filters([metric_info], data)
        filter_mock.assert_called_once_with(filters_mock, data)
        self.assertTrue(match)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._check_filters")
    def test_check_metric_filters_no_match(self, filter_mock):
        metric_info = mock.Mock()
        group_mock = mock.Mock()
        filters_mock = mock.Mock()
        group_mock.filters = filters_mock
        metric_info.filter_groups = [group_mock]
        filter_mock.return_value = False
        data = mock.Mock()
        match = _check_metric_filters([metric_info], data)
        filter_mock.assert_called_once_with(filters_mock, data)
        self.assertFalse(match)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._set_quickpulse_projection_map")
    def test_init_derived_metric_projection(self, set_map_mock):
        filter_mock = mock.Mock()
        filter_mock.aggregation = AggregationType.MIN
        filter_mock.id = "mock_id"
        _init_derived_metric_projection(filter_mock)
        set_map_mock.assert_called_once_with("mock_id", AggregationType.MIN, _QUICKPULSE_PROJECTION_MAX_VALUE, 0)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._set_quickpulse_projection_map")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._calculate_aggregation")
    def test_create_projections_count(self, aggregation_mock, set_map_mock):
        data_mock = mock.Mock()
        metric_info = mock.Mock()
        metric_info.id = "mock_id"
        metric_info.projection = "Count()"
        metric_info.aggregation = AggregationType.SUM
        aggregation_mock.return_value = (1, 2)
        _create_projections([metric_info], data_mock)
        aggregation_mock.assert_called_once_with(AggregationType.SUM, "mock_id", 1)
        set_map_mock.assert_called_once_with("mock_id", AggregationType.SUM, 1, 2)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._set_quickpulse_projection_map")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._calculate_aggregation")
    def test_create_projections_duration(self, aggregation_mock, set_map_mock):
        data_mock = _RequestData(
            duration=5.0,
            success=True,
            name="test",
            response_code=200,
            url="",
            custom_dimensions={},
        )
        metric_info = mock.Mock()
        metric_info.id = "mock_id"
        metric_info.projection = "Duration"
        metric_info.aggregation = AggregationType.SUM
        aggregation_mock.return_value = (6.0, 2)
        _create_projections([metric_info], data_mock)
        aggregation_mock.assert_called_once_with(AggregationType.SUM, "mock_id", 5.0)
        set_map_mock.assert_called_once_with("mock_id", AggregationType.SUM, 6.0, 2)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._set_quickpulse_projection_map")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._calculate_aggregation")
    def test_create_projections_dimensions(self, aggregation_mock, set_map_mock):
        data_mock = mock.Mock()
        data_mock.custom_dimensions = {
            "test-key": "6.7",
        }
        metric_info = mock.Mock()
        metric_info.id = "mock_id"
        metric_info.projection = "CustomDimensions.test-key"
        metric_info.aggregation = AggregationType.SUM
        aggregation_mock.return_value = (8.2, 2)
        _create_projections([metric_info], data_mock)
        aggregation_mock.assert_called_once_with(AggregationType.SUM, "mock_id", 6.7)
        set_map_mock.assert_called_once_with("mock_id", AggregationType.SUM, 8.2, 2)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_quickpulse_projection_map")
    def test_calculate_aggregation_sum(self, projection_map_mock):
        projection_map_mock.return_value = {"test-id": (AggregationType.SUM, 3.0, 6)}
        agg_tuple = _calculate_aggregation(AggregationType.SUM, "test-id", 4.0)
        self.assertEqual(agg_tuple, (7.0, 7))

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_quickpulse_projection_map")
    def test_calculate_aggregation_min(self, projection_map_mock):
        projection_map_mock.return_value = {"test-id": (AggregationType.MIN, 3.0, 6)}
        agg_tuple = _calculate_aggregation(AggregationType.MIN, "test-id", 4.0)
        self.assertEqual(agg_tuple, (3.0, 7))

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_quickpulse_projection_map")
    def test_calculate_aggregation_max(self, projection_map_mock):
        projection_map_mock.return_value = {"test-id": (AggregationType.MAX, 3.0, 6)}
        agg_tuple = _calculate_aggregation(AggregationType.MAX, "test-id", 4.0)
        self.assertEqual(agg_tuple, (4.0, 7))

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_quickpulse_projection_map")
    def test_calculate_aggregation_avg(self, projection_map_mock):
        projection_map_mock.return_value = {"test-id": (AggregationType.AVG, 3.0, 3)}
        agg_tuple = _calculate_aggregation(AggregationType.AVG, "test-id", 5.0)
        self.assertEqual(agg_tuple, (8.0, 4))

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_quickpulse_projection_map")
    def test_calculate_aggregation_none(self, projection_map_mock):
        projection_map_mock.return_value = {"test-id": (AggregationType.AVG, 3.0, 3)}
        agg_tuple = _calculate_aggregation(AggregationType.AVG, "test-id2", 5.0)
        self.assertIsNone(agg_tuple)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_quickpulse_projection_map")
    def test_get_metrics_from_projections(self, projection_map_mock):
        projection_map_mock.return_value = {
            "test-id": (AggregationType.MIN, 3.0, 3),
            "test-id2": (AggregationType.MAX, 5.0, 4),
            "test-id3": (AggregationType.SUM, 2.0, 2),
            "test-id4": (AggregationType.AVG, 12.0, 3),
        }
        metric_tuples = _get_metrics_from_projections()
        self.assertEqual(
            metric_tuples,
            [
                ("test-id", 3.0),
                ("test-id2", 5.0),
                ("test-id3", 2.0),
                ("test-id4", 4.0),
            ],
        )

    def test_validate_info_invalid_telemetry_type(self):
        invalid_metric_info = mock.Mock(telemetry_type="Request", projection=None, filter_groups=[])
        invalid_metric_info.telemetry_type = "INVALID_TYPE"
        self.assertFalse(_validate_derived_metric_info(invalid_metric_info))

    def test_validate_info_custom_metric_projection(self):
        valid_metric_info = mock.Mock(telemetry_type="Request", projection=None, filter_groups=[])
        valid_metric_info.telemetry_type = "Request"
        valid_metric_info.projection = "CustomMetrics.MyMetric"
        self.assertFalse(_validate_derived_metric_info(valid_metric_info))

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._validate_filter_predicate_and_comparand")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._validate_filter_field_name")
    def test_validate_info_valid_filters(self, field_mock, pred_mock):
        valid_metric_info = mock.Mock(telemetry_type="Request", projection=None, filter_groups=[])
        filter = mock.Mock()
        filter_group = mock.Mock()
        filter_group.filters = [filter]
        valid_metric_info.filter_groups = [filter_group]
        field_mock.return_value = True
        pred_mock.return_value = True

        self.assertTrue(_validate_derived_metric_info(valid_metric_info))

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._validate_filter_predicate_and_comparand")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._validate_filter_field_name")
    def test_validate_info_invalid_filters(self, field_mock, pred_mock):
        valid_metric_info = mock.Mock(telemetry_type="Request", projection=None, filter_groups=[])
        filter = mock.Mock()
        filter_group = mock.Mock()
        filter_group.filters = [filter]
        valid_metric_info.filter_groups = [filter_group]
        field_mock.return_value = True
        pred_mock.return_value = False

        self.assertFalse(_validate_derived_metric_info(valid_metric_info))

    def test_valid_time_stamp_with_decimal_seconds(self):
        time_stamp = "14.6:56:7.89"
        expected_ms = 1234567890  # Expected milliseconds
        self.assertEqual(_filter_time_stamp_to_ms(time_stamp), expected_ms)

    def test_valid_time_stamp_with_whole_seconds(self):
        time_stamp = "0.0:0:0.2"
        expected_ms = 200  # Expected milliseconds
        self.assertEqual(_filter_time_stamp_to_ms(time_stamp), expected_ms)

    def test_valid_time_stamp_with_no_days(self):
        time_stamp = "0.5:30:15.5"
        expected_ms = 19815500  # 0 days, 5 hours, 30 minutes, 15.5 seconds
        self.assertEqual(_filter_time_stamp_to_ms(time_stamp), expected_ms)

    def test_valid_time_stamp_with_large_days(self):
        time_stamp = "100.0:0:0"
        expected_ms = 8640000000  # 100 days
        self.assertEqual(_filter_time_stamp_to_ms(time_stamp), expected_ms)

    def test_invalid_time_stamp(self):
        time_stamp = "invalid_format"
        self.assertIsNone(_filter_time_stamp_to_ms(time_stamp))

    def test_time_stamp_missing_seconds(self):
        time_stamp = "1.0:0:"
        self.assertIsNone(_filter_time_stamp_to_ms(time_stamp))

    def test_time_stamp_empty_string(self):
        time_stamp = ""
        self.assertIsNone(_filter_time_stamp_to_ms(time_stamp))

    def test_no_filters(self):
        data = mock.Mock()
        result = _check_filters([], data)
        self.assertTrue(result)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._check_any_field_filter")
    def test_check_any_filters(self, check_mock):
        filter_info = mock.Mock()
        filter_info.field_name = "*"
        filter_info.predicate = "Equal"
        filter_info.comparand = "true"
        data_mock = mock.Mock()
        check_mock.return_value = True
        result = _check_filters([filter_info], data_mock)
        self.assertTrue(result)
        check_mock.assert_called_once_with(filter_info, data_mock)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._check_custom_dim_field_filter")
    def test_check_custom_dim_filters(self, check_mock):
        filter_info = mock.Mock()
        filter_info.field_name = "CustomDimensions."
        filter_info.predicate = "Equal"
        filter_info.comparand = "true"
        data_mock = mock.Mock()
        check_mock.return_value = True
        result = _check_filters([filter_info], data_mock)
        self.assertTrue(result)
        check_mock.assert_called_once_with(filter_info, data_mock.custom_dimensions)

    def test_success_filter_equal(self):
        filter_info = mock.Mock()
        filter_info.field_name = "Success"
        filter_info.predicate = "Equal"
        filter_info.comparand = "true"
        data_mock = _RequestData(
            duration=5.0,
            success=True,
            name="test",
            response_code=200,
            url="",
            custom_dimensions={},
        )
        result = _check_filters([filter_info], data_mock)
        self.assertTrue(result)

    def test_success_not_equal(self):
        filter_info = mock.Mock()
        filter_info.field_name = "Success"
        filter_info.predicate = "NotEqual"
        filter_info.comparand = "false"
        data_mock = _RequestData(
            duration=5.0,
            success=True,
            name="test",
            response_code=200,
            url="",
            custom_dimensions={},
        )
        result = _check_filters([filter_info], data_mock)
        self.assertTrue(result)

    def test_result_code_greater_than(self):
        filter_info = mock.Mock()
        filter_info.field_name = "ResponseCode"
        filter_info.predicate = "GreaterThan"
        filter_info.comparand = "200"
        data_mock = _RequestData(
            duration=5.0,
            success=True,
            name="test",
            response_code=404,
            url="",
            custom_dimensions={},
        )
        result = _check_filters([filter_info], data_mock)
        self.assertTrue(result)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._filter_time_stamp_to_ms")
    def test_duration_less_than(self, timestamp_mock):
        filter_info = mock.Mock()
        filter_info.field_name = "Duration"
        filter_info.predicate = "LessThan"
        filter_info.comparand = "5000"
        timestamp_mock.return_value = 5000
        data_mock = _RequestData(
            duration=3000,
            success=True,
            name="test",
            response_code=200,
            url="",
            custom_dimensions={},
        )
        result = _check_filters([filter_info], data_mock)
        self.assertTrue(result)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._field_string_compare")
    def test_field_string_compare(self, string_mock):
        filter_info = mock.Mock()
        filter_info.field_name = "url"
        filter_info.predicate = "Contains"
        filter_info.comparand = "example"
        string_mock.return_value = True
        data_mock = _RequestData(
            duration=3000,
            success=True,
            name="test",
            response_code=200,
            url="example.com",
            custom_dimensions={},
        )
        result = _check_filters([filter_info], data_mock)
        self.assertTrue(result)
        string_mock.assert_called_once_with(str("example.com"), "example", "Contains")
