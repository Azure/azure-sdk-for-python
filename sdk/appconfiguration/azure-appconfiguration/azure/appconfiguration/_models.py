# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
from typing import Any, Dict, List, Optional, Union
from ._generated._serialization import Model
from ._generated.models import KeyValue, KeyValueFilter, Snapshot


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
    :param key:
    :type key: str
    :param label:
    :type label: str
    :param content_type:
    :type content_type: str
    :ivar last_modified:
    :vartype last_modified: datetime
    :ivar read_only:
    :vartype read_only: bool
    :param tags:
    :type tags: Dict[str, str]
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


class FeatureFlagConfigurationSetting(ConfigurationSetting): # pylint: disable=too-many-instance-attributes
    """A feature flag configuration value.
    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar etag: Entity tag (etag) of the object
    :vartype etag: str
    :ivar feature_id:
    :vartype feature_id: str
    :ivar value: The value of the configuration setting
    :vartype value: str
    :keyword enabled:
    :paramtype enabled: bool
    :keyword filters:
    :paramtype filters: List[Dict[str, Any]]
    :param label:
    :type label: str
    :param display_name:
    :type display_name: str
    :param description:
    :type description: str
    :param content_type:
    :type content_type: str
    :ivar last_modified:
    :vartype last_modified: datetime
    :ivar read_only:
    :vartype read_only: bool
    :param tags:
    :type tags: Dict[str, str]
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
    _feature_flag_content_type = (
        "application/vnd.microsoft.appconfig.ff+json;charset=utf-8"
    )
    kind = "FeatureFlag"

    def __init__( # pylint: disable=super-init-not-called
        self,
        feature_id: str,
        *,
        enabled: Optional[bool] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> None:
        if "key" in kwargs.keys() or "value" in kwargs.keys():
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
            filters=filters
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
    :ivar key:
    :vartype key: str
    :ivar secret_id:
    :vartype secret_id: str
    :param label:
    :type label: str
    :param content_type:
    :type content_type: str
    :ivar value: The value of the configuration setting
    :vartype value: Dict[str, Any]
    :ivar last_modified:
    :vartype last_modified: datetime
    :ivar read_only:
    :vartype read_only: bool
    :param tags:
    :type tags: Dict[str, str]
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
    _secret_reference_content_type = (
        "application/vnd.microsoft.appconfig.keyvaultref+json;charset=utf-8"
    )
    kind = "SecretReference"

    def __init__(self, key: str, secret_id: str, **kwargs) -> None: # pylint: disable=super-init-not-called
        if "value" in kwargs.keys():
            raise TypeError("Unexpected keyword argument, do not provide 'value' as a keyword-arg")
        self.key = key
        self.label = kwargs.pop("label", None)
        self.content_type = kwargs.get(
            "content_type", self._secret_reference_content_type
        )
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
        except(json.JSONDecodeError, ValueError):
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

class ConfigurationSettingSnapshot(Model):  # pylint: disable=too-many-instance-attributes
    """The snapshot.
    Variables are only populated by the server, and will be ignored when sending a request.
    :ivar name: The name of the snapshot.
    :vartype name: str
    :ivar status: The current status of the snapshot. Known values are: "provisioning", "ready",
        "archived", and "failed".
    :vartype status: str or ~azure.appconfiguration.models.SnapshotStatus
    :ivar status_code: Provides additional information about the status of the snapshot. The status
        code values are modeled after HTTP status codes.
    :vartype status_code: int
    :ivar filters: A list of filters used to filter the configuration settings included in the snapshot. Required.
    :vartype filters: list[dict[str, str]]
    :ivar composition_type: The composition type describes how the key-values within the snapshot
        are composed. The 'all' composition type includes all key-values. The 'group_by_key'
        composition type ensures there are no two key-values containing the same key. Known values are:
        "all" and "group_by_key".
    :vartype composition_type: str or ~azure.appconfiguration.models.CompositionType
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

    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "status": {"key": "status", "type": "str"},
        "status_code": {"key": "status_code", "type": "int"},
        "filters": {"key": "filters", "type": "[{str}]"},
        "composition_type": {"key": "composition_type", "type": "str"},
        "created": {"key": "created", "type": "iso-8601"},
        "expires": {"key": "expires", "type": "iso-8601"},
        "retention_period": {"key": "retention_period", "type": "int"},
        "size": {"key": "size", "type": "int"},
        "items_count": {"key": "items_count", "type": "int"},
        "tags": {"key": "tags", "type": "{str}"},
        "etag": {"key": "etag", "type": "str"},
    }

    def __init__(
        self,
        filters: List[Dict[str, str]],
        *,
        composition_type: Optional[str] = None,
        retention_period: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> None:
        super(ConfigurationSettingSnapshot, self).__init__(**kwargs)
        self.name = kwargs.get("name", None)
        self.status = kwargs.get("status", None)
        self.status_code = kwargs.get("status_code", None)
        self.filters = filters
        self.composition_type = composition_type
        self.created = kwargs.get("created", None)
        self.expires = kwargs.get("expires", None)
        self.retention_period = retention_period
        self.size = kwargs.get("size", None)
        self.items_count = kwargs.get("items_count", None)
        self.tags = tags
        self.etag = kwargs.get("etag", None)

    @classmethod
    def _from_generated(cls, snapshot: Snapshot) -> "ConfigurationSettingSnapshot":
        if snapshot is None:
            return snapshot
        filters = []
        for kv_filter in snapshot.filters:
            if not kv_filter.label:
                filters.append({"key": kv_filter.key})
            else:
                filters.append({"key": kv_filter.key, "label": kv_filter.label})
        return cls(
            name = snapshot.name,
            status = snapshot.status,
            status_code = snapshot.status_code,
            filters = filters,
            composition_type = snapshot.composition_type,
            created = snapshot.created,
            expires = snapshot.expires,
            retention_period = snapshot.retention_period,
            size = snapshot.size,
            items_count = snapshot.items_count,
            tags = snapshot.tags,
            etag = snapshot.etag
        )

    def _to_generated(self) -> Snapshot:
        kv_filters = []
        for kv_filter in self.filters:
            try:
                kv_filters.append(KeyValueFilter(key=kv_filter["key"], label=kv_filter["label"]))
            except KeyError:
                kv_filters.append(KeyValueFilter(key=kv_filter["key"]))
        return Snapshot(
            filters=kv_filters,
            composition_type=self.composition_type,
            retention_period=self.retention_period,
            tags=self.tags
        )
