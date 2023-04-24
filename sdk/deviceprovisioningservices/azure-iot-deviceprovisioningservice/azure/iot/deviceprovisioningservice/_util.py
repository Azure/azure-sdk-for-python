# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from typing import Any, Dict, List, Optional


def validate_key_value_pairs(string: str) -> Dict[str, Any]:
    """
    Function to validate key-value pairs in the format: a=b;c=d

    :param str string: Semicolon delimited string of key/value pairs.
    :return: A dictionary of key/value pairs
    :rtype: Dict[str,str]
    """
    result = {}
    if string:
        kv_list = [x for x in string.split(";") if "=" in x]  # key-value pairs
        result = dict(x.split("=", 1) for x in kv_list)
    return result


def _parse_connection_string(
    connection_string: str,
    validate: Optional[List[str]] = None,
    cstring_type: str = "entity",
) -> Dict[str, Any]:
    decomposed = validate_key_value_pairs(connection_string)
    decomposed_lower = dict((k.lower(), v) for k, v in decomposed.items())
    if validate:
        for k in validate:
            if not any([decomposed.get(k), decomposed_lower.get(k.lower())]):
                raise ValueError(
                    f"{cstring_type} connection string has missing property: {k}"
                )
    return decomposed


def parse_connection_string(connection_string: str) -> Dict[str, str]:
    """
    Function to parse a Device Provisioning Service connection string into
    key/value pairs.

    :param str connection_string: Semicolon delimited connection string of key/value pairs.
    :return: A dictionary of key/value pairs
    :rtype: Dict[str,str]
    """
    validate = ["HostName", "SharedAccessKeyName", "SharedAccessKey"]
    return _parse_connection_string(
        connection_string=connection_string, validate=validate, cstring_type="IoT DPS"
    )
