# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from __future__ import annotations
from typing import TypedDict, Union, Any

from ...._bicep.expressions import Parameter


VERSION = '2024-05-01'


class ConfigSettingKeyValueProperties(TypedDict, total=False):
    contentType: Union[str, Parameter]
    """The content type of the key-value's value.Providing a proper content-type can enable transformations of values when they are retrieved by applications."""
    tags: Union[ConfigSettingKeyValueProperties, Parameter]
    """A dictionary of tags that can help identify what a key-value may be applicable for."""
    value: Union[str, Parameter]
    """The value of the key-value."""


class ConfigSettingResource(TypedDict, total=False):
    name: Union[str, Parameter]
    """The resource name"""
    properties: Union[ConfigSettingKeyValueProperties, Parameter]
    """All key-value properties."""
    parent: Any
    """The Symbolic name of the resource that is the parent for this resource."""
