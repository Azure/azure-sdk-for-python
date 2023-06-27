# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
import json
import random
from datetime import datetime, timedelta
from functools import wraps
import logging
from azure.core.exceptions import HttpResponseError
from azure.core import MatchConditions
from typing import (
    Any,
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
from azure.appconfiguration import (
    AzureAppConfigurationClient,
    FeatureFlagConfigurationSetting,
    SecretReferenceConfigurationSetting,
)
from azure.keyvault.secrets import SecretClient, KeyVaultSecretIdentifier
from ._models import (
    AzureAppConfigurationKeyVaultOptions,
    SettingSelector,
    AzureAppConfigurationRefreshOptions,
)
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


@overload
def load(
    endpoint: str,
    credential: "TokenCredential",
    *,
    selects: Optional[List[SettingSelector]] = None,
    trim_prefixes: Optional[List[str]] = None,
    key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = None,
    refresh_options: Optional[AzureAppConfigurationRefreshOptions] = None,
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
    :keyword key_vault_options: Options for resolving Key Vault references
    :paramtype key_vault_options: ~azure.appconfiguration.provider.AzureAppConfigurationKeyVaultOptions
    :keyword refresh_options: Options for refreshing configuration settings
    :paramtype refresh_options: ~azure.appconfiguration.provider.AzureAppConfigurationRefreshOptions
    """
    ...


@overload
def load(
    *,
    connection_string: str,
    selects: Optional[List[SettingSelector]] = None,
    trim_prefixes: Optional[List[str]] = None,
    key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = None,
    refresh_options: Optional[AzureAppConfigurationRefreshOptions] = None,
    **kwargs
) -> "AzureAppConfigurationProvider":
    """
    Loads configuration settings from Azure App Configuration into a Python application.

    :keyword str connection_string: Connection string for App Configuration resource.
    :keyword selects: List of setting selectors to filter configuration settings
    :paramtype selects: Optional[List[~azure.appconfiguration.provider.SettingSelector]]
    :keyword trim_prefixes: List of prefixes to trim from configuration keys
    :paramtype trim_prefixes: Optional[List[str]]
    :keyword key_vault_options: Options for resolving Key Vault references
    :paramtype key_vault_options: ~azure.appconfiguration.provider.AzureAppConfigurationKeyVaultOptions
    :keyword refresh_options: Options for refreshing configuration settings
    :paramtype refresh_options: ~azure.appconfiguration.provider.AzureAppConfigurationRefreshOptions
    """
    ...


def load(*args, **kwargs) -> "AzureAppConfigurationProvider":
    # pylint:disable=protected-access

    # Start by parsing kwargs
    endpoint: Optional[str] = kwargs.pop("endpoint", None)
    credential: Optional["TokenCredential"] = kwargs.pop("credential", None)
    connection_string: Optional[str] = kwargs.pop("connection_string", None)

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

    provider = _buildprovider(connection_string, endpoint, credential, **kwargs)
    provider._load_all()

    if provider._configuration_refresh.refresh_options is not None:
        for register in provider._configuration_refresh.refresh_options._refresh_registrations:
            key = provider._client.get_configuration_setting(register.key_filter, register.label_filter)
            register.etag = key.etag
    return provider


def _get_headers(key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions], **kwargs) -> str:
    headers = kwargs.pop("headers", {})
    if os.environ.get(REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE, default="").lower() != "true":
        correlation_context = "RequestType=Startup"
        if key_vault_options and (
            key_vault_options.credential or key_vault_options.client_configs or key_vault_options.secret_resolver
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
    headers = _get_headers(provider._key_vault_options, **kwargs)
    retry_total = kwargs.pop("retry_total", 2)
    retry_backoff_max = kwargs.pop("retry_backoff_max", 60)

    if connection_string:
        provider._client = AzureAppConfigurationClient.from_connection_string(
            connection_string,
            user_agent=USER_AGENT,
            headers=headers,
            retry_total=retry_total,
            retry_backoff_max=retry_backoff_max,
            **kwargs
        )
        return provider
    provider._client = AzureAppConfigurationClient(
        endpoint,
        credential,
        user_agent=USER_AGENT,
        headers=headers,
        retry_total=retry_total,
        retry_backoff_max=retry_backoff_max,
        **kwargs
    )
    return provider


def _resolve_keyvault_reference(config, provider: "AzureAppConfigurationProvider") -> str:
    # pylint:disable=protected-access
    if provider._key_vault_options is None:
        raise ValueError("Key Vault options must be set to resolve Key Vault references.")

    if config.secret_id is None:
        raise ValueError("Key Vault reference must have a uri value.")

    key_vault_identifier = KeyVaultSecretIdentifier(config.secret_id)

    vault_url = key_vault_identifier.vault_url + "/"

    # pylint:disable=protected-access
    referenced_client = provider._secret_clients.get(vault_url, None)

    vault_config = provider._key_vault_options.client_configs.get(vault_url, {})
    credential = vault_config.pop("credential", provider._key_vault_options.credential)

    if referenced_client is None and credential is not None:
        referenced_client = SecretClient(vault_url=vault_url, credential=credential, **vault_config)
        provider._secret_clients[vault_url] = referenced_client

    if referenced_client:
        return referenced_client.get_secret(key_vault_identifier.name, version=key_vault_identifier.version).value

    if provider._key_vault_options.secret_resolver is not None:
        return provider._key_vault_options.secret_resolver(config.secret_id)

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


class AzureAppConfigurationProvider(Mapping[str, Union[str, JSON]]):
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
        self._key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = kwargs.pop("key_vault_options", None)
        self._selects: List[SettingSelector] = kwargs.pop(
            "selects", [SettingSelector(key_filter="*", label_filter=EMPTY_LABEL)]
        )
        self._sentinel_keys: List[str] = []

        trim_prefixes: List[str] = kwargs.pop("trim_prefixes", [])
        self._trim_prefixes = sorted(trim_prefixes, key=len, reverse=True)
        self._configuration_refresh = self._ConfigurationRefresh(**kwargs)

    def refresh_configuration_settings(self, func):
        @wraps(func)
        def refresh_wrapper(*args, **kwargs):
            self.refresh()
            return func(*args, **kwargs)

        return refresh_wrapper

    def refresh(self, **kwargs) -> None:
        # pylint:disable=protected-access
        refresh_registrations = self._configuration_refresh.refresh_options._refresh_registrations
        if len(refresh_registrations) == 0:
            logging.debug("Refresh called but no refresh options set.")
            self._configuration_refresh.refresh_options._on_error()
            return

        if datetime.now() < self._configuration_refresh.next_refresh_time:
            return

        try:
            # pylint:disable=protected-access
            for registration in refresh_registrations:
                if registration.refresh_all:
                    updated_sentinel = self._client.get_configuration_setting(
                        key=registration.key_filter, label=registration.label_filter, etag=registration.etag, match_condition=MatchConditions.IfModified,  **kwargs
                    )
                    if updated_sentinel != None:
                        logging.debug(
                            "Refresh all triggered by key: %s label %s.",
                            registration.key_filter,
                            registration.label_filter,
                        )
                        updated_registration = registration
                        updated_registration_etag = updated_sentinel.etag
                        self._load_all(**kwargs)
                        updated_registration.etag = updated_registration_etag
                        self._configuration_refresh.updated_configurations()
                        return
        except HttpResponseError as ex:
            # refresh should never throw an exception
            self._configuration_refresh.failed_update(ex, "Refresh all trigger failed by exception: %s")
            return

        # Only update individual keys if the refresh_all didn't trigger
        updated_dict = self._dict.copy()
        updated_registrations = refresh_registrations.copy()
        updated_keys = False

        try:
            for registration in updated_registrations:
                if not registration.refresh_all:
                    updated_sentinel = self._client.get_configuration_setting(
                        key=registration.key_filter, label=registration.label_filter, etag=registration.etag, match_condition=MatchConditions.IfModified,  **kwargs
                    )
                    if updated_sentinel != None:
                        registration.etag = updated_sentinel.etag
                        updated_dict[self._proccess_key_name(updated_sentinel)] = self._proccess_key_value(
                            updated_sentinel
                        )
                        logging.debug(
                            "Refresh triggered for key: %s label: %s",
                            registration.key_filter,
                            registration.label_filter,
                        )
                        updated_keys = True
            if updated_keys:
                self._dict = updated_dict
                # pylint:disable=protected-access
                self._configuration_refresh.refresh_options._refresh_registrations = updated_registrations
                self._configuration_refresh.updated_configurations()
        except HttpResponseError as ex:
            # refresh should never throw an exception
            self._configuration_refresh.failed_update(
                ex,
                "An error occurred while checking for configuration updates. \
                %s attempts have been made.\n %r",
            )

    def _load_all(self, **kwargs):
        configuration_settings = {}
        for select in self._selects:
            configurations = self._client.list_configuration_settings(
                key_filter=select.key_filter, label_filter=select.label_filter, **kwargs
            )
            for config in configurations:
                key = self._proccess_key_name(config)
                value = self._proccess_key_value(config)

                if isinstance(config, FeatureFlagConfigurationSetting):
                    feature_management = self._dict.get(FEATURE_MANAGEMENT_KEY, {})
                    feature_management[key] = value
                    if FEATURE_MANAGEMENT_KEY not in self.keys():
                        configuration_settings[FEATURE_MANAGEMENT_KEY] = feature_management
                else:
                    configuration_settings[key] = value
        self._dict = configuration_settings

    def _proccess_key_name(self, config):
        trimmed_key = config.key
        # Trim the key if it starts with one of the prefixes provided
        for trim in self._trim_prefixes:
            if config.key.startswith(trim):
                trimmed_key = config.key[len(trim) :]
                break
        if isinstance(config, FeatureFlagConfigurationSetting) and trimmed_key.startswith(FEATURE_FLAG_PREFIX):
            return trimmed_key[len(FEATURE_FLAG_PREFIX) :]
        return trimmed_key

    def _proccess_key_value(self, config):
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
        """
        Returns the value of the specified key.
        """
        return self._dict[key]

    def __iter__(self) -> Iterable[str]:
        return self._dict.__iter__()

    def __len__(self) -> int:
        return len(self._dict)

    def __contains__(self, __x: object) -> bool:
        """
        Returns True if the configuration settings contains the specified key.
        """
        return self._dict.__contains__(__x)

    def keys(self) -> Iterable[str]:
        """
        Returns a list of keys loaded from Azure App Configuration.
        """
        return self._dict.keys()

    def items(self) -> Iterable[Tuple[str, str]]:
        """
        Returns a list of key-value pairs loaded from Azure App Configuration. Any values that are Key Vault references
        will be resolved.
        """
        return self._dict.items()

    def values(self) -> Iterable[str]:
        """
        Returns a list of values loaded from Azure App Configuration. Any values that are Key Vault references will be
        resolved.
        """
        return self._dict.values()

    def get(self, key: str, default: Optional[str] = None) -> str:
        """
        Returns the value of the specified key. If the key does not exist, returns the default value.
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

    class _ConfigurationRefresh:
        def __init__(self, **kwargs):
            self.refresh_options: Optional[AzureAppConfigurationRefreshOptions] = kwargs.pop(
                "refresh_options", AzureAppConfigurationRefreshOptions()
            )
            if self.refresh_options is not None:
                self.next_refresh_time = datetime.now() + timedelta(seconds=self.refresh_options.refresh_interval)
            self.attempts = 1
            self.min_backoff: Optional[int] = kwargs.pop("min_backoff", 30)
            self.max_backoff: Optional[int] = kwargs.pop("max_backoff", 600)

        def updated_configurations(self):
            # pylint:disable=protected-access
            self.next_refresh_time = datetime.now() + timedelta(seconds=self.refresh_options.refresh_interval)
            self.attempts = 1
            self.refresh_options._callback()

        def failed_update(self, error, message):
            logging.warning(message, self.attempts, error)
            # Refresh All or None, any failure will trigger a backoff
            # pylint:disable=protected-access
            self.next_refresh_time = datetime.now() + timedelta(milliseconds=min(self.calculate_backoff(), self.refresh_options.refresh_interval/1000))
            self.attempts += 1
            self.refresh_options._on_error()

        def calculate_backoff(self):
            max_attempts = 30
            millisecond = 1000  # 1 Second in milliseconds

            min_backoff_milliseconds = self.min_backoff * millisecond
            max_backoff_milliseconds = self.max_backoff * millisecond

            if self.attempts <= 1 or self.max_backoff <= self.min_backoff:
                return min_backoff_milliseconds

            calculated_milliseconds = max(1, min_backoff_milliseconds) * (1 << min(self.attempts, max_attempts))

            if calculated_milliseconds > max_backoff_milliseconds or calculated_milliseconds <= 0:
                calculated_milliseconds = max_backoff_milliseconds

            return min_backoff_milliseconds + (
                random.uniform(0.0, 1.0) * (calculated_milliseconds - min_backoff_milliseconds)
            )
