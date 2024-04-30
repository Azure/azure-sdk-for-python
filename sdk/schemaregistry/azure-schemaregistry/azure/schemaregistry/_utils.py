# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations
from typing import cast, Union
from ._common._constants import SchemaFormat


def get_http_request_kwargs(kwargs):
    http_request_keywords = ["params", "headers", "json", "data", "files"]
    http_request_kwargs = {
        key: kwargs.pop(key, None) for key in http_request_keywords if key in kwargs
    }
    return http_request_kwargs


def get_content_type(format: str):  # pylint:disable=redefined-builtin
    if format.lower() == SchemaFormat.CUSTOM.value.lower():
        return "text/plain; charset=utf-8"
    if format.lower() == SchemaFormat.PROTOBUF.value.lower():
        return "text/vnd.ms.protobuf"
    return f"application/json; serialization={format}"


def get_case_insensitive_format(
    format: Union[str, SchemaFormat]  # pylint:disable=redefined-builtin
) -> str:
    try:
        format = cast(SchemaFormat, format)
        format = format.value
    except AttributeError:
        pass
    return format.capitalize()
