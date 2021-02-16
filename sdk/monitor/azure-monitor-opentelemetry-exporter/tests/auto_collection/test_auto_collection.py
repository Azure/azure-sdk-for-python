# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
from unittest import mock

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider

from azure.monitor.opentelemetry.sdk.auto_collection import (
    AutoCollection,
    standard_metrics_processor
)
from azure.monitor.opentelemetry.sdk.auto_collection._performance_metrics import (
    PerformanceMetrics
)

# pylint: disable=protected-access
class TestAutoCollection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        metrics.set_meter_provider(MeterProvider())
        cls._meter = metrics.get_meter(__name__)
        cls._test_labels = tuple({"environment": "staging"}.items())

    @classmethod
    def tearDownClass(cls):
        metrics._METER_PROVIDER = None

    def test_constructor(self):
        """Test the constructor."""

        auto_collection = AutoCollection(meter=self._meter, labels=self._test_labels)
        self.assertTrue(isinstance(auto_collection._performance_metrics, PerformanceMetrics))
        self.assertEqual(auto_collection._performance_metrics._meter, self._meter)
        self.assertEqual(auto_collection._performance_metrics._labels, self._test_labels)


class TestStandardMetrics(unittest.TestCase):

    def test_standard_metrics_processor(self):
        envelope = mock.Mock()
        point = mock.Mock()
        tags = {"ai.cloud.role":"testrole", "ai.cloud.roleInstance":"testinstance"}
        envelope.tags = tags

        point.name = "http.client.duration"
        base_data = mock.Mock()
        base_data.metrics = [point]
        base_data.properties = {
            "http.status_code": "200",
            "http.url": "http://example.com",
        }
        envelope.data.base_data = base_data
        standard_metrics_processor(envelope)
        self.assertEqual(point.name, "Dependency duration")
        self.assertEqual(point.kind, "Aggregation")
        self.assertEqual(
            base_data.properties["_MS.MetricId"], "dependencies/duration"
        )
        self.assertEqual(base_data.properties["_MS.IsAutocollected"], "True")
        self.assertEqual(
            base_data.properties["cloud/roleInstance"], "testinstance"
        )
        self.assertEqual(base_data.properties["cloud/roleName"], "testrole")
        self.assertEqual(base_data.properties["Dependency.Success"], "True")
        self.assertEqual(
            base_data.properties["dependency/target"], "http://example.com"
        )
        self.assertEqual(base_data.properties["Dependency.Type"], "HTTP")
        self.assertEqual(base_data.properties["dependency/resultCode"], "200")
        self.assertEqual(
            base_data.properties["dependency/performanceBucket"], ""
        )
        self.assertEqual(base_data.properties["operation/synthetic"], "")
        base_data.properties["http.status_code"] = "500"
        point.name = "http.client.duration"
        standard_metrics_processor(envelope)
        self.assertEqual(base_data.properties["Dependency.Success"], "False")
        base_data.properties["http.status_code"] = "asd"
        point.name = "http.client.duration"
        standard_metrics_processor(envelope)
        self.assertEqual(base_data.properties["Dependency.Success"], "False")
