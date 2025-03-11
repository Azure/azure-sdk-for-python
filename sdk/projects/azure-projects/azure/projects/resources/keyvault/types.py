# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import Dict, Literal, List, Union
from typing_extensions import Required, TypedDict

from ..._bicep.expressions import Parameter


VERSION = "2024-12-01-preview"


class KeyVaultIpRule(TypedDict, total=False):
    value: Required[Union[str, Parameter]]
    """An IPv4 address range in CIDR notation, such as '124.56.78.91' (simple IP address) or '124.56.78.0/24'
    (all addresses that start with 124.56.78).
    """


class VirtualNetworkRule(TypedDict, total=False):
    id: Required[Union[str, Parameter]]
    """Full resource id of a vnet subnet, such as 
    '/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/subnet1'.
    """
    ignoreMissingVnetServiceEndpoint: Union[bool, Parameter]
    """Ignore missing vnet service endpoint or not."""


class KeyVaultNetworkRuleSet(TypedDict, total=False):
    bypass: Union[Parameter, Literal["AzureServices", "None"]]
    """Setting for trusted services."""
    defaultAction: Union[Parameter, Literal["Allow", "Deny"]]
    """The default action when no rule from ipRules and from virtualNetworkRules match. This is only used after the
    bypass property has been evaluated.
    """
    ipRules: Union[Parameter, List[Union[KeyVaultIpRule, Parameter]]]
    """The list of IP address rules."""
    virtualNetworkRules: Union[Parameter, List[Union[VirtualNetworkRule, Parameter]]]
    """The list of virtual network rules."""


# class VaultProperties(TypedDict, total=False):


class KeyVaultResource(TypedDict, total=False):
    location: Union[str, Parameter]
    """The geo-location where the resource lives."""
    name: Union[str, Parameter]
    """The resource name."""
    properties: "VaultProperties"  # type: ignore[name-defined]  # TODO
    """Properties of the KeyVault account."""
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Dictionary of tag names and values."""
