# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import base64
import hashlib
import json
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
    FeatureFlagConfigurationSetting,
)
from ._models import SettingSelector
from ._refresh_timer import RefreshTimer
from ._utils import (
    is_json_content_type,
)
from ._constants import (
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
)

JSON = Mapping[str, Any]
_T = TypeVar("_T")
logger = logging.getLogger(__name__)


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
        if allocated_variants and isinstance(variants_value, list) and all(isinstance(v, dict) for v in variants_value):
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


def _build_sentinel(setting: Union[str, Tuple[str, str]]) -> Tuple[str, str]:
    """
    Builds a sentinel tuple from a setting specification.

    :param setting: Either a string key or a tuple of (key, label).
    :type setting: Union[str, Tuple[str, str]]
    :return: A tuple of (key, label).
    :rtype: Tuple[str, str]
    :raises ValueError: If wildcard characters are used in key or label.
    """
    try:
        key, label = setting  # type:ignore
    except (IndexError, ValueError):
        key = str(setting)  # Ensure key is a string
        label = NULL_CHAR
    if "*" in key or "*" in label:
        raise ValueError("Wildcard key or label filters are not supported for refresh.")
    return key, label


def process_load_arguments(*args, **kwargs) -> dict:
    """
    Common validation logic for load function arguments.

    :param args: Positional arguments (endpoint and optionally credential).
    :type args: Tuple[Any, ...]
    :return: Updated kwargs with validated arguments.
    :rtype: dict
    :raises TypeError: If unexpected positional parameters are provided.
    :raises ValueError: If both endpoint/credential and connection_string are provided, or if neither is provided.
    """
    endpoint = kwargs.get("endpoint", None)
    credential = kwargs.get("credential", None)
    connection_string = kwargs.get("connection_string", None)

    # Update endpoint and credential if specified positionally.
    if len(args) > 2:
        raise TypeError(
            "Unexpected positional parameters. Please pass either endpoint and credential, or a connection string."
        )
    if len(args) == 1:
        if endpoint is not None:
            raise TypeError("Received multiple values for argument 'endpoint'")
        kwargs["endpoint"] = args[0]
        endpoint = args[0]  # Update local variable for validation
    elif len(args) == 2:
        if credential is not None:
            raise TypeError("Received multiple values for argument 'credential'")
        kwargs["endpoint"], kwargs["credential"] = args
        endpoint, credential = args  # Update local variables for validation

    # Validate that either endpoint or connection_string is provided
    if not endpoint and not connection_string:
        raise ValueError("Either 'endpoint' or 'connection_string' must be provided.")

    if (endpoint or credential) and connection_string:
        raise ValueError("Please pass either endpoint and credential, or a connection string.")

    # Grabbing the endpoint for future use
    connection_string = kwargs.get("connection_string")

    if connection_string:
        kwargs["endpoint"] = connection_string.split(";")[0].split("=")[1]
    if not kwargs["endpoint"]:
        raise ValueError("No endpoint specified.")

    return kwargs


def process_key_vault_options(**kwargs):
    """
    Process key vault options and update kwargs accordingly.

    :return: Updated kwargs with processed key vault options.
    :rtype: Dict[str, Any]
    :raises ValueError: If conflicting key vault options are specified.
    """
    key_vault_options = kwargs.pop("key_vault_options", None)

    # Removing use of AzureAppConfigurationKeyVaultOptions
    if key_vault_options:
        if "keyvault_credential" in kwargs or "secret_resolver" in kwargs or "keyvault_client_configs" in kwargs:
            raise ValueError(
                "Cannot specify 'key_vault_options' along with 'keyvault_credential', "
                "'secret_resolver', or 'keyvault_client_configs'."
            )
        kwargs["keyvault_credential"] = key_vault_options.credential
        kwargs["secret_resolver"] = key_vault_options.secret_resolver
        kwargs["keyvault_client_configs"] = key_vault_options.client_configs

    if kwargs.get("keyvault_credential") is not None and kwargs.get("secret_resolver") is not None:
        raise ValueError("A keyvault credential and secret resolver can't both be configured.")

    kwargs["uses_key_vault"] = (
        "keyvault_credential" in kwargs
        or "keyvault_client_configs" in kwargs
        or "secret_resolver" in kwargs
        or kwargs.get("uses_key_vault", False)
    )

    return kwargs


class AzureAppConfigurationProviderBase(Mapping[str, Union[str, JSON]]):  # pylint: disable=too-many-instance-attributes
    """
    Provides a dictionary-like interface to Azure App Configuration settings. Enables loading of sets of configuration
    settings from Azure App Configuration into a Python application. Enables trimming of prefixes from configuration
    keys. Enables resolution of Key Vault references in configuration settings.
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the Azure App Configuration Provider.

        :keyword kwargs: Configuration options for the provider.
        :paramtype kwargs: Dict[str, Any]
        """
        self._origin_endpoint: str = kwargs.get("endpoint", "")
        self._dict: Dict[str, Any] = {}
        self._selects: List[SettingSelector] = kwargs.pop(
            "selects", [SettingSelector(key_filter="*", label_filter=NULL_CHAR)]
        )

        trim_prefixes: List[str] = kwargs.pop("trim_prefixes", [])
        self._trim_prefixes: List[str] = sorted(trim_prefixes, key=len, reverse=True)

        refresh_on: List[Tuple[str, str]] = kwargs.pop("refresh_on", None) or []
        self._refresh_on: Mapping[Tuple[str, str], Optional[str]] = {_build_sentinel(s): None for s in refresh_on}
        self._refresh_timer: RefreshTimer = RefreshTimer(**kwargs)
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
        self._refresh_on_feature_flags: Dict[Tuple[str, str], Optional[str]] = {}
        self._feature_flag_refresh_timer: RefreshTimer = RefreshTimer(**kwargs)
        self._feature_flag_refresh_enabled = kwargs.pop("feature_flag_refresh_enabled", False)
        self._feature_filter_usage: Dict[str, bool] = {}
        self._uses_load_balancing = kwargs.pop("load_balancing_enabled", False)
        self._uses_ai_configuration = False
        self._uses_aicc_configuration = False  # AI Chat Completion
        self._update_lock = Lock()
        self._refresh_lock = Lock()

    def _process_key_name(self, config):
        """
        Process the configuration key name by trimming configured prefixes.

        :param config: The configuration setting object.
        :type config: Any
        :return: The processed key name with trimmed prefix.
        :rtype: str
        """
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
                allocation_id = _generate_allocation_id(feature_flag_value)
                if allocation_id:
                    feature_flag_value[TELEMETRY_KEY][METADATA_KEY][ALLOCATION_ID_KEY] = allocation_id

    def _feature_flag_appconfig_telemetry(self, feature_flag: FeatureFlagConfigurationSetting):
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

    def _process_non_keyvault_value(self, config):
        """
        Process configuration values that are not KeyVault references.

        :param config: The configuration setting to process.
        :type config: Any
        :return: The processed configuration value (JSON object if JSON content type, string otherwise).
        :rtype: Union[str, Dict[str, Any]]
        """
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
