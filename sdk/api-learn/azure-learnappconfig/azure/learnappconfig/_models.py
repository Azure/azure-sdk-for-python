# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from enum import Enum


class DictMixin(object):

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, key):
        self.__dict__[key] = None

    def __eq__(self, other):
        """Compare objects by comparing all attributes."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        """Compare objects by comparing all attributes."""
        return not self.__eq__(other)

    def __str__(self):
        return str({k: v for k, v in self.__dict__.items() if not k.startswith('_')})

    def __contains__(self, k):
        return k in self.__dict__

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return [k for k in self.__dict__ if not k.startswith('_')]

    def values(self):
        return [v for k, v in self.__dict__.items() if not k.startswith('_')]

    def items(self):
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith('_')]

    def get(self, key, default=None):
        if key in self.__dict__:
            return self.__dict__[key]
        return default


class ConfigurationSetting(DictMixin):
    """A configuration value.

    :param str key: The key name of the setting.
    :param str value: The value of the setting.
    :keyword str label: The setting label.
    :ivar str etag: Entity tag (etag) of the setting.
    :ivar  ~datetime.datetime last_modified: The time the setting was last modified.
    :ivar bool read_only: Whether the setting is read-only.
    :ivar str content_type: The content type of the setting value.
    :ivar dict[str, str] tags: User tags added to the setting.
    """

    def __init__(self, key, value, **kwargs):
        # type: (str, str, Any) -> None
        self.key = key
        self.value = value
        self.etag = kwargs.get('etag', None)
        self.label = kwargs.get('label', None)
        self.content_type = kwargs.get('content_type', None)
        self.last_modified = kwargs.get('last_modified', None)
        self.read_only = kwargs.get('read_only', None)
        self.tags = kwargs.get('tags', None)


class SettingFields(str, Enum):
    """The specific settings for a given ConfigurationSetting that can be selected."""

    KEY = "key"
    LABEL = "label"
    CONTENT_TYPE = "content_type"
    VALUE = "value"
    LAST_MODIFIED = "last_modified"
    TAGS = "tags"
    READ_ONLY = "locked"
    ETAG = "etag"