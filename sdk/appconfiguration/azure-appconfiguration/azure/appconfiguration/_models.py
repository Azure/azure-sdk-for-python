# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import sys
from typing import Any, Dict, List, Optional, Union, cast

from azure.core.rest import HttpResponse
from ._generated._serialization import Model
from ._generated.models import (
    KeyValue,
    Snapshot as GeneratedSnapshot,
    KeyValueFilter,
)

if sys.version_info >= (3, 8):
    from typing import Literal  # pylint: disable=no-name-in-module, ungrouped-imports
else:
    from typing_extensions import Literal  # type: ignore  # pylint: disable=ungrouped-imports


PolymorphicConfigurationSetting = Union[
    "ConfigurationSetting", "SecretReferenceConfigurationSetting", "FeatureFlagConfigurationSetting"
]


class ConfigurationSetting(Model):
    """A configuration value.
    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar value: The value of the configuration setting
    :vartype value: str
    :ivar etag: Entity tag (etag) of the object
    :vartype etag: str
    :ivar key:
    :vartype key: str
    :ivar label:
    :vartype label: str
    :ivar content_type:
    :vartype content_type: str
    :ivar last_modified:
    :vartype last_modified: datetime
    :ivar read_only:
    :vartype read_only: bool
    :ivar tags:
    :vartype tags: dict[str, str]
    """

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

    def __init__(self, **kwargs) -> None:
        super(ConfigurationSetting, self).__init__(**kwargs)
        self.key = kwargs.get("key", None)
        self.label = kwargs.get("label", None)
        self.value = kwargs.get("value", None)
        self.etag = kwargs.get("etag", None)
        self.content_type = kwargs.get("content_type", self.content_type)
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
    """A feature flag configuration value.
    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar etag: Entity tag (etag) of the object
    :vartype etag: str
    :param feature_id:
    :type feature_id: str
    :ivar value: The value of the configuration setting
    :vartype value: str
    :keyword enabled:
    :paramtype enabled: bool
    :keyword filters:
    :paramtype filters: list[dict[str, Any]]
    :ivar label:
    :vartype label: str
    :ivar display_name:
    :vartype display_name: str
    :ivar description:
    :vartype description: str
    :ivar content_type:
    :vartype content_type: str
    :ivar last_modified:
    :vartype last_modified: datetime
    :ivar read_only:
    :vartype read_only: bool
    :ivar tags:
    :vartype tags: dict[str, str]
    """

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
        **kwargs,
    ) -> None:
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
        self._value = json.dumps({"enabled": self.enabled, "conditions": {"client_filters": self.filters}})

    @property
    def value(self):
        try:
            temp = json.loads(self._value)
            temp["enabled"] = self.enabled

            if "conditions" not in temp.keys():
                temp["conditions"] = {}
            temp["conditions"]["client_filters"] = self.filters
            self._value = json.dumps(temp)
            return self._value
        except (json.JSONDecodeError, ValueError):
            return self._value

    @value.setter
    def value(self, new_value):
        try:
            temp = json.loads(new_value)
            self._value = new_value
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
    """A configuration value that references a KeyVault Secret
    Variables are only populated by the server, and will be ignored when
    sending a request.

    :ivar etag: Entity tag (etag) of the object
    :vartype etag: str
    :param key:
    :type key: str
    :param secret_id:
    :type secret_id: str
    :ivar label:
    :vartype label: str
    :ivar content_type:
    :vartype content_type: str
    :ivar value: The value of the configuration setting
    :vartype value: dict[str, Any]
    :ivar last_modified:
    :vartype last_modified: datetime
    :ivar read_only:
    :vartype read_only: bool
    :ivar tags:
    :vartype tags: dict[str, str]
    """

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

    def __init__(self, key: str, secret_id: str, **kwargs) -> None:  # pylint: disable=super-init-not-called
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
    def value(self):
        try:
            temp = json.loads(self._value)
            temp["uri"] = self.secret_id
            self._value = json.dumps(temp)
            return self._value
        except (json.JSONDecodeError, ValueError):
            return self._value

    @value.setter
    def value(self, new_value):
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


class ConfigurationSettingFilter:
    """Enables filtering of key-values.

    All required parameters must be populated in order to send to Azure.

    :ivar key: Filters key-values by their key field. Required.
    :vartype key: str
    :ivar label: Filters key-values by their label field.
    :vartype label: str
    """

    def __init__(self, *, key: str, label: Optional[str] = None) -> None:
        """
        :keyword key: Filters key-values by their key field. Required.
        :paramtype key: str
        :keyword label: Filters key-values by their label field.
        :paramtype label: str
        """
        self.key = key
        self.label = label


class Snapshot:  # pylint: disable=too-many-instance-attributes
    """Snapshot.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :ivar name: The name of the snapshot.
    :vartype name: str
    :ivar status: The current status of the snapshot. Known values are: "provisioning", "ready",
        "archived", and "failed".
    :vartype status: str
    :param filters: A list of filters used to filter the key-values included in the snapshot.
        Required.
    :type filters: list[~azure.appconfiguration.ConfigurationSettingFilter]
    :ivar composition_type: The composition type describes how the key-values within the snapshot
        are composed. The 'key' composition type ensures there are no two key-values containing the
        same key. The 'key_label' composition type ensures there are no two key-values containing the
        same key and label. Known values are: "key" and "key_label".
    :vartype composition_type: str
    :ivar created: The time that the snapshot was created.
    :vartype created: ~datetime.datetime
    :ivar expires: The time that the snapshot will expire.
    :vartype expires: ~datetime.datetime
    :ivar retention_period: The amount of time, in seconds, that a snapshot will remain in the
        archived state before expiring. This property is only writable during the creation of a
        snapshot. If not specified, the default lifetime of key-value revisions will be used.
    :vartype retention_period: int
    :ivar size: The size in bytes of the snapshot.
    :vartype size: int
    :ivar items_count: The amount of key-values in the snapshot.
    :vartype items_count: int
    :ivar tags: The tags of the snapshot.
    :vartype tags: dict[str, str]
    :ivar etag: A value representing the current state of the snapshot.
    :vartype etag: str
    """

    def __init__(
        self,
        filters: List[ConfigurationSettingFilter],
        *,
        composition_type: Optional[Literal["key", "key_label"]] = None,
        retention_period: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None,
    ):
        """
        :param filters: A list of filters used to filter the key-values included in the snapshot.
            Required.
        :type filters: list[~azure.appconfiguration.ConfigurationSettingFilter]
        :keyword composition_type: The composition type describes how the key-values within the
            snapshot are composed. The 'key' composition type ensures there are no two key-values
            containing the same key. The 'key_label' composition type ensures there are no two key-values
            containing the same key and label. Known values are: "key" and "key_label".
        :paramtype composition_type: str
        :keyword retention_period: The amount of time, in seconds, that a snapshot will remain in the
            archived state before expiring. This property is only writable during the creation of a
            snapshot. If not specified, the default lifetime of key-value revisions will be used.
        :paramtype retention_period: int
        :keyword tags: The tags of the snapshot.
        :paramtype tags: dict[str, str]
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
    def _from_generated(cls, generated: GeneratedSnapshot) -> "Snapshot":
        if generated is None:
            return generated

        filters = []
        for config_setting_filter in generated.filters:
            filters.append(ConfigurationSettingFilter(key=config_setting_filter.key, label=config_setting_filter.label))
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
        deserialized: GeneratedSnapshot,
        response_headers: Dict,
    ) -> "Snapshot":
        if deserialized is None:
            return deserialized
        filters = []
        for config_setting_filter in deserialized.filters:
            filters.append(ConfigurationSettingFilter(key=config_setting_filter.key, label=config_setting_filter.label))
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

    def _to_generated(self) -> GeneratedSnapshot:
        config_setting_filters = []
        for kv_filter in self.filters:
            config_setting_filters.append(KeyValueFilter(key=kv_filter.key, label=kv_filter.label))
        return GeneratedSnapshot(
            filters=config_setting_filters,
            composition_type=self.composition_type,
            retention_period=self.retention_period,
            tags=self.tags,
        )
