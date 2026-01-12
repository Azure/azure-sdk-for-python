# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import random
from dataclasses import dataclass
from typing import Optional, Mapping, Any

FALLBACK_CLIENT_REFRESH_EXPIRED_INTERVAL = 3600  # 1 hour in seconds
MINIMAL_CLIENT_REFRESH_INTERVAL = 30  # 30 seconds

JSON = Mapping[str, Any]


@dataclass
class _ConfigurationClientWrapperBase:
    endpoint: str


class ConfigurationClientManagerBase:  # pylint:disable=too-many-instance-attributes
    def __init__(
        self,
        endpoint: str,
        user_agent: str,
        retry_total,
        retry_backoff_max,
        replica_discovery_enabled,
        min_backoff_sec,
        max_backoff_sec,
        _load_balancing_enabled: bool,
        **kwargs,
    ):
        self._last_active_client_name = ""
        self._original_endpoint = endpoint
        self._user_agent = user_agent
        self._retry_total = retry_total
        self._retry_backoff_max = retry_backoff_max
        self._replica_discovery_enabled = replica_discovery_enabled
        self._next_update_time: Optional[float] = None
        self._args = dict(kwargs)
        self._min_backoff_sec = min_backoff_sec
        self._max_backoff_sec = max_backoff_sec
        self._load_balancing_enabled = _load_balancing_enabled

    def _calculate_backoff(self, attempts: int) -> float:
        max_attempts = 63
        ms_per_second = 1000  # 1 Second in milliseconds

        min_backoff_milliseconds = self._min_backoff_sec * ms_per_second
        max_backoff_milliseconds = self._max_backoff_sec * ms_per_second

        if self._max_backoff_sec <= self._min_backoff_sec:
            return min_backoff_milliseconds

        calculated_milliseconds = max(1, min_backoff_milliseconds) * (1 << min(attempts, max_attempts))

        if calculated_milliseconds > max_backoff_milliseconds or calculated_milliseconds <= 0:
            calculated_milliseconds = max_backoff_milliseconds

        return min_backoff_milliseconds + (
            random.uniform(0.0, 1.0) * (calculated_milliseconds - min_backoff_milliseconds)  # nosec
        )
