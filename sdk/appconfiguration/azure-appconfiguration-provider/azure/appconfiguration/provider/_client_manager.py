# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from logging import getLogger
import time
import random
from dataclasses import dataclass
from typing import Tuple, Union, Dict, List, Optional, Mapping
from typing_extensions import Self
from azure.core import MatchConditions
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import HttpResponseError, AzureError
from azure.core.credentials import TokenCredential
from azure.appconfiguration import (  # type:ignore # pylint:disable=no-name-in-module
    ConfigurationSetting,
    AzureAppConfigurationClient,
    FeatureFlagConfigurationSetting,
    SnapshotComposition,
)
from ._client_manager_base import (
    _ConfigurationClientWrapperBase,
    ConfigurationClientManagerBase,
    FALLBACK_CLIENT_REFRESH_EXPIRED_INTERVAL,
    MINIMAL_CLIENT_REFRESH_INTERVAL,
)
from ._models import SettingSelector
from ._constants import FEATURE_FLAG_PREFIX
from ._discovery import find_auto_failover_endpoints
from ._snapshot_reference_parser import SnapshotReferenceParser
from ._constants import APP_CONFIG_SNAPSHOT_REF_MIME_PROFILE


@dataclass
class _ConfigurationClientWrapper(_ConfigurationClientWrapperBase):
    _client: AzureAppConfigurationClient
    backoff_end_time: float = 0
    failed_attempts: int = 0
    LOGGER = getLogger(__name__)

    @classmethod
    def from_credential(
        cls,
        endpoint: str,
        credential: TokenCredential,
        user_agent: str,
        retry_total: int,
        retry_backoff_max: int,
        **kwargs,
    ) -> Self:
        """
        Creates a new instance of the _ConfigurationClientWrapper class, using the provided credential to authenticate
        requests.

        :param str endpoint: The endpoint of the App Configuration store
        :param TokenCredential credential: The credential to use for authentication
        :param str user_agent: The user agent string to use for the request
        :param int retry_total: The total number of retries to allow for requests
        :param int retry_backoff_max: The maximum backoff time for retries
        :return: A new instance of the _ConfigurationClientWrapper class
        :rtype: _ConfigurationClientWrapper
        """
        return cls(
            endpoint,
            AzureAppConfigurationClient(
                endpoint,
                credential,
                user_agent=user_agent,
                retry_total=retry_total,
                retry_backoff_max=retry_backoff_max,
                **kwargs,
            ),
        )

    @classmethod
    def from_connection_string(
        cls, endpoint: str, connection_string: str, user_agent: str, retry_total: int, retry_backoff_max: int, **kwargs
    ) -> Self:
        """
        Creates a new instance of the _ConfigurationClientWrapper class, using the provided connection string to
        authenticate requests.

        :param str endpoint: The endpoint of the App Configuration store
        :param str connection_string: The connection string to use for authentication
        :param str user_agent: The user agent string to use for the request
        :param int retry_total: The total number of retries to allow for requests
        :param int retry_backoff_max: The maximum backoff time for retries
        :return: A new instance of the _ConfigurationClientWrapper class
        :rtype: _ConfigurationClientWrapper
        """
        return cls(
            endpoint,
            AzureAppConfigurationClient.from_connection_string(
                connection_string,
                user_agent=user_agent,
                retry_total=retry_total,
                retry_backoff_max=retry_backoff_max,
                **kwargs,
            ),
        )

    def _check_configuration_setting(
        self, key: str, label: str, etag: Optional[str], headers: Dict[str, str], **kwargs
    ) -> Tuple[bool, Union[ConfigurationSetting, None]]:
        """
        Checks if the configuration setting have been updated since the last refresh.

        :param str key: key to check for chances
        :param str label: label to check for changes
        :param str etag: etag to check for changes
        :param Mapping[str, str] headers: headers to use for the request
        :return: A tuple with the first item being true/false if a change is detected. The second item is the updated
        value if a change was detected.
        :rtype: Tuple[bool, Union[ConfigurationSetting, None]]
        """
        try:
            updated_watched_setting = self._client.get_configuration_setting(  # type: ignore
                key=key, label=label, etag=etag, match_condition=MatchConditions.IfModified, headers=headers, **kwargs
            )
            if updated_watched_setting is not None:
                self.LOGGER.debug(
                    "Refresh all triggered by key: %s label %s.",
                    key,
                    label,
                )
                return True, updated_watched_setting
        except HttpResponseError as e:
            if e.status_code == 404:
                if etag is not None:
                    # If the watched setting is not found, it means the key/label was deleted, so we should refresh
                    self.LOGGER.debug("Refresh all triggered by key: %s label %s.", key, label)
                    return True, None
            else:
                raise e
        return False, None

    @distributed_trace
    def load_configuration_settings(self, selects: List[SettingSelector], **kwargs) -> List[ConfigurationSetting]:
        configuration_settings = []
        for select in selects:
            if select.snapshot_name is not None:
                # When loading from a snapshot, ignore key_filter, label_filter, and tag_filters
                snapshot = self._client.get_snapshot(select.snapshot_name)
                if snapshot.composition_type != SnapshotComposition.KEY:
                    raise ValueError(f"Snapshot '{select.snapshot_name}' is not a key snapshot.")
                configurations = self._client.list_configuration_settings(snapshot_name=select.snapshot_name, **kwargs)
            else:
                # Use traditional filtering when not loading from a snapshot
                configurations = self._client.list_configuration_settings(
                    key_filter=select.key_filter,
                    label_filter=select.label_filter,
                    tags_filter=select.tag_filters,
                    **kwargs,
                )
            for config in configurations:
                if not isinstance(config, FeatureFlagConfigurationSetting):
                    # Feature flags are ignored when loaded by Selects, as they are selected from
                    # `feature_flag_selectors`
                    configuration_settings.append(config)
        return configuration_settings

    @distributed_trace
    def load_feature_flags(
        self, feature_flag_selectors: List[SettingSelector], **kwargs
    ) -> List[FeatureFlagConfigurationSetting]:
        loaded_feature_flags = []
        # Needs to be removed unknown keyword argument for list_configuration_settings
        kwargs.pop("sentinel_keys", None)
        for select in feature_flag_selectors:
            # Handle None key_filter by converting to empty string
            key_filter = select.key_filter if select.key_filter is not None else ""
            feature_flags = self._client.list_configuration_settings(
                key_filter=FEATURE_FLAG_PREFIX + key_filter,
                label_filter=select.label_filter,
                tags_filter=select.tag_filters,
                **kwargs,
            )
            for feature_flag in feature_flags:
                if not isinstance(feature_flag, FeatureFlagConfigurationSetting):
                    # If the feature flag is not a FeatureFlagConfigurationSetting, it means it was selected by
                    # mistake, so we should ignore it.
                    continue
                loaded_feature_flags.append(feature_flag)

        return loaded_feature_flags

    @distributed_trace
    def get_updated_watched_settings(
        self, watched_settings: Mapping[Tuple[str, str], Optional[str]], headers: Dict[str, str], **kwargs
    ) -> Mapping[Tuple[str, str], Optional[str]]:
        """
        Checks if any of the watch keys have changed, and updates them if they have.

        :param Mapping[Tuple[str, str], Optional[str]] watched_settings: The configuration settings to check for changes
        :param Mapping[str, str] headers: The headers to use for the request

        :return: Updated value of the configuration watched settings.
        :rtype: Union[Dict[Tuple[str, str], str], None]
        """
        updated_watched_settings = dict(watched_settings)
        for (key, label), etag in watched_settings.items():
            changed, updated_watched_setting = self._check_configuration_setting(
                key=key, label=label, etag=etag, headers=headers, **kwargs
            )
            if changed and updated_watched_setting is not None:
                updated_watched_settings[(key, label)] = updated_watched_setting.etag
            elif changed:
                # The key was deleted
                updated_watched_settings[(key, label)] = None
        return updated_watched_settings

    @distributed_trace
    def try_check_feature_flags(
        self, watched_feature_flags: Mapping[Tuple[str, str], Optional[str]], headers: Dict[str, str], **kwargs
    ) -> bool:
        """
        Gets the refreshed feature flags if they have changed.

        :param Mapping[Tuple[str, str], Optional[str]] watched_feature_flags: The feature flags to check for changes
        :param Mapping[str, str] headers: The headers to use for the request

        :return: True if any feature flags have changed, False otherwise
        :rtype: bool
        """
        for (key, label), etag in watched_feature_flags.items():
            changed, _ = self._check_configuration_setting(key=key, label=label, etag=etag, headers=headers, **kwargs)
            if changed:
                return True
        return False

    @distributed_trace
    def get_configuration_setting(self, key: str, label: str, **kwargs) -> Optional[ConfigurationSetting]:
        """
        Gets a configuration setting from the replica client.

        :param str key: The key of the configuration setting
        :param str label: The label of the configuration setting
        :return: The configuration setting
        :rtype: ConfigurationSetting
        """
        return self._client.get_configuration_setting(key=key, label=label, **kwargs)

    def is_active(self) -> bool:
        """
        Checks if the client is active and can be used.

        :return: True if the client is active, False otherwise
        :rtype: bool
        """
        return self.backoff_end_time <= (time.time() * 1000)

    def close(self) -> None:
        """
        Closes the connection to Azure App Configuration.
        """
        self._client.close()

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)

    def resolve_snapshot_reference(self, setting: ConfigurationSetting, **kwargs) -> Dict[str, ConfigurationSetting]:
        """
        Resolve a snapshot reference configuration setting to the actual snapshot data.

        :param ConfigurationSetting setting: The snapshot reference configuration setting
        :return: A dictionary of resolved configuration settings from the snapshot
        :rtype: Dict[str, ConfigurationSetting]
        :raises ValueError: When the setting is not a valid snapshot reference
        """
        if not setting.content_type or not APP_CONFIG_SNAPSHOT_REF_MIME_PROFILE in setting.content_type:
            raise ValueError("Setting is not a snapshot reference")

        try:
            # Parse the snapshot reference
            snapshot_name = SnapshotReferenceParser.parse(setting)

            # Create a selector for the snapshot
            snapshot_selector = SettingSelector(snapshot_name=snapshot_name)

            # Use existing load_configuration_settings to load from snapshot
            configurations = self.load_configuration_settings([snapshot_selector], **kwargs)

            # Build a dictionary keyed by configuration key
            snapshot_settings = {}
            for config in configurations:
                # Last wins for duplicate keys during iteration
                snapshot_settings[config.key] = config

            return snapshot_settings

        except AzureError as e:
            # Wrap Azure errors with more context
            raise ValueError(
                f"Failed to resolve snapshot reference for key '{setting.key}' "
                f"(label: '{setting.label}'). Azure service error occurred."
            ) from e


class ConfigurationClientManager(ConfigurationClientManagerBase):  # pylint:disable=too-many-instance-attributes
    def __init__(
        self,
        connection_string: Optional[str],
        endpoint: str,
        credential: Optional["TokenCredential"],
        user_agent: str,
        retry_total,
        retry_backoff_max,
        replica_discovery_enabled,
        min_backoff_sec,
        max_backoff_sec,
        load_balancing_enabled,
        **kwargs,
    ):
        super(ConfigurationClientManager, self).__init__(
            endpoint,
            user_agent,
            retry_total,
            retry_backoff_max,
            replica_discovery_enabled,
            min_backoff_sec,
            max_backoff_sec,
            load_balancing_enabled,
            **kwargs,
        )
        self._original_connection_string = connection_string
        self._credential = credential
        self._replica_clients: List[_ConfigurationClientWrapper] = []
        self._active_clients: List[_ConfigurationClientWrapper] = []

        if connection_string and endpoint:
            self._original_client = _ConfigurationClientWrapper.from_connection_string(
                endpoint, connection_string, user_agent, retry_total, retry_backoff_max, **self._args
            )
        elif endpoint and credential:
            self._original_client = _ConfigurationClientWrapper.from_credential(
                endpoint, credential, user_agent, retry_total, retry_backoff_max, **self._args
            )
        else:
            raise ValueError("Please pass either endpoint and credential, or a connection string with a value.")
        self._replica_clients.append(self._original_client)

    def get_next_active_client(self) -> Optional[_ConfigurationClientWrapper]:
        """
        Get the next active client to be used for the request. if `find_active_clients` has never been invoked, this
        method returns None.

        :return: The next client to be used for the request.
        """
        if not self._active_clients:
            self._last_active_client_name = ""
            return None
        if not self._load_balancing_enabled:
            for client in self._active_clients:
                if client.is_active():
                    return client
            return None
        next_client = self._active_clients.pop(0)
        self._last_active_client_name = next_client.endpoint
        return next_client

    def find_active_clients(self):
        """
        Return a list of clients that are not in backoff state. If load balancing is enabled, the most recently used
        client is moved to the end of the list.
        """
        active_clients = [client for client in self._replica_clients if client.is_active()]

        self._active_clients = active_clients
        if not self._load_balancing_enabled or len(self._last_active_client_name) == 0:
            return
        for i, client in enumerate(active_clients):
            if client.endpoint == self._last_active_client_name:
                swap_point = (i + 1) % len(active_clients)
                self._active_clients = active_clients[swap_point:] + active_clients[:swap_point]
                return

    def get_client_count(self) -> int:
        return len(self._replica_clients)

    def refresh_clients(self):
        if not self._replica_discovery_enabled:
            return
        if self._next_update_time and self._next_update_time > time.time():
            return

        failover_endpoints = find_auto_failover_endpoints(self._original_endpoint, self._replica_discovery_enabled)

        if failover_endpoints is None:
            # SRV record not found, so we should refresh after a longer interval
            self._next_update_time = time.time() + FALLBACK_CLIENT_REFRESH_EXPIRED_INTERVAL
            return

        if len(failover_endpoints) == 0:
            # No failover endpoints in SRV record.
            self._next_update_time = time.time() + MINIMAL_CLIENT_REFRESH_INTERVAL
            return

        discovered_clients = []
        for failover_endpoint in failover_endpoints:
            found_client = False
            for client in self._replica_clients:
                if client.endpoint == failover_endpoint:
                    discovered_clients.append(client)
                    found_client = True
                    break
            if not found_client:
                if self._original_connection_string:
                    failover_connection_string = self._original_connection_string.replace(
                        self._original_endpoint, failover_endpoint
                    )
                    discovered_clients.append(
                        _ConfigurationClientWrapper.from_connection_string(
                            failover_endpoint,
                            failover_connection_string,
                            self._user_agent,
                            self._retry_total,
                            self._retry_backoff_max,
                            **self._args,
                        )
                    )
                elif self._credential:
                    discovered_clients.append(
                        _ConfigurationClientWrapper.from_credential(
                            failover_endpoint,
                            self._credential,
                            self._user_agent,
                            self._retry_total,
                            self._retry_backoff_max,
                            **self._args,
                        )
                    )
        self._next_update_time = time.time() + MINIMAL_CLIENT_REFRESH_INTERVAL
        if not self._load_balancing_enabled:
            random.shuffle(discovered_clients)
            self._replica_clients = [self._original_client] + discovered_clients
        else:
            self._replica_clients = [self._original_client] + discovered_clients
            random.shuffle(self._replica_clients)

    def backoff(self, client: _ConfigurationClientWrapper):
        client.failed_attempts += 1
        backoff_time = self._calculate_backoff(client.failed_attempts)
        client.backoff_end_time = (time.time() * 1000) + backoff_time

    def __eq__(self, other):
        if len(self._replica_clients) != len(other._replica_clients):
            return False
        for i in range(len(self._replica_clients)):  # pylint:disable=consider-using-enumerate
            if self._replica_clients[i] != other._replica_clients[i]:
                return False
        return True

    def close(self):
        for client in self._replica_clients:
            client.close()

    def __enter__(self):
        for client in self._replica_clients:
            client.__enter__()
        return self

    def __exit__(self, *args):
        for client in self._replica_clients:
            client.__exit__(*args)
