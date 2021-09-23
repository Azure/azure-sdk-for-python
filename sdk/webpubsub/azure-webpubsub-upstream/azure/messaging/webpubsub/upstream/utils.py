# coding=utf-8
# --------------------------------------------------------------------------
# Created on Sun Sep 26 2021
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.
# --------------------------------------------------------------------------

def parse_connection_string(connection_string, **kwargs):
    for segment in connection_string.split(";"):
        if "=" in segment:
            key, value = segment.split("=", maxsplit=1)
            key = key.lower()
            if key not in ("version", ):
                kwargs.setdefault(key, value)
        elif segment:
            raise ValueError(
                "Malformed connection string - expected 'key=value', found segment '{}' in '{}'".format(
                    segment, connection_string
                )
            )

    if "endpoint" not in kwargs:
        raise ValueError("connection_string missing 'endpoint' field")

    if "accesskey" not in kwargs:
        raise ValueError("connection_string missing 'accesskey' field")

    return kwargs