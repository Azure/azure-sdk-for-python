# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import base64
import hashlib
import json
from threading import Lock
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
    cast,
)
from azure.appconfiguration import (  # type:ignore # pylint:disable=no-name-in-module
    ConfigurationSetting,
    FeatureFlagConfigurationSetting,
    FeatureFlag,
)
from ._models import FeatureFlagSelector, SettingSelector
from ._constants import (
    NULL_CHAR,
    TELEMETRY_KEY,
    METADATA_KEY,
    ETAG_KEY,
    FEATURE_FLAG_REFERENCE_KEY,
    ALLOCATION_ID_KEY,
    APP_CONFIG_AI_MIME_PROFILE,
    APP_CONFIG_AICC_MIME_PROFILE,
    FEATURE_MANAGEMENT_KEY,
    FEATURE_FLAG_KEY,
    FEATURE_FLAG_ID_FIELD,
    FEATURE_FLAG_KV_REFERENCE_SEGMENT,
    ENHANCED_FEATURE_FLAG_REFERENCE_SEGMENT,
)
from ._refresh_timer import _RefreshTimer
from ._request_tracing_context import _RequestTracingContext


JSON = Mapping[str, Any]
_T = TypeVar("_T")


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
    if isinstance(setting, str):
        key, label = setting, NULL_CHAR
    else:
        try:
            key, label = setting
        except (TypeError, ValueError):
            key, label = str(setting), NULL_CHAR
    if "*" in key or "*" in label:
        raise ValueError("Wildcard key or label filters are not supported for refresh.")
    return key, label


def _normalize_feature_flag_selectors(
    selectors: Optional[Union[List[SettingSelector], List[FeatureFlagSelector]]]
) -> Tuple[List[SettingSelector], List[FeatureFlagSelector]]:
    """
    Normalizes the customer-provided ``feature_flag_selectors``, which may be either a ``List[SettingSelector]``
    or a ``List[FeatureFlagSelector]`` (the two types cannot be mixed in the same list), into the two selector
    lists used internally to load both kinds of feature flags:

    - kv_selectors: Used to load key-value based feature flags (``SettingSelector.key_filter`` is used as the key
      filter).
    - enhanced_selectors: Used to load enhanced feature flags from the dedicated feature flag resource endpoint
      (``FeatureFlagSelector.name_filter`` is used as the name filter).

    :param selectors: The customer-provided feature flag selectors, or None to use the default (all feature flags
     without a label).
    :type selectors: Optional[Union[List[SettingSelector], List[FeatureFlagSelector]]]
    :return: A tuple of (kv_selectors, enhanced_selectors).
    :rtype: Tuple[List[SettingSelector], List[FeatureFlagSelector]]
    """
    if selectors is None:
        return [SettingSelector(key_filter="*")], [FeatureFlagSelector(name_filter="*")]
    if not selectors:
        # An explicitly empty collection of selectors means no feature flags should be loaded, unlike None
        # which falls back to the default of loading all unlabeled feature flags.
        return [], []

    selectors_iter = iter(selectors)
    first_selector = next(selectors_iter)
    is_feature_flag_selector = isinstance(first_selector, FeatureFlagSelector)
    for select in selectors_iter:
        if isinstance(select, FeatureFlagSelector) != is_feature_flag_selector:
            raise TypeError(
                "feature_flag_selectors must be either a list of SettingSelector or a list of FeatureFlagSelector, "
                "not a mix of both."
            )

    if is_feature_flag_selector:
        feature_flag_selectors = cast(List[FeatureFlagSelector], selectors)
        kv_selectors = [
            SettingSelector(
                key_filter=select.name_filter, label_filter=select.label_filter, tag_filters=select.tag_filters
            )
            for select in feature_flag_selectors
        ]
        # FeatureFlagSelector has no snapshot_name, so every selector is used for enhanced feature flags.
        enhanced_selectors = list(feature_flag_selectors)
        return kv_selectors, enhanced_selectors

    setting_selectors = cast(List[SettingSelector], selectors)
    kv_selectors = list(setting_selectors)
    enhanced_selectors = [
        FeatureFlagSelector(
            name_filter=select.key_filter, label_filter=select.label_filter, tag_filters=select.tag_filters
        )
        for select in setting_selectors
        if select.snapshot_name is None
    ]
    return kv_selectors, enhanced_selectors


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
        self._feature_flag_selectors, self._enhanced_feature_flag_selectors = _normalize_feature_flag_selectors(
            kwargs.pop("feature_flag_selectors", None)
        )
        self._feature_flag_refresh_timer: _RefreshTimer = _RefreshTimer(**kwargs)
        self._feature_flag_refresh_enabled = kwargs.pop("feature_flag_refresh_enabled", False)
        refresh_enabled = kwargs.pop("refresh_enabled", None)
        if refresh_enabled is None and len(refresh_on) > 0:
            # If refresh_enabled is not explicitly set, enable refresh if there are settings to refresh on
            refresh_enabled = True
        self._refresh_enabled = refresh_enabled
        self._page_etags: List[List[str]] = []
        self._feature_flag_page_etags: List[List[str]] = []
        self._enhanced_feature_flag_etags: List[List[str]] = []
        self._processed_kv_feature_flags: List[Dict[str, Any]] = []
        self._processed_enhanced_feature_flags: List[Dict[str, Any]] = []
        self._tracing_context = _RequestTracingContext(kwargs.pop("load_balancing_enabled", False))
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
        Add telemetry metadata to feature flag values loaded from the key-value store.

        :param endpoint: The App Configuration endpoint URL.
        :type endpoint: str
        :param feature_flag: The feature flag configuration setting.
        :type feature_flag: FeatureFlagConfigurationSetting
        :param feature_flag_value: The feature flag value dictionary to update.
        :type feature_flag_value: Dict[str, Any]
        """
        self._update_ff_telemetry_metadata_common(
            endpoint,
            feature_flag.key,
            feature_flag.label,
            feature_flag.etag,
            feature_flag_value,
            FEATURE_FLAG_KV_REFERENCE_SEGMENT,
        )

    def _update_enhanced_feature_flag_telemetry_metadata(
        self, endpoint: str, feature_flag: FeatureFlag, feature_flag_value: Dict
    ):
        """
        Add telemetry metadata to enhanced feature flag values loaded from the enhanced feature flag endpoint.

        :param endpoint: The App Configuration endpoint URL.
        :type endpoint: str
        :param feature_flag: The enhanced feature flag.
        :type feature_flag: ~azure.appconfiguration.FeatureFlag
        :param feature_flag_value: The feature flag value dictionary to update.
        :type feature_flag_value: Dict[str, Any]
        """
        self._update_ff_telemetry_metadata_common(
            endpoint,
            feature_flag.name,
            feature_flag.label,
            feature_flag.etag,
            feature_flag_value,
            ENHANCED_FEATURE_FLAG_REFERENCE_SEGMENT,
        )

    def _update_ff_telemetry_metadata_common(  # pylint: disable=too-many-positional-arguments
        self,
        endpoint: str,
        identifier: str,
        label: Optional[str],
        etag: Optional[str],
        feature_flag_value: Dict,
        reference_path_segment: str,
    ):
        """
        Add telemetry metadata to a feature flag value dictionary, regardless of which endpoint it was loaded from.

        :param endpoint: The App Configuration endpoint URL.
        :type endpoint: str
        :param identifier: The identifier of the feature flag (key for key-value based, name for enhanced feature
            flags).
        :type identifier: str
        :param label: The label of the feature flag.
        :type label: Optional[str]
        :param etag: The etag of the feature flag.
        :type etag: Optional[str]
        :param feature_flag_value: The feature flag value dictionary to update.
        :type feature_flag_value: Dict[str, Any]
        :param reference_path_segment: The path segment to use when building the feature flag reference URL, e.g.
            "kv" for key-value based feature flags or "ff" for enhanced feature flags.
        :type reference_path_segment: str
        """
        if TELEMETRY_KEY not in feature_flag_value:
            # Initialize telemetry dictionary if not present
            feature_flag_value[TELEMETRY_KEY] = {}

        # Update telemetry metadata for application insights/logging in feature management
        if METADATA_KEY not in feature_flag_value[TELEMETRY_KEY]:
            feature_flag_value[TELEMETRY_KEY][METADATA_KEY] = {}
        feature_flag_value[TELEMETRY_KEY][METADATA_KEY][ETAG_KEY] = etag

        if feature_flag_value[TELEMETRY_KEY].get("enabled"):
            self._tracing_context.uses_telemetry = True
            if not endpoint.endswith("/"):
                endpoint += "/"
            feature_flag_reference = f"{endpoint}{reference_path_segment}/{identifier}"
            if label:
                feature_flag_reference += f"?label={label}"

            feature_flag_value[TELEMETRY_KEY][METADATA_KEY][FEATURE_FLAG_REFERENCE_KEY] = feature_flag_reference
            allocation_id = self._generate_allocation_id(feature_flag_value)
            if allocation_id:
                feature_flag_value[TELEMETRY_KEY][METADATA_KEY][ALLOCATION_ID_KEY] = allocation_id

        allocation = feature_flag_value.get("allocation")
        if allocation and allocation.get("seed"):
            self._tracing_context.uses_seed = True

        variants = feature_flag_value.get("variants")
        if variants:
            # Update Usage Data for Telemetry
            self._tracing_context.update_max_variants(len(variants))

    @staticmethod
    def _generate_allocation_id(feature_flag_value: Dict[str, JSON]) -> Optional[str]:
        """
        Generates an allocation ID for the specified feature.
        seed=123abc\ndefault_when_enabled=Control\npercentiles=0,Control,20;20,Test,100\nvariants=Control,standard;Test,special # pylint:disable=line-too-long

        :param  Dict[str, JSON] feature_flag_value: The feature to generate an allocation ID for.
        :rtype: Optional[str]
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
         based on their content type.
        :rtype: ValuesView[Union[str, Mapping[str, Any]]]
        """
        with self._update_lock:
            return self._dict.values()

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
                    self._tracing_context.uses_ai_configuration = True
                if APP_CONFIG_AICC_MIME_PROFILE in config.content_type:
                    self._tracing_context.uses_aicc_configuration = True
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

    def _process_and_merge_feature_flags(
        self,
        processed_settings: Dict[str, Any],
        processed_feature_flags: List[Dict[str, Any]],
        feature_flags: Optional[List[FeatureFlagConfigurationSetting]],
        enhanced_feature_flags: Optional[List[FeatureFlag]] = None,
    ) -> Dict[str, Any]:
        if feature_flags is not None or enhanced_feature_flags is not None:
            # Reset feature flag usage
            self._tracing_context.reset_feature_filter_usage()

        if feature_flags is not None:
            # Only overwrite the cached key-value feature flags when a refresh actually occurred. This preserves
            # the previous state (including an intentional empty list) when this source wasn't refreshed.
            self._processed_kv_feature_flags = [self._process_kv_feature_flag(ff) for ff in feature_flags]

        if enhanced_feature_flags is not None:
            # Only overwrite the cached enhanced feature flags when a refresh actually occurred, so the previous
            # state is carried over when this source wasn't refreshed.
            self._processed_enhanced_feature_flags = [
                self._process_enhanced_feature_flag(ff) for ff in enhanced_feature_flags
            ]
        self._tracing_context.uses_enhanced_feature_flags = bool(enhanced_feature_flags)

        if feature_flags is not None or enhanced_feature_flags is not None:
            processed_feature_flags = self._merge_feature_flags(
                self._processed_kv_feature_flags, self._processed_enhanced_feature_flags
            )

        if self._feature_flag_enabled:
            processed_settings[FEATURE_MANAGEMENT_KEY] = {}
            processed_settings[FEATURE_MANAGEMENT_KEY][FEATURE_FLAG_KEY] = processed_feature_flags
        return processed_settings

    @staticmethod
    def _merge_feature_flags(
        kv_feature_flags: List[Dict[str, Any]], enhanced_feature_flags: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge feature flags loaded from the key-value store with enhanced feature flags loaded from the
        enhanced feature flag endpoint. Both sources populate the ``id`` field using the feature management
        library's schema (for enhanced feature flags, the enhanced feature flag's name is used as the ``id``).
        Feature flags are matched by their ``id`` field. When both sources contain a feature flag with the
        same identifier, the enhanced feature flag takes precedence.

        :param kv_feature_flags: The feature flags loaded from the key-value store.
        :type kv_feature_flags: List[Dict[str, Any]]
        :param enhanced_feature_flags: The enhanced feature flags loaded from the enhanced feature flag endpoint.
        :type enhanced_feature_flags: List[Dict[str, Any]]
        :return: The merged list of feature flags.
        :rtype: List[Dict[str, Any]]
        """
        merged: Dict[str, Dict[str, Any]] = {}
        for ff in kv_feature_flags:
            identifier = ff.get(FEATURE_FLAG_ID_FIELD)
            if identifier is None:
                continue
            merged[identifier] = ff
        for ff in enhanced_feature_flags:
            identifier = ff.get(FEATURE_FLAG_ID_FIELD)
            if identifier is None:
                continue
            merged[identifier] = ff
        return list(merged.values())

    def _process_kv_feature_flag(self, feature_flag: FeatureFlagConfigurationSetting) -> Dict[str, Any]:
        try:
            feature_flag_value = json.loads(feature_flag.value)
            self._update_ff_telemetry_metadata(self._origin_endpoint, feature_flag, feature_flag_value)
            self._tracing_context.update_feature_filter_telemetry(feature_flag)
            return feature_flag_value
        except json.JSONDecodeError:
            # Feature flag value is not a valid JSON
            return {}

    @staticmethod
    def _parse_variant_value(value: Optional[str], content_type: Optional[str]) -> Any:
        """
        Parses an enhanced feature flag variant's raw string value, similar to how a regular key-value setting's
        value is processed. If the variant's content type indicates JSON, the value is parsed and returned as a
        JSON object; otherwise the raw string value is returned unchanged.

        :param value: The variant's raw value, as returned by the enhanced feature flag endpoint.
        :type value: Optional[str]
        :param content_type: The variant's content type.
        :type content_type: Optional[str]
        :return: The parsed JSON object if the content type is JSON, otherwise the original raw value.
        :rtype: Any
        :raises json.JSONDecodeError: If the content type indicates JSON but the value is not valid JSON.
        """
        if not isinstance(value, str) or not is_json_content_type(content_type or ""):
            return value
        return json.loads(value)

    @staticmethod
    def _parse_filter_parameter_value(value: Optional[str]) -> Any:
        """
        Parses a single enhanced feature flag filter parameter value as a best-effort attempt. Unlike variant
        values, filter parameters don't have a content type, so there's no explicit signal that a value is
        intended to be JSON. Only strings that look like a JSON object or array are attempted to be parsed;
        if parsing fails, or the value doesn't look like an object/array, the original raw string is returned
        unchanged. This avoids misinterpreting a customer's intentional string value (e.g. "true", "123", or a
        plain string) as some other JSON type.

        :param value: The filter parameter's raw string value.
        :type value: Optional[str]
        :return: The parsed JSON object/array if the value looks like JSON and parses successfully, otherwise
            the original raw value.
        :rtype: Any
        """
        if not isinstance(value, str):
            return value
        trimmed = value.strip()
        if not trimmed or trimmed[0] not in "{[":
            return value
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            # Not valid JSON after all: fall back to the original string, since the customer may have
            # actually intended a literal string value.
            return value

    def _process_enhanced_feature_flag(self, feature_flag: FeatureFlag) -> Dict[str, Any]:
        """
        Convert an enhanced feature flag, loaded from the enhanced feature flag endpoint, into a dictionary that
        matches the feature management library's schema.
        Ref: https://github.com/microsoft/FeatureManagement/blob/main/Schema/FeatureFlag.v2.0.0.schema.json

        :param feature_flag: The enhanced feature flag.
        :type feature_flag: ~azure.appconfiguration.FeatureFlag
        :return: The feature flag as a dictionary.
        :rtype: Dict[str, Any]
        """
        feature_flag_value: Dict[str, Any] = {
            FEATURE_FLAG_ID_FIELD: feature_flag.name,
            "enabled": feature_flag.enabled,
        }
        if feature_flag.label:
            feature_flag_value["label"] = feature_flag.label
        if feature_flag.description:
            feature_flag_value["description"] = feature_flag.description

        filter_names: List[Optional[str]] = []
        if feature_flag.conditions:
            conditions_value: Dict[str, Any] = {}
            if feature_flag.conditions.requirement_type:
                conditions_value["requirement_type"] = feature_flag.conditions.requirement_type
            if feature_flag.conditions.filters:
                conditions_value["client_filters"] = [
                    {
                        "name": client_filter.name,
                        "parameters": (
                            {
                                key: self._parse_filter_parameter_value(value)
                                for key, value in client_filter.parameters.items()
                            }
                            if client_filter.parameters
                            else client_filter.parameters
                        ),
                    }
                    for client_filter in feature_flag.conditions.filters
                ]
                filter_names = [client_filter.name for client_filter in feature_flag.conditions.filters]
            if conditions_value:
                feature_flag_value["conditions"] = conditions_value

        if feature_flag.variants:
            try:
                feature_flag_value["variants"] = [
                    {
                        "name": variant.name,
                        "configuration_value": self._parse_variant_value(variant.value, variant.content_type),
                        "content_type": variant.content_type,
                        "status_override": variant.status_override,
                    }
                    for variant in feature_flag.variants
                ]
            except json.JSONDecodeError as e:
                raise ValueError(f"Enhanced feature flag '{feature_flag.name}' has an invalid variant value.") from e

        if feature_flag.allocation:
            allocation_value: Dict[str, Any] = {}
            if feature_flag.allocation.default_when_disabled:
                allocation_value["default_when_disabled"] = feature_flag.allocation.default_when_disabled
            if feature_flag.allocation.default_when_enabled:
                allocation_value["default_when_enabled"] = feature_flag.allocation.default_when_enabled
            if feature_flag.allocation.percentile:
                allocation_value["percentile"] = [
                    {
                        "variant": percentile.variant,
                        "from": percentile.percentile_from,
                        "to": percentile.percentile_to,
                    }
                    for percentile in feature_flag.allocation.percentile
                ]
            if feature_flag.allocation.user:
                allocation_value["user"] = [
                    {"variant": user.variant, "users": user.users} for user in feature_flag.allocation.user
                ]
            if feature_flag.allocation.group:
                allocation_value["group"] = [
                    {"variant": group.variant, "groups": group.groups} for group in feature_flag.allocation.group
                ]
            if feature_flag.allocation.seed:
                allocation_value["seed"] = feature_flag.allocation.seed
            if allocation_value:
                feature_flag_value["allocation"] = allocation_value

        if feature_flag.telemetry:
            feature_flag_value["telemetry"] = {
                "enabled": feature_flag.telemetry.enabled,
                "metadata": dict(feature_flag.telemetry.metadata) if feature_flag.telemetry.metadata else {},
            }

        if feature_flag.tags:
            feature_flag_value["tags"] = dict(feature_flag.tags)

        self._update_enhanced_feature_flag_telemetry_metadata(self._origin_endpoint, feature_flag, feature_flag_value)
        self._tracing_context.update_feature_filter_telemetry_by_names(filter_names)
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
        return self._tracing_context.update_correlation_context_header(
            headers=headers,
            request_type=request_type,
            replica_count=replica_count,
            uses_key_vault=uses_key_vault,
            feature_flag_enabled=self._feature_flag_enabled,
            is_failover_request=is_failover_request,
        )

    def _deduplicate_settings(self, configuration_settings: List[ConfigurationSetting]) -> List[ConfigurationSetting]:
        """
        Deduplicates configuration settings by key, ignoring label. The provider exposes a flat
        key->value mapping, so when multiple selectors return the same key the last one wins,
        regardless of label.

        :param List[ConfigurationSetting] configuration_settings: The list of configuration settings to deduplicate
        :return: A list of unique configuration settings
        :rtype: List[ConfigurationSetting]
        """
        unique_settings: Dict[str, ConfigurationSetting] = {}
        for settings in configuration_settings:
            unique_settings[settings.key] = settings
        return list(unique_settings.values())
