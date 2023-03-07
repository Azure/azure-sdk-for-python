# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
import os
import platform
import re
import sys
import threading
from typing import Iterable

import requests

from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry.sdk.metrics import MeterProvider

from azure.monitor.opentelemetry.exporter import VERSION
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
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _REQUESTS_MAP_LOCK,
    _REQUESTS_MAP,
)
from azure.monitor.opentelemetry.exporter import _utils

# cSpell:disable

_AIMS_URI = "http://169.254.169.254/metadata/instance/compute"
_AIMS_API_VERSION = "api-version=2017-12-01"
_AIMS_FORMAT = "format=json"

_ENDPOINT_TYPES = ["breeze"]
_RP_NAMES = ["appsvc", "functions", "vm", "unknown"]

_HOST_PATTERN = re.compile('^https?://(?:www\\.)?([^/.]+)')


class _FEATURE_TYPES:
    FEATURE = 0
    INSTRUMENTATION = 1


class _StatsbeatFeature:
    NONE = 0
    DISK_RETRY = 1
    AAD = 2


# pylint: disable=R0902
class _StatsbeatMetrics:

    _COMMON_ATTRIBUTES = {
        "rp": _RP_NAMES[3],
        "attach": "sdk", # TODO: attach
        "cikey": None,
        "runtimeVersion": platform.python_version(),
        "os": platform.system(),
        "language": "Python",
        "version": VERSION
    }

    _NETWORK_ATTRIBUTES = {
        "endpoint": _ENDPOINT_TYPES[0],  # breeze
        "host": None,
    }

    _FEATURE_ATTRIBUTES = {
        "feature": None,  # 64-bit long, bits represent features enabled
        "type": _FEATURE_TYPES.FEATURE,
    }

    _INSTRUMENTATION_ATTRIBUTES = {
        "feature": 0,  # 64-bit long, bits represent instrumentations used
        "type": _FEATURE_TYPES.INSTRUMENTATION,
    }

    def __init__(
        self,
        meter_provider: MeterProvider,
        instrumentation_key: str,
        endpoint: str,
        disable_offline_storage: bool,
        long_interval_threshold: int,
        has_credential: bool,
    ) -> None:
        self._ikey = instrumentation_key
        self._feature = _StatsbeatFeature.NONE
        if not disable_offline_storage:
            self._feature |= _StatsbeatFeature.DISK_RETRY
        if has_credential:
            self._feature |= _StatsbeatFeature.AAD
        self._ikey = instrumentation_key
        self._meter = meter_provider.get_meter(__name__)
        self._long_interval_threshold = long_interval_threshold
        # Start internal count at the max size for initial statsbeat export
        self._long_interval_count_map = {
            _ATTACH_METRIC_NAME[0]: sys.maxsize,
            _FEATURE_METRIC_NAME[0]: sys.maxsize,
        }
        self._long_interval_lock = threading.Lock()
        _StatsbeatMetrics._COMMON_ATTRIBUTES["cikey"] = instrumentation_key
        _StatsbeatMetrics._NETWORK_ATTRIBUTES["host"] = _shorten_host(endpoint)
        _StatsbeatMetrics._FEATURE_ATTRIBUTES["feature"] = self._feature
        _StatsbeatMetrics._INSTRUMENTATION_ATTRIBUTES["feature"] = _utils.get_instrumentations()

        self._vm_retry = True  # True if we want to attempt to find if in VM
        self._vm_data = {}

        # Initial metrics - metrics exported on application start

        # Attach metrics - metrics related to identifying which rp is application being run in
        self._attach_metric = self._meter.create_observable_gauge(
            _ATTACH_METRIC_NAME[0],
            callbacks=[self._get_attach_metric],
            unit="",
            description="Statsbeat metric tracking tracking rp information"
        )

        # Feature metrics - metrics related to features/instrumentations being used
        self._feature_metric = self._meter.create_observable_gauge(
            _FEATURE_METRIC_NAME[0],
            callbacks=[self._get_feature_metric],
            unit="",
            description="Statsbeat metric tracking tracking enabled features"
        )

    # pylint: disable=unused-argument
    # pylint: disable=protected-access
    def _get_attach_metric(self, options: CallbackOptions) -> Iterable[Observation]:
        observations = []
        # Check if it is time to observe long interval metrics
        if not self._meets_long_interval_threshold(_ATTACH_METRIC_NAME[0]):
            return observations
        rp = ''
        rpId = ''
        os_type = platform.system()
        # rp, rpId
        if os.environ.get("WEBSITE_SITE_NAME") is not None:
            # Web apps
            rp = _RP_NAMES[0]
            rpId = '{}/{}'.format(
                        os.environ.get("WEBSITE_SITE_NAME"),
                        os.environ.get("WEBSITE_HOME_STAMPNAME", '')
            )
        elif os.environ.get("FUNCTIONS_WORKER_RUNTIME") is not None:
            # Function apps
            rp = _RP_NAMES[1]
            rpId = os.environ.get("WEBSITE_HOSTNAME")
        elif self._vm_retry and self._get_azure_compute_metadata():
            # VM
            rp = _RP_NAMES[2]
            rpId = '{}/{}'.format(
                        self._vm_data.get("vmId", ''),
                        self._vm_data.get("subscriptionId", ''))
            os_type = self._vm_data.get("osType", '')
        else:
            # Not in any rp or VM metadata failed
            rp = _RP_NAMES[3]
            rpId = _RP_NAMES[3]

        _StatsbeatMetrics._COMMON_ATTRIBUTES["rp"] = rp
        _StatsbeatMetrics._COMMON_ATTRIBUTES["os"] = os_type or platform.system()
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        attributes['rpId'] = rpId
        observations.append(Observation(1, dict(attributes)))
        return observations

    def _get_azure_compute_metadata(self) -> bool:
        try:
            request_url = "{0}?{1}&{2}".format(
                _AIMS_URI, _AIMS_API_VERSION, _AIMS_FORMAT)
            response = requests.get(
                request_url, headers={"MetaData": "True"}, timeout=5.0)
        except (requests.exceptions.ConnectionError, requests.Timeout):
            # Not in VM
            self._vm_retry = False
            return False
        except requests.exceptions.RequestException:
            self._vm_retry = True  # retry
            return False

        try:
            text = response.text
            self._vm_data = json.loads(text)
        except Exception:  # pylint: disable=broad-except
            # Error in reading response body, retry
            self._vm_retry = True
            return False

        # Vm data is perpetually updated
        self._vm_retry = True
        return True

    # pylint: disable=unused-argument
    # pylint: disable=protected-access
    def _get_feature_metric(self, options: CallbackOptions) -> Iterable[Observation]:
        observations = []
        # Check if it is time to observe long interval metrics
        if not self._meets_long_interval_threshold(_FEATURE_METRIC_NAME[0]):
            return observations
        # Feature metric
        # Don't send observation if no features enabled
        if self._feature is not _StatsbeatFeature.NONE:
            attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
            attributes.update(_StatsbeatMetrics._FEATURE_ATTRIBUTES)
            observations.append(Observation(1, dict(attributes)))

        # instrumentation metric
        # Don't send observation if no instrumentations enabled
        instrumentation_bits = _utils.get_instrumentations()
        if instrumentation_bits != 0:
            _StatsbeatMetrics._INSTRUMENTATION_ATTRIBUTES["feature"] = instrumentation_bits
            attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
            attributes.update(_StatsbeatMetrics._INSTRUMENTATION_ATTRIBUTES)
            observations.append(Observation(1, dict(attributes)))

        return observations

    def _meets_long_interval_threshold(self, name) -> bool:
        with self._long_interval_lock:
            # if long interval theshold not met, it is not time to export
            # statsbeat metrics that are long intervals
            count = self._long_interval_count_map.get(name, sys.maxsize)
            if count < self._long_interval_threshold:
                return False
            # reset the count if long interval theshold is met
            self._long_interval_count_map[name] = 0
            return True

    # pylint: disable=W0201
    def init_non_initial_metrics(self):
        # Network metrics - metrics related to request calls to ingestion service
        self._success_count = self._meter.create_observable_gauge(
            _REQ_SUCCESS_NAME[0],
            callbacks=[self._get_success_count],
            unit="count",
            description="Statsbeat metric tracking request success count"
        )
        self._failure_count = self._meter.create_observable_gauge(
            _REQ_FAILURE_NAME[0],
            callbacks=[self._get_failure_count],
            unit="count",
            description="Statsbeat metric tracking request failure count"
        )
        self._retry_count = self._meter.create_observable_gauge(
            _REQ_RETRY_NAME[0],
            callbacks=[self._get_retry_count],
            unit="count",
            description="Statsbeat metric tracking request retry count"
        )
        self._throttle_count = self._meter.create_observable_gauge(
            _REQ_THROTTLE_NAME[0],
            callbacks=[self._get_throttle_count],
            unit="count",
            description="Statsbeat metric tracking request throttle count"
        )
        self._exception_count = self._meter.create_observable_gauge(
            _REQ_EXCEPTION_NAME[0],
            callbacks=[self._get_exception_count],
            unit="count",
            description="Statsbeat metric tracking request exception count"
        )
        self._average_duration = self._meter.create_observable_gauge(
            _REQ_DURATION_NAME[0],
            callbacks=[self._get_average_duration],
            unit="avg",
            description="Statsbeat metric tracking average request duration"
        )

    # pylint: disable=unused-argument
    # pylint: disable=protected-access
    def _get_success_count(self, options: CallbackOptions) -> Iterable[Observation]:
        # get_success_count is special in such that it is the indicator of when
        # a short interval collection has happened, which is why we increment
        # the long_interval_count when it is called
        with self._long_interval_lock:
            for name, count in self._long_interval_count_map.items():
                self._long_interval_count_map[name] = count + 1
        observations = []
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        attributes["statusCode"] = 200
        with _REQUESTS_MAP_LOCK:
            # only observe if value is not 0
            count = _REQUESTS_MAP.get(_REQ_SUCCESS_NAME[1], 0)
            if count != 0:
                observations.append(
                    Observation(int(count), dict(attributes))
                )
                _REQUESTS_MAP[_REQ_SUCCESS_NAME[1]] = 0
        return observations

    # pylint: disable=unused-argument
    # pylint: disable=protected-access
    # pylint: disable=no-self-use
    def _get_failure_count(self, options: CallbackOptions) -> Iterable[Observation]:
        observations = []
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        with _REQUESTS_MAP_LOCK:
            for code, count in _REQUESTS_MAP.get(_REQ_FAILURE_NAME[1], {}).items():
                # only observe if value is not 0
                if count != 0:
                    attributes["statusCode"] = code
                    observations.append(
                        Observation(int(count), dict(attributes))
                    )
                    _REQUESTS_MAP[_REQ_FAILURE_NAME[1]][code] = 0
        return observations

    # pylint: disable=unused-argument
    # pylint: disable=protected-access
    # pylint: disable=no-self-use
    def _get_average_duration(self, options: CallbackOptions) -> Iterable[Observation]:
        observations = []
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        with _REQUESTS_MAP_LOCK:
            interval_duration = _REQUESTS_MAP.get(_REQ_DURATION_NAME[1], 0)
            interval_count = _REQUESTS_MAP.get("count", 0)
            # only observe if value is not 0
            if interval_duration > 0 and interval_count > 0:
                result = interval_duration / interval_count
                observations.append(
                    Observation(result * 1000, dict(attributes))
                )
                _REQUESTS_MAP[_REQ_DURATION_NAME[1]] = 0
                _REQUESTS_MAP["count"] = 0
        return observations

    # pylint: disable=unused-argument
    # pylint: disable=protected-access
    # pylint: disable=no-self-use
    def _get_retry_count(self, options: CallbackOptions) -> Iterable[Observation]:
        observations = []
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        with _REQUESTS_MAP_LOCK:
            for code, count in _REQUESTS_MAP.get(_REQ_RETRY_NAME[1], {}).items():
                # only observe if value is not 0
                if count != 0:
                    attributes["statusCode"] = code
                    observations.append(
                        Observation(int(count), dict(attributes))
                    )
                    _REQUESTS_MAP[_REQ_RETRY_NAME[1]][code] = 0
        return observations

    # pylint: disable=unused-argument
    # pylint: disable=protected-access
    # pylint: disable=no-self-use
    def _get_throttle_count(self, options: CallbackOptions) -> Iterable[Observation]:
        observations = []
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        with _REQUESTS_MAP_LOCK:
            for code, count in _REQUESTS_MAP.get(_REQ_THROTTLE_NAME[1], {}).items():
                # only observe if value is not 0
                if count != 0:
                    attributes["statusCode"] = code
                    observations.append(
                        Observation(int(count), dict(attributes))
                    )
                    _REQUESTS_MAP[_REQ_THROTTLE_NAME[1]][code] = 0
        return observations

    # pylint: disable=unused-argument
    # pylint: disable=protected-access
    # pylint: disable=no-self-use
    def _get_exception_count(self, options: CallbackOptions) -> Iterable[Observation]:
        observations = []
        attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
        attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
        with _REQUESTS_MAP_LOCK:
            for code, count in _REQUESTS_MAP.get(_REQ_EXCEPTION_NAME[1], {}).items():
                # only observe if value is not 0
                if count != 0:
                    attributes["exceptionType"] = code
                    observations.append(
                        Observation(int(count), dict(attributes))
                    )
                    _REQUESTS_MAP[_REQ_EXCEPTION_NAME[1]][code] = 0
        return observations

# cSpell:enable

def _shorten_host(host: str) -> str:
    if not host:
        host = ""
    match = _HOST_PATTERN.match(host)
    if match:
        host = match.group(1)
    return host
