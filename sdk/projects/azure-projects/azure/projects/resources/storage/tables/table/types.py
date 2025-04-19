# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import Union, List
from typing_extensions import TypedDict, Required

from ....._bicep.expressions import Parameter


VERSION = "2024-01-01"


class TableAccessPolicy(TypedDict, total=False):
    expiryTime: Union[str, Parameter]
    """Expiry time of the access policy"""
    permission: Required[Union[str, Parameter]]
    """List of abbreviated permissions. Supported permission values include 'r','a','u','d'."""
    startTime: Union[str, Parameter]
    """Start time of the access policy."""


class TableSignedIdentifier(TypedDict, total=False):
    accessPolicy: Union[TableAccessPolicy, Parameter]
    """Access policy."""
    id: Required[Union[str, Parameter]]
    """Unique 64-character value of the stored access policy."""


class TableProperties(TypedDict, total=False):
    signedIdentifiers: Union[List[Union[TableSignedIdentifier, Parameter]], Parameter]
    """List of stored access policies specified on the table."""


class TableResource(TypedDict, total=False):
    name: Union[str, Parameter]
    """The resource name."""
    properties: TableProperties
    """The properties of a Table."""
