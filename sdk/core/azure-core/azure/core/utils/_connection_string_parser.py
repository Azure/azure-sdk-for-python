# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Mapping


def parse_connection_string(conn_str, case_sensitive_keys=False):
    # type: (str, bool) -> Mapping[str, str]
    """Parses the connection string into a dict of its component parts, with the option of preserving case
    of keys, and validates that each key in the connection string has a provided value. If case of keys
    is not preserved (ie. `case_sensitive_keys=False`), then a dict with LOWERCASE KEYS will be returned.
    :param conn_str: String with connection details provided by Azure services.
    :type conn_str: str
    :param case_sensitive_keys: Indicates whether returned object should retrieve
        keys with case sensitive checking. True means that case of keys will be preserved.
        Default is False.
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
        new_args_dict = {}
        for key in args_dict.keys():
            new_key = key.lower()
            if new_key in new_args_dict:
                raise ValueError(
                    "Duplicate key in connection string: {}".format(new_key)
                )
            new_args_dict[new_key] = args_dict[key]
        return new_args_dict

    return args_dict
