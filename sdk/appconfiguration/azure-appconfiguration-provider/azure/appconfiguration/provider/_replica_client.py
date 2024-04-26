# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import logging
import json
import time
import random
from dataclasses import dataclass
from typing import Tuple, Union, Dict
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.appconfiguration import (  # type:ignore # pylint:disable=no-name-in-module
    ConfigurationSetting,
    AzureAppConfigurationClient,
    FeatureFlagConfigurationSetting,
)
from ._constants import FEATURE_FLAG_PREFIX


@dataclass
class ReplicaClient:
    endpoint: str
    _client: AzureAppConfigurationClient
    backoff_end_time: int = 0
    failed_attempts: int = 0

    @classmethod
    def from_credential(cls, endpoint, credential, user_agent, retry_total, retry_backoff_max, **kwargs):
        return cls(
            endpoint,
            AzureAppConfigurationClient(
                endpoint,
                credential,
                user_agent=user_agent,
                retry_total=retry_total,
                retry_backoff_max=retry_backoff_max,
                **kwargs
            ),
        )

    @classmethod
    def from_connection_string(cls, endpoint, connection_string, user_agent, retry_total, retry_backoff_max, **kwargs):
        return cls(
            endpoint,
            AzureAppConfigurationClient.from_connection_string(
                connection_string,
                user_agent=user_agent,
                retry_total=retry_total,
                retry_backoff_max=retry_backoff_max,
                **kwargs
            ),
        )

    def _check_configuration_setting(
        self, key, label, etag, headers, **kwargs
    ) -> Tuple[bool, Union[ConfigurationSetting, None]]:
        """
        Checks if the configuration setting have been updated since the last refresh.

        :keyword key: key to check for chances
        :paramtype key: str
        :keyword label: label to check for changes
        :paramtype label: str
        :keyword etag: etag to check for changes
        :paramtype etag: str
        :keyword headers: headers to use for the request
        :paramtype headers: Mapping[str, str]
        :return: A tuple with the first item being true/false if a change is detected. The second item is the updated
        value if a change was detected.
        :rtype: Tuple[bool, Union[ConfigurationSetting, None]]
        """
        try:
            updated_sentinel = self._client.get_configuration_setting(  # type: ignore
                key=key, label=label, etag=etag, match_condition=MatchConditions.IfModified, headers=headers, **kwargs
            )
            if updated_sentinel is not None:
                logging.debug(
                    "Refresh all triggered by key: %s label %s.",
                    key,
                    label,
                )
                return True, updated_sentinel
        except HttpResponseError as e:
            if e.status_code == 404:
                if etag is not None:
                    # If the sentinel is not found, it means the key/label was deleted, so we should refresh
                    logging.debug("Refresh all triggered by key: %s label %s.", key, label)
                    return True, None
            else:
                raise e
        return False, None

    def _load_configuration_settings(self, selects, refresh_on, **kwargs):
        configuration_settings = []
        sentinel_keys = kwargs.pop("sentinel_keys", refresh_on)
        for select in selects:
            configurations = self._client.list_configuration_settings(
                key_filter=select.key_filter, label_filter=select.label_filter, **kwargs
            )
            for config in configurations:
                if isinstance(config, FeatureFlagConfigurationSetting):
                    # Feature flags are ignored when loaded by Selects, as they are selected from
                    # `feature_flag_selectors`
                    pass
                else:
                    configuration_settings.append(config)
                # Every time we run load_all, we should update the etag of our refresh sentinels
                # so they stay up-to-date.
                # Sentinel keys will have unprocessed key names, so we need to use the original key.
                if (config.key, config.label) in refresh_on:
                    sentinel_keys[(config.key, config.label)] = config.etag
        return configuration_settings, sentinel_keys

    def _load_feature_flags(self, feature_flag_selectors, feature_flag_refresh_enabled, **kwargs):
        feature_flag_sentinel_keys = {}
        loaded_feature_flags = []
        # Needs to be removed unknown keyword argument for list_configuration_settings
        kwargs.pop("sentinel_keys", None)
        for select in feature_flag_selectors:
            feature_flags = self._client.list_configuration_settings(
                key_filter=FEATURE_FLAG_PREFIX + select.key_filter, label_filter=select.label_filter, **kwargs
            )
            for feature_flag in feature_flags:
                loaded_feature_flags.append(json.loads(feature_flag.value))

                if feature_flag_refresh_enabled:
                    feature_flag_sentinel_keys[(feature_flag.key, feature_flag.label)] = feature_flag.etag
        return loaded_feature_flags, feature_flag_sentinel_keys

    def refresh_configuration_settings(self, selects, refresh_on, headers, **kwargs) -> bool:
        need_refresh = False
        updated_sentinel_keys = dict(refresh_on)
        for (key, label), etag in updated_sentinel_keys.items():
            changed, updated_sentinel = self._check_configuration_setting(
                key=key, label=label, etag=etag, headers=headers, **kwargs
            )
            if changed:
                need_refresh = True
            if updated_sentinel is not None:
                updated_sentinel_keys[(key, label)] = updated_sentinel.etag
        # Need to only update once, no matter how many sentinels are updated
        if need_refresh:
            configuration_settings, sentinel_keys = self._load_configuration_settings(selects, refresh_on, **kwargs)
        return need_refresh, sentinel_keys, configuration_settings

    def refresh_feature_flags(self, refresh_on, feature_flag_selectors, headers, **kwargs) -> bool:
        feature_flag_sentinel_keys = dict(refresh_on)
        for (key, label), etag in feature_flag_sentinel_keys.items():
            changed = self._check_configuration_setting(key=key, label=label, etag=etag, headers=headers, **kwargs)
            if changed:
                feature_flags, feature_flag_sentinel_keys = self._load_feature_flags(
                    feature_flag_selectors, True, **kwargs
                )
                return True, feature_flag_sentinel_keys, feature_flags
        return False, None, None


class ReplicaClientManager:
    def __init__(self, replica_clients: Dict[str, ReplicaClient], min_backoff: int, max_backoff: int):
        self._replica_clients = replica_clients
        self._min_backoff = min_backoff
        self._max_backoff = max_backoff

    def get_active_clients(self):
        active_clients = []
        for client in self._replica_clients:
            if client.backoff_end_time <= time.time():
                active_clients.append(client)
        return active_clients

    def backoff(self, client: ReplicaClient):
        client.failed_attempts += 1
        backoff_time = self._calculate_backoff(client.failed_attempts)
        client.backoff_end_time = time.time() + backoff_time

    def _calculate_backoff(self, attempts) -> float:
        max_attempts = 63
        millisecond = 1000  # 1 Second in milliseconds

        min_backoff_milliseconds = self._min_backoff * millisecond
        max_backoff_milliseconds = self._max_backoff * millisecond

        if self._max_backoff <= self._min_backoff:
            return min_backoff_milliseconds

        calculated_milliseconds = max(1, min_backoff_milliseconds) * (1 << min(attempts, max_attempts))

        if calculated_milliseconds > max_backoff_milliseconds or calculated_milliseconds <= 0:
            calculated_milliseconds = max_backoff_milliseconds

        return min_backoff_milliseconds + (
            random.uniform(0.0, 1.0) * (calculated_milliseconds - min_backoff_milliseconds)
        )
