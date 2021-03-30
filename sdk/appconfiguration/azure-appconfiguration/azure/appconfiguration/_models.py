# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
from msrest.serialization import Model
from ._generated.models import KeyValue


class ConfigurationSetting(Model):
    """A configuration value.
    Variables are only populated by the server, and will be ignored when
    sending a request.
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
    :param value:
    :type value: str
    :ivar last_modified:
    :vartype last_modified: datetime
    :ivar read_only:
    :vartype read_only: bool
    :param tags:
    :type tags: dict[str, str]
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

    def __init__(self, **kwargs):
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
    def _from_generated(cls, key_value):
        # type: (KeyValue) -> ConfigurationSetting
        if key_value is None:
            return None
        if key_value.content_type is not None:
            if key_value.content_type.startswith(
                FeatureFlagConfigurationSetting._feature_flag_content_type  # pylint:disable=protected-access
            ) and key_value.key.startswith(FeatureFlagConfigurationSetting.key_prefix):
                return FeatureFlagConfigurationSetting._from_generated(  # pylint: disable=protected-access
                    key_value
                )
            if key_value.content_type.startswith(
                SecretReferenceConfigurationSetting._secret_reference_content_type  # pylint:disable=protected-access
            ):
                return SecretReferenceConfigurationSetting._from_generated(  # pylint: disable=protected-access
                    key_value
                )

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

    def _to_generated(self):
        # type: (...) -> KeyValue
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


class FeatureFlagConfigurationSetting(
    ConfigurationSetting
):  # pylint: disable=too-many-instance-attributes
    """A feature flag configuration value.
    Variables are only populated by the server, and will be ignored when
    sending a request.
    :ivar etag: Entity tag (etag) of the object
    :vartype etag: str
    :ivar key:
    :vartype key: str
    :ivar enabled:
    :vartype enabled: bool
    :param filters:
    :type filters: list[dict[str, Any]]
    :param label:
    :type label: str
    :param content_type:
    :type content_type: str
    :ivar last_modified:
    :vartype last_modified: datetime
    :ivar read_only:
    :vartype read_only: bool
    :param tags:
    :type tags: dict[str, str]
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
    key_prefix = ".appconfig.featureflag/"
    _feature_flag_content_type = (
        "application/vnd.microsoft.appconfig.ff+json;charset=utf-8"
    )
    kind = "FeatureFlag"

    def __init__(self, key, enabled, filters=None, **kwargs):
        # type: (str, bool, Optional[List[Dict[str, Any]]]) -> None
        super(FeatureFlagConfigurationSetting, self).__init__(**kwargs)
        self.key = key
        if not key.startswith(self.key_prefix):
            self.key = self.key_prefix + key
        self._enabled = enabled
        self.label = kwargs.get("label", None)
        self.content_type = kwargs.get("content_type", self._feature_flag_content_type)
        self.last_modified = kwargs.get("last_modified", None)
        self.tags = kwargs.get("tags", {})
        self.read_only = kwargs.get("read_only", None)
        self.etag = kwargs.get("etag", None)
        self.description = kwargs.get("description", None)
        self.display_name = kwargs.get("display_name", None)
        self._filters = filters or []
        self._value = kwargs.get("value", {})

    @property
    def enabled(self):
        # type: () -> bool
        if self._value is None:
            self._value = {"enabled": self._enabled}
        elif isinstance(self._value, dict):
            self._value["enabled"] = self._enabled
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        # type: (bool) -> bool
        if self._value is None:
            self._value = {"enabled": value}
        elif isinstance(self._value, dict):
            self._value["enabled"] = self._enabled
        self._enabled = value

    @property
    def value(self):
        # type: () -> Dict[str, Any]
        self._enabled = self._value.get("enabled", self._enabled)
        return self._value

    @value.setter
    def value(self, new_value):
        # type: (Dict[str, Any]) -> None
        try:
            self._enabled = new_value.get("enabled", self._enabled)
        except AttributeError:
            pass
        self._value = new_value

    @property
    def filters(self):
        # type: () -> List[Any]
        if self._value is None:
            self._value = {
                "conditions": {
                    "client_filters": [
                        self._filters
                    ]
                }
            }
        elif isinstance(self._value, dict):
            try:
                self._value['conditions']['client_filters'] = self._filters
            except KeyError:
                self._value['conditions'] = {'client_filters': [self._filters]}
        return self._filters

    @filters.setter
    def filters(self, new_filters):
        if self._value is None:
            self._value = {
                "conditions": {
                    "client_filters": [
                        self._filters
                    ]
                }
            }
        elif isinstance(self._value, dict):
            try:
                self._value['conditions']['client_filters'] = new_filters
            except KeyError:
                self._value['conditions'] = {'client_filters': [new_filters]}
        self._filters = new_filters

    @classmethod
    def _from_generated(cls, key_value):
        # type: (KeyValue) -> FeatureFlagConfigurationSetting
        try:
            if key_value is None:
                return None
            if key_value.value:
                try:
                    key_value.value = json.loads(key_value.value)
                except json.decoder.JSONDecodeError:
                    pass

            filters = key_value.value["conditions"]["client_filters"]

            return cls(
                key=key_value.key,
                enabled=key_value.value["enabled"],
                label=key_value.label,
                content_type=key_value.content_type,
                last_modified=key_value.last_modified,
                tags=key_value.tags,
                read_only=key_value.locked,
                etag=key_value.etag,
                filters=filters,
                value=key_value.value,
            )
        except (KeyError, AttributeError):
            return ConfigurationSetting._from_generated(key_value)

    def _to_generated(self):
        # type: (...) -> KeyValue
        value = {
            u"id": self.key,
            u"description": self.description,
            u"enabled": self._enabled,
            u"conditions": {u"client_filters": self._filters},
        }
        value = json.dumps(value)

        return KeyValue(
            key=self.key,
            label=self.label,
            value=value,
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
    :ivar secret_uri:
    :vartype secret_uri: str
    :param label:
    :type label: str
    :param content_type:
    :type content_type: str
    :param value:
    :type value: str
    :ivar last_modified:
    :vartype last_modified: datetime
    :ivar read_only:
    :vartype read_only: bool
    :param tags:
    :type tags: dict[str, str]
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

    def __init__(self, key, secret_uri, label=None, **kwargs):
        # type: (str, str, str) -> None
        super(SecretReferenceConfigurationSetting, self).__init__(**kwargs)
        self.key = key
        self.label = label
        self._secret_uri = secret_uri
        self.content_type = kwargs.get(
            "content_type", self._secret_reference_content_type
        )
        self.etag = kwargs.get("etag", None)
        self.last_modified = kwargs.get("last_modified", None)
        self.read_only = kwargs.get("read_only", None)
        self.tags = kwargs.get("tags", {})
        self._value = {"secret_uri": self._secret_uri}

    @property
    def secret_uri(self):
        # type: () -> str
        self._value['secret_uri'] = self._secret_uri
        return self._secret_uri

    @secret_uri.setter
    def secret_uri(self, value):
        self._value['secret_uri'] = value
        self._secret_uri = value

    @property
    def value(self):
        # type: () -> str
        self._secret_uri = self._value['secret_uri']
        return self._value

    @value.setter
    def value(self, value):
        # type: (dict) -> None
        try:
            self._secret_uri = value.get("secret_uri", self._secret_uri)
            self._value = value
        except AttributeError:
            self._secret_uri = None
            self._value = value

    @classmethod
    def _from_generated(cls, key_value):
        # type: (KeyValue) -> SecretReferenceConfigurationSetting
        try:
            if key_value is None:
                return None
            if key_value.value:
                try:
                    key_value.value = json.loads(key_value.value)
                except json.decoder.JSONDecodeError:
                    pass
            return cls(
                key=key_value.key,
                secret_uri=key_value.value[u"secret_uri"],
                label=key_value.label,
                secret_id=key_value.value,
                last_modified=key_value.last_modified,
                tags=key_value.tags,
                read_only=key_value.locked,
                etag=key_value.etag,
            )
        except (KeyError, AttributeError):
            return ConfigurationSetting._from_generated(key_value)

    def _to_generated(self):
        # type: (...) -> KeyValue
        return KeyValue(
            key=self.key,
            label=self.label,
            value=json.dumps({u"secret_uri": self.secret_uri}),
            content_type=self.content_type,
            last_modified=self.last_modified,
            tags=self.tags,
            locked=self.read_only,
            etag=self.etag,
        )
