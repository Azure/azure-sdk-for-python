# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import platform
import re
from typing import Iterable

from opentelemetry.metrics import CallbackOptions, MeterProvider, Observation

from azure.monitor.opentelemetry.exporter import VERSION
from azure.monitor.opentelemetry.exporter._constants import (
    _REQ_DURATION_NAME,
    _REQ_EXCEPTION_NAME,
    _REQ_FAILURE_NAME,
    _REQ_RETRY_NAME,
    _REQ_SUCCESS_NAME,
    _REQ_THROTTLE_NAME,
)
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _REQUESTS_LOCK,
    _REQUESTS_MAP,
)


_ENDPOINT_TYPES = ["breeze"]
_RP_NAMES = ["appsvc", "functions", "vm", "unknown"]

_HOST_PATTERN = re.compile('^https?://(?:www\\.)?([^/.]+)')

# cSpell:disable

# pylint: disable=unused-argument
# pylint: disable=protected-access
def _get_success_count(options: CallbackOptions) -> Iterable[Observation]:
    observations = []
    attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
    attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
    attributes["statusCode"] = 200
    with _REQUESTS_LOCK:
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
def _get_failure_count(options: CallbackOptions) -> Iterable[Observation]:
    observations = []
    attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
    attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
    with _REQUESTS_LOCK:
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
def _get_average_duration(options: CallbackOptions) -> Iterable[Observation]:
    observations = []
    attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
    attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
    with _REQUESTS_LOCK:
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
def _get_retry_count(options: CallbackOptions) -> Iterable[Observation]:
    observations = []
    attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
    attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
    with _REQUESTS_LOCK:
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
def _get_throttle_count(options: CallbackOptions) -> Iterable[Observation]:
    observations = []
    attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
    attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
    with _REQUESTS_LOCK:
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
def _get_exception_count(options: CallbackOptions) -> Iterable[Observation]:
    observations = []
    attributes = dict(_StatsbeatMetrics._COMMON_ATTRIBUTES)
    attributes.update(_StatsbeatMetrics._NETWORK_ATTRIBUTES)
    with _REQUESTS_LOCK:
        for code, count in _REQUESTS_MAP.get(_REQ_EXCEPTION_NAME[1], {}).items():
            # only observe if value is not 0
            if count != 0:
                attributes["exceptionType"] = code
                observations.append(
                    Observation(int(count), dict(attributes))
                )
                _REQUESTS_MAP[_REQ_EXCEPTION_NAME[1]][code] = 0
    return observations


class _StatsbeatMetrics:

    _COMMON_ATTRIBUTES = {
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

    def __init__(
        self,
        meter_provider: MeterProvider,
        instrumentation_key: str,
        endpoint: str,
    ) -> None:
        self._mp = meter_provider
        self._ikey = instrumentation_key
        _StatsbeatMetrics._COMMON_ATTRIBUTES["cikey"] = instrumentation_key
        _StatsbeatMetrics._NETWORK_ATTRIBUTES["host"] = _shorten_host(endpoint)
        self._rp = _RP_NAMES[3]
        meter = meter_provider.get_meter(__name__)

        # Network metrics - metrics related to request calls to ingestion service
        self._success_count = meter.create_observable_gauge(
            _REQ_SUCCESS_NAME[0],
            callbacks=[_get_success_count],
            unit="count",
            description="Statsbeat metric tracking request success count"
        )
        self._failure_count = meter.create_observable_gauge(
            _REQ_FAILURE_NAME[0],
            callbacks=[_get_failure_count],
            unit="count",
            description="Statsbeat metric tracking request failure count"
        )
        self._retry_count = meter.create_observable_gauge(
            _REQ_RETRY_NAME[0],
            callbacks=[_get_retry_count],
            unit="count",
            description="Statsbeat metric tracking request retry count"
        )
        self._throttle_count = meter.create_observable_gauge(
            _REQ_THROTTLE_NAME[0],
            callbacks=[_get_throttle_count],
            unit="count",
            description="Statsbeat metric tracking request throttle count"
        )
        self._exception_count = meter.create_observable_gauge(
            _REQ_EXCEPTION_NAME[0],
            callbacks=[_get_exception_count],
            unit="count",
            description="Statsbeat metric tracking request exception count"
        )
        self._average_duration = meter.create_observable_gauge(
            _REQ_DURATION_NAME[0],
            callbacks=[_get_average_duration],
            unit="avg",
            description="Statsbeat metric tracking average request duration"
        )

# cSpell:enable

def _shorten_host(host):
    if not host:
        host = ""
    match = _HOST_PATTERN.match(host)
    if match:
        host = match.group(1)
    return host
