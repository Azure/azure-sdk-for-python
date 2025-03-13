# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Dict, Union
from typing_extensions import TypedDict

from ..._bicep.expressions import Parameter


VERSION = "2023-07-31-preview"


class UserAssignedIdentityResource(TypedDict, total=False):
    name: Union[str, Parameter]
    """The name of the User Assigned Identity."""
    location: Union[str, Parameter]
    """Location of the identity. It uses the deployment's location when not provided."""
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Tags of the resource."""
