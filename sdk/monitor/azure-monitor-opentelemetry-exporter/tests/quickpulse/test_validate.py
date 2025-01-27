# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
from unittest import mock

from azure.monitor.opentelemetry.exporter._quickpulse._validate import (
    _validate_derived_metric_info,
)


class TestValidate(unittest.TestCase):

    def test_valid_telemetry_type(self):
        valid_metric_info = mock.Mock(telemetry_type="Request", projection=None, filter_groups=[])
        self.assertTrue(_validate_derived_metric_info(valid_metric_info))

    def test_validate_info_invalid_telemetry_type(self):
        invalid_metric_info = mock.Mock(telemetry_type="Request", projection=None, filter_groups=[])
        invalid_metric_info.telemetry_type = "INVALID_TYPE"
        self.assertFalse(_validate_derived_metric_info(invalid_metric_info))

    def test_validate_info_custom_metric_projection(self):
        valid_metric_info = mock.Mock(telemetry_type="Request", projection=None, filter_groups=[])
        valid_metric_info.telemetry_type = "Request"
        valid_metric_info.projection = "CustomMetrics.MyMetric"
        self.assertFalse(_validate_derived_metric_info(valid_metric_info))

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._validate._validate_filter_predicate_and_comparand")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._validate._validate_filter_field_name")
    def test_validate_info_valid_filters(self, field_mock, pred_mock):
        valid_metric_info = mock.Mock(telemetry_type="Request", projection=None, filter_groups=[])
        filter = mock.Mock()
        filter_group = mock.Mock()
        filter_group.filters = [filter]
        valid_metric_info.filter_groups = [filter_group]
        field_mock.return_value = True
        pred_mock.return_value = True

        self.assertTrue(_validate_derived_metric_info(valid_metric_info))

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._validate._validate_filter_predicate_and_comparand")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._validate._validate_filter_field_name")
    def test_validate_info_invalid_filters(self, field_mock, pred_mock):
        valid_metric_info = mock.Mock(telemetry_type="Request", projection=None, filter_groups=[])
        filter = mock.Mock()
        filter_group = mock.Mock()
        filter_group.filters = [filter]
        valid_metric_info.filter_groups = [filter_group]
        field_mock.return_value = True
        pred_mock.return_value = False

        self.assertFalse(_validate_derived_metric_info(valid_metric_info))
