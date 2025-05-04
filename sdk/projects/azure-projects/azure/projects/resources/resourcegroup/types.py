# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Dict, Union
from typing_extensions import TypedDict

from ..._bicep.expressions import Parameter


VERSION = "2021-04-01"


class ResourceGroupResource(TypedDict, total=False):
    name: Union[str, Parameter]
    """The name of the Resource Group."""
    location: Union[str, Parameter]
    """Location of the Resource Group. It uses the deployment's location when not provided."""
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Tags of the Resource Group."""
