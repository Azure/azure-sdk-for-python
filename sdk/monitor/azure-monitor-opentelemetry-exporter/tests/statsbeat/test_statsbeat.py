# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import unittest
from unittest import mock

from opentelemetry.sdk.metrics import MeterProvider, ObservableGauge
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from azure.monitor.opentelemetry.exporter.statsbeat import _statsbeat
from azure.monitor.opentelemetry.exporter.statsbeat._exporter import _StatsBeatExporter
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _REQ_SUCCESS_NAME,
    _REQUESTS_MAP,
)
from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics import (
    _StatsbeatMetrics,
    _RP_NAMES,
)

_StatsbeatMetrics_COMMON_ATTRS = dict(
    _StatsbeatMetrics._COMMON_ATTRIBUTES
)
_StatsbeatMetrics_METWORK_ATTRS = dict(
    _StatsbeatMetrics._NETWORK_ATTRIBUTES
)


# pylint: disable=protected-access
class TestStatsbeat(unittest.TestCase):
    def setUp(self):
        _statsbeat._STATSBEAT_METER_PROVIDER = None
        _StatsbeatMetrics._COMMON_ATTRIBUTES = dict(
            _StatsbeatMetrics_COMMON_ATTRS
        )
        _StatsbeatMetrics._NETWORK_ATTRIBUTES = dict(
            _StatsbeatMetrics_METWORK_ATTRS
        )

    def test_collect_statsbeat_metrics(self):
        exporter = mock.Mock()
        exporter._endpoint = "test endpoint"
        exporter._instrumentation_key = "test ikey"
        self.assertIsNone(_statsbeat._STATSBEAT_METER_PROVIDER)
        metrics = _statsbeat.collect_statsbeat_metrics(exporter)
        mp = _statsbeat._STATSBEAT_METER_PROVIDER
        self.assertTrue(isinstance(mp, MeterProvider))
        self.assertTrue(len(mp._sdk_config.metric_readers), 1)
        mr = mp._sdk_config.metric_readers[0]
        self.assertTrue(isinstance(mr, PeriodicExportingMetricReader))
        self.assertIsNotNone(mr._exporter)
        self.assertTrue(isinstance(mr._exporter, _StatsBeatExporter))
        self.assertTrue(isinstance(metrics, _StatsbeatMetrics))
        self.assertEqual(metrics._mp, mp)
        self.assertTrue(metrics._ikey, "test ikey")

    def test_collect_statsbeat_metrics_exists(self):
        exporter = mock.Mock()
        mock_mp = mock.Mock()
        self.assertIsNone(_statsbeat._STATSBEAT_METER_PROVIDER)
        _statsbeat._STATSBEAT_METER_PROVIDER = mock_mp
        _statsbeat.collect_statsbeat_metrics(exporter)
        self.assertEqual(_statsbeat._STATSBEAT_METER_PROVIDER, mock_mp)

    def test_collect_statsbeat_metrics_non_eu(self):
        exporter = mock.Mock()
        exporter._instrumentation_key = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3333"
        exporter._endpoint = "https://westus-0.in.applicationinsights.azure.com/"
        self.assertIsNone(_statsbeat._STATSBEAT_METER_PROVIDER)
        with mock.patch.dict(
                os.environ, {
                    "APPLICATION_INSIGHTS_STATS_CONNECTION_STRING": "",
                }):
            _statsbeat.collect_statsbeat_metrics(exporter)
            mp = _statsbeat._STATSBEAT_METER_PROVIDER
            mr = mp._sdk_config.metric_readers[0]
            stats_exporter = mr._exporter
            self.assertEqual(
                stats_exporter._instrumentation_key,
                _statsbeat._DEFAULT_NON_EU_STATS_CONNECTION_STRING.split(";")[0].split("=")[1]
            )
            self.assertEqual(
                stats_exporter._endpoint,
                _statsbeat._DEFAULT_NON_EU_STATS_CONNECTION_STRING.split(";")[1].split("=")[1]   # noqa: E501
            )

    def test_collect_statsbeat_metrics_eu(self):
        exporter = mock.Mock()
        exporter._instrumentation_key = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3333"
        exporter._endpoint = "https://northeurope-0.in.applicationinsights.azure.com/"
        self.assertIsNone(_statsbeat._STATSBEAT_METER_PROVIDER)
        with mock.patch.dict(
                os.environ, {
                    "APPLICATION_INSIGHTS_STATS_CONNECTION_STRING": "",
                }):
            _statsbeat.collect_statsbeat_metrics(exporter)
            mp = _statsbeat._STATSBEAT_METER_PROVIDER
            mr = mp._sdk_config.metric_readers[0]
            stats_exporter = mr._exporter
            self.assertEqual(
                stats_exporter._instrumentation_key,
                _statsbeat._DEFAULT_EU_STATS_CONNECTION_STRING.split(";")[0].split("=")[1]
            )
            self.assertEqual(
                stats_exporter._endpoint,
                _statsbeat._DEFAULT_EU_STATS_CONNECTION_STRING.split(";")[1].split("=")[1]   # noqa: E501
            )


# pylint: disable=protected-access
class TestStatsbeatMetrics(unittest.TestCase):
    def setUp(self):
        _statsbeat._STATSBEAT_METER_PROVIDER = None
        _StatsbeatMetrics._COMMON_ATTRIBUTES = dict(
            _StatsbeatMetrics_COMMON_ATTRS
        )
        _StatsbeatMetrics._NETWORK_ATTRIBUTES = dict(
            _StatsbeatMetrics_METWORK_ATTRS
        )
        _REQUESTS_MAP.clear()
        self._metric = _StatsbeatMetrics(
            MeterProvider(),
            "1aa11111-bbbb-1ccc-8ddd-eeeeffff3333",
            "https://westus-0.in.applicationinsights.azure.com/",
        )

    def test_statsbeat_metric_init(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
        )
        self.assertEqual(_StatsbeatMetrics._COMMON_ATTRIBUTES["cikey"], ikey)
        self.assertEqual(_StatsbeatMetrics._NETWORK_ATTRIBUTES["host"], "westus-1")
        self.assertEqual(metric._mp, mp)
        self.assertEqual(metric._ikey, ikey)
        self.assertEqual(metric._rp, _RP_NAMES[3])
        self.assertTrue(isinstance(metric._success_count, ObservableGauge))
        self.assertEqual(metric._success_count.name, _REQ_SUCCESS_NAME[0])

    def test_get_success_count(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["statusCode"] = 200
        _REQUESTS_MAP["success"] = 3
        obs = self._metric._get_success_count(options=None)
        self.assertEqual(len(obs), 1)
        self.assertEqual(obs[0].value, 3)
        self.assertEqual(obs[0].attributes, attributes)
        self.assertEqual(_REQUESTS_MAP["success"], 0)

    def test_get_success_zero_value(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["statusCode"] = 200
        _REQUESTS_MAP["success"] = 0
        obs = self._metric._get_success_count(options=None)
        self.assertEqual(len(obs), 0)
