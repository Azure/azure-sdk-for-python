# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations
from typing import cast, Union, Any, TYPE_CHECKING, Iterable
from ._common._constants import SchemaFormat

from ._generated.rest import schema as schema_rest

if TYPE_CHECKING:
    from azure.core.rest import HttpRequest


def get_http_request_kwargs(kwargs):
    http_request_keywords = ["params", "headers", "json", "data", "files"]
    http_request_kwargs = {
        key: kwargs.pop(key, None) for key in http_request_keywords if key in kwargs
    }
    return http_request_kwargs

def get_content_type(format: str):  # pylint:disable=redefined-builtin
    if format.lower() == SchemaFormat.CUSTOM.value.lower():
        return "text/plain; charset=utf-8"
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

def build_register_schema_request(
    group_name: str,
    name: str,
    definition: str,
    format: str,  # pylint:disable=redefined-builtin
    kwargs: Any,
) -> HttpRequest:

    http_request_kwargs = get_http_request_kwargs(kwargs)
    return schema_rest.build_register_request(
        group_name=group_name,
        schema_name=name,
        content=definition,
        content_type=kwargs.pop(
            "content_type", get_content_type(format)
        ),
        **http_request_kwargs,
    )

def build_get_schema_props_request(
    group_name: str,
    name: str,
    definition: str,
    format: Union[str, SchemaFormat],  # pylint:disable=redefined-builtin
    kwargs: Any,
) -> HttpRequest:

    http_request_kwargs = get_http_request_kwargs(kwargs)
    return schema_rest.build_query_id_by_content_request(
        group_name=group_name,
        schema_name=name,
        content=definition,
        content_type=kwargs.pop(
            "content_type", get_content_type(format)
        ),
        **http_request_kwargs,
    )

def build_get_schema_request(args: Iterable, kwargs: Any) -> HttpRequest:
    http_request_kwargs = get_http_request_kwargs(kwargs)
    try:
        # Check positional args for schema_id.
        # Else, check if schema_id was passed in with keyword.
        try:
            schema_id = args[0]
        except IndexError:
            schema_id = kwargs.pop("schema_id")
        schema_id = cast(str, schema_id)
        return schema_rest.build_get_by_id_request(id=schema_id, **http_request_kwargs)
    except KeyError:
        # If group_name, name, and version aren't passed in as kwargs, raise error.
        try:
            group_name = kwargs.pop("group_name")
            name = kwargs.pop("name")
            version = kwargs.pop("version")
        except KeyError:
            raise TypeError(
                """Missing required argument(s). Specify either `schema_id` """
                """or `group_name`, `name`, `version."""
            )
        return schema_rest.build_get_schema_version_request(
            group_name=group_name,
            schema_name=name,
            schema_version=version,
            **http_request_kwargs,
        )
