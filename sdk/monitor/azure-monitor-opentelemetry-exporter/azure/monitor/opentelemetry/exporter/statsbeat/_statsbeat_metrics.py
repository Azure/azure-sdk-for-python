# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import platform
import re
from typing import Iterable

from opentelemetry.metrics import CallbackOptions, MeterProvider, Observation

from azure.monitor.opentelemetry.exporter import VERSION
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _REQ_SUCCESS_NAME,
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
        interval_count = _REQUESTS_MAP.get(_REQ_SUCCESS_NAME[1], 0)
        _REQUESTS_MAP[_REQ_SUCCESS_NAME[1]] = 0
        # only observe if value is not 0
        if interval_count != 0:
            observations.append(
                Observation(
                    int(interval_count),
                    attributes,
                )
            )
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

# cSpell:enable

def _shorten_host(host):
    if not host:
        host = ""
    match = _HOST_PATTERN.match(host)
    if match:
        host = match.group(1)
    return host
