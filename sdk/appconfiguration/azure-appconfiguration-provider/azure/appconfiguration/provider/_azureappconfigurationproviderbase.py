# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import base64
import hashlib
import json
import os
import time
import datetime
from importlib.metadata import version, PackageNotFoundError
from threading import Lock
import logging
from typing import (
    Any,
    Dict,
    Mapping,
    Optional,
    overload,
    List,
    Tuple,
    Union,
    Iterator,
    KeysView,
    ItemsView,
    ValuesView,
    TypeVar,
)
from azure.appconfiguration import (  # type:ignore # pylint:disable=no-name-in-module
    ConfigurationSetting,
    FeatureFlagConfigurationSetting,
)
from ._models import SettingSelector
from ._constants import (
    REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE,
    ServiceFabricEnvironmentVariable,
    AzureFunctionEnvironmentVariable,
    AzureWebAppEnvironmentVariable,
    ContainerAppEnvironmentVariable,
    KubernetesEnvironmentVariable,
    NULL_CHAR,
    CUSTOM_FILTER_KEY,
    PERCENTAGE_FILTER_KEY,
    TIME_WINDOW_FILTER_KEY,
    TARGETING_FILTER_KEY,
    PERCENTAGE_FILTER_NAMES,
    TIME_WINDOW_FILTER_NAMES,
    TARGETING_FILTER_NAMES,
    TELEMETRY_KEY,
    METADATA_KEY,
    ETAG_KEY,
    FEATURE_FLAG_REFERENCE_KEY,
    ALLOCATION_ID_KEY,
    APP_CONFIG_AI_MIME_PROFILE,
    APP_CONFIG_AICC_MIME_PROFILE,
    FEATURE_MANAGEMENT_KEY,
    FEATURE_FLAG_KEY,
)
from ._refresh_timer import _RefreshTimer

JSON = Mapping[str, Any]
_T = TypeVar("_T")
logger = logging.getLogger(__name__)

min_uptime = 5


def delay_failure(start_time: datetime.datetime) -> None:
    """
    We want to make sure we are up a minimum amount of time before we kill the process.
    Otherwise, we could get stuck in a quick restart loop.

    :param start_time: The time when the process started.
    :type start_time: datetime.datetime
    """
    min_time = datetime.timedelta(seconds=min_uptime)
    current_time = datetime.datetime.now()
    if current_time - start_time < min_time:
        time.sleep((min_time - (current_time - start_time)).total_seconds())


def process_load_parameters(*args, **kwargs: Any) -> Dict[str, Any]:
    """
    Process and validate all load function parameters in one place.
    This consolidates the most obviously duplicated logic from both sync and async load functions.

    :param args: Positional arguments, either endpoint and credential, or connection string.
    :type args: Any
    :return: Dictionary containing processed parameters
    :rtype: Dict[str, Any]
    """
    endpoint: Optional[str] = kwargs.pop("endpoint", None)
    credential = kwargs.pop("credential", None)
    connection_string: Optional[str] = kwargs.pop("connection_string", None)
    start_time = datetime.datetime.now()

    # Handle positional arguments
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

    # Validate endpoint/credential vs connection_string
    if (endpoint or credential) and connection_string:
        raise ValueError("Please pass either endpoint and credential, or a connection string.")

    # Process Key Vault options in one place
    key_vault_options = kwargs.pop("key_vault_options", None)
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

    # Validate feature flag selectors don't use snapshots
    feature_flag_selectors = kwargs.get("feature_flag_selectors")
    if feature_flag_selectors:
        for selector in feature_flag_selectors:
            if hasattr(selector, "snapshot_name") and selector.snapshot_name is not None:
                raise ValueError(
                    "snapshot_name cannot be used with feature_flag_selectors. "
                    "Use snapshot_name with regular selects instead to load feature flags from snapshots."
                )

    # Determine Key Vault usage
    uses_key_vault = (
        "keyvault_credential" in kwargs
        or "keyvault_client_configs" in kwargs
        or "secret_resolver" in kwargs
        or kwargs.get("uses_key_vault", False)
    )

    return {
        "endpoint": endpoint,
        "credential": credential,
        "connection_string": connection_string,
        "uses_key_vault": uses_key_vault,
        "start_time": start_time,
        "kwargs": kwargs,
    }


def is_json_content_type(content_type: str) -> bool:
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


def _build_watched_setting(setting: Union[str, Tuple[str, str]]) -> Tuple[str, str]:
    try:
        key, label = setting  # type:ignore
    except (IndexError, ValueError):
        key = str(setting)  # Ensure key is a string
        label = NULL_CHAR
    if "*" in key or "*" in label:
        raise ValueError("Wildcard key or label filters are not supported for refresh.")
    return key, label


def sdk_allowed_kwargs(kwargs):
    allowed_kwargs = [
        "headers",
        "request_id",
        "user_agent",
        "logging_enable",
        "logger",
        "response_encoding",
        "raw_request_hook",
        "raw_response_hook",
        "network_span_namer",
        "tracing_attributes",
        "permit_redirects",
        "redirect_max",
        "retry_total",
        "retry_connect",
        "retry_read",
        "retry_status",
        "retry_backoff_factor",
        "retry_backoff_max",
        "retry_mode",
        "timeout",
        "connection_timeout",
        "read_timeout",
        "connection_verify",
        "connection_cert",
        "proxies",
        "cookies",
        "connection_data_block_size",
    ]
    return {k: v for k, v in kwargs.items() if k in allowed_kwargs}


class AzureAppConfigurationProviderBase(Mapping[str, Union[str, JSON]]):  # pylint: disable=too-many-instance-attributes
    """
    Provides a dictionary-like interface to Azure App Configuration settings. Enables loading of sets of configuration
    settings from Azure App Configuration into a Python application. Enables trimming of prefixes from configuration
    keys. Enables resolution of Key Vault references in configuration settings.
    """

    def __init__(self, **kwargs: Any) -> None:
        self._origin_endpoint: str = kwargs.get("endpoint", "")
        self._dict: Dict[str, Any] = {}
        self._selects: List[SettingSelector] = kwargs.pop(
            "selects", [SettingSelector(key_filter="*", label_filter=NULL_CHAR)]
        )

        trim_prefixes: List[str] = kwargs.pop("trim_prefixes", [])
        self._trim_prefixes: List[str] = sorted(trim_prefixes, key=len, reverse=True)
        refresh_on: List[Tuple[str, str]] = kwargs.pop("refresh_on", None) or []
        self._watched_settings: Dict[Tuple[str, str], Optional[str]] = {
            _build_watched_setting(s): None for s in refresh_on
        }
        self._refresh_timer: _RefreshTimer = _RefreshTimer(**kwargs)
        self._feature_flag_enabled = kwargs.pop("feature_flag_enabled", False)
        self._feature_flag_selectors = kwargs.pop("feature_flag_selectors", [SettingSelector(key_filter="*")])
        self._watched_feature_flags: Dict[Tuple[str, str], Optional[str]] = {}
        self._feature_flag_refresh_timer: _RefreshTimer = _RefreshTimer(**kwargs)
        self._feature_flag_refresh_enabled = kwargs.pop("feature_flag_refresh_enabled", False)
        self._feature_filter_usage: Dict[str, bool] = {}
        self._uses_load_balancing = kwargs.pop("load_balancing_enabled", False)
        self._uses_ai_configuration = False
        self._uses_aicc_configuration = False  # AI Chat Completion
        self._update_lock = Lock()
        self._refresh_lock = Lock()

    def _process_key_name(self, config):
        trimmed_key = config.key
        # Trim the key if it starts with one of the prefixes provided
        for trim in self._trim_prefixes:
            if config.key.startswith(trim):
                trimmed_key = config.key[len(trim) :]
                break
        return trimmed_key

    def _update_ff_telemetry_metadata(
        self, endpoint: str, feature_flag: FeatureFlagConfigurationSetting, feature_flag_value: Dict
    ):
        """
        Add telemetry metadata to feature flag values.

        :param endpoint: The App Configuration endpoint URL.
        :type endpoint: str
        :param feature_flag: The feature flag configuration setting.
        :type feature_flag: FeatureFlagConfigurationSetting
        :param feature_flag_value: The feature flag value dictionary to update.
        :type feature_flag_value: Dict[str, Any]
        """
        if TELEMETRY_KEY in feature_flag_value:
            if METADATA_KEY not in feature_flag_value[TELEMETRY_KEY]:
                feature_flag_value[TELEMETRY_KEY][METADATA_KEY] = {}
            feature_flag_value[TELEMETRY_KEY][METADATA_KEY][ETAG_KEY] = feature_flag.etag

            if not endpoint.endswith("/"):
                endpoint += "/"
            feature_flag_reference = f"{endpoint}kv/{feature_flag.key}"
            if feature_flag.label and not feature_flag.label.isspace():
                feature_flag_reference += f"?label={feature_flag.label}"
            if feature_flag_value[TELEMETRY_KEY].get("enabled"):
                feature_flag_value[TELEMETRY_KEY][METADATA_KEY][FEATURE_FLAG_REFERENCE_KEY] = feature_flag_reference
                allocation_id = self._generate_allocation_id(feature_flag_value)
                if allocation_id:
                    feature_flag_value[TELEMETRY_KEY][METADATA_KEY][ALLOCATION_ID_KEY] = allocation_id

    def _update_feature_filter_telemetry(self, feature_flag: FeatureFlagConfigurationSetting):
        """
        Track feature filter usage for App Configuration telemetry.

        :param feature_flag: The feature flag to analyze for filter usage.
        :type feature_flag: FeatureFlagConfigurationSetting
        """
        if feature_flag.filters:
            for filter in feature_flag.filters:
                if filter.get("name") in PERCENTAGE_FILTER_NAMES:
                    self._feature_filter_usage[PERCENTAGE_FILTER_KEY] = True
                elif filter.get("name") in TIME_WINDOW_FILTER_NAMES:
                    self._feature_filter_usage[TIME_WINDOW_FILTER_KEY] = True
                elif filter.get("name") in TARGETING_FILTER_NAMES:
                    self._feature_filter_usage[TARGETING_FILTER_KEY] = True
                else:
                    self._feature_filter_usage[CUSTOM_FILTER_KEY] = True

    @staticmethod
    def _generate_allocation_id(feature_flag_value: Dict[str, JSON]) -> Optional[str]:
        """
        Generates an allocation ID for the specified feature.
        seed=123abc\ndefault_when_enabled=Control\npercentiles=0,Control,20;20,Test,100\nvariants=Control,standard;Test,special # pylint:disable=line-too-long

        :param  Dict[str, JSON] feature_flag_value: The feature to generate an allocation ID for.
        :rtype: str
        :return: The allocation ID.
        """

        allocation_id = ""
        allocated_variants = []

        allocation: Optional[JSON] = feature_flag_value.get("allocation")

        if not allocation:
            return None

        # Seed
        allocation_id = f"seed={allocation.get('seed', '')}"

        # DefaultWhenEnabled
        if "default_when_enabled" in allocation:
            allocated_variants.append(allocation.get("default_when_enabled"))

        allocation_id += f"\ndefault_when_enabled={allocation.get('default_when_enabled', '')}"

        # Percentile
        allocation_id += "\npercentiles="

        percentile = allocation.get("percentile")

        if percentile:
            percentile_allocations = sorted(
                (x for x in percentile if x.get("from") != x.get("to")),
                key=lambda x: x.get("from"),
            )

            for percentile_allocation in percentile_allocations:
                if "variant" in percentile_allocation:
                    allocated_variants.append(percentile_allocation.get("variant"))

            allocation_id += ";".join(
                f"{pa.get('from')}," f"{base64.b64encode(pa.get('variant').encode()).decode()}," f"{pa.get('to')}"
                for pa in percentile_allocations
            )

        if not allocated_variants and not allocation.get("seed"):
            return None

        # Variants
        allocation_id += "\nvariants="

        variants_value = feature_flag_value.get("variants")
        if variants_value and (isinstance(variants_value, list) or all(isinstance(v, dict) for v in variants_value)):
            if (
                allocated_variants
                and isinstance(variants_value, list)
                and all(isinstance(v, dict) for v in variants_value)
            ):
                sorted_variants: List[Dict[str, Any]] = sorted(
                    (v for v in variants_value if v.get("name") in allocated_variants),
                    key=lambda v: v.get("name"),
                )

                for v in sorted_variants:
                    allocation_id += f"{base64.b64encode(v.get('name', '').encode()).decode()},"
                    if "configuration_value" in v:
                        allocation_id += (
                            f"{json.dumps(v.get('configuration_value', ''), separators=(',', ':'), sort_keys=True)}"
                        )
                    allocation_id += ";"
                if sorted_variants:
                    allocation_id = allocation_id[:-1]

        # Create a sha256 hash of the allocation_id
        hash_object = hashlib.sha256(allocation_id.encode())
        hash_digest = hash_object.digest()

        # Encode the first 15 bytes in base64 url
        return base64.urlsafe_b64encode(hash_digest[:15]).decode()

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

        :param key: The key of the value to get.
        :type key: str
        :param default: The default value to return.
        :type default: Optional[Union[str, JSON, _T]]
        :return: The value of the specified key.
        :rtype: Union[str, JSON, _T, None]
        """
        with self._update_lock:
            return self._dict.get(key, default)

    def __ne__(self, other: Any) -> bool:
        return not self == other

    def _process_key_value_base(self, config: ConfigurationSetting) -> Union[str, Dict[str, Any]]:
        """
        Process configuration values that are not KeyVault references. If the content type is None, the value is
        returned as-is.

        :param config: The configuration setting to process.
        :type config: ConfigurationSetting
        :return: The processed configuration value (JSON object if JSON content type, string otherwise).
        :rtype: Union[str, Dict[str, Any]]
        """
        if config.content_type is None:
            return config.value
        if is_json_content_type(config.content_type) and not isinstance(config, FeatureFlagConfigurationSetting):
            # Feature flags are of type json, but don't treat them as such
            try:
                if APP_CONFIG_AI_MIME_PROFILE in config.content_type:
                    self._uses_ai_configuration = True
                if APP_CONFIG_AICC_MIME_PROFILE in config.content_type:
                    self._uses_aicc_configuration = True
                return json.loads(config.value)
            except json.JSONDecodeError:
                try:
                    # If the value is not a valid JSON, check if it has comments and remove them
                    from ._json import remove_json_comments

                    return json.loads(remove_json_comments(config.value))
                except (json.JSONDecodeError, ValueError):
                    # If the value is not a valid JSON, treat it like regular string value
                    return config.value
        return config.value

    def _process_feature_flags(
        self,
        processed_settings: Dict[str, Any],
        processed_feature_flags: List[Dict[str, Any]],
        feature_flags: Optional[List[FeatureFlagConfigurationSetting]],
    ) -> Dict[str, Any]:
        if feature_flags:
            # Reset feature flag usage
            self._feature_filter_usage = {}
            processed_feature_flags = [self._process_feature_flag(ff) for ff in feature_flags]
            self._watched_feature_flags = self._update_watched_feature_flags(feature_flags)

        if self._feature_flag_enabled:
            processed_settings[FEATURE_MANAGEMENT_KEY] = {}
            processed_settings[FEATURE_MANAGEMENT_KEY][FEATURE_FLAG_KEY] = processed_feature_flags
        return processed_settings

    def _process_feature_flag(self, feature_flag: FeatureFlagConfigurationSetting) -> Dict[str, Any]:
        feature_flag_value = json.loads(feature_flag.value)
        self._update_ff_telemetry_metadata(self._origin_endpoint, feature_flag, feature_flag_value)
        self._update_feature_filter_telemetry(feature_flag)
        return feature_flag_value

    def _update_watched_settings(
        self, configuration_settings: List[ConfigurationSetting]
    ) -> Dict[Tuple[str, str], Optional[str]]:
        """
        Updates the etags of watched settings that are part of the configuration
        :param List[ConfigurationSetting] configuration_settings: The list of configuration settings to update
        :return: A dictionary mapping (key, label) tuples to their updated etags
        :rtype: Dict[Tuple[str, str], Optional[str]]
        """
        watched_settings: Dict[Tuple[str, str], Optional[str]] = {}
        for config in configuration_settings:
            if (config.key, config.label) in self._watched_settings:
                watched_settings[(config.key, config.label)] = config.etag
        return watched_settings

    def _update_watched_feature_flags(
        self, feature_flags: List[FeatureFlagConfigurationSetting]
    ) -> Dict[Tuple[str, str], Optional[str]]:
        """
        Updates the etags of watched feature flags that are part of the configuration
        :param List[FeatureFlagConfigurationSetting] feature_flags: The list of feature flags to update
        :return: A dictionary mapping (key, label) tuples to their updated etags
        :rtype: Dict[Tuple[str, str], Optional[str]]
        """
        watched_feature_flags: Dict[Tuple[str, str], Optional[str]] = {}
        for feature_flag in feature_flags:
            watched_feature_flags[(feature_flag.key, feature_flag.label)] = feature_flag.etag
        return watched_feature_flags

    def _update_correlation_context_header(
        self,
        headers: Dict[str, str],
        request_type: str,
        replica_count: int,
        uses_key_vault: bool,
        is_failover_request: bool = False,
    ) -> Dict[str, str]:
        """
        Update the correlation context header with telemetry information.

        :param headers: The headers dictionary to update.
        :type headers: Dict[str, str]
        :param request_type: The type of request (e.g., "Startup", "Watch").
        :type request_type: str
        :param replica_count: The number of replica endpoints.
        :type replica_count: int
        :param uses_key_vault: Whether this request uses Key Vault.
        :type uses_key_vault: bool
        :param is_failover_request: Whether this is a failover request.
        :type is_failover_request: bool
        :return: The updated headers dictionary.
        :rtype: Dict[str, str]
        """
        if os.environ.get(REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE, default="").lower() == "true":
            return headers
        correlation_context = f"RequestType={request_type}"

        if len(self._feature_filter_usage) > 0:
            filters_used = ""
            if CUSTOM_FILTER_KEY in self._feature_filter_usage:
                filters_used = CUSTOM_FILTER_KEY
            if PERCENTAGE_FILTER_KEY in self._feature_filter_usage:
                filters_used += ("+" if filters_used else "") + PERCENTAGE_FILTER_KEY
            if TIME_WINDOW_FILTER_KEY in self._feature_filter_usage:
                filters_used += ("+" if filters_used else "") + TIME_WINDOW_FILTER_KEY
            if TARGETING_FILTER_KEY in self._feature_filter_usage:
                filters_used += ("+" if filters_used else "") + TARGETING_FILTER_KEY
            correlation_context += f",Filters={filters_used}"

        correlation_context += self._uses_feature_flags()

        if uses_key_vault:
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
            correlation_context += f",Host={host_type}"

        if replica_count > 0:
            correlation_context += f",ReplicaCount={replica_count}"

        if is_failover_request:
            correlation_context += ",Failover"

        features = ""

        if self._uses_load_balancing:
            features += "LB+"

        if self._uses_ai_configuration:
            features += "AI+"

        if self._uses_aicc_configuration:
            features += "AICC+"

        if features:
            correlation_context += f",Features={features[:-1]}"

        headers["Correlation-Context"] = correlation_context
        return headers

    def _uses_feature_flags(self) -> str:
        if not self._feature_flag_enabled:
            return ""
        package_name = "featuremanagement"
        try:
            feature_management_version = version(package_name)
            return f",FMPyVer={feature_management_version}"
        except PackageNotFoundError:
            pass
        return ""

    def _deduplicate_settings(
        self, configuration_settings: List[ConfigurationSetting]
    ) -> Dict[str, ConfigurationSetting]:
        """
        Deduplicates configuration settings by key.

        :param List[ConfigurationSetting] configuration_settings: The list of configuration settings to deduplicate
        :return: A dictionary mapping keys to their unique configuration settings
        :rtype: Dict[str, ConfigurationSetting]
        """
        unique_settings: Dict[str, ConfigurationSetting] = {}
        for settings in configuration_settings:
            unique_settings[settings.key] = settings
        return unique_settings
