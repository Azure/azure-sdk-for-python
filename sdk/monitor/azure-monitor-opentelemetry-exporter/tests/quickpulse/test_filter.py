# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
from unittest import mock

from azure.monitor.opentelemetry.exporter._quickpulse._types import (
    _RequestData,
)
from azure.monitor.opentelemetry.exporter._quickpulse._filter import (
    _check_filters,
    _check_metric_filters,
)


class TestFilter(unittest.TestCase):

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
