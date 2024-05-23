# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json
from threading import Lock
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
    TYPE_CHECKING,
    Union,
    Iterator,
    KeysView,
    ItemsView,
    ValuesView,
    TypeVar,
)

from azure.appconfiguration import (  # type: ignore # pylint:disable=no-name-in-module
    FeatureFlagConfigurationSetting,
    SecretReferenceConfigurationSetting,
    ConfigurationSetting,
)
from azure.appconfiguration.aio import AzureAppConfigurationClient
from azure.keyvault.secrets.aio import SecretClient
from azure.keyvault.secrets import KeyVaultSecretIdentifier
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError, ServiceRequestError, ServiceResponseError

from .._models import AzureAppConfigurationKeyVaultOptions, SettingSelector
from .._constants import (
    FEATURE_MANAGEMENT_KEY,
    FEATURE_FLAG_KEY,
    FEATURE_FLAG_PREFIX,
    EMPTY_LABEL,
    PERCENTAGE_FILTER_NAMES,
    TIME_WINDOW_FILTER_NAMES,
    TARGETING_FILTER_NAMES,
    CUSTOM_FILTER_KEY,
    PERCENTAGE_FILTER_KEY,
    TIME_WINDOW_FILTER_KEY,
    TARGETING_FILTER_KEY,
)
from .._azureappconfigurationprovider import (
    _is_json_content_type,
    _get_headers,
    _RefreshTimer,
    _build_sentinel,
    _delay_failure,
)
from .._user_agent import USER_AGENT

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential

JSON = Mapping[str, Any]  # pylint: disable=unsubscriptable-object
_T = TypeVar("_T")


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
    **kwargs
) -> "AzureAppConfigurationProvider":
    """
    Loads configuration settings from Azure App Configuration into a Python application.

    :param str endpoint: Endpoint for App Configuration resource.
    :param credential: Credential for App Configuration resource.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword selects: List of setting selectors to filter configuration settings
    :paramtype selects: Optional[List[~azure.appconfiguration.provider.SettingSelector]]
    :keyword trim_prefixes: List of prefixes to trim from configuration keys
    :paramtype trim_prefixes: Optional[List[str]]
    :keyword keyvault_credential: A credential for authenticating with the key vault. This is optional if
     keyvault_client_configs is provided.
    :paramtype keyvault_credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword keyvault_client_configs: A Mapping of SecretClient endpoints to client configurations from
     azure-keyvault-secrets. This is optional if keyvault_credential is provided. If a credential isn't provided a
     credential will need to be in each set for each.
    :paramtype keyvault_client_configs: Mapping[str, Mapping]
    :keyword secret_resolver: A function that takes a URI and returns a value.
    :paramtype secret_resolver: Callable[[str], str]
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
    **kwargs
) -> "AzureAppConfigurationProvider":
    """
    Loads configuration settings from Azure App Configuration into a Python application.

    :keyword str connection_string: Connection string for App Configuration resource.
    :keyword selects: List of setting selectors to filter configuration settings
    :paramtype selects: Optional[List[~azure.appconfiguration.provider.SettingSelector]]
    :keyword trim_prefixes: List of prefixes to trim from configuration keys
    :paramtype trim_prefixes: Optional[List[str]]
    :keyword keyvault_credential: A credential for authenticating with the key vault. This is optional if
     keyvault_client_configs is provided.
    :paramtype keyvault_credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword keyvault_client_configs: A Mapping of SecretClient endpoints to client configurations from
     azure-keyvault-secrets. This is optional if keyvault_credential is provided. If a credential isn't provided a
     credential will need to be in each set for each.
    :paramtype keyvault_client_configs: Mapping[str, Mapping]
    :keyword secret_resolver: A function that takes a URI and returns a value.
    :paramtype secret_resolver: Callable[[str], str]
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
    """


async def load(*args, **kwargs) -> "AzureAppConfigurationProvider":
    # pylint:disable=protected-access

    # Start by parsing kwargs
    endpoint: Optional[str] = kwargs.pop("endpoint", None)
    credential: Optional["AsyncTokenCredential"] = kwargs.pop("credential", None)
    connection_string: Optional[str] = kwargs.pop("connection_string", None)
    key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = kwargs.pop("key_vault_options", None)
    start_time = datetime.datetime.now()

    # Update endpoint and credential if specified positionally.
    if len(args) > 2:
        raise TypeError(
            "Unexpected positional parameters. Please pass either endpoint and credential, or a connection string."
        )
    if len(args) == 1:
        if endpoint is not None:
            raise TypeError("Received multiple values for parameter 'endpoint'.")
        endpoint = args[0]
    elif len(args) == 2:
        if credential is not None:
            raise TypeError("Received multiple values for parameter 'credential'.")
        endpoint, credential = args

    if (endpoint or credential) and connection_string:
        raise ValueError("Please pass either endpoint and credential, or a connection string.")

    # Removing use of AzureAppConfigurationKeyVaultOptions
    if key_vault_options:
        if "keyvault_credential" in kwargs or "secret_resolver" in kwargs or "keyvault_client_configs" in kwargs:
            raise ValueError(
                "Key Vault configurations should only be set by either the key_vault_options or kwargs not both."
            )
        kwargs["keyvault_credential"] = key_vault_options.credential
        kwargs["secret_resolver"] = key_vault_options.secret_resolver
        kwargs["keyvault_client_configs"] = key_vault_options.client_configs

    if kwargs.get("keyvault_credential") is not None and kwargs.get("secret_resolver") is not None:
        raise ValueError("A keyvault credential and secret resolver can't both be configured.")

    headers = _get_headers("Startup", **kwargs)
    provider = _buildprovider(
        connection_string, endpoint, credential, uses_key_vault="UsesKeyVault" in headers, **kwargs
    )

    try:
        await provider._load_all(headers=headers)
    except Exception as e:
        _delay_failure(start_time)
        raise e

    # Refresh-All sentinels are not updated on load_all, as they are not necessarily included in the provider.
    for (key, label), etag in provider._refresh_on.items():
        if not etag:
            try:
                sentinel = await provider._client.get_configuration_setting(key, label, headers=headers)  # type: ignore
                provider._refresh_on[(key, label)] = sentinel.etag  # type: ignore
            except HttpResponseError as e:
                if e.status_code == 404:
                    # If the sentinel is not found a refresh should be triggered when it is created.
                    logging.debug(
                        "WatchKey key: %s label %s was configured but not found. Refresh will be triggered if created.",
                        key,
                        label,
                    )
                    provider._refresh_on[(key, label)] = None  # type: ignore
                else:
                    _delay_failure(start_time)
                    raise e
            except Exception as e:
                _delay_failure(start_time)
                raise e
    return provider


def _buildprovider(
    connection_string: Optional[str], endpoint: Optional[str], credential: Optional["AsyncTokenCredential"], **kwargs
) -> "AzureAppConfigurationProvider":
    # pylint:disable=protected-access
    provider = AzureAppConfigurationProvider(**kwargs)
    retry_total = kwargs.pop("retry_total", 2)
    retry_backoff_max = kwargs.pop("retry_backoff_max", 60)

    if "user_agent" in kwargs:
        user_agent = kwargs.pop("user_agent") + " " + USER_AGENT
    else:
        user_agent = USER_AGENT

    if connection_string:
        provider._client = AzureAppConfigurationClient.from_connection_string(
            connection_string,
            user_agent=user_agent,
            retry_total=retry_total,
            retry_backoff_max=retry_backoff_max,
            **kwargs
        )
        return provider
    if endpoint is not None and credential is not None:
        provider._client = AzureAppConfigurationClient(
            endpoint,
            credential,
            user_agent=user_agent,
            retry_total=retry_total,
            retry_backoff_max=retry_backoff_max,
            **kwargs
        )
        return provider
    raise ValueError("Please pass either endpoint and credential, or a connection string.")


async def _resolve_keyvault_reference(
    config: "SecretReferenceConfigurationSetting", provider: "AzureAppConfigurationProvider"
) -> str:
    # pylint:disable=protected-access
    if not (provider._keyvault_credential or provider._keyvault_client_configs or provider._secret_resolver):
        raise ValueError(
            """
            Either a credential to Key Vault, custom Key Vault client, or a secret resolver must be set to resolve Key
             Vault references.
            """
        )

    if config.secret_id is None:
        raise ValueError("Key Vault reference must have a uri value.")

    keyvault_identifier = KeyVaultSecretIdentifier(config.secret_id)

    vault_url = keyvault_identifier.vault_url + "/"

    # pylint:disable=protected-access
    referenced_client = provider._secret_clients.get(vault_url, None)

    vault_config = provider._keyvault_client_configs.get(vault_url, {})
    credential = vault_config.pop("credential", provider._keyvault_credential)

    if referenced_client is None and credential is not None:
        referenced_client = SecretClient(vault_url=vault_url, credential=credential, **vault_config)
        provider._secret_clients[vault_url] = referenced_client

    if referenced_client:
        secret_value = (
            await referenced_client.get_secret(keyvault_identifier.name, version=keyvault_identifier.version)
        ).value
        if secret_value is not None:
            return secret_value

    if provider._secret_resolver:
        resolved = provider._secret_resolver(config.secret_id)
        try:
            # Secret resolver was async
            return await resolved
        except TypeError:
            # Secret resolver was sync
            return resolved

    raise ValueError("No Secret Client found for Key Vault reference %s" % (vault_url))


class AzureAppConfigurationProvider(Mapping[str, Union[str, JSON]]):  # pylint: disable=too-many-instance-attributes
    """
    Provides a dictionary-like interface to Azure App Configuration settings. Enables loading of sets of configuration
    settings from Azure App Configuration into a Python application. Enables trimming of prefixes from configuration
    keys. Enables resolution of Key Vault references in configuration settings.
    """

    def __init__(self, **kwargs) -> None:
        self._dict: Dict[str, str] = {}
        self._client: Optional[AzureAppConfigurationClient] = None
        self._secret_clients: Dict[str, SecretClient] = {}
        self._selects: List[SettingSelector] = kwargs.pop(
            "selects", [SettingSelector(key_filter="*", label_filter=EMPTY_LABEL)]
        )

        trim_prefixes: List[str] = kwargs.pop("trim_prefixes", [])
        self._trim_prefixes: List[str] = sorted(trim_prefixes, key=len, reverse=True)

        refresh_on: List[Tuple[str, str]] = kwargs.pop("refresh_on", None) or []
        self._refresh_on: Mapping[Tuple[str, str], Optional[str]] = {_build_sentinel(s): None for s in refresh_on}
        self._refresh_timer: _RefreshTimer = _RefreshTimer(**kwargs)
        self._on_refresh_success: Optional[Callable] = kwargs.pop("on_refresh_success", None)
        self._on_refresh_error: Optional[Union[Callable[[Exception], Awaitable[None]], None]] = kwargs.pop(
            "on_refresh_error", None
        )
        self._keyvault_credential = kwargs.pop("keyvault_credential", None)
        self._secret_resolver = kwargs.pop("secret_resolver", None)
        self._keyvault_client_configs = kwargs.pop("keyvault_client_configs", {})
        self._uses_key_vault = (
            self._keyvault_credential is not None
            or (self._keyvault_client_configs is not None and len(self._keyvault_client_configs) > 0)
            or self._secret_resolver is not None
        )
        self._feature_flag_enabled = kwargs.pop("feature_flag_enabled", False)
        self._feature_flag_selectors = kwargs.pop("feature_flag_selectors", [SettingSelector(key_filter="*")])
        self._refresh_on_feature_flags: Mapping[Tuple[str, str], Optional[str]] = {}
        self._feature_flag_refresh_timer: _RefreshTimer = _RefreshTimer(**kwargs)
        self._feature_flag_refresh_enabled = kwargs.pop("feature_flag_refresh_enabled", False)
        self._feature_filter_usage: Mapping[str, bool] = {}
        self._update_lock = Lock()
        self._refresh_lock = Lock()

    async def refresh(self, **kwargs) -> None:
        if not self._refresh_on and not self._feature_flag_refresh_enabled:
            logging.debug("Refresh called but no refresh enabled.")
            return
        if not self._refresh_timer.needs_refresh():
            logging.debug("Refresh called but refresh interval not elapsed.")
            return
        if not self._refresh_lock.acquire(blocking=False):  # pylint: disable= consider-using-with
            logging.debug("Refresh called but refresh already in progress.")
            return
        success = False
        need_refresh = False
        try:
            if self._refresh_on:
                need_refresh = await self._refresh_configuration_settings(**kwargs)
            if self._feature_flag_refresh_enabled:
                need_refresh = await self._refresh_feature_flags(**kwargs) or need_refresh
            # Even if we don't need to refresh, we should reset the timer
            self._refresh_timer.reset()
            success = True
        except (ServiceRequestError, ServiceResponseError, HttpResponseError) as e:
            # If we get an error we should retry sooner than the next refresh interval
            if self._on_refresh_error:
                await self._on_refresh_error(e)
                return
            raise
        finally:
            self._refresh_lock.release()
            if not success:
                self._refresh_timer.backoff()
            elif need_refresh and self._on_refresh_success:
                await self._on_refresh_success()

    async def _refresh_configuration_settings(self, **kwargs) -> bool:
        need_refresh = False
        updated_sentinel_keys = dict(self._refresh_on)
        headers = _get_headers(
            "Watch",
            uses_key_vault=self._uses_key_vault,
            feature_filters_used=self._feature_filter_usage,
            uses_feature_flags=self._feature_flag_enabled,
            **kwargs
        )
        for (key, label), etag in updated_sentinel_keys.items():
            changed, updated_sentinel = await self._check_configuration_setting(
                key=key, label=label, etag=etag, headers=headers, **kwargs
            )
            if changed:
                need_refresh = True
            if updated_sentinel is not None:
                updated_sentinel_keys[(key, label)] = updated_sentinel.etag
        # Need to only update once, no matter how many sentinels are updated
        if need_refresh:
            configuration_settings, sentinel_keys = await self._load_configuration_settings(**kwargs)
            if self._feature_flag_enabled:
                configuration_settings[FEATURE_MANAGEMENT_KEY] = self._dict[FEATURE_MANAGEMENT_KEY]
            with self._update_lock:
                self._refresh_on = sentinel_keys
                self._dict = configuration_settings
        return need_refresh

    async def _refresh_feature_flags(self, **kwargs) -> bool:
        feature_flag_sentinel_keys = dict(self._refresh_on_feature_flags)
        headers = _get_headers(
            "Watch",
            uses_key_vault=self._uses_key_vault,
            feature_filters_used=self._feature_filter_usage,
            uses_feature_flags=self._feature_flag_enabled,
            **kwargs
        )
        for (key, label), etag in feature_flag_sentinel_keys.items():
            changed = await self._check_configuration_setting(
                key=key, label=label, etag=etag, headers=headers, **kwargs
            )
            if changed:
                feature_flags, feature_flag_sentinel_keys = await self._load_feature_flags(**kwargs)
                with self._update_lock:
                    updated_configurations: Dict[str, Any] = {}
                    updated_configurations[FEATURE_MANAGEMENT_KEY] = {}
                    updated_configurations[FEATURE_MANAGEMENT_KEY][FEATURE_FLAG_KEY] = feature_flags
                    self._dict.update(updated_configurations)
                self._refresh_on_feature_flags = feature_flag_sentinel_keys
                return True
        return False

    async def _check_configuration_setting(
        self, key, label, etag, headers, **kwargs
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
            updated_sentinel = await self._client.get_configuration_setting(  # type: ignore
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

    async def _load_all(self, **kwargs):
        configuration_settings, sentinel_keys = await self._load_configuration_settings(**kwargs)
        if self._feature_flag_enabled:
            feature_flags, feature_flag_sentinel_keys = await self._load_feature_flags(**kwargs)
            configuration_settings[FEATURE_MANAGEMENT_KEY] = {}
            configuration_settings[FEATURE_MANAGEMENT_KEY][FEATURE_FLAG_KEY] = feature_flags
            self._refresh_on_feature_flags = feature_flag_sentinel_keys
        with self._update_lock:
            self._refresh_on = sentinel_keys
            self._dict = configuration_settings

    async def _load_configuration_settings(self, **kwargs):
        configuration_settings = {}
        sentinel_keys = kwargs.pop("sentinel_keys", self._refresh_on)
        for select in self._selects:
            configurations = self._client.list_configuration_settings(
                key_filter=select.key_filter, label_filter=select.label_filter, **kwargs
            )
            async for config in configurations:
                if isinstance(config, FeatureFlagConfigurationSetting):
                    # Feature flags are ignored when loaded by Selects, as they are selected from
                    # `feature_flag_selectors`
                    pass
                else:
                    key = self._process_key_name(config)
                    value = await self._process_key_value(config)
                    configuration_settings[key] = value
                # Every time we run load_all, we should update the etag of our refresh sentinels
                # so they stay up-to-date.
                # Sentinel keys will have unprocessed key names, so we need to use the original key.
                if (config.key, config.label) in self._refresh_on:
                    sentinel_keys[(config.key, config.label)] = config.etag
        return configuration_settings, sentinel_keys

    async def _load_feature_flags(self, **kwargs):
        feature_flag_sentinel_keys = {}
        loaded_feature_flags = []
        # Needs to be removed unknown keyword argument for list_configuration_settings
        kwargs.pop("sentinel_keys", None)
        filters_used = {}
        for select in self._feature_flag_selectors:
            feature_flags = self._client.list_configuration_settings(
                key_filter=FEATURE_FLAG_PREFIX + select.key_filter, label_filter=select.label_filter, **kwargs
            )
            async for feature_flag in feature_flags:
                loaded_feature_flags.append(json.loads(feature_flag.value))

                if self._feature_flag_refresh_enabled:
                    feature_flag_sentinel_keys[(feature_flag.key, feature_flag.label)] = feature_flag.etag
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
        self._feature_filter_usage = filters_used

        return loaded_feature_flags, feature_flag_sentinel_keys

    def _process_key_name(self, config):
        trimmed_key = config.key
        # Trim the key if it starts with one of the prefixes provided
        for trim in self._trim_prefixes:
            if config.key.startswith(trim):
                trimmed_key = config.key[len(trim) :]
                break
        return trimmed_key

    async def _process_key_value(self, config):
        if isinstance(config, SecretReferenceConfigurationSetting):
            return await _resolve_keyvault_reference(config, self)
        if _is_json_content_type(config.content_type) and not isinstance(config, FeatureFlagConfigurationSetting):
            # Feature flags are of type json, but don't treat them as such
            try:
                return json.loads(config.value)
            except json.JSONDecodeError:
                # If the value is not a valid JSON, treat it like regular string value
                return config.value
        return config.value

    def __getitem__(self, key: str) -> Any:
        # pylint:disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
        """
        Returns the value of the specified key.
        """
        return self._dict[key]

    def __iter__(self) -> Iterator[str]:
        return self._dict.__iter__()

    def __len__(self) -> int:
        return len(self._dict)

    def __contains__(self, __x: object) -> bool:
        # pylint:disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
        """
        Returns True if the configuration settings contains the specified key.
        """
        return self._dict.__contains__(__x)

    def keys(self) -> KeysView[str]:
        """
        Returns a list of keys loaded from Azure App Configuration.

        :return: A list of keys loaded from Azure App Configuration.
        :rtype: KeysView[str]
        """
        return self._dict.keys()

    def items(self) -> ItemsView[str, Union[str, Mapping[str, Any]]]:
        """
        Returns a set-like object of key-value pairs loaded from Azure App Configuration. Any values that are Key Vault
         references will be resolved.

        :return: A set-like object of key-value pairs loaded from Azure App Configuration.
        :rtype: ItemsView[str, Union[str, Mapping[str, Any]]]
        """
        return self._dict.items()

    def values(self) -> ValuesView[Union[str, Mapping[str, Any]]]:
        """
        Returns a list of values loaded from Azure App Configuration. Any values that are Key Vault references will be
        resolved.

        :return: A list of values loaded from Azure App Configuration. The values are either Strings or JSON objects,
         based on there content type.
        :rtype: ValuesView[Union[str, Mapping[str, Any]]]
        """
        return self._dict.values()

    @overload
    def get(self, key: str, default: None = None) -> Union[str, JSON, None]: ...

    @overload
    def get(self, key: str, default: Union[str, JSON, _T]) -> Union[str, JSON, _T]:  # pylint: disable=signature-differs
        ...

    def get(self, key: str, default: Optional[Union[str, JSON, _T]] = None) -> Union[str, JSON, _T, None]:
        """
        Returns the value of the specified key. If the key does not exist, returns the default value.

        :param str key: The key of the value to get.
        :param default: The default value to return.
        :type: str or None
        :return: The value of the specified key.
        :rtype: Union[str, JSON]
        """
        return self._dict.get(key, default)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AzureAppConfigurationProvider):
            return False
        if self._dict != other._dict:
            return False
        if self._trim_prefixes != other._trim_prefixes:
            return False
        if self._client != other._client:
            return False
        return True

    def __ne__(self, other: Any) -> bool:
        return not self == other

    async def close(self) -> None:
        """
        Closes the connection to Azure App Configuration.
        """
        for client in self._secret_clients.values():
            await client.close()
        await self._client.close()  # type: ignore

    async def __aenter__(self) -> "AzureAppConfigurationProvider":
        await self._client.__aenter__()  # type: ignore
        for client in self._secret_clients.values():
            await client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.__aexit__(*args)  # type: ignore
        for client in self._secret_clients.values():
            await client.__aexit__()
