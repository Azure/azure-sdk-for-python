# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import sys
import json
import os
import platform
import unittest
from unittest import mock
import requests

from opentelemetry.sdk.metrics import Meter, MeterProvider, ObservableGauge

from azure.monitor.opentelemetry.exporter._constants import (
    _ATTACH_METRIC_NAME,
    _FEATURE_METRIC_NAME,
    _REQ_DURATION_NAME,
    _REQ_EXCEPTION_NAME,
    _REQ_FAILURE_NAME,
    _REQ_RETRY_NAME,
    _REQ_SUCCESS_NAME,
    _REQ_THROTTLE_NAME,
)
from opentelemetry.metrics import Observation
from azure.monitor.opentelemetry.exporter.statsbeat import _utils as statsbeat_utils
from azure.monitor.opentelemetry.exporter.statsbeat._manager import StatsbeatManager
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _REQUESTS_MAP,
    _STATSBEAT_STATE,
    _STATSBEAT_STATE_LOCK,
    get_statsbeat_feature_attribute_bits,
    set_statsbeat_feature_attribute_bits,
)
from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics import (
    _shorten_host,
    _FEATURE_TYPES,
    _StatsbeatFeature,
    _StatsbeatMetrics,
    _AttachTypes,
    _RP_Names,
)
from azure.monitor.opentelemetry.exporter.statsbeat._utils import (
    _get_additional_observations,
)


class MockResponse(object):
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


# cSpell:disable

_StatsbeatMetrics_COMMON_ATTRS = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
_StatsbeatMetrics_NETWORK_ATTRS = dict(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
_StatsbeatMetrics_FEATURE_ATTRIBUTES = dict(_StatsbeatMetrics._FEATURE_ATTRIBUTES)
_StatsbeatMetrics_INSTRUMENTATION_ATTRIBUTES = dict(_StatsbeatMetrics._INSTRUMENTATION_ATTRIBUTES)


# pylint: disable=protected-access, unused-argument, line-too-long, too-many-public-methods
class TestStatsbeatMetrics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.pop("WEBSITE_SITE_NAME", None)
        os.environ.pop("WEBSITE_HOME_STAMPNAME", None)
        os.environ.pop("FUNCTIONS_WORKER_RUNTIME", None)
        os.environ.pop("WEBSITE_HOSTNAME", None)
        os.environ.pop("AKS_ARM_NAMESPACE_ID", None)
        os.environ.pop("KUBERNETES_SERVICE_HOST", None)

        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        cls._metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            True,
            0,
            False,
        )

    def setUp(self):
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["INITIAL_FAILURE_COUNT"] = 0
            _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
            _STATSBEAT_STATE["SHUTDOWN"] = False
            _STATSBEAT_STATE["CUSTOM_EVENTS_FEATURE_SET"] = False
            _STATSBEAT_STATE["LIVE_METRICS_FEATURE_SET"] = False
            _STATSBEAT_STATE["CUSTOMER_SDKSTATS_FEATURE_SET"] = False
            _STATSBEAT_STATE["FEATURE_ATTRIBUTE_BITS"] = 0

        _StatsbeatMetrics._COMMON_ATTRIBUTES = dict(_StatsbeatMetrics_COMMON_ATTRS)
        _StatsbeatMetrics._NETWORK_ATTRIBUTES = dict(_StatsbeatMetrics_NETWORK_ATTRS)
        _StatsbeatMetrics._FEATURE_ATTRIBUTES = dict(_StatsbeatMetrics_FEATURE_ATTRIBUTES)
        _StatsbeatMetrics._INSTRUMENTATION_ATTRIBUTES = dict(_StatsbeatMetrics_INSTRUMENTATION_ATTRIBUTES)
        _REQUESTS_MAP.clear()

    def test_statsbeat_metric_init(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            5,
            False,
        )
        self.assertEqual(_StatsbeatMetrics._COMMON_ATTRIBUTES["cikey"], ikey)
        self.assertEqual(_StatsbeatMetrics._COMMON_ATTRIBUTES["attach"], _AttachTypes.MANUAL)
        self.assertEqual(_StatsbeatMetrics._NETWORK_ATTRIBUTES["host"], "westus-1")
        self.assertEqual(_StatsbeatMetrics._COMMON_ATTRIBUTES["rp"], _RP_Names.UNKNOWN.value)
        self.assertEqual(_StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"], 1)
        self.assertEqual(_StatsbeatMetrics._FEATURE_ATTRIBUTES["type"], _FEATURE_TYPES.FEATURE)
        self.assertEqual(metric._meter_provider, mp)
        self.assertTrue(isinstance(metric._meter, Meter))
        self.assertEqual(metric._ikey, ikey)
        self.assertEqual(metric._long_interval_threshold, 5)
        self.assertTrue(metric._vm_retry)
        self.assertEqual(len(metric._vm_data), 0)
        self.assertEqual(metric._feature, 1)
        for count in metric._long_interval_count_map.values():
            self.assertEqual(count, sys.maxsize)
        self.assertTrue(isinstance(metric._attach_metric, ObservableGauge))
        self.assertTrue(isinstance(metric._feature_metric, ObservableGauge))
        self.assertEqual(metric._attach_metric.name, _ATTACH_METRIC_NAME[0])
        self.assertEqual(metric._feature_metric.name, _FEATURE_METRIC_NAME[0])

    def test_statsbeat_feature_attribute_bits_getter_default(self):
        self.assertEqual(get_statsbeat_feature_attribute_bits(), 0)

    def test_statsbeat_feature_attribute_bits_setter_and_getter(self):
        feature_bits = _StatsbeatFeature.DISK_RETRY | _StatsbeatFeature.LIVE_METRICS
        set_statsbeat_feature_attribute_bits(feature_bits)
        self.assertEqual(get_statsbeat_feature_attribute_bits(), feature_bits)

    @mock.patch("azure.monitor.opentelemetry.exporter._utils._is_attach_enabled")
    def test_statsbeat_metric_init_attach_enabled(self, attach_mock):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        attach_mock.return_value = True
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            5,
            False,
        )
        self.assertEqual(_StatsbeatMetrics._COMMON_ATTRIBUTES["cikey"], ikey)
        self.assertEqual(_StatsbeatMetrics._COMMON_ATTRIBUTES["attach"], _AttachTypes.INTEGRATED)
        self.assertEqual(_StatsbeatMetrics._NETWORK_ATTRIBUTES["host"], "westus-1")
        self.assertEqual(_StatsbeatMetrics._COMMON_ATTRIBUTES["rp"], _RP_Names.UNKNOWN.value)
        self.assertEqual(_StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"], 1)
        self.assertEqual(_StatsbeatMetrics._FEATURE_ATTRIBUTES["type"], _FEATURE_TYPES.FEATURE)
        self.assertEqual(metric._meter_provider, mp)
        self.assertTrue(isinstance(metric._meter, Meter))
        self.assertEqual(metric._ikey, ikey)
        self.assertEqual(metric._long_interval_threshold, 5)
        self.assertTrue(metric._vm_retry)
        self.assertEqual(len(metric._vm_data), 0)
        self.assertEqual(metric._feature, 1)
        for count in metric._long_interval_count_map.values():
            self.assertEqual(count, sys.maxsize)
        self.assertTrue(isinstance(metric._attach_metric, ObservableGauge))
        self.assertTrue(isinstance(metric._feature_metric, ObservableGauge))
        self.assertEqual(metric._attach_metric.name, _ATTACH_METRIC_NAME[0])
        self.assertEqual(metric._feature_metric.name, _FEATURE_METRIC_NAME[0])

    # pylint: disable=protected-access
    def test_get_attach_metric_meet_threshold(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            2,
            False,
        )
        metric._long_interval_count_map[_ATTACH_METRIC_NAME[0]] = 2
        metric._vm_retry = False
        observations = metric._get_attach_metric(options=None)
        self.assertEqual(len(observations), 1)
        self.assertEqual(metric._long_interval_count_map[_ATTACH_METRIC_NAME[0]], 0)

    # pylint: disable=protected-access
    def test_get_attach_metric_does_not_meet_threshold(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            2,
            False,
        )
        metric._long_interval_count_map[_ATTACH_METRIC_NAME[0]] = 1
        observations = metric._get_attach_metric(options=None)
        self.assertEqual(len(observations), 0)
        self.assertEqual(metric._long_interval_count_map[_ATTACH_METRIC_NAME[0]], 1)

    # pylint: disable=protected-access
    @mock.patch.dict(
        os.environ,
        {
            "WEBSITE_SITE_NAME": "site_name",
            "WEBSITE_HOME_STAMPNAME": "stamp_name",
        },
    )
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics._StatsbeatMetrics._get_azure_compute_metadata",
        return_value=False,
    )
    def test_get_attach_metric_appsvc(self, metadata_mock):
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        self.assertEqual(attributes["rp"], _RP_Names.UNKNOWN.value)
        attributes["rp"] = _RP_Names.APP_SERVICE.value
        attributes["rpId"] = "site_name/stamp_name"
        observations = self._metric._get_attach_metric(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 1)
            self.assertEqual(obs.attributes, attributes)
        self.assertEqual(_StatsbeatMetrics._COMMON_ATTRIBUTES["rp"], _RP_Names.APP_SERVICE.value)

    # pylint: disable=protected-access
    @mock.patch.dict(
        os.environ,
        {
            "FUNCTIONS_WORKER_RUNTIME": "runtime",
            # Functions can have WEBSITE_SITE_NAME
            "WEBSITE_SITE_NAME": "site_name",
            "WEBSITE_HOSTNAME": "host_name",
        },
    )
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics._StatsbeatMetrics._get_azure_compute_metadata",
        return_value=False,
    )
    def test_get_attach_metric_functions(self, metadata_mock):
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        self.assertEqual(attributes["rp"], _RP_Names.UNKNOWN.value)
        attributes["rp"] = _RP_Names.FUNCTIONS.value
        attributes["rpId"] = "host_name"
        observations = self._metric._get_attach_metric(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 1)
            self.assertEqual(obs.attributes, attributes)
        self.assertEqual(_StatsbeatMetrics._COMMON_ATTRIBUTES["rp"], _RP_Names.FUNCTIONS.value)

    # pylint: disable=protected-access
    @mock.patch.dict(
        os.environ,
        {
            "AKS_ARM_NAMESPACE_ID": "namespace_id",
            "KUBERNETES_SERVICE_HOST": "TEST_KUBERNETES_SERVICE_HOST",
        },
    )
    def test_get_attach_metric_aks_attach(self):
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        self.assertEqual(attributes["rp"], _RP_Names.UNKNOWN.value)
        attributes["rp"] = _RP_Names.AKS.value
        attributes["rpId"] = "namespace_id"
        observations = self._metric._get_attach_metric(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 1)
            self.assertEqual(obs.attributes, attributes)
        self.assertEqual(_StatsbeatMetrics._COMMON_ATTRIBUTES["rp"], _RP_Names.AKS.value)

    # pylint: disable=protected-access
    @mock.patch.dict(
        os.environ,
        {
            "KUBERNETES_SERVICE_HOST": "TEST_KUBERNETES_SERVICE_HOST",
        },
    )
    def test_get_attach_metric_aks_manual(self):
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        self.assertEqual(attributes["rp"], _RP_Names.UNKNOWN.value)
        attributes["rp"] = _RP_Names.AKS.value
        attributes["rpId"] = "TEST_KUBERNETES_SERVICE_HOST"
        observations = self._metric._get_attach_metric(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 1)
            self.assertEqual(obs.attributes, attributes)
        self.assertEqual(_StatsbeatMetrics._COMMON_ATTRIBUTES["rp"], _RP_Names.AKS.value)

    @mock.patch(
        "azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics._StatsbeatMetrics._get_azure_compute_metadata"
    )
    def test_get_attach_metric_vm(self, metadata_mock):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            0,
            False,
        )
        _vm_data = {}
        _vm_data["vmId"] = "123"
        _vm_data["subscriptionId"] = "sub123"
        _vm_data["osType"] = "test_os"
        metric._vm_data = _vm_data
        metric._vm_retry = True
        metadata_mock.return_value = True
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        self.assertEqual(attributes["rp"], _RP_Names.UNKNOWN.value)
        self.assertEqual(attributes["os"], platform.system())
        attributes["rp"] = _RP_Names.VM.value
        attributes["rpId"] = "123/sub123"
        attributes["os"] = "test_os"
        observations = metric._get_attach_metric(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 1)
            self.assertEqual(obs.attributes, attributes)
        self.assertEqual(_StatsbeatMetrics._COMMON_ATTRIBUTES["rp"], _RP_Names.VM.value)
        self.assertEqual(_StatsbeatMetrics._COMMON_ATTRIBUTES["os"], "test_os")

    @mock.patch(
        "azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics._StatsbeatMetrics._get_azure_compute_metadata",
        return_value=False,
    )
    def test_get_attach_metric_vm_no_os(self, metadata_mock):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            0,
            False,
        )
        _vm_data = {}
        _vm_data["vmId"] = "123"
        _vm_data["subscriptionId"] = "sub123"
        _vm_data["osType"] = None
        metric._vm_data = _vm_data
        metric._vm_retry = True
        metadata_mock.return_value = True
        self.assertEqual(_StatsbeatMetrics._COMMON_ATTRIBUTES["os"], platform.system())
        observations = metric._get_attach_metric(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 1)
            self.assertEqual(obs.attributes["os"], platform.system())
        self.assertEqual(_StatsbeatMetrics._COMMON_ATTRIBUTES["os"], platform.system())

    def test_get_attach_metric_unknown(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            0,
            False,
        )
        metric._vm_retry = False
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        self.assertEqual(attributes["rp"], _RP_Names.UNKNOWN.value)
        observations = metric._get_attach_metric(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 1)
            self.assertEqual(obs.attributes["rp"], _RP_Names.UNKNOWN.value)

    def test_get_azure_compute_metadata(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            0,
            False,
        )
        with mock.patch("requests.get") as get:
            get.return_value = MockResponse(200, json.dumps({"vmId": 5, "subscriptionId": 3, "osType": "Linux"}))
            vm_result = metric._get_azure_compute_metadata()
            self.assertTrue(vm_result)
            self.assertEqual(metric._vm_data["vmId"], 5)
            self.assertEqual(metric._vm_data["subscriptionId"], 3)
            self.assertEqual(metric._vm_data["osType"], "Linux")
            self.assertTrue(metric._vm_retry)

    def test_get_azure_compute_metadata_not_vm(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            0,
            False,
        )
        with mock.patch("requests.get", throw(requests.exceptions.ConnectionError)):
            vm_result = metric._get_azure_compute_metadata()
            self.assertFalse(vm_result)
            self.assertEqual(len(metric._vm_data), 0)
            self.assertFalse(metric._vm_retry)

    def test_get_azure_compute_metadata_not_vm_timeout(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            0,
            False,
        )
        with mock.patch("requests.get", throw(requests.Timeout)):
            vm_result = metric._get_azure_compute_metadata()
            self.assertFalse(vm_result)
            self.assertEqual(len(metric._vm_data), 0)
            self.assertFalse(metric._vm_retry)

    def test_get_azure_compute_metadata_vm_retry(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            0,
            False,
        )
        with mock.patch("requests.get", throw(requests.exceptions.RequestException)):
            vm_result = metric._get_azure_compute_metadata()
            self.assertFalse(vm_result)
            self.assertEqual(len(metric._vm_data), 0)
            self.assertTrue(metric._vm_retry)

    # pylint: disable=protected-access
    def test_get_feature_metric_meet_threshold(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            2,
            False,
        )
        metric._long_interval_count_map[_FEATURE_METRIC_NAME[0]] = 2
        observations = metric._get_feature_metric(options=None)
        self.assertEqual(len(observations), 1)
        self.assertEqual(metric._long_interval_count_map[_FEATURE_METRIC_NAME[0]], 0)

    # pylint: disable=protected-access
    def test_get_feature_metric_does_not_meet_threshold(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            2,
            False,
        )
        metric._long_interval_count_map[_FEATURE_METRIC_NAME[0]] = 1
        observations = metric._get_feature_metric(options=None)
        self.assertEqual(len(observations), 0)
        self.assertEqual(metric._long_interval_count_map[_FEATURE_METRIC_NAME[0]], 1)

    # pylint: disable=protected-access
    def test_get_feature_metric_storage(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            0,
            False,
        )
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        attributes.update(_StatsbeatMetrics._FEATURE_ATTRIBUTES)
        self.assertEqual(attributes["feature"], _StatsbeatFeature.DISK_RETRY)
        self.assertEqual(attributes["type"], _FEATURE_TYPES.FEATURE)
        observations = metric._get_feature_metric(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 1)
            self.assertEqual(obs.attributes, attributes)

    # pylint: disable=protected-access
    def test_get_feature_metric_none(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            True,
            0,
            False,
        )
        self.assertEqual(_StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"], 0)
        observations = metric._get_feature_metric(options=None)
        self.assertEqual(len(observations), 0)
        self.assertEqual(_StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"], 0)

    # pylint: disable=protected-access
    def test_get_feature_metric_aad(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(mp, ikey, endpoint, True, 0, True)
        self.assertEqual(_StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"], _StatsbeatFeature.AAD)
        observations = metric._get_feature_metric(options=None)
        self.assertEqual(len(observations), 1)
        self.assertEqual(_StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"], _StatsbeatFeature.AAD)

    # pylint: disable=protected-access
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics.get_statsbeat_custom_events_feature_set"
    )
    def test_get_feature_metric_custom_events(self, feature_mock):
        feature_mock.return_value = True
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            True,
            0,
            False,
        )
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        attributes.update(_StatsbeatMetrics._FEATURE_ATTRIBUTES)
        self.assertEqual(attributes["feature"], 4)
        self.assertEqual(attributes["type"], _FEATURE_TYPES.FEATURE)
        observations = metric._get_feature_metric(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 1)
            self.assertEqual(obs.attributes, attributes)

    # pylint: disable=protected-access
    def test_get_feature_metric_custom_events_runtime(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        _STATSBEAT_STATE["CUSTOM_EVENTS_FEATURE_SET"] = False
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            True,
            0,
            False,
        )
        self.assertTrue((metric._feature >> 2) & 1 == 0)
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        attributes.update(_StatsbeatMetrics._FEATURE_ATTRIBUTES)
        self.assertEqual(attributes["feature"], 0)
        self.assertEqual(attributes["type"], _FEATURE_TYPES.FEATURE)
        _STATSBEAT_STATE["CUSTOM_EVENTS_FEATURE_SET"] = True
        observations = metric._get_feature_metric(options=None)
        attributes["feature"] = _StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"]
        for obs in observations:
            self.assertEqual(obs.value, 1)
            self.assertEqual(obs.attributes, attributes)
        self.assertTrue((_StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"] >> 2) & 1 == 1)
        _STATSBEAT_STATE["CUSTOM_EVENTS_FEATURE_SET"] = False

    # pylint: disable=protected-access
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics.get_statsbeat_live_metrics_feature_set"
    )
    def test_get_feature_metric_live_metrics(self, feature_mock):
        feature_mock.return_value = True
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            True,
            0,
            False,
        )
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        attributes.update(_StatsbeatMetrics._FEATURE_ATTRIBUTES)
        self.assertEqual(attributes["feature"], 16)
        self.assertEqual(attributes["type"], _FEATURE_TYPES.FEATURE)
        observations = metric._get_feature_metric(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 1)
            self.assertEqual(obs.attributes, attributes)

    # pylint: disable=protected-access
    def test_get_feature_metric_live_metrics_runtime(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        _STATSBEAT_STATE["LIVE_METRICS_FEATURE_SET"] = False
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            True,
            0,
            False,
        )
        self.assertTrue((metric._feature >> 4) & 1 == 0)
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        attributes.update(_StatsbeatMetrics._FEATURE_ATTRIBUTES)
        self.assertEqual(attributes["feature"], 0)
        self.assertEqual(attributes["type"], _FEATURE_TYPES.FEATURE)
        _STATSBEAT_STATE["LIVE_METRICS_FEATURE_SET"] = True
        observations = metric._get_feature_metric(options=None)
        attributes["feature"] = _StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"]
        for obs in observations:
            self.assertEqual(obs.value, 1)
            self.assertEqual(obs.attributes, attributes)
        self.assertTrue((_StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"] >> 4) & 1 == 1)
        _STATSBEAT_STATE["LIVE_METRICS_FEATURE_SET"] = False

    # pylint: disable=protected-access
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics.get_statsbeat_customer_sdkstats_feature_set"
    )
    def test_get_feature_metric_customer_sdkstats(self, feature_mock):
        feature_mock.return_value = True
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            True,
            0,
            False,
        )
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        attributes.update(_StatsbeatMetrics._FEATURE_ATTRIBUTES)
        self.assertEqual(attributes["feature"], 32)
        self.assertEqual(attributes["type"], _FEATURE_TYPES.FEATURE)
        observations = metric._get_feature_metric(options=None)
        for obs in observations:
            self.assertEqual(obs.value, 1)
            self.assertEqual(obs.attributes, attributes)

    # pylint: disable=protected-access
    def test_get_feature_metric_customer_sdkstats_runtime(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        _STATSBEAT_STATE["CUSTOMER_SDKSTATS_FEATURE_SET"] = False
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            True,
            0,
            False,
        )
        self.assertTrue((metric._feature >> 5) & 1 == 0)
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        attributes.update(_StatsbeatMetrics._FEATURE_ATTRIBUTES)
        self.assertEqual(attributes["feature"], 0)
        self.assertEqual(attributes["type"], _FEATURE_TYPES.FEATURE)
        _STATSBEAT_STATE["CUSTOMER_SDKSTATS_FEATURE_SET"] = True
        observations = metric._get_feature_metric(options=None)
        attributes["feature"] = _StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"]
        for obs in observations:
            self.assertEqual(obs.value, 1)
            self.assertEqual(obs.attributes, attributes)
        self.assertTrue((_StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"] >> 5) & 1 == 1)
        _STATSBEAT_STATE["CUSTOMER_SDKSTATS_FEATURE_SET"] = False

    # pylint: disable=protected-access
    def test_get_feature_metric_distro(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(mp, ikey, endpoint, True, 0, False, "1.0.0")
        self.assertEqual(_StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"], _StatsbeatFeature.DISTRO)
        observations = metric._get_feature_metric(options=None)
        self.assertEqual(len(observations), 1)
        self.assertEqual(_StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"], _StatsbeatFeature.DISTRO)

    # pylint: disable=protected-access
    def test_get_feature_metric_instrumentation(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            0,
            False,
        )
        metric._feature = _StatsbeatFeature.NONE
        _StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"] = _StatsbeatFeature.NONE
        set_statsbeat_feature_attribute_bits(_StatsbeatFeature.NONE)
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        attributes.update(_StatsbeatMetrics._INSTRUMENTATION_ATTRIBUTES)
        self.assertEqual(attributes["type"], _FEATURE_TYPES.INSTRUMENTATION)
        self.assertEqual(attributes["feature"], 0)
        with mock.patch("azure.monitor.opentelemetry.exporter._utils.get_instrumentations") as instrumentations:
            instrumentations.return_value = 1026
            observations = metric._get_feature_metric(options=None)
        self.assertEqual(
            _StatsbeatMetrics._INSTRUMENTATION_ATTRIBUTES["feature"],
            1026,
        )
        attributes["feature"] = 1026
        for obs in observations:
            self.assertEqual(obs.value, 1)
            self.assertEqual(obs.attributes, attributes)
        self.assertEqual(_StatsbeatMetrics._INSTRUMENTATION_ATTRIBUTES["feature"], 1026)

    # pylint: disable=protected-access
    def test_get_feature_metric_instrumentation_none(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            0,
            False,
        )
        metric._feature = _StatsbeatFeature.NONE
        _StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"] = _StatsbeatFeature.NONE
        set_statsbeat_feature_attribute_bits(_StatsbeatFeature.NONE)
        self.assertEqual(_StatsbeatMetrics._INSTRUMENTATION_ATTRIBUTES["feature"], 0)
        with mock.patch("azure.monitor.opentelemetry.exporter._utils.get_instrumentations") as instrumentations:
            instrumentations.return_value = 0
            observations = metric._get_feature_metric(options=None)
        self.assertEqual(len(observations), 0)
        self.assertEqual(_StatsbeatMetrics._INSTRUMENTATION_ATTRIBUTES["feature"], 0)

    def test_init_non_initial_metrics(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            0,
            False,
        )
        metric.init_non_initial_metrics()
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
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            0,
            False,
        )
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["statusCode"] = 200
        _REQUESTS_MAP[_REQ_SUCCESS_NAME[1]] = 3
        for count in metric._long_interval_count_map.values():
            self.assertEqual(count, sys.maxsize)
        observations = metric._get_success_count(options=None)
        for count in metric._long_interval_count_map.values():
            self.assertEqual(count, sys.maxsize + 1)
        for obs in observations:
            self.assertEqual(obs.value, 3)
            self.assertEqual(obs.attributes, attributes)
            self.assertEqual(_REQUESTS_MAP[_REQ_SUCCESS_NAME[1]], 0)

    def test_get_success_zero_value(self):
        mp = MeterProvider()
        ikey = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        metric = _StatsbeatMetrics(
            mp,
            ikey,
            endpoint,
            False,
            0,
            False,
        )
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["statusCode"] = 200
        _REQUESTS_MAP[_REQ_SUCCESS_NAME[1]] = 0
        for count in metric._long_interval_count_map.values():
            self.assertEqual(count, sys.maxsize)
        observations = metric._get_success_count(options=None)
        for count in metric._long_interval_count_map.values():
            self.assertEqual(count, sys.maxsize + 1)
        self.assertEqual(len(observations), 0)

    def test_get_average_duration(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        _REQUESTS_MAP[_REQ_DURATION_NAME[1]] = 10.0
        _REQUESTS_MAP["count"] = 4
        observations = self._metric._get_average_duration(options=None)
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
        observations = self._metric._get_average_duration(options=None)
        self.assertEqual(len(observations), 0)

    def test_get_failure_count(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["statusCode"] = 400
        _REQUESTS_MAP[_REQ_FAILURE_NAME[1]] = {}
        _REQUESTS_MAP[_REQ_FAILURE_NAME[1]][400] = 3
        observations = self._metric._get_failure_count(options=None)
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
        observations = self._metric._get_failure_count(options=None)
        self.assertEqual(len(observations), 0)

    def test_get_retry_count(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["statusCode"] = 500
        _REQUESTS_MAP[_REQ_RETRY_NAME[1]] = {}
        _REQUESTS_MAP[_REQ_RETRY_NAME[1]][500] = 3
        observations = self._metric._get_retry_count(options=None)
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
        observations = self._metric._get_retry_count(options=None)
        self.assertEqual(len(observations), 0)

    def test_get_throttle_count(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["statusCode"] = 402
        _REQUESTS_MAP[_REQ_THROTTLE_NAME[1]] = {}
        _REQUESTS_MAP[_REQ_THROTTLE_NAME[1]][402] = 3
        observations = self._metric._get_throttle_count(options=None)
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
        observations = self._metric._get_throttle_count(options=None)
        self.assertEqual(len(observations), 0)

    def test_get_exception_count(self):
        attributes = _StatsbeatMetrics._COMMON_ATTRIBUTES
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["exceptionType"] = "Exception"
        _REQUESTS_MAP[_REQ_EXCEPTION_NAME[1]] = {}
        _REQUESTS_MAP[_REQ_EXCEPTION_NAME[1]]["Exception"] = 3
        observations = self._metric._get_exception_count(options=None)
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
        observations = self._metric._get_exception_count(options=None)
        self.assertEqual(len(observations), 0)

    def test_shorten_host(self):
        url = "https://fakehost-1.example.com/"
        self.assertEqual(_shorten_host(url), "fakehost-1")
        url = "https://fakehost-2.example.com/"
        self.assertEqual(_shorten_host(url), "fakehost-2")
        url = "http://www.fakehost-3.example.com/"
        self.assertEqual(_shorten_host(url), "fakehost-3")
        url = "http://www.fakehost.com/v2/track"
        self.assertEqual(_shorten_host(url), "fakehost")
        url = "https://www.fakehost0-4.com/"
        self.assertEqual(_shorten_host(url), "fakehost0-4")
        url = "https://www.fakehost-5.com"
        self.assertEqual(_shorten_host(url), "fakehost-5")
        url = "https://fakehost.com"
        self.assertEqual(_shorten_host(url), "fakehost")
        url = "http://fakehost-5/"
        self.assertEqual(_shorten_host(url), "fakehost-5")


# pylint: disable=protected-access
class TestAdditionalObservationCallbacks(unittest.TestCase):
    """Tests for statsbeat callback registration and _get_additional_observations."""

    def setUp(self):
        _REQUESTS_MAP.clear()
        # Force a fresh StatsbeatManager so its __init__ runs again (which
        # rebuilds an empty _additional_callbacks dict on the instance).
        StatsbeatManager._instances.pop(StatsbeatManager, None)

    def tearDown(self):
        _REQUESTS_MAP.clear()
        StatsbeatManager._instances.pop(StatsbeatManager, None)

    @staticmethod
    def _register(metric_name, callback):
        StatsbeatManager().add_additional_metric_callbacks(metric_name, callback)

    def _make_metric(self):
        return _StatsbeatMetrics(
            MeterProvider(),
            "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334",
            "https://westus-1.in.applicationinsights.azure.com/",
            False,
            0,
            False,
        )

    # ---- _get_additional_observations ----

    def test_get_unregistered_name_returns_empty(self):
        self.assertEqual(_get_additional_observations(_REQ_SUCCESS_NAME[0], None), [])

    def test_get_returns_observations_from_registered_callback(self):
        obs = Observation(7, {"endpoint": "ep1"})

        def cb(_options):
            yield obs

        self._register(_REQ_SUCCESS_NAME[0], cb)
        self.assertEqual(_get_additional_observations(_REQ_SUCCESS_NAME[0], None), [obs])

    def test_get_aggregates_across_multiple_callbacks(self):
        obs1 = Observation(1, {"endpoint": "ep1"})
        obs2 = Observation(2, {"endpoint": "ep2"})
        self._register(_REQ_SUCCESS_NAME[0], lambda _options: [obs1])
        self._register(_REQ_SUCCESS_NAME[0], lambda _options: [obs2])
        self.assertEqual(
            _get_additional_observations(_REQ_SUCCESS_NAME[0], None),
            [obs1, obs2],
        )

    def test_get_swallows_callback_exception_and_continues(self):
        good_obs = Observation(42, {"endpoint": "ok"})

        def bad_cb(_options):
            raise RuntimeError("boom")

        self._register(_REQ_SUCCESS_NAME[0], bad_cb)
        self._register(_REQ_SUCCESS_NAME[0], lambda _options: [good_obs])
        # Should not raise; should still emit the good observation.
        self.assertEqual(
            _get_additional_observations(_REQ_SUCCESS_NAME[0], None),
            [good_obs],
        )

    def test_get_callbacks_for_other_metrics_not_invoked(self):
        called = []
        self._register(_REQ_FAILURE_NAME[0], lambda _options: called.append("failure") or [])
        _get_additional_observations(_REQ_SUCCESS_NAME[0], None)
        self.assertEqual(called, [])

    # ---- integration with built-in callbacks ----

    def test_success_count_callback_emits_extras(self):
        metric = self._make_metric()
        _REQUESTS_MAP[_REQ_SUCCESS_NAME[1]] = 5

        extra = Observation(99, {"endpoint": "extra-ep", "statusCode": 200})
        self._register(_REQ_SUCCESS_NAME[0], lambda _options: [extra])

        observations = metric._get_success_count(options=None)

        # Built-in observation followed by the extra one.
        self.assertEqual(len(observations), 2)
        self.assertEqual(observations[0].value, 5)
        self.assertIs(observations[-1], extra)

    def test_success_count_callback_unchanged_without_extras(self):
        metric = self._make_metric()
        _REQUESTS_MAP[_REQ_SUCCESS_NAME[1]] = 3

        observations = metric._get_success_count(options=None)

        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].value, 3)

    def test_extras_for_other_metric_do_not_leak_into_success(self):
        metric = self._make_metric()
        _REQUESTS_MAP[_REQ_SUCCESS_NAME[1]] = 1

        unrelated = Observation(123, {"endpoint": "other"})
        self._register(_REQ_FAILURE_NAME[0], lambda _options: [unrelated])

        observations = metric._get_success_count(options=None)

        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].value, 1)
        self.assertNotIn(unrelated, observations)


# cSpell:enable
