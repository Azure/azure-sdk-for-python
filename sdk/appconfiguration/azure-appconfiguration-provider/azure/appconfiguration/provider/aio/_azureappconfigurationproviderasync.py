# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json
import datetime
from threading import Lock
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
from azure.appconfiguration import (  # type:ignore # pylint:disable=no-name-in-module
    FeatureFlagConfigurationSetting,
    SecretReferenceConfigurationSetting,
)
from azure.keyvault.secrets.aio import SecretClient
from azure.keyvault.secrets import KeyVaultSecretIdentifier
from azure.core.exceptions import AzureError, HttpResponseError

from .._models import AzureAppConfigurationKeyVaultOptions, SettingSelector
from .._constants import (
    FEATURE_MANAGEMENT_KEY,
    FEATURE_FLAG_KEY,
    EMPTY_LABEL,
)
from ._async_client_manager import AsyncConfigurationClientManager
from .._azureappconfigurationprovider import (
    _get_headers,
    _RefreshTimer,
    _build_sentinel,
    _delay_failure,
    _is_json_content_type,
)
from .._user_agent import USER_AGENT

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential

JSON = Mapping[str, Any]
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
    **kwargs
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
    """


async def load(*args, **kwargs) -> "AzureAppConfigurationProvider":
    # pylint:disable=protected-access
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

    uses_key_vault = (
        "keyvault_credential" in kwargs
        or "keyvault_client_configs" in kwargs
        or "secret_resolver" in kwargs
        or kwargs.get("uses_key_vault", False)
    )

    provider = await _buildprovider(connection_string, endpoint, credential, uses_key_vault=uses_key_vault, **kwargs)
    # Discovering replicas outside of init as it's async
    await provider._replica_client_manager.setup_initial_clients()  # pylint:disable=protected-access
    headers = _get_headers(
        kwargs.pop("headers", {}),
        "Startup",
        provider._replica_client_manager.get_client_count() - 1,  # pylint:disable=protected-access
        provider._feature_flag_enabled,  # pylint:disable=protected-access
        provider._feature_filter_usage,  # pylint:disable=protected-access
        provider._uses_key_vault,  # pylint:disable=protected-access
    )

    try:
        await provider._load_all(headers=headers)  # pylint:disable=protected-access
    except Exception as e:
        _delay_failure(start_time)
        raise e
    return provider


async def _buildprovider(
    connection_string: Optional[str], endpoint: Optional[str], credential: Optional["AsyncTokenCredential"], **kwargs
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
        endpoint = kwargs.pop("endpoint", None)
        self._origin_endpoint = endpoint

        if "user_agent" in kwargs:
            user_agent = kwargs.pop("user_agent") + " " + USER_AGENT
        else:
            user_agent = USER_AGENT

        interval: int = kwargs.get("refresh_interval", 30)
        if interval < 1:
            raise ValueError("Refresh interval must be greater than or equal to 1 second.")

        min_backoff: int = min(kwargs.pop("min_backoff", 30), interval)
        max_backoff: int = min(kwargs.pop("max_backoff", 600), interval)

        self._replica_client_manager = AsyncConfigurationClientManager(
            connection_string=kwargs.pop("connection_string", None),
            endpoint=endpoint,
            credential=kwargs.pop("credential", None),
            user_agent=user_agent,
            retry_total=kwargs.pop("retry_total", 2),
            retry_backoff_max=kwargs.pop("retry_backoff_max", 60),
            replica_discovery_enabled=kwargs.pop("replica_discovery_enabled", True),
            min_backoff_sec=min_backoff,
            max_backoff_sec=max_backoff,
            **kwargs
        )
        self._dict: Dict[str, Any] = {}
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
        error_message = """
                        Failed to refresh configuration settings from Azure App Configuration.
                        """
        exception: Exception = RuntimeError(error_message)
        try:
            await self._replica_client_manager.refresh_clients()
            active_clients = self._replica_client_manager.get_active_clients()

            headers = _get_headers(
                kwargs.pop("headers", {}),
                "Watch",
                self._replica_client_manager.get_client_count() - 1,
                self._feature_flag_enabled,
                self._feature_filter_usage,
                self._uses_key_vault,
            )
            for client in active_clients:
                try:
                    if self._refresh_on:
                        need_refresh, self._refresh_on, configuration_settings = (
                            await client.refresh_configuration_settings(
                                self._selects, self._refresh_on, headers, **kwargs
                            )
                        )
                        configuration_settings_processed = {}
                        for config in configuration_settings:
                            key = self._process_key_name(config)
                            value = await self._process_key_value(config)
                            configuration_settings_processed[key] = value
                        if self._feature_flag_enabled:
                            configuration_settings_processed[FEATURE_MANAGEMENT_KEY] = self._dict[
                                FEATURE_MANAGEMENT_KEY
                            ]
                        if need_refresh:
                            self._dict = configuration_settings_processed
                    if self._feature_flag_refresh_enabled:
                        need_ff_refresh, self._refresh_on_feature_flags, feature_flags, filters_used = (
                            await client.refresh_feature_flags(
                                self._refresh_on_feature_flags, self._feature_flag_selectors, headers, **kwargs
                            )
                        )
                        self._feature_filter_usage = filters_used

                        if need_refresh or need_ff_refresh:
                            self._dict[FEATURE_MANAGEMENT_KEY] = {}
                            self._dict[FEATURE_MANAGEMENT_KEY][FEATURE_FLAG_KEY] = feature_flags
                    # Even if we don't need to refresh, we should reset the timer
                    self._refresh_timer.reset()
                    success = True
                    break
                except AzureError as e:
                    exception = e
                    self._replica_client_manager.backoff(client)

            if not success:
                self._refresh_timer.backoff()
                if self._on_refresh_error:
                    self._on_refresh_error(exception)
                    return
                raise exception
            if self._on_refresh_success:
                await self._on_refresh_success()
        finally:
            self._refresh_lock.release()

    async def _load_all(self, **kwargs):
        active_clients = self._replica_client_manager.get_active_clients()

        for client in active_clients:
            try:
                configuration_settings, sentinel_keys = await client.load_configuration_settings(
                    self._selects, self._refresh_on, **kwargs
                )
                configuration_settings_processed = {}
                for config in configuration_settings:
                    key = self._process_key_name(config)
                    value = await self._process_key_value(config)
                    configuration_settings_processed[key] = value
                if self._feature_flag_enabled:
                    feature_flags, feature_flag_sentinel_keys, used_filters = await client.load_feature_flags(
                        self._feature_flag_selectors, self._feature_flag_refresh_enabled, **kwargs
                    )
                    self._feature_filter_usage = used_filters
                    configuration_settings_processed[FEATURE_MANAGEMENT_KEY] = {}
                    configuration_settings_processed[FEATURE_MANAGEMENT_KEY][FEATURE_FLAG_KEY] = feature_flags
                    self._refresh_on_feature_flags = feature_flag_sentinel_keys
                for (key, label), etag in self._refresh_on.items():
                    if not etag:
                        try:
                            headers = kwargs.get("headers", {})
                            sentinel = await client.get_configuration_setting(
                                key, label, headers=headers
                            )  # type:ignore
                            self._refresh_on[(key, label)] = sentinel.etag  # type:ignore
                        except HttpResponseError as e:
                            if e.status_code == 404:
                                # If the sentinel is not found a refresh should be triggered when it is created.
                                logging.debug(
                                    """
                                    WatchKey key: %s label %s was configured but not found. Refresh will be triggered
                                    if created.
                                    """,
                                    key,
                                    label,
                                )
                                self._refresh_on[(key, label)] = None  # type: ignore
                            else:
                                raise e
                with self._update_lock:
                    self._refresh_on = sentinel_keys
                    self._dict = configuration_settings_processed
                return
            except AzureError:
                self._replica_client_manager.backoff(client)
        raise RuntimeError(
            "Failed to load configuration settings. No Azure App Configuration stores successfully loaded from."
        )

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
        with self._update_lock:
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
        with self._update_lock:
            return self._dict.keys()

    def items(self) -> ItemsView[str, Union[str, Mapping[str, Any]]]:
        """
        Returns a set-like object of key-value pairs loaded from Azure App Configuration. Any values that are Key Vault
         references will be resolved.

        :return: A set-like object of key-value pairs loaded from Azure App Configuration.
        :rtype: ItemsView[str, Union[str, Mapping[str, Any]]]
        """
        with self._update_lock:
            return self._dict.items()

    def values(self) -> ValuesView[Union[str, Mapping[str, Any]]]:
        """
        Returns a list of values loaded from Azure App Configuration. Any values that are Key Vault references will be
        resolved.

        :return: A list of values loaded from Azure App Configuration. The values are either Strings or JSON objects,
         based on there content type.
        :rtype: ValuesView[Union[str, Mapping[str, Any]]]
        """
        with self._update_lock:
            return (self._dict).values()

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
        with self._update_lock:
            return self._dict.get(key, default)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AzureAppConfigurationProvider):
            return False
        if self._dict != other._dict:
            return False
        if self._trim_prefixes != other._trim_prefixes:
            return False
        return self._replica_client_manager == other._replica_client_manager

    def __ne__(self, other: Any) -> bool:
        return not self == other

    async def close(self) -> None:
        """
        Closes the connection to Azure App Configuration.
        """
        for client in self._secret_clients.values():
            await client.close()
        await self._replica_client_manager.close()

    async def __aenter__(self) -> "AzureAppConfigurationProvider":
        await self._replica_client_manager.__aenter__()
        for client in self._secret_clients.values():
            await client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._replica_client_manager.__aexit__(*args)
        for client in self._secret_clients.values():
            await client.__aexit__()
