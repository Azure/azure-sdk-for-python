# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Dict, TypedDict, Literal, List, Union
from typing_extensions import Required

from ..._bicep.expressions import Parameter


RESOURCE = "Microsoft.KeyVault/vaults"
VERSION = "2024-12-01-preview"


class KeyVaultIpRule(TypedDict, total=False):
    value: Required[Union[str, Parameter[str]]]
    """An IPv4 address range in CIDR notation, such as '124.56.78.91' (simple IP address) or '124.56.78.0/24' (all addresses that start with 124.56.78)."""


class VirtualNetworkRule(TypedDict, total=False):
    id: Required[Union[str, Parameter[str]]]
    """Full resource id of a vnet subnet, such as '/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/subnet1'."""
    ignoreMissingVnetServiceEndpoint: Union[bool, Parameter[bool]]
    """Ignore missing vnet service endpoint or not."""


class KeyVaultNetworkRuleSet(TypedDict, total=False):
    bypass: Union[Parameter[str], Literal['AzureServices', 'None']]
    """Setting for trusted services."""
    defaultAction: Union[Parameter[str], Literal['Allow', 'Deny']]
    """The default action when no rule from ipRules and from virtualNetworkRules match. This is only used after the bypass property has been evaluated."""
    ipRules: Union[Parameter[List[KeyVaultIpRule]], List[Union[KeyVaultIpRule, Parameter[KeyVaultIpRule]]]]
    """The list of IP address rules."""
    virtualNetworkRules: Union[Parameter[List[VirtualNetworkRule]], List[Union[VirtualNetworkRule, Parameter[VirtualNetworkRule]]]]
    """The list of virtual network rules."""

#class VaultProperties(TypedDict, total=False):

class KeyVaultResource(TypedDict, total=False):
    location: Union[str, Parameter[str]]
    """The geo-location where the resource lives."""
    name: Union[str, Parameter[str]]
    """The resource name."""
    properties:	'VaultProperties'
    """Properties of Cognitive Services account."""
    tags: Union[Dict[str, Union[str, Parameter[str]]], Parameter[Dict[str, str]]]
    """Dictionary of tag names and values."""
