# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from __future__ import annotations
from typing import Union, TypedDict, Any

from ....._bicep.expressions import Parameter


VERSION = '2024-01-01'


class TableResource(TypedDict, total=False):
    name: Union[str, Parameter]
    """The resource name"""
    properties: Union[TableProperties, Parameter]
    """Table resource properties."""
    parent: Any
    """The Symbolic name of the resource that is the parent for this resource."""


class TableAccessPolicy(TypedDict, total=False):
    expiryTime: Union[str, Parameter]
    """Expiry time of the access policy"""
    permission: Union[str, Parameter]
    """Required. List of abbreviated permissions. Supported permission values include 'r','a','u','d'"""
    startTime: Union[str, Parameter]
    """Start time of the access policy"""


class TableProperties(TypedDict, total=False):
    signedIdentifiers: Union[list[TableSignedIdentifier], Parameter]
    """List of stored access policies specified on the table."""


class TableSignedIdentifier(TypedDict, total=False):
    accessPolicy: Union[TableAccessPolicy, Parameter]
    """Access policy"""
    id: Union[str, Parameter]
    """unique-64-character-value of the stored access policy."""
