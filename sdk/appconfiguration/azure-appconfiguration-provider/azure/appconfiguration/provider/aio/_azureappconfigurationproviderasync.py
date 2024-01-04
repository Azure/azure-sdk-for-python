# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json
import copy
from threading import Lock
import datetime
import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    Mapping,
    Optional,
    overload,
    List,
    Tuple,
    TYPE_CHECKING,
    Union,
)

from azure.appconfiguration import (  # pylint:disable=no-name-in-module
    FeatureFlagConfigurationSetting,
    SecretReferenceConfigurationSetting,
)
from azure.appconfiguration.aio import AzureAppConfigurationClient
from azure.keyvault.secrets.aio import SecretClient
from azure.keyvault.secrets import KeyVaultSecretIdentifier
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError, ServiceRequestError, ServiceResponseError

from .._models import AzureAppConfigurationKeyVaultOptions, SettingSelector
from .._constants import (
    FEATURE_MANAGEMENT_KEY,
    FEATURE_FLAG_PREFIX,
    EMPTY_LABEL,
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

JSON = Union[str, Mapping[str, Any]]  # pylint: disable=unsubscriptable-object


@overload
async def load(
    endpoint: str,
    credential: "AsyncTokenCredential",
    *,
    selects: Optional[List[SettingSelector]] = None,
    trim_prefixes: Optional[List[str]] = None,
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
    :paramtype on_refresh_success: Optional[Callable]
    :keyword on_refresh_success: Optional callback to be invoked when a change is found and a successful refresh has
    happened.
    :paramtype on_refresh_error: Optional[Callable[[Exception], Awaitable[None]]]
    :keyword on_refresh_error: Optional callback to be invoked when an error occurs while refreshing settings. If not
    specified, errors will be raised.
    """


@overload
async def load(
    *,
    connection_string: str,
    selects: Optional[List[SettingSelector]] = None,
    trim_prefixes: Optional[List[str]] = None,
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
    :paramtype on_refresh_success: Optional[Callable]
    :keyword on_refresh_success: Optional callback to be invoked when a change is found and a successful refresh has
    happened.
    :paramtype on_refresh_error: Optional[Callable[[Exception], Awaitable[None]]]
    :keyword on_refresh_error: Optional callback to be invoked when an error occurs while refreshing settings. If not
    specified, errors will be raised.
    """


async def load(*args, **kwargs) -> "AzureAppConfigurationProvider":
    # pylint:disable=protected-access
    # Will remove when merged with Refresh Async PR
    # pylint:disable=too-many-statements
    # pylint:disable=too-many-branches

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
    provider = _buildprovider(connection_string, endpoint, credential, **kwargs)

    try:
        await provider._load_all(headers=headers)
    except Exception as e:
        _delay_failure(start_time)
        raise e

    # Refresh-All sentinels are not updated on load_all, as they are not necessarily included in the provider.
    for (key, label), etag in provider._refresh_on.items():
        if not etag:
            try:
                sentinel = await provider._client.get_configuration_setting(key, label, headers=headers)
                provider._refresh_on[(key, label)] = sentinel.etag
            except HttpResponseError as e:
                if e.status_code == 404:
                    # If the sentinel is not found a refresh should be triggered when it is created.
                    logging.debug(
                        "WatchKey key: %s label %s was configured but not found. Refresh will be triggered if created.",
                        key,
                        label,
                    )
                    provider._refresh_on[(key, label)] = None
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
    provider._client = AzureAppConfigurationClient(
        endpoint,
        credential,
        user_agent=user_agent,
        retry_total=retry_total,
        retry_backoff_max=retry_backoff_max,
        **kwargs
    )
    return provider


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
        return (await referenced_client.get_secret(keyvault_identifier.name, version=keyvault_identifier.version)).value

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
        self._trim_prefixes: List[str] = []
        self._client: Optional[AzureAppConfigurationClient] = None
        self._secret_clients: Dict[str, SecretClient] = {}
        self._selects: List[SettingSelector] = kwargs.pop(
            "selects", [SettingSelector(key_filter="*", label_filter=EMPTY_LABEL)]
        )

        trim_prefixes: List[str] = kwargs.pop("trim_prefixes", [])
        self._trim_prefixes = sorted(trim_prefixes, key=len, reverse=True)

        refresh_on: List[Tuple[str, str]] = kwargs.pop("refresh_on", None) or []
        self._refresh_on: Mapping[Tuple[str, str] : Optional[str]] = {_build_sentinel(s): None for s in refresh_on}
        self._refresh_timer: _RefreshTimer = _RefreshTimer(**kwargs)
        self._on_refresh_success: Optional[Callable] = kwargs.pop("on_refresh_success", None)
        self._on_refresh_error: Optional[Callable[[Exception], None]] = kwargs.pop("on_refresh_error", None)
        self._keyvault_credential = kwargs.pop("keyvault_credential", None)
        self._secret_resolver = kwargs.pop("secret_resolver", None)
        self._keyvault_client_configs = kwargs.pop("keyvault_client_configs", {})
        self._uses_key_vault = (
            self._keyvault_credential is not None
            or self._keyvault_client_configs is not None
            or self._secret_resolver is not None
        )
        self._update_lock = Lock()
        self._refresh_lock = Lock()

    async def refresh(self, **kwargs) -> None:
        if not self._refresh_on:
            logging.debug("Refresh called but no refresh options set.")
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
            updated_sentinel_keys = dict(self._refresh_on)
            headers = _get_headers("Watch", uses_key_vault=self._uses_key_vault, **kwargs)
            for (key, label), etag in updated_sentinel_keys.items():
                try:
                    updated_sentinel = await self._client.get_configuration_setting(
                        key=key,
                        label=label,
                        etag=etag,
                        match_condition=MatchConditions.IfModified,
                        headers=headers,
                        **kwargs
                    )
                    if updated_sentinel is not None:
                        logging.debug("Refresh all triggered by key: %s label %s.", key, label)
                        need_refresh = True

                        updated_sentinel_keys[(key, label)] = updated_sentinel.etag
                except HttpResponseError as e:
                    if e.status_code == 404:
                        if etag is not None:
                            # If the sentinel is not found, it means the key/label was deleted, so we should refresh
                            logging.debug("Refresh all triggered by key: %s label %s.", key, label)
                            need_refresh = True
                            updated_sentinel_keys[(key, label)] = None
                    else:
                        raise e
            # Need to only update once, no matter how many sentinels are updated
            if need_refresh:
                await self._load_all(headers=headers, sentinel_keys=updated_sentinel_keys, **kwargs)
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

    async def _load_all(self, **kwargs):
        configuration_settings = {}
        sentinel_keys = kwargs.pop("sentinel_keys", self._refresh_on)
        for select in self._selects:
            configurations = self._client.list_configuration_settings(
                key_filter=select.key_filter, label_filter=select.label_filter, **kwargs
            )
            async for config in configurations:
                key = self._process_key_name(config)
                value = await self._process_key_value(config)

                if isinstance(config, FeatureFlagConfigurationSetting):
                    feature_management = configuration_settings.get(FEATURE_MANAGEMENT_KEY, {})
                    feature_management[key] = value
                    if FEATURE_MANAGEMENT_KEY not in configuration_settings:
                        configuration_settings[FEATURE_MANAGEMENT_KEY] = feature_management
                else:
                    configuration_settings[key] = value
                # Every time we run load_all, we should update the etag of our refresh sentinels
                # so they stay up-to-date.
                # Sentinel keys will have unprocessed key names, so we need to use the original key.
                if (config.key, config.label) in self._refresh_on:
                    sentinel_keys[(config.key, config.label)] = config.etag
        self._refresh_on = sentinel_keys
        self._dict = configuration_settings

    def _process_key_name(self, config):
        trimmed_key = config.key
        # Trim the key if it starts with one of the prefixes provided
        for trim in self._trim_prefixes:
            if config.key.startswith(trim):
                trimmed_key = config.key[len(trim) :]
                break
        if isinstance(config, FeatureFlagConfigurationSetting) and trimmed_key.startswith(FEATURE_FLAG_PREFIX):
            return trimmed_key[len(FEATURE_FLAG_PREFIX) :]
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

    def __getitem__(self, key: str) -> str:
        # pylint:disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
        """
        Returns the value of the specified key.
        """
        return self._dict[key]

    def __iter__(self) -> Iterable[str]:
        return self._dict.__iter__()

    def __len__(self) -> int:
        return len(self._dict)

    def __contains__(self, __x: object) -> bool:
        # pylint:disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
        """
        Returns True if the configuration settings contains the specified key.
        """
        return self._dict.__contains__(__x)

    def keys(self) -> Iterable[str]:
        """
        Returns a list of keys loaded from Azure App Configuration.

        :return: A list of keys loaded from Azure App Configuration.
        :rtype: Iterable[str]
        """
        return list(self._dict.keys())

    def items(self) -> Iterable[Tuple[str, Union[str, JSON]]]:
        """
        Returns a set-like object of key-value pairs loaded from Azure App Configuration. Any values that are Key Vault
         references will be resolved.

        :return: A set-like object of key-value pairs loaded from Azure App Configuration.
        :rtype: Iterable[Tuple[str, Union[str, JSON]]]
        """
        return copy.deepcopy(self._dict.items())

    def values(self) -> Iterable[Union[str, JSON]]:
        """
        Returns a list of values loaded from Azure App Configuration. Any values that are Key Vault references will be
        resolved.

        :return: A list of values loaded from Azure App Configuration. The values are either Strings or JSON objects,
        based on there content type.
        :rtype: Iterable[[str], [JSON]]
        """
        return copy.deepcopy(list((self._dict.values())))

    def get(self, key: str, default: Optional[str] = None) -> Union[str, JSON]:
        """
        Returns the value of the specified key. If the key does not exist, returns the default value.

        :param str key: The key of the value to get.
        :param default: The default value to return.
        :type: str or None
        :return: The value of the specified key.
        :rtype: Union[str, JSON]
        """
        return copy.deepcopy(self._dict.get(key, default))

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
        await self._client.close()

    async def __aenter__(self) -> "AzureAppConfigurationProvider":
        await self._client.__aenter__()
        for client in self._secret_clients.values():
            await client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.__aexit__(*args)
        for client in self._secret_clients.values():
            await client.__aexit__()
