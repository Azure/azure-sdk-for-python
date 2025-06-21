# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TypedDict, Union

from ..._bicep.expressions import Parameter


VERSION = "2023-07-31-preview"


class UserAssignedIdentityResource(TypedDict, total=False):
    location: Union[str, Parameter]
    """The geo-location where the resource lives"""
    name: Union[str, Parameter]
    """The resource name"""
    tags: dict[str, Union[None, str, Parameter]]
    """Resource tags"""
