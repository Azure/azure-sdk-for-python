# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Mapping, TYPE_CHECKING
from .._utils import _case_insensitive_dict


def parse_connection_string(conn_str, case_sensitive_keys=False):
    # type: (str, bool) -> Mapping[str, str]
    """Parses the connection string into its component parts. Checks that each
    key in the connection string has a provided value.
    :param conn_str: String with connection details provided by Azure services.
    :type conn_str: str
    :param case_sensitive_keys: Indicates whether returned object should retrieve
        keys with case sensitive checking. Default is False.
    :type case_sensitive_keys: bool
    :rtype: Mapping
    :raises:
        ValueError: if each key in conn_str does not have a corresponding value and
            for other bad formatting of connection strings - including duplicate
            args, bad syntax, etc.
    """

    cs_args = [s.split("=", 1) for s in conn_str.strip().rstrip(";").split(";")]
    if any(len(tup) != 2 or not all(tup) for tup in cs_args):
        raise ValueError("Connection string is either blank or malformed.")
    args_dict = dict(cs_args)  # type: ignore

    if len(cs_args) != len(args_dict):
        raise ValueError("Connection string is either blank or malformed.")

    if not case_sensitive_keys:
        # if duplicate case insensitive keys are passed in, raise error
        duplicate_keys = set()
        for key in args_dict.keys():
            if key.lower() in duplicate_keys:
                raise ValueError(
                    "Duplicate key in connection string: {}".format(key.lower())
                )
            duplicate_keys.add(key.lower())
        args_dict = _case_insensitive_dict(**args_dict)

    return args_dict
