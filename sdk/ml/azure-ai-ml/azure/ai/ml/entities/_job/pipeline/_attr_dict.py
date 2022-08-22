# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from abc import ABC
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class _AttrDict(Generic[K, V], dict, ABC):
    """This class is used for accessing values with instance.some_key. It
    supports the following scenarios:

    1. Setting arbitrary attribute, eg: obj.resource_layout.node_count = 2
      1.1 Setting same nested filed twice will return same object, eg:
              obj.resource_layout.node_count = 2
              obj.resource_layout.process_count_per_node = 2
              obj.resource_layout will be {"node_count": 2, "process_count_per_node": 2}
      1.2 Only public attribute is supported, eg: obj._resource_layout._node_count = 2 will raise AttributeError
      1.3 All set attribute can be recorded, eg:
              obj.target = "aml"
              obj.resource_layout.process_count_per_node = 2
              obj.get_attr() will return {"target": "aml", "resource_layout": {"process_count_per_node": 2}}
    2. Getting arbitrary attribute, getting non-exist attribute will return an empty dict.
    3. Calling arbitrary methods is not allowed, eg: obj.resource_layout() should raise AttributeError
    """

    def __init__(self, allowed_keys=None, **kwargs):
        """Initialize a attribute dictionary.

        :param allowed_keys: A dictionary of keys that allowed to set as arbitrary attributes. None means all keys can
            be set as arbitrary attributes.
        :type dict
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        """
        super(_AttrDict, self).__init__(**kwargs)
        if allowed_keys is None:
            # None allowed_keys means no restriction on keys can be set for _AttrDict
            self._allowed_keys = {}
            self._key_restriction = False
        else:
            # Otherwise use allowed_keys to restrict keys can be set for _AttrDict
            self._allowed_keys = dict(allowed_keys)
            self._key_restriction = True
        self._logger = logging.getLogger("attr_dict")

    def _initializing(self) -> bool:
        # use this to indicate ongoing init process, sub class need to make sure this return True during init process.
        return False

    def _get_attrs(self) -> dict:
        """Get all arbitrary attributes which has been set, empty values are
        excluded.

        :return: A dict which contains all arbitrary attributes set by user.
        :rtype: dict
        """
        # TODO: check this
        def remove_empty_values(data):
            if not isinstance(data, dict):
                return data
            return {k: remove_empty_values(v) for k, v in data.items() if v}

        return remove_empty_values(self)

    def _is_arbitrary_attr(self, attr_name: str) -> bool:
        """Checks if a given attribute name should be treat as arbitrary
        attribute.

        Attributes inside _AttrDict can be non-arbitrary attribute or arbitrary attribute.
        Non-arbitrary attributes are normal attributes like other object which stores in self.__dict__.
        Arbitrary attributes are attributes stored in the dictionary it self, what makes it special it it's value
        can be an instance of _AttrDict
        Take `obj = _AttrDict(allowed_keys={"resource_layout": {"node_count": None}})` as an example.
        `obj.some_key` is accessing non-arbitrary attribute.
        `obj.resource_layout` is accessing arbitrary attribute, user can use `obj.resource_layout.node_count = 1` to
        assign value to it.

        :param attr_name: Attribute name
        :return: If the given attribute name should be treated as arbitrary attribute.
        """
        # Internal attribute won't be set as arbitrary attribute.
        if attr_name.startswith("_"):
            return False
        # All attributes set in __init__ won't be set as arbitrary attribute
        if self._initializing():
            return False
        # If there's key restriction, only keys in it can be set as arbitrary attribute.
        if self._key_restriction and attr_name not in self._allowed_keys.keys():
            return False
        # Attributes already in attribute dict will not be set as arbitrary attribute.
        try:
            self.__getattribute__(attr_name)
        except AttributeError:
            return True
        else:
            return False

    def __getattr__(self, key: K) -> V:
        if not self._is_arbitrary_attr(key):
            return super().__getattribute__(key)
        self._logger.debug(f"getting {key}")
        try:
            return super().__getitem__(key)
        except KeyError:
            allowed_keys = self._allowed_keys.get(key, None) if self._key_restriction else None
            result = _AttrDict(allowed_keys=allowed_keys)
            self.__setattr__(key, result)
            return result

    def __setattr__(self, key: K, value: V):
        if not self._is_arbitrary_attr(key):
            super().__setattr__(key, value)
        else:
            self._logger.debug(f"setting {key} to {value}")
            return super().__setitem__(key, value)

    def __setitem__(self, key: K, value: V):
        self.__setattr__(key, value)

    def __getitem__(self, item: V):
        # support attr_dict[item] since dumping it in marshmallow requires this.
        return self.__getattr__(item)

    def __dir__(self):
        # For Jupyter Notebook auto-completion
        return list(super().__dir__()) + list(self.keys())


def try_get_non_arbitrary_attr_for_potential_attr_dict(obj, attr):
    """Try to get non-arbitrary attribute for potential attribute dict.

    Will not create target attribute if it is an arbitrary attribute in
    _AttrDict.
    """
    if isinstance(obj, _AttrDict):
        has_attr = not obj._is_arbitrary_attr(attr)
    elif isinstance(obj, dict):
        return obj[attr] if attr in obj else None
    else:
        has_attr = hasattr(obj, attr)
    if has_attr:
        return getattr(obj, attr)
    else:
        return None
