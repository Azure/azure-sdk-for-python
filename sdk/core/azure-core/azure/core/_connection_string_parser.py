# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Dict

CS_DELIMITER = ";"
CS_VAL_SEPARATOR = "="

def parse_connection_string_to_dict(conn_str):
    # type: (str) -> Dict[str, str]
    """Parses the connection string into a dict containing its component parts.
    each key in the connection string has a provided value. Checks that
    :param conn_str: String with connection details provided by Azure services.
    :type conn_str: str
    :rtype: Dict[str, str]
    :raises:
        ValueError: if each key in conn_str does not have a corresponding value and
            for other bad formatting of connection strings - including duplicate
            args, bad syntax, etc.
    """

    cs_args = [s.split("=", 1) for s in conn_str.strip().rstrip(";").split(CS_DELIMITER)]
    if any(len(tup) != 2 for tup in cs_args):
        raise ValueError("Connection string is either blank or malformed.")
    args_dict = dict(cs_args)   # type: ignore

    if len(cs_args) != len(args_dict):
        raise ValueError("Connection string is either blank or malformed.")
    return args_dict
