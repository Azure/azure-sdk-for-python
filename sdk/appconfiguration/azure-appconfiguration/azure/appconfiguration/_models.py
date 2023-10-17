# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, cast
from typing_extensions import Literal

from azure.core.rest import HttpResponse
from ._generated._serialization import Model
from ._generated.models import (
    KeyValue,
    KeyValueFilter,
    Snapshot as GeneratedConfigurationSnapshot,
    SnapshotStatus,
)

PolymorphicConfigurationSetting = Union[
    "ConfigurationSetting", "SecretReferenceConfigurationSetting", "FeatureFlagConfigurationSetting"
]


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

    _attribute_map = {
        "etag": {"key": "etag", "type": "str"},
        "key": {"key": "key", "type": "str"},
        "label": {"key": "label", "type": "str"},
        "content_type": {"key": "content_type", "type": "str"},
        "value": {"key": "value", "type": "str"},
        "last_modified": {"key": "last_modified", "type": "iso-8601"},
        "read_only": {"key": "read_only", "type": "bool"},
        "tags": {"key": "tags", "type": "{str}"},
    }

    kind = "Generic"
    content_type = None

    def __init__(self, **kwargs: Any) -> None:
        super(ConfigurationSetting, self).__init__(**kwargs)
        self.key = kwargs.get("key", None)
        self.label = kwargs.get("label", None)
        self.value = kwargs.get("value", None)
        self.etag = kwargs.get("etag", None)
        self.content_type = kwargs.get("content_type", None)
        self.last_modified = kwargs.get("last_modified", None)
        self.read_only = kwargs.get("read_only", None)
        self.tags = kwargs.get("tags", {})

    @classmethod
    def _from_generated(cls, key_value: KeyValue) -> PolymorphicConfigurationSetting:
        if key_value is None:
            return key_value
        if key_value.content_type is not None:
            try:
                if key_value.content_type.startswith(
                    FeatureFlagConfigurationSetting._feature_flag_content_type  # pylint:disable=protected-access
                ) and key_value.key.startswith(  # type: ignore
                    FeatureFlagConfigurationSetting._key_prefix  # pylint: disable=protected-access
                ):
                    return FeatureFlagConfigurationSetting._from_generated(  # pylint: disable=protected-access
                        key_value
                    )
                if key_value.content_type.startswith(
                    SecretReferenceConfigurationSetting._secret_reference_content_type  # pylint:disable=protected-access
                ):
                    return SecretReferenceConfigurationSetting._from_generated(  # pylint: disable=protected-access
                        key_value
                    )
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


class FeatureFlagConfigurationSetting(ConfigurationSetting):  # pylint: disable=too-many-instance-attributes
    """A configuration setting that stores a feature flag value."""

    etag: str
    """A value representing the current state of the resource."""
    feature_id: str
    """The identity of the configuration setting."""
    key: str
    """The key of the configuration setting."""
    enabled: Optional[bool]
    """The value indicating whether the feature flag is enabled. A feature is OFF if enabled is false.
        If enabled is true, then the feature is ON if there are no conditions or if all conditions are satisfied."""
    filters: Optional[List[Dict[str, Any]]]
    """Filters that must run on the client and be evaluated as true for the feature
        to be considered enabled."""
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
        enabled: Optional[bool] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        """
        :param feature_id: The identity of the configuration setting.
        :type feature_id: str
        :keyword enabled: The value indicating whether the feature flag is enabled.
            A feature is OFF if enabled is false. If enabled is true, then the feature is ON
            if there are no conditions or if all conditions are satisfied.
        :paramtype enabled: bool or None
        :keyword filters: Filters that must run on the client and be evaluated as true for the feature
            to be considered enabled.
        :paramtype filters: list[dict[str, Any]] or None
        """
        if "key" in kwargs or "value" in kwargs:
            raise TypeError("Unexpected keyword argument, do not provide 'key' or 'value' as a keyword-arg")
        self.feature_id = feature_id
        self.key = self._key_prefix + self.feature_id
        self.label = kwargs.get("label", None)
        self.content_type = kwargs.get("content_type", self._feature_flag_content_type)
        self.last_modified = kwargs.get("last_modified", None)
        self.tags = kwargs.get("tags", {})
        self.read_only = kwargs.get("read_only", None)
        self.etag = kwargs.get("etag", None)
        self.description = kwargs.get("description", None)
        self.display_name = kwargs.get("display_name", None)
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
            self.enabled = temp.get("enabled", None)
            self.filters = None
            conditions = temp.get("conditions", None)
            if conditions:
                self.filters = conditions.get("client_filters", None)
        except (json.JSONDecodeError, ValueError):
            self._value = new_value
            self.enabled = None
            self.filters = None

    @classmethod
    def _from_generated(cls, key_value: KeyValue) -> Union["FeatureFlagConfigurationSetting", ConfigurationSetting]:
        if key_value is None:
            return key_value
        enabled = None
        filters = None
        try:
            temp = json.loads(key_value.value)  # type: ignore
            if isinstance(temp, dict):
                enabled = temp.get("enabled")
                if "conditions" in temp.keys():
                    filters = temp["conditions"].get("client_filters")
        except (ValueError, json.JSONDecodeError):
            pass

        return cls(
            feature_id=key_value.key.lstrip(".appconfig.featureflag").lstrip("/"),  # type: ignore
            label=key_value.label,
            content_type=key_value.content_type,
            last_modified=key_value.last_modified,
            tags=key_value.tags,
            read_only=key_value.locked,
            etag=key_value.etag,
            enabled=enabled,
            filters=filters,
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
    """A configuration value that references a configuration setting secret."""

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

    _attribute_map = {
        "etag": {"key": "etag", "type": "str"},
        "key": {"key": "key", "type": "str"},
        "label": {"key": "label", "type": "str"},
        "content_type": {"key": "content_type", "type": "str"},
        "value": {"key": "value", "type": "str"},
        "last_modified": {"key": "last_modified", "type": "iso-8601"},
        "read_only": {"key": "read_only", "type": "bool"},
        "tags": {"key": "tags", "type": "{str}"},
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
        self.content_type = kwargs.get("content_type", self._secret_reference_content_type)
        self.etag = kwargs.get("etag", None)
        self.last_modified = kwargs.get("last_modified", None)
        self.read_only = kwargs.get("read_only", None)
        self.tags = kwargs.get("tags", {})
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
        if key_value is None:
            return key_value
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


class ConfigurationSettingsFilter:
    """Enables filtering of configuration settings."""

    key: str
    """Filters configuration settings by their key field. Required."""
    label: Optional[str]
    """Filters configuration settings by their label field."""

    def __init__(self, *, key: str, label: Optional[str] = None) -> None:
        """
        :keyword key: Filters configuration settings by their key field. Required.
        :paramtype key: str
        :keyword label: Filters configuration settings by their label field.
        :paramtype label: str or None
        """
        self.key = key
        self.label = label


class ConfigurationSnapshot:  # pylint: disable=too-many-instance-attributes
    """A point-in-time snapshot of configuration settings."""

    name: Optional[str]
    """The name of the configuration snapshot."""
    status: Optional[Union[str, SnapshotStatus]]
    """The current status of the snapshot. Known values are: "provisioning", "ready",
        "archived", and "failed"."""
    filters: List[ConfigurationSettingsFilter]
    """A list of filters used to filter the key-values included in the configuration snapshot."""
    composition_type: Optional[str]
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

    def __init__(
        self,
        filters: List[ConfigurationSettingsFilter],
        *,
        composition_type: Optional[Literal["key", "key_label"]] = None,
        retention_period: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None,
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

    @classmethod
    def _from_generated(cls, generated: GeneratedConfigurationSnapshot) -> "ConfigurationSnapshot":
        if generated is None:
            return generated

        filters = []
        if generated.filters:
            for config_setting_filter in generated.filters:
                filters.append(
                    ConfigurationSettingsFilter(key=config_setting_filter.key, label=config_setting_filter.label)
                )
        snapshot = cls(
            filters=filters,
            composition_type=cast(Optional[Literal["key", "key_label"]], generated.composition_type),
            retention_period=generated.retention_period,
            tags=generated.tags,
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
    def _from_deserialized(  # pylint:disable=unused-argument
        cls,
        response: HttpResponse,
        deserialized: GeneratedConfigurationSnapshot,
        response_headers: Dict,
    ) -> "ConfigurationSnapshot":
        if deserialized is None:
            return deserialized
        filters = []
        if deserialized.filters:
            for config_setting_filter in deserialized.filters:
                filters.append(
                    ConfigurationSettingsFilter(key=config_setting_filter.key, label=config_setting_filter.label)
                )
        snapshot = cls(
            filters=filters,
            composition_type=cast(Optional[Literal["key", "key_label"]], deserialized.composition_type),
            retention_period=deserialized.retention_period,
            tags=deserialized.tags,
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
            config_setting_filters.append(KeyValueFilter(key=kv_filter.key, label=kv_filter.label))
        return GeneratedConfigurationSnapshot(
            filters=config_setting_filters,
            composition_type=self.composition_type,
            retention_period=self.retention_period,
            tags=self.tags,
        )
