# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from __future__ import annotations
from typing import Literal, Union, TypedDict, Any

from ...._bicep.expressions import Parameter


VERSION = '2024-01-01'


class TableServiceCorsRule(TypedDict, total=False):
    allowedHeaders: Union[list[Union[str, Parameter]], Parameter]
    """Required if CorsRule element is present. A list of headers allowed to be part of the cross-origin request."""
    allowedMethods: Union[Literal['GET', 'MERGE', 'TRACE', 'PUT', 'PATCH', 'HEAD', 'CONNECT', 'POST', 'OPTIONS', 'DELETE'], Parameter]
    """Required if CorsRule element is present. A list of HTTP methods that are allowed to be executed by the origin."""
    allowedOrigins: Union[list[Union[str, Parameter]], Parameter]
    """Required if CorsRule element is present. A list of origin domains that will be allowed via CORS, or \"*\" to allow all domains"""
    exposedHeaders: Union[list[Union[str, Parameter]], Parameter]
    """Required if CorsRule element is present. A list of response headers to expose to CORS clients."""
    maxAgeInSeconds: Union[int, Parameter]
    """Required if CorsRule element is present. The number of seconds that the client/browser should cache a preflight response."""


class TableServiceCorsRules(TypedDict, total=False):
    corsRules: Union[list[TableServiceCorsRule], Parameter]
    """The List of CORS rules. You can include up to five CorsRule elements in the request."""


class TableServiceResource(TypedDict, total=False):
    name: Union[Literal['default'], Parameter]
    """The resource name"""
    properties: Union[TableServicePropertiesProperties, Parameter]
    """properties"""
    parent: Any
    """The Symbolic name of the resource that is the parent for this resource."""


class TableServicePropertiesProperties(TypedDict, total=False):
    cors: Union[TableServiceCorsRule, Parameter]
    """Specifies CORS rules for the Table service. You can include up to five CorsRule elements in the request. If no CorsRule elements are included in the request body, all CORS rules will be deleted, and CORS will be disabled for the Table service."""
