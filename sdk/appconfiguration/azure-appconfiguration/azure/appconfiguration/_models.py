# pylint: disable=too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import collections
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, cast, Callable, TypeVar, Iterator, AsyncIterator

from azure.core import MatchConditions
from azure.core.exceptions import AzureError
from azure.core.rest import HttpResponse
from azure.core.paging import PageIterator, ItemPaged
from azure.core.async_paging import AsyncPageIterator, AsyncItemPaged, AsyncList
from ._generated._utils.serialization import Model
from ._generated.models import (
    KeyValue,
    KeyValueFilter,
    Snapshot as GeneratedConfigurationSnapshot,
    SnapshotStatus,
    SnapshotComposition,
    FeatureFlag as _GeneratedFeatureFlag,
    FeatureFlagAllocation as _GeneratedFeatureFlagAllocation,
    FeatureFlagConditions as _GeneratedFeatureFlagConditions,
    FeatureFlagFilter as _GeneratedFeatureFlagFilter,
    FeatureFlagTelemetryConfiguration as _GeneratedFeatureFlagTelemetryConfiguration,
    FeatureFlagVariantDefinition as _GeneratedFeatureFlagVariantDefinition,
    GroupAllocation as _GeneratedGroupAllocation,
    PercentileAllocation as _GeneratedPercentileAllocation,
    RequirementType,
    StatusOverride,
    UserAllocation as _GeneratedUserAllocation,
)
from ._generated._utils.model_base import _deserialize

ReturnType = TypeVar("ReturnType")


class ConfigurationSetting(Model):
    """A setting, defined by a unique combination of a key and label."""

    value: str
    """The value of the configuration setting."""
    etag: str
    """A value representing the current state of the resource."""
    key: str
    """The key of the configuration setting."""
    label: str
    """The label of the configuration setting."""
    content_type: Optional[str]
    """The content_type of the configuration setting."""
    last_modified: datetime
    """A date representing the last time the key-value was modified."""
    read_only: bool
    """Indicates whether the key-value is locked."""
    tags: Dict[str, str]
    """The tags assigned to the configuration setting."""
    description: Optional[str]
    """The description of the configuration setting."""

    _attribute_map = {
        "etag": {"key": "etag", "type": "str"},
        "key": {"key": "key", "type": "str"},
        "label": {"key": "label", "type": "str"},
        "content_type": {"key": "content_type", "type": "str"},
        "value": {"key": "value", "type": "str"},
        "last_modified": {"key": "last_modified", "type": "iso-8601"},
        "read_only": {"key": "read_only", "type": "bool"},
        "tags": {"key": "tags", "type": "{str}"},
        "description": {"key": "description", "type": "str"},
    }

    kind = "Generic"
    content_type = None

    def __init__(
        self,
        *,
        key: Optional[str] = None,
        label: Optional[str] = None,
        value: Optional[str] = None,
        etag: Optional[str] = None,
        content_type: Optional[str] = None,
        last_modified: Optional[datetime] = None,
        read_only: Optional[bool] = None,
        tags: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        :keyword key: The key of the configuration setting.
        :paramtype key: str or None
        :keyword label: The label of the configuration setting.
        :paramtype label: str or None
        :keyword value: The value of the configuration setting.
        :paramtype value: str or None
        :keyword etag: A value representing the current state of the resource.
        :paramtype etag: str or None
        :keyword content_type: The content type of the configuration setting.
        :paramtype content_type: str or None
        :keyword last_modified: The last time the configuration setting was modified.
        :paramtype last_modified: ~datetime.datetime or None
        :keyword read_only: Whether the configuration setting is read-only.
        :paramtype read_only: bool or None
        :keyword tags: The tags assigned to the configuration setting.
        :paramtype tags: dict[str, str] or None
        :keyword description: The description of the configuration setting.
        :paramtype description: str or None
        """
        super(ConfigurationSetting, self).__init__(**kwargs)
        self.key = key  # type: ignore[assignment]
        self.label = label  # type: ignore[assignment]
        self.value = value  # type: ignore[assignment]
        self.etag = etag  # type: ignore[assignment]
        self.content_type = content_type
        self.last_modified = last_modified  # type: ignore[assignment]
        self.read_only = read_only  # type: ignore[assignment]
        self.tags = tags or {}
        self.description = description

    @classmethod
    def _from_generated(cls, key_value: KeyValue) -> "ConfigurationSetting":
        # pylint:disable=protected-access
        if key_value.content_type is not None:
            try:
                if key_value.content_type.startswith(
                    FeatureFlagConfigurationSetting._feature_flag_content_type
                ) and key_value.key.startswith(  # type: ignore
                    FeatureFlagConfigurationSetting._key_prefix
                ):
                    config_setting = FeatureFlagConfigurationSetting._from_generated(key_value)
                    if key_value.value:
                        config_setting.value = key_value.value
                    return config_setting
                if key_value.content_type.startswith(
                    SecretReferenceConfigurationSetting._secret_reference_content_type
                ):
                    return SecretReferenceConfigurationSetting._from_generated(key_value)
            except (KeyError, AttributeError):
                pass

        return cls(
            key=key_value.key,
            label=key_value.label,
            value=key_value.value,
            content_type=key_value.content_type,
            last_modified=key_value.last_modified,
            tags=key_value.tags,
            read_only=key_value.locked,
            etag=key_value.etag,
            description=key_value.description,
        )

    def _to_generated(self) -> KeyValue:
        return KeyValue(
            key=self.key,
            label=self.label,
            value=self.value,
            content_type=self.content_type,
            last_modified=self.last_modified,
            tags=self.tags,
            locked=self.read_only,
            etag=self.etag,
            description=self.description,
        )


class FeatureFlagConfigurationSetting(ConfigurationSetting):  # pylint: disable=too-many-instance-attributes
    """A configuration setting that stores a feature flag value.

    :param feature_id: The identity of the configuration setting.
    :type feature_id: str
    :keyword enabled: The value indicating whether the feature flag is enabled.
        A feature is OFF if enabled is false. If enabled is true, then the feature flag is evaluated
        against its conditions to determine its state. Default value of this property is False.
    :paramtype enabled: bool
    :keyword filters: Filters that run on the client to determine whether the feature is enabled.
        By default (requirement type "Any"), the feature is considered enabled if at least one filter
        evaluates to true. With requirement type "All", every filter must evaluate to true.
    :paramtype filters: list[dict[str, Any]] or None
    """

    etag: str
    """A value representing the current state of the resource."""
    feature_id: str
    """The identity of the configuration setting."""
    key: str
    """The key of the configuration setting."""
    enabled: bool
    """The value indicating whether the feature flag is enabled. A feature is OFF if enabled is false.
        If enabled is true, then the feature flag is evaluated against its conditions/filters to determine
        its state."""
    filters: Optional[List[Dict[str, Any]]]
    """Filters that run on the client to determine whether the feature is enabled. By default
        (requirement type "Any"), the feature is considered enabled if at least one filter evaluates
        to true. With requirement type "All", every filter must evaluate to true."""
    label: str
    """The label used to group this configuration setting with others."""
    display_name: str
    """The name for the feature to use for display rather than the ID."""
    description: str
    """The description of the feature."""
    content_type: str
    """The content_type of the configuration setting."""
    last_modified: datetime
    """A date representing the last time the key-value was modified."""
    read_only: bool
    """Indicates whether the key-value is locked."""
    tags: Dict[str, str]
    """The tags assigned to the configuration setting."""

    _attribute_map = {
        "etag": {"key": "etag", "type": "str"},
        "feature_id": {"key": "feature_id", "type": "str"},
        "label": {"key": "label", "type": "str"},
        "content_type": {"key": "_feature_flag_content_type", "type": "str"},
        "value": {"key": "value", "type": "str"},
        "last_modified": {"key": "last_modified", "type": "iso-8601"},
        "read_only": {"key": "read_only", "type": "bool"},
        "tags": {"key": "tags", "type": "{str}"},
    }
    _key_prefix = ".appconfig.featureflag/"
    _feature_flag_content_type = "application/vnd.microsoft.appconfig.ff+json;charset=utf-8"
    kind = "FeatureFlag"

    def __init__(  # pylint: disable=super-init-not-called
        self,
        feature_id: str,
        *,
        enabled: bool = False,
        filters: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        """
        :param feature_id: The identity of the configuration setting.
        :type feature_id: str
        :keyword enabled: The value indicating whether the feature flag is enabled.
            A feature is OFF if enabled is false. If enabled is true, then the feature flag is evaluated
            against its conditions/filters to determine its state. Default value of this property is False.
        :paramtype enabled: bool
        :keyword filters: Filters that run on the client to determine whether the feature is enabled.
            By default (requirement type "Any"), the feature is considered enabled if at least one filter
            evaluates to true. With requirement type "All", every filter must evaluate to true.
        :paramtype filters: list[dict[str, Any]] or None
        """
        if "value" in kwargs:
            raise TypeError("Unexpected keyword argument, do not provide 'value' as a keyword-arg")
        self.feature_id = feature_id
        self.key = kwargs.get("key", None) or (self._key_prefix + self.feature_id)
        self.label = kwargs.get("label", None)  # type: ignore[assignment]
        self.content_type = kwargs.get("content_type", self._feature_flag_content_type)  # type: ignore[assignment]
        self.last_modified = kwargs.get("last_modified", None)  # type: ignore[assignment]
        self.tags = kwargs.get("tags", {})
        self.read_only = kwargs.get("read_only", None)  # type: ignore[assignment]
        self.etag = kwargs.get("etag", None)  # type: ignore[assignment]
        self.description = kwargs.get("description", None)  # type: ignore[assignment]
        self.display_name = kwargs.get("display_name", None)  # type: ignore[assignment]
        self.filters = [] if filters is None else filters
        self.enabled = enabled
        self._value = json.dumps(
            {"id": self.feature_id, "enabled": self.enabled, "conditions": {"client_filters": self.filters}}
        )

    @property
    def value(self) -> str:
        """The value of the configuration setting.

        :rtype: str
        """
        try:
            temp = json.loads(self._value)
            temp["id"] = self.feature_id
            temp["enabled"] = self.enabled
            temp["display_name"] = self.display_name
            temp["description"] = self.description
            if "conditions" not in temp.keys():
                temp["conditions"] = {}
            temp["conditions"]["client_filters"] = self.filters
            self._value = json.dumps(temp)
            return self._value
        except (json.JSONDecodeError, ValueError):
            return self._value

    @value.setter
    def value(self, new_value: str) -> None:
        try:
            temp = json.loads(new_value)
            temp["id"] = self.feature_id
            self._value = json.dumps(temp)
            self.enabled = temp.get("enabled", False)
            self.display_name = temp.get("display_name", None)
            self.description = temp.get("description", None)
            self.filters = None
            conditions = temp.get("conditions", None)
            if conditions:
                self.filters = conditions.get("client_filters", None)
        except (json.JSONDecodeError, ValueError):
            self._value = new_value
            self.enabled = False
            self.filters = None

    @classmethod
    def _from_generated(cls, key_value: KeyValue) -> "FeatureFlagConfigurationSetting":
        enabled = False
        filters = None
        display_name = None
        description = None
        feature_id = None
        try:
            temp = json.loads(key_value.value)  # type: ignore
            if isinstance(temp, dict):
                enabled = temp.get("enabled", False)
                display_name = temp.get("display_name")
                description = temp.get("description")
                feature_id = temp.get("id")

                if "conditions" in temp.keys():
                    filters = temp["conditions"].get("client_filters")
        except (ValueError, json.JSONDecodeError):
            pass

        return cls(
            feature_id=feature_id,  # type: ignore
            key=key_value.key,
            label=key_value.label,
            content_type=key_value.content_type,
            last_modified=key_value.last_modified,
            tags=key_value.tags,
            read_only=key_value.locked,
            etag=key_value.etag,
            enabled=enabled,
            filters=filters,
            display_name=display_name,
            description=description,
        )

    def _to_generated(self) -> KeyValue:
        return KeyValue(
            key=self.key,
            label=self.label,
            value=self.value,
            content_type=self.content_type,
            last_modified=self.last_modified,
            tags=self.tags,
            locked=self.read_only,
            etag=self.etag,
        )


class SecretReferenceConfigurationSetting(ConfigurationSetting):
    """A configuration value that references a configuration setting secret.

    :param key: The key of the configuration setting.
    :type key: str
    :param secret_id: The URI of the secret referenced by this configuration setting.
    :type secret_id: str
    """

    etag: str
    """A value representing the current state of the resource."""
    key: str
    """The key of the configuration setting."""
    secret_id: Optional[str]
    """The identity of the configuration setting."""
    label: str
    """The label used to group this configuration setting with others."""
    content_type: str
    """The content_type of the configuration setting."""
    last_modified: datetime
    """A date representing the last time the key-value was modified."""
    read_only: bool
    """Indicates whether the key-value is locked."""
    tags: Dict[str, str]
    """The tags assigned to the configuration setting."""
    description: Optional[str]
    """The description of the configuration setting."""

    _attribute_map = {
        "etag": {"key": "etag", "type": "str"},
        "key": {"key": "key", "type": "str"},
        "label": {"key": "label", "type": "str"},
        "content_type": {"key": "content_type", "type": "str"},
        "value": {"key": "value", "type": "str"},
        "last_modified": {"key": "last_modified", "type": "iso-8601"},
        "read_only": {"key": "read_only", "type": "bool"},
        "tags": {"key": "tags", "type": "{str}"},
        "description": {"key": "description", "type": "str"},
    }
    _secret_reference_content_type = "application/vnd.microsoft.appconfig.keyvaultref+json;charset=utf-8"
    kind = "SecretReference"

    def __init__(self, key: str, secret_id: str, **kwargs: Any) -> None:  # pylint: disable=super-init-not-called
        """
        :param key: The key of the configuration setting.
        :type key: str
        :param secret_id: The identity of the configuration setting.
        :type secret_id: str
        """
        if "value" in kwargs:
            raise TypeError("Unexpected keyword argument, do not provide 'value' as a keyword-arg")
        self.key = key
        self.label = kwargs.pop("label", None)
        self.content_type = kwargs.get("content_type", self._secret_reference_content_type)  # type: ignore[assignment]
        self.etag = kwargs.get("etag", None)  # type: ignore[assignment]
        self.last_modified = kwargs.get("last_modified", None)  # type: ignore[assignment]
        self.read_only = kwargs.get("read_only", None)  # type: ignore[assignment]
        self.tags = kwargs.get("tags", {})
        self.description = kwargs.get("description", None)
        self.secret_id = secret_id
        self._value = json.dumps({"uri": secret_id})

    @property
    def value(self) -> str:
        """The value of the configuration setting.

        :rtype: str
        """
        try:
            temp = json.loads(self._value)
            temp["uri"] = self.secret_id
            self._value = json.dumps(temp)
            return self._value
        except (json.JSONDecodeError, ValueError):
            return self._value

    @value.setter
    def value(self, new_value: str) -> None:
        try:
            temp = json.loads(new_value)
            self._value = new_value
            self.secret_id = temp.get("uri")
        except (json.JSONDecodeError, ValueError):
            self._value = new_value
            self.secret_id = None

    @classmethod
    def _from_generated(cls, key_value: KeyValue) -> "SecretReferenceConfigurationSetting":
        secret_uri = None
        try:
            temp = json.loads(key_value.value)  # type: ignore
            secret_uri = temp.get("uri")
            if not secret_uri:
                secret_uri = temp.get("secret_uri")
        except (ValueError, json.JSONDecodeError):
            pass

        return cls(
            key=key_value.key,  # type: ignore
            label=key_value.label,
            secret_id=secret_uri,  # type: ignore
            last_modified=key_value.last_modified,
            tags=key_value.tags,
            read_only=key_value.locked,
            etag=key_value.etag,
            description=key_value.description,
        )

    def _to_generated(self) -> KeyValue:
        return KeyValue(
            key=self.key,
            label=self.label,
            value=self.value,
            content_type=self.content_type,
            last_modified=self.last_modified,
            tags=self.tags,
            locked=self.read_only,
            etag=self.etag,
            description=self.description,
        )


class FeatureFilter(Model):
    """A filter that conditionally enables or disables a feature flag.

    :ivar name: The name of the filter. Required.
    :vartype name: str
    :ivar parameters: The parameters used by the filter.
    :vartype parameters: dict[str, str] or None
    """

    name: str
    """The name of the filter. Required."""
    parameters: Optional[Dict[str, str]]
    """The parameters used by the filter."""

    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "parameters": {"key": "parameters", "type": "{str}"},
    }

    def __init__(self, *, name: str, parameters: Optional[Dict[str, str]] = None) -> None:
        """
        :keyword name: The name of the filter. Required.
        :paramtype name: str
        :keyword parameters: The parameters used by the filter.
        :paramtype parameters: dict[str, str] or None
        """
        super().__init__()
        self.name = name
        self.parameters = parameters

    @classmethod
    def _from_generated(cls, generated: _GeneratedFeatureFlagFilter) -> "FeatureFilter":
        return cls(name=generated.name, parameters=generated.parameters)

    def _to_generated(self) -> _GeneratedFeatureFlagFilter:
        return _GeneratedFeatureFlagFilter(name=self.name, parameters=self.parameters)


class FeatureFlagConditions(Model):
    """The conditions that must be met for a feature flag to be enabled.

    :ivar requirement_type: The requirement type for the conditions. Known values are: "Any" and
     "All".
    :vartype requirement_type: str or ~azure.appconfiguration.RequirementType or None
    :ivar filters: The filters that will conditionally enable or disable the flag.
    :vartype filters: list[~azure.appconfiguration.FeatureFilter] or None
    """

    requirement_type: Optional[Union[str, RequirementType]]
    """The requirement type for the conditions. Known values are: "Any" and "All"."""
    filters: Optional[List[FeatureFilter]]
    """The filters that will conditionally enable or disable the flag."""

    _attribute_map = {
        "requirement_type": {"key": "requirement_type", "type": "RequirementType"},
        "filters": {"key": "filters", "type": "[FeatureFilter]"},
    }

    def __init__(
        self,
        *,
        requirement_type: Optional[Union[str, RequirementType]] = None,
        filters: Optional[List[FeatureFilter]] = None,
    ) -> None:
        """
        :keyword requirement_type: The requirement type for the conditions. Known values are: "Any"
         and "All".
        :paramtype requirement_type: str or ~azure.appconfiguration.RequirementType or None
        :keyword filters: The filters that will conditionally enable or disable the flag.
        :paramtype filters: list[~azure.appconfiguration.FeatureFilter] or None
        """
        super().__init__()
        self.requirement_type = requirement_type
        self.filters = filters

    @classmethod
    def _from_generated(cls, generated: _GeneratedFeatureFlagConditions) -> "FeatureFlagConditions":
        # pylint:disable=protected-access
        return cls(
            requirement_type=generated.requirement_type,
            filters=(
                [FeatureFilter._from_generated(f) for f in generated.filters] if generated.filters is not None else None
            ),
        )

    def _to_generated(self) -> _GeneratedFeatureFlagConditions:
        # pylint:disable=protected-access
        return _GeneratedFeatureFlagConditions(
            requirement_type=self.requirement_type,
            filters=([f._to_generated() for f in self.filters] if self.filters is not None else None),
        )


class FeatureFlagVariantDefinition(Model):
    """A variant of a feature flag.

    :ivar name: The name of the variant. Required.
    :vartype name: str
    :ivar value: The value of the variant.
    :vartype value: str or None
    :ivar content_type: The content type of the value stored within the key-value.
    :vartype content_type: str or None
    :ivar status_override: Determines if the variant should override the status of the flag. Known
     values are: "None", "Enabled", and "Disabled".
    :vartype status_override: str or ~azure.appconfiguration.StatusOverride or None
    """

    name: str
    """The name of the variant. Required."""
    value: Optional[str]
    """The value of the variant."""
    content_type: Optional[str]
    """The content type of the value stored within the key-value."""
    status_override: Optional[Union[str, StatusOverride]]
    """Determines if the variant should override the status of the flag."""

    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "value": {"key": "value", "type": "str"},
        "content_type": {"key": "content_type", "type": "str"},
        "status_override": {"key": "status_override", "type": "StatusOverride"},
    }

    def __init__(
        self,
        *,
        name: str,
        value: Optional[str] = None,
        content_type: Optional[str] = None,
        status_override: Optional[Union[str, StatusOverride]] = None,
    ) -> None:
        """
        :keyword name: The name of the variant. Required.
        :paramtype name: str
        :keyword value: The value of the variant.
        :paramtype value: str or None
        :keyword content_type: The content type of the value stored within the key-value.
        :paramtype content_type: str or None
        :keyword status_override: Determines if the variant should override the status of the flag.
         Known values are: "None", "Enabled", and "Disabled".
        :paramtype status_override: str or ~azure.appconfiguration.StatusOverride or None
        """
        super().__init__()
        self.name = name
        self.value = value
        self.content_type = content_type
        self.status_override = status_override

    @classmethod
    def _from_generated(cls, generated: _GeneratedFeatureFlagVariantDefinition) -> "FeatureFlagVariantDefinition":
        return cls(
            name=generated.name,
            value=generated.value,
            content_type=generated.content_type,
            status_override=generated.status_override,
        )

    def _to_generated(self) -> _GeneratedFeatureFlagVariantDefinition:
        return _GeneratedFeatureFlagVariantDefinition(
            name=self.name,
            value=self.value,
            content_type=self.content_type,
            status_override=self.status_override,
        )


class PercentileAllocation(Model):
    """Allocates a percentile range of users to a variant.

    :ivar variant: The variant to allocate these percentiles to. Required.
    :vartype variant: str
    :ivar percentile_from: The lower bounds for this percentile allocation. Required.
    :vartype percentile_from: float
    :ivar percentile_to: The upper bounds for this percentile allocation. Required.
    :vartype percentile_to: float
    """

    variant: str
    """The variant to allocate these percentiles to. Required."""
    percentile_from: float
    """The lower bounds for this percentile allocation. Required."""
    percentile_to: float
    """The upper bounds for this percentile allocation. Required."""

    _attribute_map = {
        "variant": {"key": "variant", "type": "str"},
        "percentile_from": {"key": "from", "type": "float"},
        "percentile_to": {"key": "to", "type": "float"},
    }

    def __init__(self, *, variant: str, percentile_from: float, percentile_to: float) -> None:
        """
        :keyword variant: The variant to allocate these percentiles to. Required.
        :paramtype variant: str
        :keyword percentile_from: The lower bounds for this percentile allocation. Required.
        :paramtype percentile_from: float
        :keyword percentile_to: The upper bounds for this percentile allocation. Required.
        :paramtype percentile_to: float
        """
        super().__init__()
        self.variant = variant
        self.percentile_from = percentile_from
        self.percentile_to = percentile_to

    @classmethod
    def _from_generated(cls, generated: _GeneratedPercentileAllocation) -> "PercentileAllocation":
        return cls(
            variant=generated.variant,
            percentile_from=generated.from_property,
            percentile_to=generated.to,
        )

    def _to_generated(self) -> _GeneratedPercentileAllocation:
        return _GeneratedPercentileAllocation(
            variant=self.variant,
            from_property=self.percentile_from,
            to=self.percentile_to,
        )


class UserAllocation(Model):
    """Allocates specific users to a variant.

    :ivar variant: The variant to allocate these users to. Required.
    :vartype variant: str
    :ivar users: The users to get this variant. Required.
    :vartype users: list[str]
    """

    variant: str
    """The variant to allocate these users to. Required."""
    users: List[str]
    """The users to get this variant. Required."""

    _attribute_map = {
        "variant": {"key": "variant", "type": "str"},
        "users": {"key": "users", "type": "[str]"},
    }

    def __init__(self, *, variant: str, users: List[str]) -> None:
        """
        :keyword variant: The variant to allocate these users to. Required.
        :paramtype variant: str
        :keyword users: The users to get this variant. Required.
        :paramtype users: list[str]
        """
        super().__init__()
        self.variant = variant
        self.users = users

    @classmethod
    def _from_generated(cls, generated: _GeneratedUserAllocation) -> "UserAllocation":
        return cls(variant=generated.variant, users=generated.users)

    def _to_generated(self) -> _GeneratedUserAllocation:
        return _GeneratedUserAllocation(variant=self.variant, users=self.users)


class GroupAllocation(Model):
    """Allocates specific groups to a variant.

    :ivar variant: The variant to allocate these groups to. Required.
    :vartype variant: str
    :ivar groups: The groups to get this variant. Required.
    :vartype groups: list[str]
    """

    variant: str
    """The variant to allocate these groups to. Required."""
    groups: List[str]
    """The groups to get this variant. Required."""

    _attribute_map = {
        "variant": {"key": "variant", "type": "str"},
        "groups": {"key": "groups", "type": "[str]"},
    }

    def __init__(self, *, variant: str, groups: List[str]) -> None:
        """
        :keyword variant: The variant to allocate these groups to. Required.
        :paramtype variant: str
        :keyword groups: The groups to get this variant. Required.
        :paramtype groups: list[str]
        """
        super().__init__()
        self.variant = variant
        self.groups = groups

    @classmethod
    def _from_generated(cls, generated: _GeneratedGroupAllocation) -> "GroupAllocation":
        return cls(variant=generated.variant, groups=generated.groups)

    def _to_generated(self) -> _GeneratedGroupAllocation:
        return _GeneratedGroupAllocation(variant=self.variant, groups=self.groups)


class FeatureFlagAllocation(Model):
    """Defines how to allocate variants based on context.

    :ivar default_when_disabled: The default variant to use when disabled.
    :vartype default_when_disabled: str or None
    :ivar default_when_enabled: The default variant to use when enabled but not allocated.
    :vartype default_when_enabled: str or None
    :ivar percentile: Allocates percentiles to variants.
    :vartype percentile: list[~azure.appconfiguration.PercentileAllocation] or None
    :ivar user: Allocates users to variants.
    :vartype user: list[~azure.appconfiguration.UserAllocation] or None
    :ivar group: Allocates groups to variants.
    :vartype group: list[~azure.appconfiguration.GroupAllocation] or None
    :ivar seed: The seed used for random allocation.
    :vartype seed: str or None
    """

    default_when_disabled: Optional[str]
    """The default variant to use when disabled."""
    default_when_enabled: Optional[str]
    """The default variant to use when enabled but not allocated."""
    percentile: Optional[List[PercentileAllocation]]
    """Allocates percentiles to variants."""
    user: Optional[List[UserAllocation]]
    """Allocates users to variants."""
    group: Optional[List[GroupAllocation]]
    """Allocates groups to variants."""
    seed: Optional[str]
    """The seed used for random allocation."""

    _attribute_map = {
        "default_when_disabled": {"key": "default_when_disabled", "type": "str"},
        "default_when_enabled": {"key": "default_when_enabled", "type": "str"},
        "percentile": {"key": "percentile", "type": "[PercentileAllocation]"},
        "user": {"key": "user", "type": "[UserAllocation]"},
        "group": {"key": "group", "type": "[GroupAllocation]"},
        "seed": {"key": "seed", "type": "str"},
    }

    def __init__(
        self,
        *,
        default_when_disabled: Optional[str] = None,
        default_when_enabled: Optional[str] = None,
        percentile: Optional[List[PercentileAllocation]] = None,
        user: Optional[List[UserAllocation]] = None,
        group: Optional[List[GroupAllocation]] = None,
        seed: Optional[str] = None,
    ) -> None:
        """
        :keyword default_when_disabled: The default variant to use when disabled.
        :paramtype default_when_disabled: str or None
        :keyword default_when_enabled: The default variant to use when enabled but not allocated.
        :paramtype default_when_enabled: str or None
        :keyword percentile: Allocates percentiles to variants.
        :paramtype percentile: list[~azure.appconfiguration.PercentileAllocation] or None
        :keyword user: Allocates users to variants.
        :paramtype user: list[~azure.appconfiguration.UserAllocation] or None
        :keyword group: Allocates groups to variants.
        :paramtype group: list[~azure.appconfiguration.GroupAllocation] or None
        :keyword seed: The seed used for random allocation.
        :paramtype seed: str or None
        """
        super().__init__()
        self.default_when_disabled = default_when_disabled
        self.default_when_enabled = default_when_enabled
        self.percentile = percentile
        self.user = user
        self.group = group
        self.seed = seed

    @classmethod
    def _from_generated(cls, generated: _GeneratedFeatureFlagAllocation) -> "FeatureFlagAllocation":
        # pylint:disable=protected-access
        return cls(
            default_when_disabled=generated.default_when_disabled,
            default_when_enabled=generated.default_when_enabled,
            percentile=(
                [PercentileAllocation._from_generated(p) for p in generated.percentile]
                if generated.percentile is not None
                else None
            ),
            user=([UserAllocation._from_generated(u) for u in generated.user] if generated.user is not None else None),
            group=(
                [GroupAllocation._from_generated(g) for g in generated.group] if generated.group is not None else None
            ),
            seed=generated.seed,
        )

    def _to_generated(self) -> _GeneratedFeatureFlagAllocation:
        # pylint:disable=protected-access
        return _GeneratedFeatureFlagAllocation(
            default_when_disabled=self.default_when_disabled,
            default_when_enabled=self.default_when_enabled,
            percentile=([p._to_generated() for p in self.percentile] if self.percentile is not None else None),
            user=[u._to_generated() for u in self.user] if self.user is not None else None,
            group=[g._to_generated() for g in self.group] if self.group is not None else None,
            seed=self.seed,
        )


class FeatureFlagTelemetryConfiguration(Model):
    """The telemetry configuration of a feature flag.

    :ivar enabled: The enabled state of the telemetry. Required.
    :vartype enabled: bool
    :ivar metadata: The metadata to include on outbound telemetry.
    :vartype metadata: dict[str, str] or None
    """

    enabled: bool
    """The enabled state of the telemetry. Required."""
    metadata: Optional[Dict[str, str]]
    """The metadata to include on outbound telemetry."""

    _attribute_map = {
        "enabled": {"key": "enabled", "type": "bool"},
        "metadata": {"key": "metadata", "type": "{str}"},
    }

    def __init__(self, *, enabled: bool, metadata: Optional[Dict[str, str]] = None) -> None:
        """
        :keyword enabled: The enabled state of the telemetry. Required.
        :paramtype enabled: bool
        :keyword metadata: The metadata to include on outbound telemetry.
        :paramtype metadata: dict[str, str] or None
        """
        super().__init__()
        self.enabled = enabled
        self.metadata = metadata

    @classmethod
    def _from_generated(
        cls, generated: _GeneratedFeatureFlagTelemetryConfiguration
    ) -> "FeatureFlagTelemetryConfiguration":
        return cls(enabled=generated.enabled, metadata=generated.metadata)

    def _to_generated(self) -> _GeneratedFeatureFlagTelemetryConfiguration:
        return _GeneratedFeatureFlagTelemetryConfiguration(enabled=self.enabled, metadata=self.metadata)


class FeatureFlag(Model):  # pylint: disable=too-many-instance-attributes
    """A feature flag used with the dedicated feature flag endpoints.

    This model represents a feature flag and is used exclusively with the
    feature flag-specific API endpoints (set_feature_flag, get_feature_flag, etc).
    """

    name: str
    """The name of the feature flag."""
    enabled: bool
    """The enabled state of the feature flag."""
    label: Optional[str]
    """The label the feature flag belongs to."""
    description: Optional[str]
    """The description of the feature flag."""
    conditions: Optional[FeatureFlagConditions]
    """The conditions of the feature flag."""
    variants: Optional[List[FeatureFlagVariantDefinition]]
    """The variants of the feature flag."""
    allocation: Optional[FeatureFlagAllocation]
    """The allocation of the feature flag."""
    telemetry: Optional[FeatureFlagTelemetryConfiguration]
    """The telemetry settings of the feature flag."""
    tags: Optional[Dict[str, str]]
    """The tags of the feature flag."""
    last_modified: Optional[datetime]
    """A date representing the last time the feature flag was modified."""
    etag: Optional[str]
    """A value representing the current state of the resource."""

    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "enabled": {"key": "enabled", "type": "bool"},
        "label": {"key": "label", "type": "str"},
        "description": {"key": "description", "type": "str"},
        "conditions": {"key": "conditions", "type": "FeatureFlagConditions"},
        "variants": {"key": "variants", "type": "[FeatureFlagVariantDefinition]"},
        "allocation": {"key": "allocation", "type": "FeatureFlagAllocation"},
        "telemetry": {"key": "telemetry", "type": "FeatureFlagTelemetryConfiguration"},
        "tags": {"key": "tags", "type": "{str}"},
        "last_modified": {"key": "last_modified", "type": "iso-8601"},
        "etag": {"key": "etag", "type": "str"},
    }

    def __init__(
        self,
        *,
        name: str,
        enabled: bool = False,
        label: Optional[str] = None,
        description: Optional[str] = None,
        conditions: Optional[FeatureFlagConditions] = None,
        variants: Optional[List[FeatureFlagVariantDefinition]] = None,
        allocation: Optional[FeatureFlagAllocation] = None,
        telemetry: Optional[FeatureFlagTelemetryConfiguration] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        :param name: The name of the feature flag.
        :type name: str
        :keyword enabled: The enabled state of the feature flag. Default is False.
        :paramtype enabled: bool
        :keyword label: The label the feature flag belongs to.
        :paramtype label: str or None
        :keyword description: The description of the feature flag.
        :paramtype description: str or None
        :keyword conditions: The conditions of the feature flag.
        :paramtype conditions: ~azure.appconfiguration.FeatureFlagConditions or None
        :keyword variants: The variants of the feature flag.
        :paramtype variants: list[~azure.appconfiguration.FeatureFlagVariantDefinition] or None
        :keyword allocation: The allocation of the feature flag.
        :paramtype allocation: ~azure.appconfiguration.FeatureFlagAllocation or None
        :keyword telemetry: The telemetry settings of the feature flag.
        :paramtype telemetry: ~azure.appconfiguration.FeatureFlagTelemetryConfiguration or None
        :keyword tags: The tags of the feature flag.
        :paramtype tags: dict[str, str] or None
        """
        super().__init__(**kwargs)
        self.name = name
        self.enabled = enabled
        self.label = label
        self.description = description
        self.conditions = conditions
        self.variants = variants
        self.allocation = allocation
        self.telemetry = telemetry
        self.tags = tags or {}
        self.last_modified = kwargs.get("last_modified", None)
        self.etag = kwargs.get("etag", None)

    @classmethod
    def _from_generated(cls, generated: _GeneratedFeatureFlag) -> "FeatureFlag":
        """Create an SDK FeatureFlag from a generated FeatureFlag object.

        :param generated: The generated FeatureFlag object
        :type generated: ~azure.appconfiguration._generated.models.FeatureFlag
        :return: An SDK FeatureFlag
        :rtype: ~azure.appconfiguration.FeatureFlag
        """
        # pylint:disable=protected-access
        return cls(
            name=generated.name,
            enabled=generated.enabled,
            label=generated.label,
            description=generated.description,
            conditions=(
                FeatureFlagConditions._from_generated(generated.conditions)
                if generated.conditions is not None
                else None
            ),
            variants=(
                [FeatureFlagVariantDefinition._from_generated(v) for v in generated.variants]
                if generated.variants is not None
                else None
            ),
            allocation=(
                FeatureFlagAllocation._from_generated(generated.allocation)
                if generated.allocation is not None
                else None
            ),
            telemetry=(
                FeatureFlagTelemetryConfiguration._from_generated(generated.telemetry)
                if generated.telemetry is not None
                else None
            ),
            tags=generated.tags,
            last_modified=generated.last_modified,
            etag=generated.etag,
        )

    def _to_generated(self) -> _GeneratedFeatureFlag:
        """Convert this SDK FeatureFlag to a generated FeatureFlag object.

        :return: A generated FeatureFlag
        :rtype: ~azure.appconfiguration._generated.models.FeatureFlag
        """
        # pylint:disable=protected-access
        return _GeneratedFeatureFlag(
            enabled=self.enabled,
            description=self.description,
            conditions=self.conditions._to_generated() if self.conditions is not None else None,
            variants=([v._to_generated() for v in self.variants] if self.variants is not None else None),
            allocation=self.allocation._to_generated() if self.allocation is not None else None,
            telemetry=self.telemetry._to_generated() if self.telemetry is not None else None,
            tags=self.tags,
        )


class ConfigurationSettingsFilter:
    """Enables filtering of configuration settings.

    :keyword key: Filters configuration settings by their key field. Required.
    :paramtype key: str
    :keyword label: Filters configuration settings by their label field.
    :paramtype label: str or None
    :keyword tags: Filters key-values by their tags field.
    :paramtype tags: list[str] or None
    """

    key: str
    """Filters configuration settings by their key field. Required."""
    label: Optional[str]
    """Filters configuration settings by their label field."""
    tags: Optional[List[str]]
    """Filters key-values by their tags field."""

    def __init__(self, *, key: str, label: Optional[str] = None, tags: Optional[List[str]] = None) -> None:
        """
        :keyword key: Filters configuration settings by their key field. Required.
        :paramtype key: str
        :keyword label: Filters configuration settings by their label field.
        :paramtype label: str or None
        :keyword tags: Filters key-values by their tags field.
        :paramtype tags: list[str] or None
        """
        self.key = key
        self.label = label
        self.tags = tags


class ConfigurationSnapshot:  # pylint: disable=too-many-instance-attributes
    """A point-in-time snapshot of configuration settings.

    :param filters: A list of filters used to filter the key-values included in the configuration snapshot.
        Required.
    :type filters: list[~azure.appconfiguration.ConfigurationSettingsFilter]
    :keyword composition_type: The composition type describes how the key-values within the configuration
        snapshot are composed. The 'key' composition type ensures there are no two key-values
        containing the same key. The 'key_label' composition type ensures there are no two key-values
        containing the same key and label. Known values are: "key" and "key_label".
    :paramtype composition_type: str or None
    :keyword retention_period: The amount of time, in seconds, that a configuration snapshot will remain in the
        archived state before expiring. This property is only writable during the creation of a configuration
        snapshot. If not specified, the default lifetime of key-value revisions will be used.
    :paramtype retention_period: int or None
    :keyword tags: The tags of the configuration snapshot.
    :paramtype tags: dict[str, str] or None
    :keyword description: The description of the configuration snapshot.
    :paramtype description: str or None
    """

    name: Optional[str]
    """The name of the configuration snapshot."""
    status: Optional[Union[str, SnapshotStatus]]
    """The current status of the snapshot. Known values are: "provisioning", "ready",
        "archived", and "failed"."""
    filters: List[ConfigurationSettingsFilter]
    """A list of filters used to filter the key-values included in the configuration snapshot. Required."""
    composition_type: Optional[Union[str, SnapshotComposition]]
    """The composition type describes how the key-values within the configuration snapshot
        are composed. The 'key' composition type ensures there are no two key-values containing the
        same key. The 'key_label' composition type ensures there are no two key-values containing the
        same key and label. Known values are: "key" and "key_label"."""
    created: Optional[datetime]
    """The time that the configuration snapshot was created."""
    expires: Optional[datetime]
    """The time that the configuration snapshot will expire."""
    retention_period: Optional[int]
    """The amount of time, in seconds, that a configuration snapshot will remain in the
        archived state before expiring. This property is only writable during the creation of a configuration
        snapshot. If not specified, the default lifetime of key-value revisions will be used."""
    size: Optional[int]
    """The size in bytes of the configuration snapshot."""
    items_count: Optional[int]
    """The amount of key-values in the configuration snapshot."""
    tags: Optional[Dict[str, str]]
    """The tags of the configuration snapshot."""
    etag: Optional[str]
    """A value representing the current state of the configuration snapshot."""
    description: Optional[str]
    """The description of the configuration snapshot."""

    def __init__(
        self,
        filters: List[ConfigurationSettingsFilter],
        *,
        composition_type: Optional[Union[str, SnapshotComposition]] = None,
        retention_period: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        :param filters: A list of filters used to filter the key-values included in the configuration snapshot.
            Required.
        :type filters: list[~azure.appconfiguration.ConfigurationSettingsFilter]
        :keyword composition_type: The composition type describes how the key-values within the configuration
            snapshot are composed. The 'key' composition type ensures there are no two key-values
            containing the same key. The 'key_label' composition type ensures there are no two key-values
            containing the same key and label. Known values are: "key" and "key_label".
        :paramtype composition_type: str or None
        :keyword retention_period: The amount of time, in seconds, that a configuration snapshot will remain in the
            archived state before expiring. This property is only writable during the creation of a configuration
            snapshot. If not specified, the default lifetime of key-value revisions will be used.
        :paramtype retention_period: int or None
        :keyword tags: The tags of the configuration snapshot.
        :paramtype tags: dict[str, str] or None
        :keyword description: The description of the configuration snapshot.
        :paramtype description: str or None
        """
        self.name = None
        self.status = None
        self.filters = filters
        self.composition_type = composition_type
        self.created = None
        self.expires = None
        self.retention_period = retention_period
        self.size = None
        self.items_count = None
        self.tags = tags
        self.etag = None
        self.description = description

    @classmethod
    def _from_generated(cls, generated: GeneratedConfigurationSnapshot) -> "ConfigurationSnapshot":
        if generated is None:
            return generated

        filters = []
        if generated.filters:
            for config_setting_filter in generated.filters:
                filters.append(
                    ConfigurationSettingsFilter(
                        key=config_setting_filter.key,
                        label=config_setting_filter.label,
                        tags=config_setting_filter.tags,
                    )
                )
        snapshot = cls(
            filters=filters,
            composition_type=cast(SnapshotComposition, generated.composition_type),
            retention_period=generated.retention_period,
            tags=generated.tags,
            description=generated.description,
        )
        snapshot.name = generated.name
        snapshot.status = generated.status
        snapshot.created = generated.created
        snapshot.expires = generated.expires
        snapshot.size = generated.size
        snapshot.items_count = generated.items_count
        snapshot.etag = generated.etag

        return snapshot

    @classmethod
    def _from_deserialized(
        cls,
        response: HttpResponse,  # pylint:disable=unused-argument
        deserialized: GeneratedConfigurationSnapshot,
        response_headers: Dict,  # pylint:disable=unused-argument
    ) -> "ConfigurationSnapshot":
        if deserialized is None:
            return deserialized
        filters = []
        if deserialized.filters:
            for config_setting_filter in deserialized.filters:
                filters.append(
                    ConfigurationSettingsFilter(
                        key=config_setting_filter.key,
                        label=config_setting_filter.label,
                        tags=config_setting_filter.tags,
                    )
                )
        snapshot = cls(
            filters=filters,
            composition_type=cast(SnapshotComposition, deserialized.composition_type),
            retention_period=deserialized.retention_period,
            tags=deserialized.tags,
            description=deserialized.description,
        )
        snapshot.name = deserialized.name
        snapshot.status = deserialized.status
        snapshot.created = deserialized.created
        snapshot.expires = deserialized.expires
        snapshot.size = deserialized.size
        snapshot.items_count = deserialized.items_count
        snapshot.etag = deserialized.etag

        return snapshot

    def _to_generated(self) -> GeneratedConfigurationSnapshot:
        config_setting_filters = []
        for kv_filter in self.filters:
            config_setting_filters.append(KeyValueFilter(key=kv_filter.key, label=kv_filter.label, tags=kv_filter.tags))
        return GeneratedConfigurationSnapshot(
            filters=config_setting_filters,
            composition_type=self.composition_type,
            retention_period=self.retention_period,
            tags=self.tags,
            description=self.description,
        )


class ConfigurationSettingLabel:
    """The label info of a configuration setting.

    :keyword name: The configuration setting label name.
    :paramtype name: str or None
    """

    name: Optional[str]
    """The name of the ConfigurationSetting label."""

    def __init__(self, *, name: Optional[str] = None) -> None:
        """
        :keyword name: The configuration setting label name.
        :paramtype composition_type: str or None
        """
        self.name = name


def _return_deserialized_and_headers(_, deserialized, response_headers):
    return deserialized, response_headers


class ConfigurationSettingPropertiesPagedBase:  # pylint:disable=too-many-instance-attributes
    """Base class for iterable of ConfigurationSetting properties.

    :param command: The command to execute for pagination.
    :type command: Callable
    """

    etag: str
    """The current etag"""
    _etags: List[str]
    """The etag expected for the pages."""
    _current_etag: int = 0
    """Current index in the etags list."""

    def __init__(self, command: Callable, **kwargs: Any):
        """Initialize common attributes for paged configuration settings.

        :param command: The command to execute for pagination.
        :type command: Callable
        """
        self._command = command
        self._key = kwargs.get("key")
        self._label = kwargs.get("label")
        self._accept_datetime = kwargs.get("accept_datetime")
        self._select = kwargs.get("select")
        self._tags = kwargs.get("tags")
        self._snapshot = kwargs.get("snapshot")
        self._etags: List[str] = kwargs.get("etags", [])
        self._current_etag = 0
        self._match_condition = kwargs.get("match_condition")
        self._deserializer = lambda objs: [
            ConfigurationSetting._from_generated(x) for x in objs  # pylint:disable=protected-access
        ]

    def _next_etag(self) -> Optional[str]:
        """Get the next etag from the list and increment the current position.

        :return: The next etag if available, otherwise None.
        :rtype: str or None
        """
        if not self._etags or self._current_etag >= len(self._etags):
            return None
        etag = self._etags[self._current_etag]
        self._current_etag += 1
        return etag

    def _extract_data_cb_base(self, get_next_return) -> tuple:
        """Extract pagination data from the response.

        :param get_next_return: Tuple of (deserialized response, response headers)
        :type get_next_return: tuple
        :return: Tuple of (next_link, page iterator or None)
        :rtype: tuple
        """
        deserialized, response_headers = get_next_return

        # Set etag from response headers, or fall back to expected etag if available
        self.etag = response_headers.get("ETag")
        if self._etags and self._current_etag > 0:
            # There was a 304 Not Modified response, we need to set the etag
            self.etag = response_headers.get("ETag", self._etags[self._current_etag - 1])

        next_link = deserialized.get("@nextLink")

        if "items" in deserialized:
            list_of_elem = _deserialize(List[KeyValue], deserialized["items"])
            return next_link, iter(self._deserializer(list_of_elem))

        # No items found in the response, skipping the page
        return next_link, None


class ConfigurationSettingPropertiesPaged(
    ConfigurationSettingPropertiesPagedBase, PageIterator
):  # pylint:disable=too-many-instance-attributes
    """An iterable of ConfigurationSetting properties.

    :param command: The command to execute for pagination.
    :type command: Callable
    """

    def __init__(self, command: Callable, **kwargs: Any):
        super().__init__(command, **kwargs)
        PageIterator.__init__(
            self,
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=kwargs.get("continuation_token"),
        )

    def _get_next_cb(self, continuation_token, **kwargs):
        etag = self._next_etag()
        return self._command(
            key=self._key,
            label=self._label,
            accept_datetime=self._accept_datetime,
            select=self._select,
            tags=self._tags,
            snapshot=self._snapshot,
            etag=etag,
            match_condition=self._match_condition,
            continuation_token=continuation_token,
            cls=kwargs.pop("cls", None) or _return_deserialized_and_headers,
        )

    def _extract_data_cb(self, get_next_return):
        return self._extract_data_cb_base(get_next_return)

    def __next__(self) -> Iterator[ReturnType]:
        """Get the next page in the iterator.

        :returns: An iterator of objects in the next page.
        :rtype: iterator[ReturnType]
        :raises StopIteration: If there are no more pages to return.
        :raises AzureError: If the request fails.
        """
        # Is the exact same method as `PageIterator`, excluding the if statement before the return.
        if self.continuation_token is None and self._did_a_call_already:
            raise StopIteration("End of paging")
        try:
            self._response = self._get_next(self.continuation_token)
        except AzureError as error:
            if not error.continuation_token:
                error.continuation_token = self.continuation_token
            raise

        self._did_a_call_already = True

        self.continuation_token, self._current_page = self._extract_data(self._response)

        # App Config's addition to skip empty pages
        if self._current_page is None:
            # We skip over pages that are empty, change from mach conditions
            return self.__next__()
        return iter(self._current_page)


class ConfigurationSettingPropertiesPagedAsync(
    ConfigurationSettingPropertiesPagedBase, AsyncPageIterator
):  # pylint:disable=too-many-instance-attributes
    """An iterable of ConfigurationSetting properties.

    :param command: The command to execute for pagination.
    :type command: Callable
    """

    def __init__(self, command: Callable, **kwargs: Any):
        ConfigurationSettingPropertiesPagedBase.__init__(self, command, **kwargs)
        AsyncPageIterator.__init__(
            self,
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=kwargs.get("continuation_token"),
        )

    async def _get_next_cb(self, continuation_token, **kwargs):
        etag = self._next_etag()
        return await self._command(
            key=self._key,
            label=self._label,
            accept_datetime=self._accept_datetime,
            select=self._select,
            tags=self._tags,
            snapshot=self._snapshot,
            etag=etag,
            match_condition=self._match_condition,
            continuation_token=continuation_token,
            cls=kwargs.pop("cls", None) or _return_deserialized_and_headers,
        )

    async def _extract_data_cb(self, get_next_return):
        return self._extract_data_cb_base(get_next_return)

    async def __anext__(self) -> AsyncIterator[ReturnType]:
        """Get the next page in the iterator.

        :returns: An iterator of objects in the next page.
        :rtype: iterator[ReturnType]
        :raises StopIteration: If there are no more pages to return.
        :raises AzureError: If the request fails.
        """
        # Is the exact same method as `PageIterator`, excluding the if statement before the return.
        if self.continuation_token is None and self._did_a_call_already:
            raise StopAsyncIteration("End of paging")
        try:
            self._response = await self._get_next(self.continuation_token)
        except AzureError as error:
            if not error.continuation_token:
                error.continuation_token = self.continuation_token
            raise

        self._did_a_call_already = True

        self.continuation_token, self._current_page = await self._extract_data(self._response)

        # App Config's addition to skip empty pages
        if self._current_page is None:
            # We skip over pages that are empty, change from mach conditions
            return await self.__anext__()

        # If current_page was a sync list, wrap it async-like
        if isinstance(self._current_page, collections.abc.Iterable):
            self._current_page = AsyncList(self._current_page)

        return self._current_page


class ConfigurationSettingPaged(ItemPaged[ConfigurationSetting]):
    """
    An iterable of ConfigurationSettings that supports etag-based change detection.

    This class extends ItemPaged to provide efficient monitoring of configuration changes
    by using ETags. When used with the `match_conditions` parameter in `by_page()`,
    it only returns pages that have changed since the provided ETags were collected.

    Example:

    .. code-block:: python

        # Get initial page ETags
        items = client.list_configuration_settings(key_filter="sample_*")
        match_conditions = [page.etag for page in items.by_page()]

        # Later, check for changes - only changed pages are returned
        items = client.list_configuration_settings(key_filter="sample_*")
        for page in items.by_page(match_conditions=match_conditions):
            # Process only changed pages
            pass
    """

    def by_page(self, continuation_token: Optional[str] = None, *, match_conditions: Optional[List[str]] = None) -> Any:
        """Get an iterator of pages of objects, instead of an iterator of objects.

        :param str continuation_token:
            An opaque continuation token. This value can be retrieved from the
            continuation_token field of a previous generator object. If specified,
            this generator will begin returning results from this point.
        :keyword match_conditions: A list of etags to check for changes. If provided, the iterator will
            check each page against the corresponding etag and only return pages that have changed.
        :paramtype match_conditions: list[str] or None
        :returns: An iterator of pages (themselves iterator of objects)
        :rtype: iterator[iterator[ReturnType]]
        """
        if "match_conditions" not in self._kwargs and match_conditions:
            self._kwargs["etags"] = match_conditions
            self._kwargs["match_condition"] = MatchConditions.IfModified
        return self._page_iterator_class(continuation_token=continuation_token, *self._args, **self._kwargs)


class AsyncConfigurationSettingPaged(AsyncItemPaged[ConfigurationSetting]):
    """
    An async iterable of ConfigurationSettings that supports etag-based change detection.

    This class provides asynchronous iteration over configuration settings, with optional support for
    etag-based change detection. By supplying a list of etags via the `match_conditions` parameter to
    the `by_page` method, you can efficiently detect and retrieve only those pages that have changed
    since your last retrieval.

    Example:

    .. code-block:: python

        async for setting in AsyncConfigurationSettingPaged(...):
            # Process each setting asynchronously
            print(setting)

        # To iterate by page and use etag-based change detection:
        etags = ["etag1", "etag2", "etag3"]
        async for page in paged.by_page(match_conditions=etags):
            async for setting in page:
                print(setting)

    When `match_conditions` is provided, each page is checked against the corresponding etag.
    If the page has not changed (HTTP 304), it is skipped. If the page has changed (HTTP 200),
    the new page is returned. This allows efficient polling for changes without retrieving
    unchanged data.
    """

    def by_page(self, continuation_token: Optional[str] = None, *, match_conditions: Optional[List[str]] = None) -> Any:
        """Get an async iterator of pages of objects, instead of an iterator of objects.

        :param str continuation_token:
            An opaque continuation token. This value can be retrieved from the
            continuation_token field of a previous generator object. If specified,
            this generator will begin returning results from this point.
        :keyword match_conditions: A list of etags to check for changes. If provided, the iterator will
            check each page against the corresponding etag and only return pages that have changed.
        :paramtype match_conditions: list[str] or None
        :returns: An async iterator of pages (themselves iterator of objects)
        :rtype: AsyncIterator[AsyncIterator[ReturnType]]
        """
        if "match_conditions" not in self._kwargs and match_conditions:
            self._kwargs["etags"] = match_conditions
            self._kwargs["match_condition"] = MatchConditions.IfModified
        return self._page_iterator_class(continuation_token=continuation_token, *self._args, **self._kwargs)


class FeatureFlagPropertiesPagedBase:  # pylint:disable=too-many-instance-attributes
    """Base class for iterable of FeatureFlag properties."""

    etag: str
    """The current etag"""
    _etags: List[str]
    """The etag expected for the pages."""
    _current_etag: int = 0
    """Current index in the etags list."""

    def __init__(self, command: Callable, **kwargs: Any):
        """Initialize common attributes for paged feature flags.

        :param command: The command to execute for pagination.
        :type command: Callable
        """
        self._command = command
        self._name = kwargs.get("name")
        self._label = kwargs.get("label")
        self._accept_datetime = kwargs.get("accept_datetime")
        self._select = kwargs.get("select")
        self._tags = kwargs.get("tags")
        self._etags: List[str] = kwargs.get("etags", [])
        self._current_etag = 0
        self._match_condition = kwargs.get("match_condition")
        self._deserializer = lambda objs: [
            FeatureFlag._from_generated(x) for x in objs  # pylint:disable=protected-access
        ]

    def _next_etag(self) -> Optional[str]:
        """Get the next etag from the list and increment the current position.

        :return: The next etag if available, otherwise None.
        :rtype: str or None
        """
        if not self._etags or self._current_etag >= len(self._etags):
            return None
        etag = self._etags[self._current_etag]
        self._current_etag += 1
        return etag

    def _extract_data_cb_base(self, get_next_return) -> tuple:
        """Extract pagination data from the response.

        :param get_next_return: Tuple of (deserialized response, response headers)
        :type get_next_return: tuple
        :return: Tuple of (next_link, page iterator or None)
        :rtype: tuple
        """
        deserialized, response_headers = get_next_return

        # Set etag from response headers, or fall back to expected etag if available
        self.etag = response_headers.get("ETag")
        if self._etags and self._current_etag > 0:
            # There was a 304 Not Modified response, we need to set the etag
            self.etag = response_headers.get("ETag", self._etags[self._current_etag - 1])

        next_link = deserialized.get("@nextLink")

        if "items" in deserialized:
            list_of_elem = _deserialize(List[_GeneratedFeatureFlag], deserialized["items"])
            return next_link, iter(self._deserializer(list_of_elem))

        # No items found in the response, skipping the page
        return next_link, None


class FeatureFlagPropertiesPaged(
    FeatureFlagPropertiesPagedBase, PageIterator
):  # pylint:disable=too-many-instance-attributes
    """An iterable of FeatureFlag properties."""

    def __init__(self, command: Callable, **kwargs: Any):
        super().__init__(command, **kwargs)
        PageIterator.__init__(
            self,
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=kwargs.get("continuation_token"),
        )

    def _get_next_cb(self, continuation_token, **kwargs):
        etag = self._next_etag()
        return self._command(
            name=self._name,
            label=self._label,
            accept_datetime=self._accept_datetime,
            select=self._select,
            tags=self._tags,
            etag=etag,
            match_condition=self._match_condition,
            continuation_token=continuation_token,
            cls=kwargs.pop("cls", None) or _return_deserialized_and_headers,
        )

    def _extract_data_cb(self, get_next_return):
        return self._extract_data_cb_base(get_next_return)

    def __next__(self) -> Iterator[ReturnType]:
        """Get the next page in the iterator.

        :returns: An iterator of objects in the next page.
        :rtype: iterator[ReturnType]
        :raises StopIteration: If there are no more pages to return.
        :raises AzureError: If the request fails.
        """
        # Is the exact same method as `PageIterator`, excluding the if statement before the return.
        if self.continuation_token is None and self._did_a_call_already:
            raise StopIteration("End of paging")
        try:
            self._response = self._get_next(self.continuation_token)
        except AzureError as error:
            if not error.continuation_token:
                error.continuation_token = self.continuation_token
            raise

        self._did_a_call_already = True

        self.continuation_token, self._current_page = self._extract_data(self._response)

        # App Config's addition to skip empty pages
        if self._current_page is None:
            # We skip over pages that are empty, change from mach conditions
            return self.__next__()
        return iter(self._current_page)


class FeatureFlagPropertiesPagedAsync(
    FeatureFlagPropertiesPagedBase, AsyncPageIterator
):  # pylint:disable=too-many-instance-attributes
    """An iterable of FeatureFlag properties."""

    def __init__(self, command: Callable, **kwargs: Any):
        FeatureFlagPropertiesPagedBase.__init__(self, command, **kwargs)
        AsyncPageIterator.__init__(
            self,
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=kwargs.get("continuation_token"),
        )

    async def _get_next_cb(self, continuation_token, **kwargs):
        etag = self._next_etag()
        return await self._command(
            name=self._name,
            label=self._label,
            accept_datetime=self._accept_datetime,
            select=self._select,
            tags=self._tags,
            etag=etag,
            match_condition=self._match_condition,
            continuation_token=continuation_token,
            cls=kwargs.pop("cls", None) or _return_deserialized_and_headers,
        )

    async def _extract_data_cb(self, get_next_return):
        return self._extract_data_cb_base(get_next_return)

    async def __anext__(self) -> AsyncIterator[ReturnType]:
        """Get the next page in the iterator.

        :returns: An iterator of objects in the next page.
        :rtype: iterator[ReturnType]
        :raises StopIteration: If there are no more pages to return.
        :raises AzureError: If the request fails.
        """
        # Is the exact same method as `PageIterator`, excluding the if statement before the return.
        if self.continuation_token is None and self._did_a_call_already:
            raise StopAsyncIteration("End of paging")
        try:
            self._response = await self._get_next(self.continuation_token)
        except AzureError as error:
            if not error.continuation_token:
                error.continuation_token = self.continuation_token
            raise

        self._did_a_call_already = True

        self.continuation_token, self._current_page = await self._extract_data(self._response)

        # App Config's addition to skip empty pages
        if self._current_page is None:
            # We skip over pages that are empty, change from mach conditions
            return await self.__anext__()

        # If current_page was a sync list, wrap it async-like
        if isinstance(self._current_page, collections.abc.Iterable):
            self._current_page = AsyncList(self._current_page)

        return self._current_page


class FeatureFlagPaged(ItemPaged[FeatureFlag]):
    """
    An iterable of FeatureFlags that supports etag-based change detection.

    This class extends ItemPaged to provide efficient monitoring of feature flag changes
    by using ETags. When used with the `match_conditions` parameter in `by_page()`,
    it only returns pages that have changed since the provided ETags were collected.

    Example:

    .. code-block:: python

        # Get initial page ETags
        flags = client.list_feature_flags(name_filter="sample_*")
        match_conditions = [page.etag for page in flags.by_page()]

        # Later, check for changes - only changed pages are returned
        flags = client.list_feature_flags(name_filter="sample_*")
        for page in flags.by_page(match_conditions=match_conditions):
            # Process only changed pages
            pass
    """

    def by_page(self, continuation_token: Optional[str] = None, *, match_conditions: Optional[List[str]] = None) -> Any:
        """Get an iterator of pages of objects, instead of an iterator of objects.

        :param str continuation_token:
            An opaque continuation token. This value can be retrieved from the
            continuation_token field of a previous generator object. If specified,
            this generator will begin returning results from this point.
        :keyword match_conditions: A list of etags to check for changes. If provided, the iterator will
            check each page against the corresponding etag and only return pages that have changed.
        :paramtype match_conditions: list[str] or None
        :returns: An iterator of pages (themselves iterator of objects)
        :rtype: iterator[iterator[ReturnType]]
        """
        if "match_conditions" not in self._kwargs and match_conditions:
            self._kwargs["etags"] = match_conditions
            self._kwargs["match_condition"] = MatchConditions.IfModified
        return self._page_iterator_class(continuation_token=continuation_token, *self._args, **self._kwargs)


class AsyncFeatureFlagPaged(AsyncItemPaged[FeatureFlag]):
    """
    An async iterable of FeatureFlags that supports etag-based change detection.

    This class provides asynchronous iteration over feature flags, with optional support for
    etag-based change detection. By supplying a list of etags via the `match_conditions` parameter to
    the `by_page` method, you can efficiently detect and retrieve only those pages that have changed
    since your last retrieval.

    Example:

    .. code-block:: python

        async for flag in AsyncFeatureFlagPaged(...):
            # Process each feature flag asynchronously
            print(flag)

        # To iterate by page and use etag-based change detection:
        etags = ["etag1", "etag2", "etag3"]
        async for page in paged.by_page(match_conditions=etags):
            async for flag in page:
                print(flag)

    When `match_conditions` is provided, each page is checked against the corresponding etag.
    If the page has not changed (HTTP 304), it is skipped. If the page has changed (HTTP 200),
    the new page is returned. This allows efficient polling for changes without retrieving
    unchanged data.
    """

    def by_page(self, continuation_token: Optional[str] = None, *, match_conditions: Optional[List[str]] = None) -> Any:
        """Get an async iterator of pages of objects, instead of an iterator of objects.

        :param str continuation_token:
            An opaque continuation token. This value can be retrieved from the
            continuation_token field of a previous generator object. If specified,
            this generator will begin returning results from this point.
        :keyword match_conditions: A list of etags to check for changes. If provided, the iterator will
            check each page against the corresponding etag and only return pages that have changed.
        :paramtype match_conditions: list[str] or None
        :returns: An async iterator of pages (themselves iterator of objects)
        :rtype: AsyncIterator[AsyncIterator[ReturnType]]
        """
        if "match_conditions" not in self._kwargs and match_conditions:
            self._kwargs["etags"] = match_conditions
            self._kwargs["match_condition"] = MatchConditions.IfModified
        return self._page_iterator_class(continuation_token=continuation_token, *self._args, **self._kwargs)
