# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
from datetime import datetime
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
        "etag": {"key": "etag", "type": "str"},
        "key": {"key": "key", "type": "str"},
        "label": {"key": "label", "type": "str"},
        "content_type": {"key": "content_type", "type": "str"},
        "value": {"key": "value", "type": "str"},
        "last_modified": {"key": "last_modified", "type": "iso-8601"},
        "read_only": {"key": "read_only", "type": "bool"},
        "tags": {"key": "tags", "type": "{str}"},
    }

    def __init__(self, **kwargs):
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
    def _from_generated(cls, key_value):
        # type: (KeyValue) -> ConfigurationSetting
        if key_value is None:
            return None
        if key_value.content_type is not None:
            if key_value.content_type.startswith(
                FeatureFlagConfigurationSetting.feature_flag_content_type
            ):
                return FeatureFlagConfigurationSetting._from_generated(  # pylint: disable=protected-access
                    key_value
                )  # pylint: disable=protected-access
            if key_value.content_type.startswith(
                SecretReferenceConfigurationSetting.secret_reference_content_type
            ):
                return SecretReferenceConfigurationSetting._from_generated(  # pylint: disable=protected-access
                    key_value
                )  # pylint: disable=protected-access

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
    :param key:
    :type key: str
    :param enabled:
    :type enabled: bool
    :param filters:
    :type filters: list[FeatureFilterBase]
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
    key_prefix = ".appconfig.featureflag/"
    feature_flag_content_type = (
        "application/vnd.microsoft.appconfig.ff+json;charset=utf-8"
    )

    def __init__(self, key, enabled, filters=None, **kwargs):
        # type: (str, bool, Optional[List[FeatureFilterBase]]) -> None
        super(FeatureFlagConfigurationSetting, self).__init__(**kwargs)
        self.key = key
        if not key.startswith(self.key_prefix):
            self.key = self.key_prefix + key
        self.enabled = enabled
        self.label = kwargs.get("label", None)
        self.content_type = kwargs.get("content_type", self.feature_flag_content_type)
        self.last_modified = kwargs.get("last_modified", None)
        self.tags = kwargs.get("tags", {})
        self.read_only = kwargs.get("read_only", None)
        self.etag = kwargs.get("etag", None)
        self.description = kwargs.get("description", None)
        self.display_name = kwargs.get("display_name", None)
        self.filters = filters or []

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
            filters = key_value.value["conditions"]["client_filters"]
            if filters == [None]:
                key_value.value["conditions"]["client_filters"] = []
            if len(filters) > 0 and filters != [None]:
                filters = [
                    FeatureFilterBase._from_generated(f) for f in filters  # pylint: disable=protected-access
                ]  # pylint: disable=protected-access
                key_value.value["conditions"]["client_filters"] = filters
        except KeyError:
            pass

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
        )

    def _to_generated(self):
        # type: (...) -> KeyValue
        value = {
            u"id": self.key,
            u"description": self.description,
            u"enabled": self.enabled,
            u"conditions": {
                u"client_filters": [
                    f._to_generated()  # pylint: disable=protected-access
                    for f in self.filters  # pylint: disable=protected-access
                ]
            },
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

    def add_feature_filter(self, feature_filter):
        # type: (FeatureFilterBase) -> None

        """Add a feature filter to the ConfigurationSetting
        :param feature_filter:
        :type feature_filter: list[FeatureFilterBase]
        """

        self.filters.append(feature_filter)


class SecretReferenceConfigurationSetting(Model):
    """A configuration value that references a KeyVault Secret
    Variables are only populated by the server, and will be ignored when
    sending a request.
    :ivar etag: Entity tag (etag) of the object
    :vartype etag: str
    :param key:
    :type key: str
    :param uri:
    :type uri: str
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
    secret_reference_content_type = (
        "application/vnd.microsoft.appconfig.keyvaultref+json;charset=utf-8"
    )

    def __init__(self, key, uri, label=None, **kwargs):
        # type: (str, str, str) -> None
        super(SecretReferenceConfigurationSetting, self).__init__(**kwargs)
        self.key = key
        self.label = label
        self.uri = uri
        self.content_type = kwargs.get(
            "content_type", self.secret_reference_content_type
        )
        self.etag = kwargs.get("etag", None)
        self.last_modified = kwargs.get("last_modified", None)
        self.read_only = kwargs.get("read_only", None)
        self.tags = kwargs.get("tags", {})

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
            uri=key_value.value[u"uri"],
            label=key_value.label,
            secret_id=key_value.value,
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
            value=json.dumps({u"uri": self.uri}),
            content_type=self.content_type,
            last_modified=self.last_modified,
            tags=self.tags,
            locked=self.read_only,
            etag=self.etag,
        )


class FeatureFilterBase(object):
    """Base class for the feature filters of FeatureFlagConfigurationSetting"""

    def __init__(self):
        pass

    @classmethod
    def _from_generated(cls, feature_filter):
        if feature_filter["name"] == "Microsoft.Targeting":
            return TargetingFeatureFilter.from_service(feature_filter["parameters"])
        if feature_filter["name"] == "Microsoft.TimeWindow":
            return TimeWindowFeatureFilter.from_service(feature_filter["parameters"])
        if feature_filter["name"] == "Microsoft.Percentage":
            return CustomFeatureFilter.from_service(feature_filter["parameters"])
        raise ValueError(
            "{} not recognized as a feature filter.".format(feature_filter["name"])
        )

    def _to_generated(self):
        pass


class TargetingFeatureFilter(FeatureFilterBase):
    """A configuration setting that controls a feature flag
    :param rollout_percentage:
    :type rollout_percentage: int
    :param users:
    :type users: list[str]
    :param groups:
    :type groups: list[dict[str,int]]
    """

    def __init__(
        self, rollout_percentage, users=None, groups=None
    ):  # pylint:disable=super-init-not-called
        # type: (str, dict) -> None
        self._name = "Microsoft.Targeting"
        self.rollout_percentage = rollout_percentage
        self.users = users or []
        self.groups = groups or []

    @classmethod
    def from_service(cls, dict_repr):
        # type: (dict[str, str]) -> TargetingFeatureFilter

        """Creates a TargetingFeatureFilter from the generated code call

        :param dict_repr:
        :type dict_repr: dict[str, str]
        """

        return cls(
            dict_repr["Audience"]["DefaultRolloutPercentage"],
            users=dict_repr["Audience"]["Users"],
            groups=dict_repr["Audience"]["Groups"],
        )

    def _to_generated(self):
        # type: (...) -> dict
        return {
            "name": self._name,
            "parameters": {
                "Audience": {
                    "Users": self.users,
                    "Groups": self.groups,
                    "DefaultRolloutPercentage": self.rollout_percentage,
                }
            },
        }


class TimeWindowFeatureFilter(FeatureFilterBase):
    """A configuration setting that controls a feature flag
    :param start:
    :type start: datetime.datetime
    :param end:
    :type end: datetime.datetime
    """

    def __init__(self, start, end=None):  # pylint:disable=super-init-not-called
        self._name = "Microsoft.TimeWindow"
        self.start = start
        self.end = end
        self._to_datetime_object()

    def _to_datetime_object(self):
        # Example: "Fri, 19 Feb 2021 18:00:00 GMT"
        if not isinstance(self.start, datetime):
            self.start = datetime.strptime(self.start, "%a, %d %b %Y %H:%M:%S %Z")

        if not isinstance(self.end, datetime) and self.end is not None:
            self.end = datetime.strptime(self.end, "%a, %d %b %Y %H:%M:%S %Z")

    @classmethod
    def from_service(cls, dict_repr):
        # type: (dict[str, str]) -> TimeWindowFeatureFilter

        """Creates a TimeWindowFeatureFilter from the generated code call

        :param dict_repr:
        :type dict_repr: dict[str, str]
        """
        return cls(dict_repr["Start"], end=dict_repr.get("End", None))

    def _to_generated(self):
        # type: (...) -> dict
        start = self.start.strftime("%a, %d %b %Y %H:%M:%S %Z") + "GMT"
        end = self.end
        if self.end and isinstance(self.end, datetime):
            end = self.end.strftime("%a, %d %b %Y %H:%M:%S %Z") + "GMT"
        return {"name": self._name, "parameters": {"Start": start, "End": end}}


class CustomFeatureFilter(FeatureFilterBase):
    """A configuration setting that controls a feature flag
    :param value: The value of the feature filter, this must range from 0-100
    :type value: int
    """

    def __init__(self, value):  # pylint:disable=super-init-not-called
        # type: (int) -> None
        self._name = "Microsoft.Percentage"
        self.value = value

    @classmethod
    def from_service(cls, dict_repr):
        # type: (dict[str, str]) -> CustomFeatureFilter

        """Creates a CustomFeatureFilter from the generated code call

        :param dict_repr:
        :type dict_repr: dict[str, str]
        """
        return cls(dict_repr["Value"])

    def _to_generated(self):
        # type: (...) -> dict
        return {"name": self._name, "parameters": {"Value": self.value}}
