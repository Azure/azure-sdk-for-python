# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
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
        self.etag = kwargs.get("etag", None)
        self.key = kwargs.get("key", None)
        self.label = kwargs.get("label", None)
        self.content_type = kwargs.get("content_type", None)
        self.value = kwargs.get("value", None)
        self.last_modified = kwargs.get("last_modified", None)
        self.read_only = kwargs.get("read_only", None)
        self.tags = kwargs.get("tags", None)

    @classmethod
    def _from_key_value(cls, key_value):
        # type: (KeyValue) -> ConfigurationSetting
        if key_value is None:
            return None
        return cls(
            key=key_value.key,
            label=key_value.label,
            content_type=key_value.content_type,
            value=key_value.value,
            last_modified=key_value.last_modified,
            tags=key_value.tags,
            read_only=key_value.locked,
            etag=key_value.etag,
        )
