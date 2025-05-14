# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Union, Any
from typing_extensions import TypedDict

from ..._bicep.expressions import Parameter


VERSION = "2021-04-01"


class ResourceGroupResource(TypedDict, total=False):
    location: Union[str, Parameter]
    """The location of the resource group. It cannot be changed after the resource group has been created.
    It must be one of the supported Azure locations.
    """
    managedBy: Union[str, Parameter]
    """The ID of the resource that manages this resource group."""
    name: Union[str, Parameter]
    """The resource name"""
    properties: dict[str, Any]
    """The resource group properties."""
    tags: dict[str, Union[None, str, Parameter]]
    """Resource tags"""
