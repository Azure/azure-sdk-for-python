# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import six
import datetime
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
                return FeatureFlagConfigurationSetting._from_generated(key_value) # pylint: disable=protected-access
            if key_value.content_type.startswith(SecretReferenceConfigurationSetting.secret_reference_content_type):
                return SecretReferenceConfigurationSetting._from_generated(key_value) # pylint: disable=protected-access

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


    def __init__(self, key, value, feature_filters=[], **kwargs):
        # type: (str, bool, str) -> None
        super(FeatureFlagConfigurationSetting, self).__init__(**kwargs)
        self.key = key
        if not key.startswith(self.key_prefix):
            self.key = self.key_prefix + key
        self.value = value
        self.label = kwargs.get('label', None)
        self.content_type = kwargs.get('content_type', self.feature_flag_content_type)
        self.last_modified = kwargs.get('last_modified', None)
        self.tags = kwargs.get('tags', {})
        self.read_only = kwargs.get('read_only', None)
        self.etag = kwargs.get('etag', None)
        self.description = kwargs.get('description', None)
        self.display_name = kwargs.get('display_name', None)

        if isinstance(self.value, bool):
            self.value = {
                'id': self.key,
                'description': self.description,
                'enabled': self.value,
                'conditions': {
                    'client_filters': feature_filters
                }
            }

    @classmethod
    def _from_generated(cls, key_value):
        # type: (KeyValue) -> FeatureFlagConfigurationSetting
        if key_value is None:
            return None
        if key_value.value:
            try:
                key_value.value = json.loads(key_value.value)
            except json.decoder.JSONDecodeError:
                pass

        filters = None
        try:
            filters = key_value.value['conditions']['client_filters']
            if len(filters) > 0:
                filters = [FeatureFilterBase._from_generated(f) for f in filters]
                key_value.value['conditions']['client_filters'] = filters
        except KeyError:
            pass

        return cls(
            key=key_value.key,
            value=key_value.value,
            label=key_value.label,
            content_type=key_value.content_type,
            last_modified=key_value.last_modified,
            tags=key_value.tags,
            read_only=key_value.locked,
            etag=key_value.etag,
            feature_filters=filters
        )

    def _to_generated(self):
        # type: (...) -> KeyValue
        value = self.value
        if isinstance(self.value, dict):
            self._to_generated_filters()
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

    def _to_generated_filters(self):
        # type: (...) -> None
        for idx, f in enumerate(self.value['conditions']['client_filters']):
            self.value['conditions']['client_filters'][idx] = f._to_generated()

    def add_feature_filter(self, feature_filter):
        # type: (FeatureFilterBase) -> None
        self.value['conditions']['client_filters'].append(feature_filter)


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
    secret_reference_content_type = "application/vnd.microsoft.appconfig.keyvaultref+json;charset=utf-8"

    def __init__(self, key, value, label=None, **kwargs):
        # type: (str, str, str) -> None
        super(SecretReferenceConfigurationSetting, self).__init__(**kwargs)
        self.key = key
        self.label = label
        self.value = value
        self.content_type = kwargs.get('content_type', self.secret_reference_content_type)
        self.etag = kwargs.get('etag', None)
        self.last_modified = kwargs.get('last_modified', None)
        self.read_only = kwargs.get('read_only', None)
        self.tags = kwargs.get('tags', {})

    @classmethod
    def _from_generated(cls, key_value):
        # type: (KeyValue) -> SecretReferenceConfigurationSetting
        if key_value is None:
            return None
        if key_value.value:
            try:
                key_value.value = json.loads(key_value.value)
            except json.decoder.JSONDecodeError:
                pass
        return cls(
            key=key_value.key,
            value=key_value.value,
            label=key_value.label,
            secret_id=key_value.value,
            last_modified=key_value.last_modified,
            tags=key_value.tags,
            read_only=key_value.locked,
            etag=key_value.etag,
        )

    def _to_generated(self):
        # type: (...) -> KeyValue
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


class FeatureFilterBase(object):
    """ Base class for the feature filters of FeatureFlagConfigurationSetting
    """

    def __init__(self):
        pass

    @classmethod
    def _from_generated(self, feature_filter):
        if feature_filter['name'] == 'Microsoft.Targeting':
            return TargetingFeatureFilter.from_service(feature_filter['parameters'])
        elif feature_filter['name'] == 'Microsoft.TimeWindow':
            return TimeWindowFeatureFilter.from_service(feature_filter['parameters'])
        elif feature_filter['name'] == 'Microsoft.Percentage':
            return CustomFeatureFilter.from_service(feature_filter['parameters'])
        else:
            raise ValueError("{} not recognized as a feature filter.".format(feature_filter['name']))

    def _to_generated(self):
        pass


class TargetingFeatureFilter(FeatureFilterBase):
    """ A configuration setting that controls a feature flag
    :param name:
    :type name: string
    """

    def __init__(self, rollout_percentage, users=None, groups=None):
        # type: (str, dict) -> None
        self._name = 'Microsoft.Targeting'
        self.rollout_percentage = rollout_percentage
        self.users = users or []
        self.groups = groups or []

    @classmethod
    def from_service(cls, dict_repr):
        return cls(
            dict_repr['Audience']['DefaultRolloutPercentage'],
            users=dict_repr['Audience']['Users'],
            groups=dict_repr['Audience']['Groups']
        )

    def _to_generated(self):
        # type: (...) -> dict
        return {
            'name': self._name,
            'parameters': {
                'Audience': {
                    'Users': self.users,
                    'Groups': self.groups,
                    'DefaultRolloutPercentage': self.rollout_percentage
                }
            }
        }


class TimeWindowFeatureFilter(FeatureFilterBase):
    """ A configuration setting that controls a feature flag
    :param name:
    :type name: string
    """

    def __init__(self, start, end=None):
        self._name = 'Microsoft.TimeWindow'
        self.start = start
        self.end = end
        self._to_datetime_object()

    def _to_datetime_object(self):
        # TODO: datetime serialization
        pass

    @classmethod
    def from_service(cls, dict_repr):
        return cls(
            dict_repr['Start'],
            end=dict_repr.get('End', None)
        )

    def _to_generated(self):
        # type: (...) -> dict
        return {
            'name': self._name,
            'parameters': {
                'Start': self.start,
                'End': self.end
            }
        }


class CustomFeatureFilter(FeatureFilterBase):
    """ A configuration setting that controls a feature flag
    :param name:
    :type name: string
    """

    def __init__(self, value):
        self._name = 'Microsoft.Percentage'
        self.value = value

    @classmethod
    def from_service(cls, dict_repr):
        return cls(
            dict_repr['Value']
        )

    def _to_generated(self):
        # type: (...) -> dict
        return {
            'name': self._name,
            'parameters': {
                'Value': self.value
            }
        }