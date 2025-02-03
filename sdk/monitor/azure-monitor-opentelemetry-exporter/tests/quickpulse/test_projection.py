# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
from unittest import mock

from azure.monitor.opentelemetry.exporter._quickpulse._constants import (
    _QUICKPULSE_PROJECTION_MAX_VALUE,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import (
    AggregationType,
)
from azure.monitor.opentelemetry.exporter._quickpulse._projection import (
    _calculate_aggregation,
    _create_projections,
    _init_derived_metric_projection,
)
from azure.monitor.opentelemetry.exporter._quickpulse._types import (
    _RequestData,
)

class TestProjection(unittest.TestCase):

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._projection._set_quickpulse_projection_map")
    def test_init_derived_metric_projection(self, set_map_mock):
        filter_mock = mock.Mock()
        filter_mock.aggregation = AggregationType.MIN
        filter_mock.id = "mock_id"
        _init_derived_metric_projection(filter_mock)
        set_map_mock.assert_called_once_with("mock_id", AggregationType.MIN, _QUICKPULSE_PROJECTION_MAX_VALUE, 0)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._projection._set_quickpulse_projection_map")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._projection._calculate_aggregation")
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

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._projection._set_quickpulse_projection_map")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._projection._calculate_aggregation")
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

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._projection._set_quickpulse_projection_map")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._projection._calculate_aggregation")
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

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._projection._get_quickpulse_projection_map")
    def test_calculate_aggregation_sum(self, projection_map_mock):
        projection_map_mock.return_value = {"test-id": (AggregationType.SUM, 3.0, 6)}
        agg_tuple = _calculate_aggregation(AggregationType.SUM, "test-id", 4.0)
        self.assertEqual(agg_tuple, (7.0, 7))

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._projection._get_quickpulse_projection_map")
    def test_calculate_aggregation_min(self, projection_map_mock):
        projection_map_mock.return_value = {"test-id": (AggregationType.MIN, 3.0, 6)}
        agg_tuple = _calculate_aggregation(AggregationType.MIN, "test-id", 4.0)
        self.assertEqual(agg_tuple, (3.0, 7))

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._projection._get_quickpulse_projection_map")
    def test_calculate_aggregation_max(self, projection_map_mock):
        projection_map_mock.return_value = {"test-id": (AggregationType.MAX, 3.0, 6)}
        agg_tuple = _calculate_aggregation(AggregationType.MAX, "test-id", 4.0)
        self.assertEqual(agg_tuple, (4.0, 7))

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._projection._get_quickpulse_projection_map")
    def test_calculate_aggregation_avg(self, projection_map_mock):
        projection_map_mock.return_value = {"test-id": (AggregationType.AVG, 3.0, 3)}
        agg_tuple = _calculate_aggregation(AggregationType.AVG, "test-id", 5.0)
        self.assertEqual(agg_tuple, (8.0, 4))

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._projection._get_quickpulse_projection_map")
    def test_calculate_aggregation_none(self, projection_map_mock):
        projection_map_mock.return_value = {"test-id": (AggregationType.AVG, 3.0, 3)}
        agg_tuple = _calculate_aggregation(AggregationType.AVG, "test-id2", 5.0)
        self.assertIsNone(agg_tuple)