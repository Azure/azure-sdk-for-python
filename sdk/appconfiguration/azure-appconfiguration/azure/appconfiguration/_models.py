# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
from typing import Dict, Optional, Any, List, Union
from msrest.serialization import Model
from ._generated.models import KeyValue


PolymorphicConfigurationSetting = Union[
    "ConfigurationSetting", "SecretReferenceConfigurationSetting", "FeatureFlagConfigurationSetting"
]


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
        # type: (**Any) -> None
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
        # type: (KeyValue) -> PolymorphicConfigurationSetting
        if key_value is None:
            return key_value
        if key_value.content_type is not None:
            try:
                if key_value.content_type.startswith(
                    FeatureFlagConfigurationSetting._feature_flag_content_type  # pylint:disable=protected-access
                ) and key_value.key.startswith(FeatureFlagConfigurationSetting.key_prefix):  # type: ignore
                    return FeatureFlagConfigurationSetting._from_generated(  # pylint: disable=protected-access
                        key_value
                    )
                if key_value.content_type.startswith(
                    SecretReferenceConfigurationSetting._secret_reference_content_type  # pylint:disable=protected-access
                ):
                    return SecretReferenceConfigurationSetting._from_generated(  # pylint: disable=protected-access
                        key_value
                    )
            except (KeyError, AttributeError, TypeError):
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

    def _to_generated(self):
        # type: () -> KeyValue
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
    :ivar feature_id:
    :vartype feature_id: str
    :ivar value: The value of the configuration setting
    :vartype value: str
    :keyword enabled:
    :paramtype enabled: bool
    :keyword filters:
    :paramtype filters: list[dict[str, Any]]
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
    :type tags: dict[str, str]
    """

    _attribute_map = {
        "etag": {"key": "etag", "type": "str"},
        "feature_id": {"key": "feaure_id", "type": "str"},
        "label": {"key": "label", "type": "str"},
        "content_type": {"key": "_feature_flag_content_type", "type": "str"},
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

    def __init__(self, feature_id, **kwargs):  # pylint: disable=dangerous-default-value
        # type: (str, **Any) -> None
        super(FeatureFlagConfigurationSetting, self).__init__(**kwargs)
        self.feature_id = feature_id
        self.key = self.key_prefix + self.feature_id
        self.label = kwargs.get("label", None)
        self.content_type = kwargs.get("content_type", self._feature_flag_content_type)
        self.last_modified = kwargs.get("last_modified", None)
        self.tags = kwargs.get("tags", {})
        self.read_only = kwargs.get("read_only", None)
        self.etag = kwargs.get("etag", None)
        self.description = kwargs.get("description", None)
        self.display_name = kwargs.get("display_name", None)
        if not self.value:
            if "enabled" in kwargs.keys() and "filters" in kwargs.keys():
                self.value = json.dumps({"enabled": kwargs.pop("enabled"), "conditions": {"client_filters": kwargs.pop("filters")}})
            elif "enabled" in kwargs.keys():
                self.value = json.dumps({"enabled": kwargs.pop("enabled"), "conditions": {"client_filters": []}})
            elif "filters" in kwargs.keys():
                self.value = json.dumps({"conditions": {"client_filters": []}})
            else:
                self.value = json.dumps({})

    @property
    def enabled(self):
        # type: () -> Union[None, bool]
        try:
            temp = json.loads(self.value)
            return temp.get("enabled", None)
        except json.decoder.JSONDecodeError:
            raise ValueError("'value' of FeatureFlagConfigurationSetting is not in the proper format. " + \
                "'value' is expected to be a dictionary")

    @enabled.setter
    def enabled(self, new_value):
        # type: (bool) -> None
        try:
            temp = json.loads(self.value)
            temp["enabled"] = new_value
            self.value = json.dumps(temp)
        except json.decoder.JSONDecodeError:
            raise ValueError("'value' of FeatureFlagConfigurationSetting is not in the proper format. " + \
                "'value' is expected to be a dictionary")

    @property
    def filters(self):
        # type: () -> Union[None, List[Any]]
        try:
            temp = json.loads(self.value)
            conditions = temp.get("conditions", None)
            if not conditions:
                return None
            try:
                return conditions.get("client_filters", [])
            except AttributeError:
                raise ValueError("'value' of FeatureFlagConfigurationSetting is not in the proper format." + \
                    " 'client_filters' is expected to be a dictionary")
        except json.decoder.JSONDecodeError:
            raise ValueError("'value' of FeatureFlagConfigurationSetting is not in the proper format. " + \
                "'value' is expected to be a dictionary")


    @filters.setter
    def filters(self, new_filters):
        # type: (List[Dict[str, Any]]) -> None
        try:
            temp = json.loads(self.value)
            if "conditions" not in temp:
                temp["conditions"] = {}
            try:
                temp["conditions"]["client_filters"] = new_filters
                self.value = json.dumps(temp)
            except AttributeError:
                raise ValueError("'value' of FeatureFlagConfigurationSetting is not in the proper format." + \
                    " 'client_filters' is expected to be a dictionary")
        except json.decoder.JSONDecodeError:
            raise ValueError("'value' of FeatureFlagConfigurationSetting is not in the proper format. " + \
                "'value' is expected to be a dictionary")

    @classmethod
    def _from_generated(cls, key_value):
        # type: (KeyValue) -> Union[FeatureFlagConfigurationSetting, ConfigurationSetting]
        if key_value is None:
            return key_value
        return cls(
            feature_id=key_value.key.lstrip(".appconfig.featureflag").lstrip("/"),  # type: ignore
            label=key_value.label,
            content_type=key_value.content_type,
            last_modified=key_value.last_modified,
            tags=key_value.tags,
            read_only=key_value.locked,
            etag=key_value.etag,
            value=key_value.value,
        )

    def _to_generated(self):
        # type: () -> KeyValue

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

    def __init__(self, key, secret_id, label=None, **kwargs):
        # type: (str, str, Optional[str], **Any) -> None
        super(SecretReferenceConfigurationSetting, self).__init__(**kwargs)
        self.key = key
        self.label = label
        self.content_type = kwargs.get(
            "content_type", self._secret_reference_content_type
        )
        self.etag = kwargs.get("etag", None)
        self.last_modified = kwargs.get("last_modified", None)
        self.read_only = kwargs.get("read_only", None)
        self.tags = kwargs.get("tags", {})
        if not self.value:
            self.value = json.dumps({"secret_uri": secret_id})

    @property
    def secret_id(self):
        # type: () -> Optional[str]
        try:
            temp = json.loads(self.value)
            return temp.get("secret_uri", None)
        except json.decoder.JSONDecodeError:
            raise ValueError("'value' of SecretReferenceConfigurationSetting is not in the proper format. " + \
                "'value' is expected to be a dictionary")

    @secret_id.setter
    def secret_id(self, secret_id):
        try:
            temp = json.loads(self.value)
            temp["secret_uri"] = secret_id
            self.value = json.dumps(temp)
        except json.decoder.JSONDecodeError:
            raise ValueError("'value' of SecretReferenceConfigurationSetting is not in the proper format. " + \
                "'value' is expected to be a dictionary")

    @classmethod
    def _from_generated(cls, key_value):
        # type: (KeyValue) -> SecretReferenceConfigurationSetting
        if key_value is None:
            return key_value

        return cls(
            key=key_value.key,  # type: ignore
            value=key_value.value,
            label=key_value.label,
            secret_id=key_value.value,  # type: ignore
            last_modified=key_value.last_modified,
            tags=key_value.tags,
            read_only=key_value.locked,
            etag=key_value.etag,
        )

    def _to_generated(self):
        # type: () -> KeyValue
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
