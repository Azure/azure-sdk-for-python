# coding=utf-8
# --------------------------------------------------------------------------
# Created on Sun Sep 26 2021
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.
# --------------------------------------------------------------------------


__all__ = []


from http import HTTPStatus


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


def iterate_headers(environ):
    try:
        for key, value in environ.iteritems():
            if key.startswith('HTTP_'):
                yield key[5:].lower().replace('_', '-'), value
    except AttributeError:
        # Python 3 does not have `iteritems` method so we falled back to call `items` method
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                yield key[5:].lower().replace('_', '-'), value


def build_status(status: HTTPStatus) -> str:
    return '{} {}'.format(status.value, status.phrase)
