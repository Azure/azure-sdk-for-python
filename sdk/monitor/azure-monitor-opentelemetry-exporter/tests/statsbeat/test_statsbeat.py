# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import unittest
from unittest import mock

from opentelemetry.sdk.metrics import MeterProvider, ObservableGauge
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from azure.monitor.opentelemetry.exporter._constants import (
    _REQ_DURATION_NAME,
    _REQ_EXCEPTION_NAME,
    _REQ_FAILURE_NAME,
    _REQ_RETRY_NAME,
    _REQ_SUCCESS_NAME,
    _REQ_THROTTLE_NAME,
)
from azure.monitor.opentelemetry.exporter.statsbeat import _statsbeat
from azure.monitor.opentelemetry.exporter.statsbeat._exporter import _StatsBeatExporter
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _REQUESTS_MAP,
)
from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics import (
    _get_average_duration,
    _get_exception_count,
    _get_failure_count,
    _get_retry_count,
    _get_success_count,
    _get_throttle_count,
    _StatsbeatMetrics,
    _RP_NAMES,
)

_StatsbeatMetrics_COMMON_ATTRS = dict(
    _StatsbeatMetrics._COMMON_ATTRIBUTES
)
_StatsbeatMetrics_METWORK_ATTRS = dict(
    _StatsbeatMetrics._NETWORK_ATTRIBUTES
)

# cSpell:disable

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
        _statsbeat.collect_statsbeat_metrics(exporter)
        mp = _statsbeat._STATSBEAT_METER_PROVIDER
        self.assertTrue(isinstance(mp, MeterProvider))
        self.assertTrue(len(mp._sdk_config.metric_readers), 1)
        mr = mp._sdk_config.metric_readers[0]
        self.assertTrue(isinstance(mr, PeriodicExportingMetricReader))
        self.assertIsNotNone(mr._exporter)
        self.assertTrue(isinstance(mr._exporter, _StatsBeatExporter))

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
        self.assertTrue(isinstance(metric._failure_count, ObservableGauge))
        self.assertTrue(isinstance(metric._retry_count, ObservableGauge))
        self.assertTrue(isinstance(metric._throttle_count, ObservableGauge))
        self.assertTrue(isinstance(metric._exception_count, ObservableGauge))
        self.assertTrue(isinstance(metric._average_duration, ObservableGauge))
        self.assertEqual(metric._success_count.name, _REQ_SUCCESS_NAME[0])
        self.assertEqual(metric._failure_count.name, _REQ_FAILURE_NAME[0])
        self.assertEqual(metric._retry_count.name, _REQ_RETRY_NAME[0])
        self.assertEqual(metric._throttle_count.name, _REQ_THROTTLE_NAME[0])
        self.assertEqual(metric._exception_count.name, _REQ_EXCEPTION_NAME[0])
        self.assertEqual(metric._average_duration.name, _REQ_DURATION_NAME[0])
        
    def test_get_success_count(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["statusCode"] = 200
        _REQUESTS_MAP[_REQ_SUCCESS_NAME[1]] = 3
        observations = _get_success_count(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 3)
            self.assertEqual(obs.attributes, attributes)
            self.assertEqual(_REQUESTS_MAP[_REQ_SUCCESS_NAME[1]], 0)

    def test_get_success_zero_value(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["statusCode"] = 200
        _REQUESTS_MAP[_REQ_SUCCESS_NAME[1]] = 0
        observations = _get_success_count(options=None)
        exists = False
        for obs in observations:
            exists = True
        self.assertFalse(exists)

    def test_get_average_duration(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        _REQUESTS_MAP[_REQ_DURATION_NAME[1]] = 10.0
        _REQUESTS_MAP["count"] = 4
        observations = _get_average_duration(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 2500)
            self.assertEqual(obs.attributes, attributes)
            self.assertEqual(_REQUESTS_MAP[_REQ_DURATION_NAME[1]], 0)
            self.assertEqual(_REQUESTS_MAP["count"], 0)

    def test_get_average_duration_zero_value(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        _REQUESTS_MAP[_REQ_DURATION_NAME[1]] = 0
        _REQUESTS_MAP["count"] = 4
        observations = _get_average_duration(options=None)
        self.assertEqual(len(observations), 0)

    def test_get_failure_count(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["statusCode"] = 400
        _REQUESTS_MAP[_REQ_FAILURE_NAME[1]] = {}
        _REQUESTS_MAP[_REQ_FAILURE_NAME[1]][400] = 3
        observations = _get_failure_count(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 3)
            self.assertEqual(obs.attributes, attributes)
            self.assertEqual(_REQUESTS_MAP[_REQ_FAILURE_NAME[1]][400], 0)

    def test_get_failure_zero_value(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["statusCode"] = 400
        _REQUESTS_MAP[_REQ_FAILURE_NAME[1]] = {}
        _REQUESTS_MAP[_REQ_FAILURE_NAME[1]][400] = 0
        observations = _get_failure_count(options=None)
        self.assertEqual(len(observations), 0)

    def test_get_retry_count(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["statusCode"] = 500
        _REQUESTS_MAP[_REQ_RETRY_NAME[1]] = {}
        _REQUESTS_MAP[_REQ_RETRY_NAME[1]][500] = 3
        observations = _get_retry_count(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 3)
            self.assertEqual(obs.attributes, attributes)
            self.assertEqual(_REQUESTS_MAP[_REQ_RETRY_NAME[1]][500], 0)

    def test_get_retry_zero_value(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["statusCode"] = 500
        _REQUESTS_MAP[_REQ_RETRY_NAME[1]] = {}
        _REQUESTS_MAP[_REQ_RETRY_NAME[1]][500] = 0
        observations = _get_retry_count(options=None)
        self.assertEqual(len(observations), 0)

    def test_get_throttle_count(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["statusCode"] = 402
        _REQUESTS_MAP[_REQ_THROTTLE_NAME[1]] = {}
        _REQUESTS_MAP[_REQ_THROTTLE_NAME[1]][402] = 3
        observations = _get_throttle_count(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 3)
            self.assertEqual(obs.attributes, attributes)
            self.assertEqual(_REQUESTS_MAP[_REQ_THROTTLE_NAME[1]][402], 0)

    def test_get_throttle_zero_value(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["statusCode"] = 402
        _REQUESTS_MAP[_REQ_THROTTLE_NAME[1]] = {}
        _REQUESTS_MAP[_REQ_THROTTLE_NAME[1]][402] = 0
        observations = _get_throttle_count(options=None)
        self.assertEqual(len(observations), 0)

    def test_get_exception_count(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["exceptionType"] = "Exception"
        _REQUESTS_MAP[_REQ_EXCEPTION_NAME[1]] = {}
        _REQUESTS_MAP[_REQ_EXCEPTION_NAME[1]]["Exception"] = 3
        observations = _get_exception_count(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 3)
            self.assertEqual(obs.attributes, attributes)
            self.assertEqual(_REQUESTS_MAP[_REQ_EXCEPTION_NAME[1]]["Exception"], 0)

    def test_get_exception_zero_value(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["exceptionType"] = "Exception"
        _REQUESTS_MAP[_REQ_EXCEPTION_NAME[1]] = {}
        _REQUESTS_MAP[_REQ_EXCEPTION_NAME[1]]["Exception"] = 0
        observations = _get_exception_count(options=None)
        self.assertEqual(len(observations), 0)

# cSpell:enable
