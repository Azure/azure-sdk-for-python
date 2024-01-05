# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import copy
import os
import json
import random
import time
import datetime
from threading import Lock
import logging
from typing import (
    Any,
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
    AzureAppConfigurationClient,
    FeatureFlagConfigurationSetting,
    SecretReferenceConfigurationSetting,
)
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError, ServiceRequestError, ServiceResponseError
from azure.keyvault.secrets import SecretClient, KeyVaultSecretIdentifier
from ._models import AzureAppConfigurationKeyVaultOptions, SettingSelector
from ._constants import (
    FEATURE_MANAGEMENT_KEY,
    FEATURE_FLAG_PREFIX,
    REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE,
    ServiceFabricEnvironmentVariable,
    AzureFunctionEnvironmentVariable,
    AzureWebAppEnvironmentVariable,
    ContainerAppEnvironmentVariable,
    KubernetesEnvironmentVariable,
    EMPTY_LABEL,
)
from ._user_agent import USER_AGENT

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

JSON = Union[str, Mapping[str, Any]]  # pylint: disable=unsubscriptable-object

logger = logging.getLogger(__name__)

min_uptime = 5


@overload
def load(
    endpoint: str,
    credential: "TokenCredential",
    *,
    selects: Optional[List[SettingSelector]] = None,
    trim_prefixes: Optional[List[str]] = None,
    key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = None,
    refresh_on: Optional[List[Tuple[str, str]]] = None,
    refresh_interval: int = 30,
    on_refresh_success: Optional[Callable] = None,
    on_refresh_error: Optional[Callable[[Exception], None]] = None,
    **kwargs
) -> "AzureAppConfigurationProvider":
    """
    Loads configuration settings from Azure App Configuration into a Python application.

    :param str endpoint: Endpoint for App Configuration resource.
    :param credential: Credential for App Configuration resource.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword selects: List of setting selectors to filter configuration settings
    :paramtype selects: Optional[List[~azure.appconfiguration.provider.SettingSelector]]
    :keyword trim_prefixes: List of prefixes to trim from configuration keys
    :paramtype trim_prefixes: Optional[List[str]]
    :keyword keyvault_credential: A credential for authenticating with the key vault. This is optional if
     keyvault_client_configs is provided.
    :paramtype keyvault_credential: ~azure.core.credentials.TokenCredential
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
    :paramtype on_refresh_error: Optional[Callable[[Exception], None]]
    :keyword on_refresh_error: Optional callback to be invoked when an error occurs while refreshing settings. If not
    specified, errors will be raised.
    """


@overload
def load(
    *,
    connection_string: str,
    selects: Optional[List[SettingSelector]] = None,
    trim_prefixes: Optional[List[str]] = None,
    key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = None,
    refresh_on: Optional[List[Tuple[str, str]]] = None,
    refresh_interval: int = 30,
    on_refresh_success: Optional[Callable] = None,
    on_refresh_error: Optional[Callable[[Exception], None]] = None,
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
    :paramtype keyvault_credential: ~azure.core.credentials.TokenCredential
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
    :paramtype on_refresh_error: Optional[Callable[[Exception], None]]
    :keyword on_refresh_error: Optional callback to be invoked when an error occurs while refreshing settings. If not
    specified, errors will be raised.
    """


def load(*args, **kwargs) -> "AzureAppConfigurationProvider":
    # pylint:disable=protected-access

    # Start by parsing kwargs
    endpoint: Optional[str] = kwargs.pop("endpoint", None)
    credential: Optional["TokenCredential"] = kwargs.pop("credential", None)
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
        provider._load_all(headers=headers)
    except Exception as e:
        _delay_failure(start_time)
        raise e

    # Refresh-All sentinels are not updated on load_all, as they are not necessarily included in the provider.
    for (key, label), etag in provider._refresh_on.items():
        if not etag:
            try:
                sentinel = provider._client.get_configuration_setting(key, label, headers=headers)
                provider._refresh_on[(key, label)] = sentinel.etag
            except HttpResponseError as e:
                if e.status_code == 404:
                    # If the sentinel is not found a refresh should be triggered when it is created.
                    logging.debug(
                        "WatchKey key: %s label %s was configured but not found. Refresh will be triggered if created.",
                        key,
                        label,
                    )
                else:
                    _delay_failure(start_time)
                    raise e
            except Exception as e:
                _delay_failure(start_time)
                raise e
    return provider


def _delay_failure(start_time: datetime.datetime) -> None:
    # We want to make sure we are up a minimum amount of time before we kill the process. Otherwise, we could get stuck
    # in a quick restart loop.
    min_time = datetime.timedelta(seconds=min_uptime)
    current_time = datetime.datetime.now()
    if current_time - start_time < min_time:
        time.sleep((min_time - (current_time - start_time)).total_seconds())


def _get_headers(request_type, **kwargs) -> str:
    headers = kwargs.pop("headers", {})
    if os.environ.get(REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE, default="").lower() != "true":
        correlation_context = "RequestType=" + request_type
        if (
            "keyvault_credential" in kwargs
            or "keyvault_client_configs" in kwargs
            or "secret_resolver" in kwargs
            or kwargs.pop("uses_key_vault", False)
        ):
            correlation_context += ",UsesKeyVault"
        host_type = ""
        if AzureFunctionEnvironmentVariable in os.environ:
            host_type = "AzureFunction"
        elif AzureWebAppEnvironmentVariable in os.environ:
            host_type = "AzureWebApp"
        elif ContainerAppEnvironmentVariable in os.environ:
            host_type = "ContainerApp"
        elif KubernetesEnvironmentVariable in os.environ:
            host_type = "Kubernetes"
        elif ServiceFabricEnvironmentVariable in os.environ:
            host_type = "ServiceFabric"
        if host_type:
            correlation_context += ",Host=" + host_type
        headers["Correlation-Context"] = correlation_context
    return headers


def _buildprovider(
    connection_string: Optional[str], endpoint: Optional[str], credential: Optional["TokenCredential"], **kwargs
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


def _resolve_keyvault_reference(
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
        return referenced_client.get_secret(keyvault_identifier.name, version=keyvault_identifier.version).value

    if provider._secret_resolver:
        return provider._secret_resolver(config.secret_id)

    raise ValueError("No Secret Client found for Key Vault reference %s" % (vault_url))


def _is_json_content_type(content_type: str) -> bool:
    if not content_type:
        return False

    content_type = content_type.strip().lower()
    mime_type = content_type.split(";")[0].strip()

    type_parts = mime_type.split("/")
    if len(type_parts) != 2:
        return False

    (main_type, sub_type) = type_parts
    if main_type != "application":
        return False

    sub_types = sub_type.split("+")
    if "json" in sub_types:
        return True

    return False


def _build_sentinel(setting: Union[str, Tuple[str, str]]) -> Tuple[str, str]:
    try:
        key, label = setting
    except IndexError:
        key = setting
        label = EMPTY_LABEL
    if "*" in key or "*" in label:
        raise ValueError("Wildcard key or label filters are not supported for refresh.")
    return key, label


class _RefreshTimer:
    """
    A timer that tracks the next refresh time and the number of attempts.
    """

    def __init__(self, **kwargs):
        self._interval: int = kwargs.pop("refresh_interval", 30)
        self._next_refresh_time: float = time.time() + self._interval
        self._attempts: int = 1
        self._min_backoff: int = (
            kwargs.pop("min_backoff", 30) if kwargs.get("min_backoff", 30) <= self._interval else self._interval
        )
        self._max_backoff: int = 600 if 600 <= self._interval else self._interval

    def reset(self) -> None:
        self._next_refresh_time = time.time() + self._interval
        self._attempts = 1

    def backoff(self) -> None:
        self._next_refresh_time = time.time() + self._calculate_backoff() / 1000
        self._attempts += 1

    def needs_refresh(self) -> bool:
        return time.time() >= self._next_refresh_time

    def _calculate_backoff(self) -> float:
        max_attempts = 63
        millisecond = 1000  # 1 Second in milliseconds

        min_backoff_milliseconds = self._min_backoff * millisecond
        max_backoff_milliseconds = self._max_backoff * millisecond

        if self._max_backoff <= self._min_backoff:
            return min_backoff_milliseconds

        calculated_milliseconds = max(1, min_backoff_milliseconds) * (1 << min(self._attempts, max_attempts))

        if calculated_milliseconds > max_backoff_milliseconds or calculated_milliseconds <= 0:
            calculated_milliseconds = max_backoff_milliseconds

        return min_backoff_milliseconds + (
            random.uniform(0.0, 1.0) * (calculated_milliseconds - min_backoff_milliseconds)
        )


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

    def refresh(self, **kwargs) -> None:
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
                    updated_sentinel = self._client.get_configuration_setting(
                        key=key,
                        label=label,
                        etag=etag,
                        match_condition=MatchConditions.IfModified,
                        headers=headers,
                        **kwargs
                    )
                    if updated_sentinel is not None:
                        logging.debug(
                            "Refresh all triggered by key: %s label %s.",
                            key,
                            label,
                        )
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
                self._load_all(headers=headers, sentinel_keys=updated_sentinel_keys, **kwargs)
            # Even if we don't need to refresh, we should reset the timer
            self._refresh_timer.reset()
            success = True
        except (ServiceRequestError, ServiceResponseError, HttpResponseError) as e:
            # If we get an error we should retry sooner than the next refresh interval
            if self._on_refresh_error:
                self._on_refresh_error(e)
                return
            raise
        finally:
            self._refresh_lock.release()
            if not success:
                self._refresh_timer.backoff()
            elif need_refresh and self._on_refresh_success:
                self._on_refresh_success()

    def _load_all(self, **kwargs):
        configuration_settings = {}
        sentinel_keys = kwargs.pop("sentinel_keys", self._refresh_on)
        for select in self._selects:
            configurations = self._client.list_configuration_settings(
                key_filter=select.key_filter, label_filter=select.label_filter, **kwargs
            )
            for config in configurations:
                key = self._process_key_name(config)
                value = self._process_key_value(config)
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
        with self._update_lock:
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

    def _process_key_value(self, config):
        if isinstance(config, SecretReferenceConfigurationSetting):
            return _resolve_keyvault_reference(config, self)
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
        with self._update_lock:
            return list(self._dict.keys())

    def items(self) -> Iterable[Tuple[str, Union[str, JSON]]]:
        """
        Returns a set-like object of key-value pairs loaded from Azure App Configuration. Any values that are Key Vault
         references will be resolved.

        :return: A set-like object of key-value pairs loaded from Azure App Configuration.
        :rtype: Iterable[Tuple[str, Union[str, JSON]]]
        """
        with self._update_lock:
            return copy.deepcopy(self._dict.items())

    def values(self) -> Iterable[Union[str, JSON]]:
        """
        Returns a list of values loaded from Azure App Configuration. Any values that are Key Vault references will be
        resolved.

        :return: A list of values loaded from Azure App Configuration. The values are either Strings or JSON objects,
        based on there content type.
        :rtype: Iterable[[str], [JSON]]
        """
        with self._update_lock:
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
        with self._update_lock:
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

    def close(self) -> None:
        """
        Closes the connection to Azure App Configuration.
        """
        for client in self._secret_clients.values():
            client.close()
        self._client.close()

    def __enter__(self) -> "AzureAppConfigurationProvider":
        self._client.__enter__()
        for client in self._secret_clients.values():
            client.__enter__()
        return self

    def __exit__(self, *args) -> None:
        self._client.__exit__(*args)
        for client in self._secret_clients.values():
            client.__exit__()
