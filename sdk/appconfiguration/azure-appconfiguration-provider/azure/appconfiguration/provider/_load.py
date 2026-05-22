# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import datetime
from typing import (
    Callable,
    List,
    Mapping,
    Optional,
    Tuple,
    overload,
)
from azure.core.credentials import TokenCredential
from ._constants import (
    DEFAULT_STARTUP_TIMEOUT,
)
from ._models import AzureAppConfigurationKeyVaultOptions, SettingSelector
from ._utils import (
    delay_failure,
    process_load_parameters,
    sdk_allowed_kwargs,
)
from ._azureappconfigurationprovider import (
    AzureAppConfigurationProvider,
    JSON,
    _buildprovider,
)


@overload
def load(  # pylint: disable=docstring-keyword-should-match-keyword-only
    endpoint: str,
    credential: "TokenCredential",
    *,
    selects: Optional[List[SettingSelector]] = None,
    trim_prefixes: Optional[List[str]] = None,
    keyvault_credential: Optional["TokenCredential"] = None,
    keyvault_client_configs: Optional[Mapping[str, JSON]] = None,
    secret_resolver: Optional[Callable[[str], str]] = None,
    key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = None,
    refresh_on: Optional[List[Tuple[str, str]]] = None,
    refresh_interval: int = 30,
    refresh_enabled: Optional[bool] = None,
    on_refresh_success: Optional[Callable] = None,
    on_refresh_error: Optional[Callable[[Exception], None]] = None,
    feature_flag_enabled: bool = False,
    feature_flag_selectors: Optional[List[SettingSelector]] = None,
    feature_flag_refresh_enabled: bool = False,
    startup_timeout: int = DEFAULT_STARTUP_TIMEOUT,
    **kwargs,
) -> "AzureAppConfigurationProvider":
    """
    Loads configuration settings from Azure App Configuration into a Python application.

    :param str endpoint: Endpoint for App Configuration resource.
    :param  ~azure.core.credentials.TokenCredential credential: Credential for App Configuration resource.
    :keyword Optional[List[~azure.appconfiguration.provider.SettingSelector]] selects: List of setting selectors to
    filter configuration settings
    :keyword Optional[List[str]] trim_prefixes: List of prefixes to trim from configuration keys
    :keyword  ~azure.core.credentials.TokenCredential keyvault_credential: A credential for authenticating with the key
    vault. This is optional if keyvault_client_configs is provided.
    :keyword Mapping[str, Mapping] keyvault_client_configs: A Mapping of SecretClient endpoints to client
    configurations from azure-keyvault-secrets. This is optional if keyvault_credential is provided. If a credential
    isn't provided a credential will need to be in each set for each.
    :keyword Callable[[str], str] secret_resolver: A function that takes a URI and returns a value.
    :keyword List[Tuple[str, str]] refresh_on: One or more settings whose modification will trigger a full refresh
    after a fixed interval. This should be a list of Key-Label pairs for specific settings (filters and wildcards are
    not supported).
    :keyword int refresh_interval: The minimum time in seconds between when a call to `refresh` will actually trigger a
     service call to update the settings. Default value is 30 seconds.
    :keyword refresh_enabled: Optional flag to enable or disable refreshing of configuration settings. Defaults to
    True if ``refresh_on`` is set, otherwise False.
    :paramtype refresh_enabled: Optional[bool]
    :keyword on_refresh_success: Optional callback to be invoked when a change is found and a successful refresh has
    happened.
    :paramtype on_refresh_success: Optional[Callable]
    :keyword on_refresh_error: Optional callback to be invoked when an error occurs while refreshing settings. If not
    specified, errors will be raised.
    :paramtype on_refresh_error: Optional[Callable[[Exception], None]]
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
    :paramtype configuration_mapper: Optional[Callable[[ConfigurationSetting], None]]
    :keyword startup_timeout: The amount of time in seconds allowed to load data from Azure App Configuration on
     startup. The default value is 100 seconds.
    :paramtype startup_timeout: int
    """


@overload
def load(  # pylint: disable=docstring-keyword-should-match-keyword-only
    *,
    connection_string: str,
    selects: Optional[List[SettingSelector]] = None,
    trim_prefixes: Optional[List[str]] = None,
    keyvault_credential: Optional["TokenCredential"] = None,
    keyvault_client_configs: Optional[Mapping[str, JSON]] = None,
    secret_resolver: Optional[Callable[[str], str]] = None,
    key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = None,
    refresh_on: Optional[List[Tuple[str, str]]] = None,
    refresh_interval: int = 30,
    refresh_enabled: Optional[bool] = None,
    on_refresh_success: Optional[Callable] = None,
    on_refresh_error: Optional[Callable[[Exception], None]] = None,
    feature_flag_enabled: bool = False,
    feature_flag_selectors: Optional[List[SettingSelector]] = None,
    feature_flag_refresh_enabled: bool = False,
    startup_timeout: int = DEFAULT_STARTUP_TIMEOUT,
    **kwargs,
) -> "AzureAppConfigurationProvider":
    """
    Loads configuration settings from Azure App Configuration into a Python application.

    :keyword str connection_string: Connection string for App Configuration resource.
    :keyword Optional[List[~azure.appconfiguration.provider.SettingSelector]] selects: List of setting selectors to
    filter configuration settings
    :keyword trim_prefixes: Optional[List[str]] trim_prefixes: List of prefixes to trim from configuration keys
    :keyword  ~azure.core.credentials.TokenCredential keyvault_credential: A credential for authenticating with the key
    vault. This is optional if keyvault_client_configs is provided.
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
    :keyword refresh_enabled: Optional flag to enable or disable refreshing of configuration settings. Defaults to
    True if ``refresh_on`` is set, otherwise False.
    :paramtype refresh_enabled: Optional[bool]
    :keyword on_refresh_success: Optional callback to be invoked when a change is found and a successful refresh has
     happened.
    :paramtype on_refresh_success: Optional[Callable]
    :keyword on_refresh_error: Optional callback to be invoked when an error occurs while refreshing settings. If not
    specified, errors will be raised.
    :paramtype on_refresh_error: Optional[Callable[[Exception], None]]
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
    :paramtype configuration_mapper: Optional[Callable[[ConfigurationSetting], None]]
    :keyword startup_timeout: The amount of time in seconds allowed to load data from Azure App Configuration on
     startup. The default value is 100 seconds.
    :paramtype startup_timeout: int
    """


def load(*args, **kwargs) -> "AzureAppConfigurationProvider":
    start_time = datetime.datetime.now()

    # Process common load parameters using shared logic
    params = process_load_parameters(*args, **kwargs)

    provider = _buildprovider(
        params["connection_string"],
        params["endpoint"],
        params["credential"],
        uses_key_vault=params["uses_key_vault"],
        startup_timeout=params["startup_timeout"],
        **params["kwargs"],
    )
    kwargs = sdk_allowed_kwargs(params["kwargs"])

    try:
        provider._load_all(**kwargs)  # pylint:disable=protected-access
    except Exception:
        delay_failure(start_time)
        raise
    return provider
