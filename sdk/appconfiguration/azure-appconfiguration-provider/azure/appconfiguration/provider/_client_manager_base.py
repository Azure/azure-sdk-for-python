# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import time
import random
from dataclasses import dataclass
from typing import Dict, List
from azure.appconfiguration import (  # type:ignore # pylint:disable=no-name-in-module
    FeatureFlagConfigurationSetting,
)
from ._constants import (
    PERCENTAGE_FILTER_NAMES,
    TIME_WINDOW_FILTER_NAMES,
    TARGETING_FILTER_NAMES,
    CUSTOM_FILTER_KEY,
    PERCENTAGE_FILTER_KEY,
    TIME_WINDOW_FILTER_KEY,
    TARGETING_FILTER_KEY,
)

FALLBACK_CLIENT_REFRESH_EXPIRED_INTERVAL = 3600  # 1 hour in seconds
MINIMAL_CLIENT_REFRESH_INTERVAL = 30  # 30 seconds


@dataclass
class _ConfigurationClientWrapperBase:
    endpoint: str

    def _feature_flag_telemetry(self, feature_flag: FeatureFlagConfigurationSetting, filters_used: Dict[str, bool]):
        if feature_flag.filters:
            for filter in feature_flag.filters:
                if filter.get("name") in PERCENTAGE_FILTER_NAMES:
                    filters_used[PERCENTAGE_FILTER_KEY] = True
                elif filter.get("name") in TIME_WINDOW_FILTER_NAMES:
                    filters_used[TIME_WINDOW_FILTER_KEY] = True
                elif filter.get("name") in TARGETING_FILTER_NAMES:
                    filters_used[TARGETING_FILTER_KEY] = True
                else:
                    filters_used[CUSTOM_FILTER_KEY] = True


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
        **kwargs
    ):
        self._replica_clients: List[_ConfigurationClientWrapperBase] = []
        self._original_endpoint = endpoint
        self._user_agent = user_agent
        self._retry_total = retry_total
        self._retry_backoff_max = retry_backoff_max
        self._replica_discovery_enabled = replica_discovery_enabled
        self._next_update_time = time.time() + MINIMAL_CLIENT_REFRESH_INTERVAL
        self._args = dict(kwargs)
        self._min_backoff_sec = min_backoff_sec
        self._max_backoff_sec = max_backoff_sec

    def get_active_clients(self):
        active_clients = []
        for client in self._replica_clients:
            if client.is_active():
                active_clients.append(client)
        return active_clients

    def get_client_count(self) -> int:
        return len(self._replica_clients)

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
            random.uniform(0.0, 1.0) * (calculated_milliseconds - min_backoff_milliseconds)
        )

    def __eq__(self, other):
        if len(self._replica_clients) != len(other._replica_clients):
            return False
        for i in range(len(self._replica_clients)):  # pylint:disable=consider-using-enumerate
            if self._replica_clients[i] != other._replica_clients[i]:
                return False
        return True
