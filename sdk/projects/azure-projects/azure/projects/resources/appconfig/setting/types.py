# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import Dict, Union
from typing_extensions import TypedDict

from ...._bicep.expressions import Parameter, ResourceSymbol


VERSION = "2024-05-01"


class ConfigSettingProperties(TypedDict, total=False):
    contentType: Union[str, Parameter]
    """The content type of the key-value's value. Providing a proper content-type can enable
    transformations of values when they are retrieved by applications.
    """
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """A dictionary of tags that can help identify what a key-value may be applicable for."""
    value: Union[str, Parameter]
    """The value of the key-value."""


class ConfigSettingResource(TypedDict, total=False):
    name: Union[str, Parameter]
    """The resource name."""
    properties: ConfigSettingProperties
    """The properties of a container."""
    parent: ResourceSymbol
    """The parent config store."""
