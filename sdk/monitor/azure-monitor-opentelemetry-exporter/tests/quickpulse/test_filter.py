# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
import unittest
from unittest import mock

from azure.monitor.opentelemetry.exporter._quickpulse._generated.livemetrics.models import (
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
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._parse_document_filter_configuration")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._clear_quickpulse_projection_map")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._parse_metric_filter_configuration")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._set_quickpulse_etag")
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
    def test_parse_metric_filter_configuration(self, init_projection_mock, set_metric_info_mock):
        test_config_dict = {
            "Metrics": [
                {
                    "Id": "94.e4b85108",
                    "TelemetryType": "Request",
                    "FilterGroups": [{"Filters": []}],
                    "Projection": "Count()",
                    "Aggregation": "Sum",
                    "BackEndAggregation": "Sum",
                }
            ]
        }
        _parse_metric_filter_configuration(test_config_dict)

        # Verify projection was initialized
        init_projection_mock.assert_called_once()
        metric_info = init_projection_mock.call_args[0][0]
        self.assertEqual(metric_info.id, "94.e4b85108")
        self.assertEqual(metric_info.telemetry_type, TelemetryType.REQUEST)

        # Verify metric infos were set correctly
        set_metric_info_mock.assert_called_once()
        metric_infos = set_metric_info_mock.call_args[0][0]
        self.assertIn(TelemetryType.REQUEST, metric_infos)
        self.assertEqual(len(metric_infos[TelemetryType.REQUEST]), 1)
        self.assertEqual(metric_infos[TelemetryType.REQUEST][0].id, "94.e4b85108")

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._set_quickpulse_derived_metric_infos")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._init_derived_metric_projection")
    def test_parse_metric_filter_configuration_invalid(self, init_projection_mock, set_metric_info_mock):
        # Config with invalid projection (CustomMetrics prefix is not supported)
        test_config_dict = {
            "Metrics": [
                {
                    "Id": "94.e4b85108",
                    "TelemetryType": "Request",
                    "FilterGroups": [{"Filters": []}],
                    "Projection": "CustomMetrics.InvalidProjection",
                    "Aggregation": "Sum",
                    "BackEndAggregation": "Sum",
                }
            ]
        }
        _parse_metric_filter_configuration(test_config_dict)

        # Invalid metrics should not have projection initialized
        init_projection_mock.assert_not_called()
        # Metric infos should be set with empty dict
        set_metric_info_mock.assert_called_once_with({})

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._set_quickpulse_doc_stream_infos")
    def test_parse_doc_filter_configuration(self, set_doc_info_mock):
        test_config_dict = {
            "DocumentStreams": [
                {
                    "Id": "26a.7cf471b0",
                    "DocumentFilterGroups": [
                        {
                            "TelemetryType": "Request",
                            "Filters": {
                                "Filters": [{"FieldName": "Success", "Predicate": "Equal", "Comparand": "true"}]
                            },
                        }
                    ],
                }
            ]
        }
        _parse_document_filter_configuration(test_config_dict)

        # Verify doc infos were set correctly
        set_doc_info_mock.assert_called_once()
        doc_infos = set_doc_info_mock.call_args[0][0]
        self.assertIn(TelemetryType.REQUEST, doc_infos)
        self.assertIn("26a.7cf471b0", doc_infos[TelemetryType.REQUEST])
        self.assertEqual(len(doc_infos[TelemetryType.REQUEST]["26a.7cf471b0"]), 1)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._filter._set_quickpulse_doc_stream_infos")
    def test_parse_doc_filter_configuration_invalid(self, set_doc_info_mock):
        # Config with invalid telemetry type (Event is not supported)
        test_config_dict = {
            "DocumentStreams": [
                {
                    "Id": "26a.7cf471b0",
                    "DocumentFilterGroups": [
                        {
                            "TelemetryType": "Event",
                            "Filters": {"Filters": []},
                        }
                    ],
                }
            ]
        }
        _parse_document_filter_configuration(test_config_dict)

        # Invalid filter groups should result in empty doc infos
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
