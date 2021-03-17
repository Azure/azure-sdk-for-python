# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Dict

CS_DELIMITER = ";"
CS_VAL_SEPARATOR = "="


class DictMixin(object):
    def __setitem__(self, key, item):
        # type: (Any, Any) -> None
        self.__dict__[key] = item

    def __getitem__(self, key):
        # type: (Any) -> Any
        return self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        # type: () -> str
        return str(self)

    def __len__(self):
        # type: () -> int
        return len(self.keys())

    def __delitem__(self, key):
        # type: (Any) -> None
        self.__dict__[key] = None

    def __eq__(self, other):
        # type: (Any) -> bool
        """Compare objects by comparing all attributes."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        # type: (Any) -> bool
        """Compare objects by comparing all attributes."""
        return not self.__eq__(other)

    def __str__(self):
        # type: () -> str
        return str({k: v for k, v in self.__dict__.items() if not k.startswith("_")})

    def has_key(self, k):
        # type: (Any) -> bool
        return k in self.__dict__

    def update(self, *args, **kwargs):
        # type: (Any, Any) -> None
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        # type: () -> list
        return [k for k in self.__dict__ if not k.startswith("_")]

    def values(self):
        # type: () -> list
        return [v for k, v in self.__dict__.items() if not k.startswith("_")]

    def items(self):
        # type: () -> list
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith("_")]

    def get(self, key, default=None):
        # type: (Any, Optional[Any]) -> Any
        if key in self.__dict__:
            return self.__dict__[key]
        return default


class ConnectionStringProperties(DictMixin):
    """
    Properties of a connection string.
    """

    def __init__(self, properties_dict, is_case_sensitive=True):
        self.__dict__.update(properties_dict)
        self._case_sensitive = is_case_sensitive
        self._case_insensitive_props = (
            dict(
                (k.lower(), v)
                for k, v in self.__dict__.items()
                if not k.startswith("_")
            )
            if not self._case_sensitive
            else None
        )

    def __getitem__(self, key):
        # type: (str) -> str
        return (
            self.__dict__[key]
            if self._case_sensitive
            else self._case_insensitive_props[key.lower()]
        )

    def __contains__(self, key):
        return (
            key in self.__dict__
            if self._case_sensitive
            else key.lower() in self._case_insensitive_props
        )

    def __getattribute__(self, key):
        if (
            not key.startswith("_")  # avoid recursion error
            and not self._case_sensitive  # case insensitive
            and key.lower()
            in self._case_insensitive_props  # check case insensitive key exists
        ):
            return self._case_insensitive_props[key.lower()]
        return super(ConnectionStringProperties, self).__getattribute__(key)

    @property
    def case_sensitive(self):
        return self._case_sensitive


def parse_connection_string(conn_str, case_sensitive=True):
    # type: (str) -> ConnectionStringProperties
    """Parses the connection string into a ConnectionStringProperties object containing its
        component parts. Checks that each key in the connection string has a provided value.
    :param conn_str: String with connection details provided by Azure services.
    :type conn_str: str
    :param case_sensitive: Indicates whether returned ConnectionStringProperties
        object should retrieve keys with case sensitive checking.
    :type case_sensitive: bool
    :rtype: ~azure.core.utils.ConnectionStringProperties
    :raises:
        ValueError: if each key in conn_str does not have a corresponding value and
            for other bad formatting of connection strings - including duplicate
            args, bad syntax, etc.
    """

    cs_args = [
        s.split("=", 1) for s in conn_str.strip().rstrip(";").split(CS_DELIMITER)
    ]
    if any(len(tup) != 2 for tup in cs_args):
        raise ValueError("Connection string is either blank or malformed.")
    args_dict = dict(cs_args)  # type: ignore

    if len(cs_args) != len(args_dict):
        raise ValueError("Connection string is either blank or malformed.")

    return ConnectionStringProperties(args_dict, case_sensitive)
