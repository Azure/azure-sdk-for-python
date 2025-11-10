# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import datetime
import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Mapping,
    Optional,
    overload,
    List,
    Tuple,
    Union,
)
from azure.appconfiguration import (  # type:ignore # pylint:disable=no-name-in-module
    ConfigurationSetting,
    FeatureFlagConfigurationSetting,
    SecretReferenceConfigurationSetting,
)
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.exceptions import AzureError, HttpResponseError
from .._models import AzureAppConfigurationKeyVaultOptions, SettingSelector
from ._key_vault._async_secret_provider import SecretProvider
from .._constants import (
    FEATURE_MANAGEMENT_KEY,
    FEATURE_FLAG_KEY,
)
from .._azureappconfigurationproviderbase import (
    AzureAppConfigurationProviderBase,
    delay_failure,
    process_load_parameters,
    sdk_allowed_kwargs,
)
from ._async_client_manager import (
    AsyncConfigurationClientManager as ConfigurationClientManager,
    _AsyncConfigurationClientWrapper as ConfigurationClient,
)
from .._user_agent import USER_AGENT

JSON = Mapping[str, Any]
logger = logging.getLogger(__name__)


@overload
async def load(  # pylint: disable=docstring-keyword-should-match-keyword-only
    endpoint: str,
    credential: "AsyncTokenCredential",
    *,
    selects: Optional[List[SettingSelector]] = None,
    trim_prefixes: Optional[List[str]] = None,
    keyvault_credential: Optional["AsyncTokenCredential"] = None,
    keyvault_client_configs: Optional[Mapping[str, JSON]] = None,
    secret_resolver: Optional[Callable[[str], str]] = None,
    key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = None,
    refresh_on: Optional[List[Tuple[str, str]]] = None,
    refresh_interval: int = 30,
    on_refresh_success: Optional[Callable] = None,
    on_refresh_error: Optional[Callable[[Exception], Awaitable[None]]] = None,
    feature_flag_enabled: bool = False,
    feature_flag_selectors: Optional[List[SettingSelector]] = None,
    feature_flag_refresh_enabled: bool = False,
    **kwargs,
) -> "AzureAppConfigurationProvider":
    """
    Loads configuration settings from Azure App Configuration into a Python application.

    :param str endpoint: Endpoint for App Configuration resource.
    :param ~azure.core.credentials_async.AsyncTokenCredential credential: Credential for App Configuration resource.
    :keyword Optional[List[~azure.appconfiguration.provider.SettingSelector]] selects: List of setting selectors to
    filter configuration settings
    :keyword Optional[List[str]] trim_prefixes: List of prefixes to trim from configuration keys
    :keyword ~azure.core.credentials_async.AsyncTokenCredential keyvault_credential: A credential for authenticating
    with the key vault. This is optional if keyvault_client_configs is provided.
    :keyword Mapping[str, Mapping] keyvault_client_configs: A Mapping of SecretClient endpoints to client
    configurations from azure-keyvault-secrets. This is optional if keyvault_credential is provided. If a credential
    isn't provided a credential will need to be in each set for each.
    :keyword Callable[[str], str] secret_resolver: A function that takes a URI and returns a value.
    :keyword List[Tuple[str, str]] refresh_on: One or more settings whose modification will trigger a full refresh
    after a fixed interval. This should be a list of Key-Label pairs for specific settings (filters and wildcards are
    not supported).
    :keyword int refresh_interval: The minimum time in seconds between when a call to `refresh` will actually trigger a
     service call to update the settings. Default value is 30 seconds.
    :keyword on_refresh_success: Optional callback to be invoked when a change is found and a successful refresh has
    happened.
    :paramtype on_refresh_success: Optional[Callable]
    :keyword on_refresh_error: Optional callback to be invoked when an error occurs while refreshing settings. If not
    specified, errors will be raised.
    :paramtype on_refresh_error: Optional[Callable[[Exception], Awaitable[None]]]
    :keyword feature_flag_enabled: Optional flag to enable or disable the loading of feature flags. Default is False.
    :paramtype feature_flag_enabled: bool
    :keyword feature_flag_selectors: Optional list of selectors to filter feature flags. By default will load all
     feature flags without a label.
    :paramtype feature_flag_selectors: List[SettingSelector]
    :keyword feature_flag_refresh_enabled: Optional flag to enable or disable the refresh of feature flags. Default is
     False.
    :paramtype feature_flag_refresh_enabled: bool
    :keyword replica_discovery_enabled: Optional flag to enable or disable the discovery of replica endpoints. Default
     is True.
    :paramtype replica_discovery_enabled: bool
    :keyword load_balancing_enabled: Optional flag to enable or disable the load balancing of replica endpoints. Default
     is False.
    :paramtype load_balancing_enabled: bool
    :keyword configuration_mapper: Optional function to map configuration settings. Enables transformation of
    configurations before they are added to the provider.
    :paramtype configuration_mapper: Optional[Callable[[ConfigurationSetting], Awaitable[None]]]
    """


@overload
async def load(  # pylint: disable=docstring-keyword-should-match-keyword-only
    *,
    connection_string: str,
    selects: Optional[List[SettingSelector]] = None,
    trim_prefixes: Optional[List[str]] = None,
    keyvault_credential: Optional["AsyncTokenCredential"] = None,
    keyvault_client_configs: Optional[Mapping[str, JSON]] = None,
    secret_resolver: Optional[Callable[[str], str]] = None,
    key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = None,
    refresh_on: Optional[List[Tuple[str, str]]] = None,
    refresh_interval: int = 30,
    on_refresh_success: Optional[Callable] = None,
    on_refresh_error: Optional[Callable[[Exception], Awaitable[None]]] = None,
    feature_flag_enabled: bool = False,
    feature_flag_selectors: Optional[List[SettingSelector]] = None,
    feature_flag_refresh_enabled: bool = False,
    **kwargs,
) -> "AzureAppConfigurationProvider":
    """
    Loads configuration settings from Azure App Configuration into a Python application.

    :keyword str connection_string: Connection string for App Configuration resource.
    :keyword Optional[List[~azure.appconfiguration.provider.SettingSelector]] selects: List of setting selectors to
    filter configuration settings
    :keyword trim_prefixes: Optional[List[str]] trim_prefixes: List of prefixes to trim from configuration keys
    :keyword ~azure.core.credentials_async.AsyncTokenCredential keyvault_credential: A credential for authenticating
    with the key vault. This is optional if keyvault_client_configs is provided.
    :keyword Mapping[str, Mapping] keyvault_client_configs: A Mapping of SecretClient endpoints to client
    configurations from azure-keyvault-secrets. This is optional if keyvault_credential is provided. If a credential
    isn't provided a credential will need to be in each set for each.
    :keyword Callable[[str], str] secret_resolver: A function that takes a URI and returns a value.
    :keyword List[Tuple[str, str]] refresh_on: One or more settings whose modification will trigger a full refresh
    after a fixed interval. This should be a list of Key-Label pairs for specific settings (filters and wildcards are
    not supported).
    :keyword refresh_on: One or more settings whose modification will trigger a full refresh after a fixed interval.
    This should be a list of Key-Label pairs for specific settings (filters and wildcards are not supported).
    :paramtype refresh_on: List[Tuple[str, str]]
    :keyword int refresh_interval: The minimum time in seconds between when a call to `refresh` will actually trigger a
     service call to update the settings. Default value is 30 seconds.
    :keyword on_refresh_success: Optional callback to be invoked when a change is found and a successful refresh has
     happened.
    :paramtype on_refresh_success: Optional[Callable]
    :keyword on_refresh_error: Optional callback to be invoked when an error occurs while refreshing settings. If not
    specified, errors will be raised.
    :paramtype on_refresh_error: Optional[Callable[[Exception], Awaitable[None]]]
    :keyword feature_flag_enabled: Optional flag to enable or disable the loading of feature flags. Default is False.
    :paramtype feature_flag_enabled: bool
    :keyword feature_flag_selectors: Optional list of selectors to filter feature flags. By default will load all
     feature flags without a label.
    :paramtype feature_flag_selectors: List[SettingSelector]
    :keyword feature_flag_refresh_enabled: Optional flag to enable or disable the refresh of feature flags. Default is
     False.
    :paramtype feature_flag_refresh_enabled: bool
    :keyword replica_discovery_enabled: Optional flag to enable or disable the discovery of replica endpoints. Default
     is True.
    :paramtype replica_discovery_enabled: bool
    :keyword load_balancing_enabled: Optional flag to enable or disable the load balancing of replica endpoints. Default
     is False.
    :paramtype load_balancing_enabled: bool
    :keyword configuration_mapper: Optional function to map configuration settings. Enables transformation of
    configurations before they are added to the provider.
    :paramtype configuration_mapper: Optional[Callable[[ConfigurationSetting], Awaitable[None]]]
    """


async def load(*args, **kwargs) -> "AzureAppConfigurationProvider":
    start_time = datetime.datetime.now()

    # Process common load parameters using shared logic
    params = process_load_parameters(*args, **kwargs)

    provider = await _buildprovider(
        params["connection_string"],
        params["endpoint"],
        params["credential"],
        uses_key_vault=params["uses_key_vault"],
        **params["kwargs"],
    )
    kwargs = sdk_allowed_kwargs(params["kwargs"])

    try:
        await provider._load_all(**kwargs)  # pylint:disable=protected-access
    except Exception as e:
        delay_failure(start_time)
        raise e
    return provider


async def _buildprovider(
    connection_string: Optional[str], endpoint: Optional[str], credential: Optional[AsyncTokenCredential], **kwargs
) -> "AzureAppConfigurationProvider":
    # pylint:disable=protected-access
    if connection_string:
        endpoint = connection_string.split(";")[0].split("=")[1]
    if not endpoint:
        raise ValueError("No endpoint specified.")

    kwargs["endpoint"] = endpoint
    kwargs["connection_string"] = connection_string
    kwargs["credential"] = credential

    return AzureAppConfigurationProvider(**kwargs)


class AzureAppConfigurationProvider(AzureAppConfigurationProviderBase):  # pylint: disable=too-many-instance-attributes
    """
    Provides a dictionary-like interface to Azure App Configuration settings. Enables loading of sets of configuration
    settings from Azure App Configuration into a Python application. Enables trimming of prefixes from configuration
    keys. Enables resolution of Key Vault references in configuration settings.
    """

    def __init__(self, **kwargs: Any) -> None:
        super(AzureAppConfigurationProvider, self).__init__(**kwargs)

        if "user_agent" in kwargs:
            user_agent = kwargs.pop("user_agent") + " " + USER_AGENT
        else:
            user_agent = USER_AGENT

        interval: int = kwargs.get("refresh_interval", 30)
        if interval < 1:
            raise ValueError("Refresh interval must be greater than or equal to 1 second.")

        min_backoff: int = min(kwargs.pop("min_backoff", 30), interval)
        max_backoff: int = min(kwargs.pop("max_backoff", 600), interval)

        self._replica_client_manager = ConfigurationClientManager(
            connection_string=kwargs.pop("connection_string", None),
            endpoint=kwargs.pop("endpoint"),
            credential=kwargs.pop("credential", None),
            user_agent=user_agent,
            retry_total=kwargs.pop("retry_total", 2),
            retry_backoff_max=kwargs.pop("retry_backoff_max", 60),
            replica_discovery_enabled=kwargs.pop("replica_discovery_enabled", True),
            min_backoff_sec=min_backoff,
            max_backoff_sec=max_backoff,
            load_balancing_enabled=kwargs.pop("load_balancing_enabled", False),
            **kwargs,
        )
        self._secret_provider = SecretProvider(**kwargs)
        self._on_refresh_success: Optional[Callable] = kwargs.pop("on_refresh_success", None)
        self._on_refresh_error: Optional[Union[Callable[[Exception], Awaitable[None]], None]] = kwargs.pop(
            "on_refresh_error", None
        )
        self._configuration_mapper: Optional[Callable[[ConfigurationSetting], Awaitable[None]]] = kwargs.pop(
            "configuration_mapper", None
        )

    async def _attempt_refresh(
        self, client: ConfigurationClient, replica_count: int, is_failover_request: bool, **kwargs
    ):
        settings_refreshed = False
        headers = self._update_correlation_context_header(
            kwargs.pop("headers", {}),
            "Watch",
            replica_count,
            self._secret_provider.uses_key_vault,
            is_failover_request,
        )
        configuration_settings: List[ConfigurationSetting] = []
        feature_flags: Optional[List[FeatureFlagConfigurationSetting]] = None

        # Timer needs to be reset even if no refresh happened if time had passed
        configuration_refresh_attempted = False
        feature_flag_refresh_attempted = False
        updated_watched_settings: Mapping[Tuple[str, str], Optional[str]] = {}
        existing_feature_flag_usage = self._tracing_context.feature_filter_usage.copy()
        try:
            if self._watched_settings and self._refresh_timer.needs_refresh():
                configuration_refresh_attempted = True

                updated_watched_settings = await client.get_updated_watched_settings(
                    self._watched_settings, headers=headers, **kwargs
                )

                if len(updated_watched_settings) > 0:
                    configuration_settings = await client.load_configuration_settings(
                        self._selects, headers=headers, **kwargs
                    )
                    settings_refreshed = True

            if self._feature_flag_refresh_enabled and self._feature_flag_refresh_timer.needs_refresh():
                feature_flag_refresh_attempted = True

                feature_flags_need_refresh = await client.try_check_feature_flags(
                    self._watched_feature_flags, headers=headers, **kwargs
                )

                if feature_flags_need_refresh:
                    feature_flags = await client.load_feature_flags(
                        self._feature_flag_selectors, headers=headers, **kwargs
                    )
            # Default to existing settings if no refresh occurred
            processed_settings = self._dict

            processed_feature_flags = self._dict.get(FEATURE_MANAGEMENT_KEY, {}).get(FEATURE_FLAG_KEY, [])

            if settings_refreshed:
                # Configuration Settings have been refreshed
                processed_settings = await self._process_configurations(configuration_settings)

            processed_settings = self._process_feature_flags(processed_settings, processed_feature_flags, feature_flags)
            self._dict = processed_settings
            if settings_refreshed:
                # Update the watch keys that have changed
                self._watched_settings.update(updated_watched_settings)
            # Reset timers at the same time as they should load from the same store.
            if configuration_refresh_attempted:
                self._refresh_timer.reset()
            if self._feature_flag_refresh_enabled and feature_flag_refresh_attempted:
                self._feature_flag_refresh_timer.reset()
            if (settings_refreshed or feature_flags) and self._on_refresh_success:
                self._on_refresh_success()
        except AzureError as e:
            logger.warning("Failed to refresh configurations from endpoint %s", client.endpoint)
            self._replica_client_manager.backoff(client)
            # Restore feature flag usage on failure
            self._tracing_context.feature_filter_usage = existing_feature_flag_usage
            raise e

    async def refresh(self, **kwargs) -> None:
        if not self._watched_settings and not self._feature_flag_refresh_enabled:
            logger.debug("Refresh called but no refresh enabled.")
            return
        if not self._refresh_lock.acquire(blocking=False):  # pylint: disable= consider-using-with
            logger.debug("Refresh called but refresh already in progress.")
            return
        error_message = """
                        Failed to refresh configuration settings from Azure App Configuration.
                        """
        exception: Optional[Exception] = None
        is_failover_request = False
        try:
            if (
                self._secret_provider.secret_refresh_timer
                and self._secret_provider.secret_refresh_timer.needs_refresh()
            ):
                self._dict.update(await self._secret_provider.refresh_secrets())
            await self._replica_client_manager.refresh_clients()
            self._replica_client_manager.find_active_clients()
            replica_count = self._replica_client_manager.get_client_count() - 1

            while client := self._replica_client_manager.get_next_active_client():
                try:
                    await self._attempt_refresh(client, replica_count, is_failover_request, **kwargs)
                    return
                except AzureError as e:
                    exception = e
                    is_failover_request = True
            if exception is None:
                exception = RuntimeError(error_message)
            self._refresh_timer.backoff()
            if self._feature_flag_refresh_enabled:
                self._feature_flag_refresh_timer.backoff()
            if self._on_refresh_error:
                await self._on_refresh_error(exception)
                return
            raise exception
        finally:
            self._refresh_lock.release()

    async def _load_all(self, **kwargs: Any) -> None:
        await self._replica_client_manager.refresh_clients()
        self._replica_client_manager.find_active_clients()
        is_failover_request = False
        replica_count = self._replica_client_manager.get_client_count() - 1

        error_message = """
        Failed to load configuration settings. No Azure App Configuration stores successfully loaded from.
        """
        exception: Exception = RuntimeError(error_message)

        while client := self._replica_client_manager.get_next_active_client():
            headers = self._update_correlation_context_header(
                kwargs.pop("headers", {}),
                "Startup",
                replica_count,
                self._secret_provider.uses_key_vault,
                is_failover_request,
            )
            try:
                configuration_settings = await client.load_configuration_settings(
                    self._selects, headers=headers, **kwargs
                )
                watched_settings = self._update_watched_settings(configuration_settings)
                processed_settings = await self._process_configurations(configuration_settings)

                if self._feature_flag_enabled:
                    feature_flags: List[FeatureFlagConfigurationSetting] = await client.load_feature_flags(
                        self._feature_flag_selectors,
                        headers=headers,
                        **kwargs,
                    )
                    processed_settings = self._process_feature_flags(processed_settings, [], feature_flags)
                for (key, label), etag in self._watched_settings.items():
                    if not etag:
                        try:
                            watch_setting = await client.get_configuration_setting(
                                key, label, headers=headers
                            )  # type:ignore
                            watched_settings[(key, label)] = watch_setting.etag  # type:ignore
                        except HttpResponseError as e:
                            if e.status_code == 404:
                                # If the watched setting is not found a refresh should be triggered when it is created.
                                logger.debug(
                                    """
                                    Watched Setting: %s label %s was configured but not found. Refresh will be triggered
                                    if created.
                                    """,
                                    key,
                                    label,
                                )
                                watched_settings[(key, label)] = None  # type: ignore
                            else:
                                raise e
                with self._update_lock:
                    self._watched_settings = watched_settings
                    self._dict = processed_settings
                return
            except AzureError as e:
                exception = e
                logger.warning("Failed to load configurations from endpoint %s.\n %s", client.endpoint, e.message)
                self._replica_client_manager.backoff(client)
                is_failover_request = True
        raise exception

    async def _process_configurations(self, configuration_settings: List[ConfigurationSetting]) -> Dict[str, Any]:
        # configuration_settings can contain duplicate keys, but they are in priority order, i.e. later settings take
        # precedence. Only process the settings with the highest priority (i.e. the last one in the list).
        unique_settings = self._deduplicate_settings(configuration_settings)

        configuration_settings_processed = {}
        feature_flags_processed = []
        for settings in unique_settings.values():
            if self._configuration_mapper:
                await self._configuration_mapper(settings)
            if isinstance(settings, FeatureFlagConfigurationSetting):
                # Feature flags are not processed like other settings
                feature_flag_value = self._process_feature_flag(settings)
                feature_flags_processed.append(feature_flag_value)

                if self._feature_flag_refresh_enabled:
                    self._watched_feature_flags[(settings.key, settings.label)] = settings.etag
            else:
                key = self._process_key_name(settings)
                value = await self._process_key_value(settings)
                configuration_settings_processed[key] = value
        return configuration_settings_processed

    async def _process_key_value(self, config: ConfigurationSetting) -> Any:
        if isinstance(config, SecretReferenceConfigurationSetting):
            return await self._secret_provider.resolve_keyvault_reference(config)
        # Use the base class helper method for non-KeyVault processing
        return self._process_key_value_base(config)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AzureAppConfigurationProvider):
            return False
        if self._dict != other._dict:
            return False
        if self._trim_prefixes != other._trim_prefixes:
            return False
        return self._replica_client_manager == other._replica_client_manager

    async def close(self) -> None:
        """
        Closes the connection to Azure App Configuration.
        """
        await self._secret_provider.close()
        await self._replica_client_manager.close()

    async def __aenter__(self) -> "AzureAppConfigurationProvider":
        await self._replica_client_manager.__aenter__()
        await self._secret_provider.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._replica_client_manager.__aexit__(*args)
        await self._secret_provider.__aexit__(*args)
