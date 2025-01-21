# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
import unittest
from unittest import mock

from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import (
    TelemetryType,
)
from azure.monitor.opentelemetry.exporter._quickpulse._types import (
    _RequestData,
)
from azure.monitor.opentelemetry.exporter._quickpulse._filter import (
    _update_filter_configuration,
    _check_filters,
    _check_metric_filters,
    _parse_document_filter_configuration,
    _parse_metric_filter_configuration,
)


class TestFilter(unittest.TestCase):

    @mock.patch('azure.monitor.opentelemetry.exporter._quickpulse._filter._parse_document_filter_configuration')
    @mock.patch('azure.monitor.opentelemetry.exporter._quickpulse._filter._clear_quickpulse_projection_map')
    @mock.patch('azure.monitor.opentelemetry.exporter._quickpulse._filter._parse_metric_filter_configuration')
    @mock.patch('azure.monitor.opentelemetry.exporter._quickpulse._filter._set_quickpulse_etag')
    def test_update_filter_configuration(self, mock_set_etag, mock_parse_metric, mock_clear_projection, mock_parse_doc):
        etag = "new_etag"
        config = {"key": "value"}
        config_bytes = json.dumps(config).encode("utf-8")
        
        _update_filter_configuration(etag, config_bytes)
        
        mock_clear_projection.assert_called_once()
        mock_parse_metric.assert_called_once_with(config)
        mock_parse_doc.assert_called_once_with(config)
        mock_set_etag.assert_called_once_with(etag)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._set_quickpulse_derived_metric_infos")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._init_derived_metric_projection")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._rename_exception_fields_for_filtering")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._validate_derived_metric_info")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter.DerivedMetricInfo")
    def test_parse_metric_filter_configuration(
        self, dict_mock, validate_mock, rename_mock,  init_projection_mock, set_metric_info_mock
    ):
        test_config_bytes = '{"Metrics":[{"Id":"94.e4b85108","TelemetryType":"Request","FilterGroups":[{"Filters":[]}],"Projection":"Count()","Aggregation":"Sum","BackEndAggregation":"Sum"}]}'.encode()
        test_config_dict = json.loads(test_config_bytes.decode())
        metric_info_mock = mock.Mock()
        filter_group_mock = mock.Mock()
        metric_info_mock.filter_groups = [filter_group_mock]
        metric_info_mock.telemetry_type = TelemetryType.REQUEST
        dict_mock.from_dict.return_value = metric_info_mock
        validate_mock.return_value = True
        _parse_metric_filter_configuration(test_config_dict)
        dict_mock.from_dict.assert_called_once_with(test_config_dict.get("Metrics")[0])
        validate_mock.assert_called_once_with(metric_info_mock)
        rename_mock.assert_called_once_with(filter_group_mock)
        init_projection_mock.assert_called_once_with(metric_info_mock)
        metric_infos = {}
        metric_infos[TelemetryType.REQUEST] = [metric_info_mock]
        set_metric_info_mock.assert_called_once_with(metric_infos)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._set_quickpulse_derived_metric_infos")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._init_derived_metric_projection")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._rename_exception_fields_for_filtering")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._validate_derived_metric_info")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter.DerivedMetricInfo")
    def test_parse_metric_filter_configuration_invalid(
        self, dict_mock, validate_mock, rename_mock,  init_projection_mock, set_metric_info_mock
    ):
        test_config_bytes = '{"Metrics":[{"Id":"94.e4b85108","TelemetryType":"Request","FilterGroups":[{"Filters":[]}],"Projection":"Count()","Aggregation":"Sum","BackEndAggregation":"Sum"}]}'.encode()
        test_config_dict = json.loads(test_config_bytes.decode())
        metric_info_mock = mock.Mock()
        metric_info_mock.telemetry_type = TelemetryType.REQUEST
        dict_mock.from_dict.return_value = metric_info_mock
        validate_mock.return_value = False
        _parse_metric_filter_configuration(test_config_dict)
        dict_mock.from_dict.assert_called_once_with(test_config_dict.get("Metrics")[0])
        validate_mock.assert_called_once_with(metric_info_mock)
        rename_mock.assert_not_called()
        init_projection_mock.assert_not_called()
        metric_infos = {}
        set_metric_info_mock.assert_called_once_with(metric_infos)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._set_quickpulse_doc_stream_infos")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._rename_exception_fields_for_filtering")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._validate_document_filter_group_info")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter.DocumentStreamInfo")
    def test_parse_doc_filter_configuration(
        self, dict_mock, validate_mock, rename_mock, set_doc_info_mock
    ):
        test_config_bytes = '{"DocumentStreams": [ { "Id": "26a.7cf471b0", "DocumentFilterGroups": [ { "TelemetryType": "Request", "Filters": { "Filters": [ { "FieldName": "Success", "Predicate": "Equal", "Comparand": "true" }, { "FieldName": "Url", "Predicate": "Contains", "Comparand": "privacy" } ] } }, { "TelemetryType": "Dependency", "Filters": { "Filters": [ { "FieldName": "Success", "Predicate": "Equal", "Comparand": "true" } ] } }, { "TelemetryType": "Exception", "Filters": { "Filters": [] } }, { "TelemetryType": "Event", "Filters": { "Filters": [] } }, { "TelemetryType": "Trace", "Filters": { "Filters": [] } }, { "TelemetryType": "Request", "Filters": { "Filters": [ { "FieldName": "Duration", "Predicate": "LessThan", "Comparand": "0.0:0:0.015" } ] } } ] } ]}'.encode()
        test_config_dict = json.loads(test_config_bytes.decode())
        doc_stream_mock = mock.Mock()
        doc_stream_mock.id = "26a.7cf471b0"
        filter_group_mock = mock.Mock()
        filter_group_mock.telemetry_type = "Request"
        doc_stream_mock.document_filter_groups = [filter_group_mock]
        dict_mock.from_dict.return_value = doc_stream_mock
        validate_mock.return_value = True
        _parse_document_filter_configuration(test_config_dict)
        dict_mock.from_dict.assert_called_once_with(test_config_dict.get("DocumentStreams")[0])
        validate_mock.assert_called_once_with(filter_group_mock)
        rename_mock.assert_called_once_with(filter_group_mock.filters)
        doc_infos = {}
        doc_infos_inner = {
            "26a.7cf471b0": [filter_group_mock.filters]
        }
        doc_infos[TelemetryType.REQUEST] = doc_infos_inner
        set_doc_info_mock.assert_called_once_with(doc_infos)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._set_quickpulse_doc_stream_infos")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._rename_exception_fields_for_filtering")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._validate_document_filter_group_info")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter.DocumentStreamInfo")
    def test_parse_doc_filter_configuration_invalid(
        self, dict_mock, validate_mock, rename_mock, set_doc_info_mock
    ):
        test_config_bytes = '{"DocumentStreams": [ { "Id": "26a.7cf471b0", "DocumentFilterGroups": [ { "TelemetryType": "Request", "Filters": { "Filters": [ { "FieldName": "Success", "Predicate": "Equal", "Comparand": "true" }, { "FieldName": "Url", "Predicate": "Contains", "Comparand": "privacy" } ] } }, { "TelemetryType": "Dependency", "Filters": { "Filters": [ { "FieldName": "Success", "Predicate": "Equal", "Comparand": "true" } ] } }, { "TelemetryType": "Exception", "Filters": { "Filters": [] } }, { "TelemetryType": "Event", "Filters": { "Filters": [] } }, { "TelemetryType": "Trace", "Filters": { "Filters": [] } }, { "TelemetryType": "Request", "Filters": { "Filters": [ { "FieldName": "Duration", "Predicate": "LessThan", "Comparand": "0.0:0:0.015" } ] } } ] } ]}'.encode()
        test_config_dict = json.loads(test_config_bytes.decode())
        doc_stream_mock = mock.Mock()
        doc_stream_mock.id = "26a.7cf471b0"
        filter_group_mock = mock.Mock()
        filter_group_mock.telemetry_type = "Request"
        doc_stream_mock.document_filter_groups = [filter_group_mock]
        dict_mock.from_dict.return_value = doc_stream_mock
        validate_mock.return_value = False
        _parse_document_filter_configuration(test_config_dict)
        dict_mock.from_dict.assert_called_once_with(test_config_dict.get("DocumentStreams")[0])
        validate_mock.assert_called_once_with(filter_group_mock)
        rename_mock.assert_not_called()
        set_doc_info_mock.assert_called_once_with({})

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._check_filters")
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

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._check_filters")
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

    def test_no_filters(self):
        data = mock.Mock()
        result = _check_filters([], data)
        self.assertTrue(result)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._check_any_field_filter")
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

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._check_custom_dim_field_filter")
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

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._filter_time_stamp_to_ms")
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

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._field_string_compare")
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
