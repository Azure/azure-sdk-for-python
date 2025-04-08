# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import Dict, Any, Union
from typing_extensions import TypedDict

from ....._bicep.expressions import ResourceSymbol, Expression


VERSION = "2024-04-01"


class SiteConfigResource(TypedDict, total=False):
    name: Union[str, Expression]
    """The resource name."""
    properties: Dict[str, Any]
    """Properties of Connection."""
    parent: ResourceSymbol
    """Parent of the Connection."""
