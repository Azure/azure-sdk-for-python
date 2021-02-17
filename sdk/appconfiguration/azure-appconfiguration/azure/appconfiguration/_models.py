# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import ast
import json
import six
from msrest.serialization import Model
from ._generated.models import KeyValue

class ConfigurationSetting(Model):
    """A configuration value.
    Variables are only populated by the server, and will be ignored when
    sending a request.
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
        'etag': {'key': 'etag', 'type': 'str'},
        'key': {'key': 'key', 'type': 'str'},
        'label': {'key': 'label', 'type': 'str'},
        'content_type': {'key': 'content_type', 'type': 'str'},
        'value': {'key': 'value', 'type': 'str'},
        'last_modified': {'key': 'last_modified', 'type': 'iso-8601'},
        'read_only': {'key': 'read_only', 'type': 'bool'},
        'tags': {'key': 'tags', 'type': '{str}'},
    }

    def __init__(self, **kwargs):
        super(ConfigurationSetting, self).__init__(**kwargs)
        self.key = kwargs.get('key', None)
        self.label = kwargs.get('label', None)
        self.value = kwargs.get('value', None)
        self.etag = kwargs.get('etag', None)
        self.content_type = kwargs.get('content_type', None)
        self.last_modified = kwargs.get('last_modified', None)
        self.read_only = kwargs.get('read_only', None)
        self.tags = kwargs.get('tags', {})

    @classmethod
    def _from_generated(cls, key_value):
        # type: (KeyValue) -> ConfigurationSetting
        if key_value is None:
            return None
        if key_value.content_type is not None:
            if key_value.content_type.startswith(FeatureFlagConfigurationSetting.feature_flag_content_type):
                return FeatureFlagConfigurationSetting._from_generated(key_value)
            if key_value.content_type.startswith(SecretReferenceConfigurationSetting.secret_reference_content_type):
                return SecretReferenceConfigurationSetting._from_generated(key_value)

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
        return KeyValue(
            key=self.key,
            label=self.label,
            value=self.value,
            content_type=self.content_type,
            last_modified=self.last_modified,
            tags=self.tags,
            locked=self.read_only,
            etag=self.etag
        )


class FeatureFlagConfigurationSetting(ConfigurationSetting):
    """A feature flag configuration value.
    Variables are only populated by the server, and will be ignored when
    sending a request.
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
        'etag': {'key': 'etag', 'type': 'str'},
        'key': {'key': 'key', 'type': 'str'},
        'label': {'key': 'label', 'type': 'str'},
        'content_type': {'key': 'content_type', 'type': 'str'},
        'value': {'key': 'value', 'type': 'str'},
        'last_modified': {'key': 'last_modified', 'type': 'iso-8601'},
        'read_only': {'key': 'read_only', 'type': 'bool'},
        'tags': {'key': 'tags', 'type': '{str}'},
    }
    key_prefix = ".appconfig.featureflag/"
    feature_flag_content_type = "application/vnd.microsoft.appconfig.ff+json;charset=utf-8"


    def __init__(self, feature_id, is_enabled, **kwargs):
        # type: (str, bool, str) -> None
        super(FeatureFlagConfigurationSetting, self).__init__(**kwargs)
        self.key = feature_id
        if not feature_id.startswith(self.key_prefix):
            self.key = self.key_prefix + feature_id
        self.is_enabled = is_enabled
        self.label = kwargs.get('label', None)
        self.content_type = kwargs.get('content_type', self.feature_flag_content_type)
        self._feature_id = feature_id
        self.last_modified = kwargs.get('last_modified', None)
        self.tags = kwargs.get('tags', {})
        self.read_only = kwargs.get('read_only', None)
        self.etag = kwargs.get('etag', None)

        self.value = kwargs.get('value', None)
        if isinstance(self.value, six.string_types):
            try:
                self.value = ast.literal_eval(self.value)
            except ValueError:
                self.value = json.loads(self.value)
            except:
                pass

        # This is for instantiating a value itself
        if isinstance(self.is_enabled, bool):
            self.value = {
                'id': self.key,
                'description': kwargs.get('description', None),
                'enabled': is_enabled,
                'conditions': {
                    'client_filters': []
                }
            }

        self.is_enabled = self.value['enabled']

        self.description = kwargs.get('description', None)
        self.display_name = kwargs.get('display_name', None)


    @classmethod
    def _from_generated(cls, key_value):
        # type: (KeyValue) -> FeatureFlagConfigurationSetting
        if key_value is None:
            return None
        return cls(
            feature_id=key_value.key,
            is_enabled=key_value.value,
            label=key_value.label,
            content_type=key_value.content_type,
            last_modified=key_value.last_modified,
            tags=key_value.tags,
            read_only=key_value.locked,
            etag=key_value.etag,
            value=key_value.value
        )

    def _to_generated(self):
        value = self.value
        if isinstance(self.value, dict):
            value = json.dumps(self.value)
        return KeyValue(
            key=self.key,
            label=self.label,
            value=value,
            content_type=self.content_type,
            last_modified=self.last_modified,
            tags=self.tags,
            locked=self.read_only,
            etag=self.etag
        )

class SecretReferenceConfigurationSetting(Model):
    """A configuration value that references a KeyVault Secret
    Variables are only populated by the server, and will be ignored when
    sending a request.
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
        'etag': {'key': 'etag', 'type': 'str'},
        'key': {'key': 'key', 'type': 'str'},
        'label': {'key': 'label', 'type': 'str'},
        'content_type': {'key': 'content_type', 'type': 'str'},
        'value': {'key': 'value', 'type': 'str'},
        'last_modified': {'key': 'last_modified', 'type': 'iso-8601'},
        'read_only': {'key': 'read_only', 'type': 'bool'},
        'tags': {'key': 'tags', 'type': '{str}'},
    }
    secret_reference_content_type = "application/vnd.microsoft.appconfig.keyvaultref+json;charset=utf-8";

    def __init__(self, key, secret_id, label=None, **kwargs):
        # type: (str, str, str) -> None
        super(SecretReferenceConfigurationSetting, self).__init__(**kwargs)
        self.key = key
        self.label = label
        self._secret_id = secret_id
        self.content_type = kwargs.get('content_type', self.secret_reference_content_type)
        self.etag = kwargs.get('etag', None)
        self.value = kwargs.get('value', None)
        self.last_modified = kwargs.get('last_modified', None)
        self.read_only = kwargs.get('read_only', None)
        self.tags = kwargs.get('tags', {})

    @classmethod
    def _from_generated(cls, key_value):
        # type: (KeyValue) -> SecretReferenceConfigurationSetting
        if key_value is None:
            return None
        return cls(
            key=key_value.key,
            label=key_value.label,
            secret_id=key_value.value,
            last_modified=key_value.last_modified,
            tags=key_value.tags,
            read_only=key_value.locked,
            etag=key_value.etag,
        )

    def _to_generated(self):
        return KeyValue(
            key=self.key,
            label=self.label,
            value=self.value,
            content_type=self.content_type,
            last_modified=self.last_modified,
            tags=self.tags,
            locked=self.read_only,
            etag=self.etag
        )

class FeatureFlagFilter(object):
    """ A configuration setting that controls a feature flag
    :param name:
    :type name: string
    """

    def __init__(self, name, parameters=dict()):
        # type: (str, dict) -> None
        self.name = name
        self.parameters = parameters

