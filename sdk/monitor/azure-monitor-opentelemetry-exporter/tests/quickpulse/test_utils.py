# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from datetime import datetime
import unittest
from unittest import mock

from opentelemetry.sdk.metrics.export import HistogramDataPoint, NumberDataPoint
from azure.monitor.opentelemetry.exporter._quickpulse._constants import _COMMITTED_BYTES_NAME
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models._models import (
    MetricPoint,
    MonitoringDataPoint,
)
from azure.monitor.opentelemetry.exporter._quickpulse._utils import (
    _metric_to_quick_pulse_data_points,
)


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_mdp = MonitoringDataPoint(
            version=1.0,
            instance="test_instance",
            role_name="test_role_name",
            machine_name="test_machine_name",
            stream_id="test_stream_id"
        )

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils.datetime")
    def test_metric_to_qp_data_point_hist(self, datetime_mock):
        point = HistogramDataPoint(
            {},
            0,
            0,
            2,
            10,
            [1,1,0],
            [0,10,20],
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
        metric_point = MetricPoint(
            name=_COMMITTED_BYTES_NAME[1],
            weight=1,
            value=5
        )
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
        metric_point = MetricPoint(
            name=_COMMITTED_BYTES_NAME[1],
            weight=1,
            value=7
        )
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