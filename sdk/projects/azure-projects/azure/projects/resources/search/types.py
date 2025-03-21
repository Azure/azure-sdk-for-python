# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import Dict, Literal, List, Union
from typing_extensions import Required, TypedDict

from ..._bicep.expressions import Parameter


VERSION = "2024-06-01-Preview"


class SearchIpRule(TypedDict, total=False):
    value: Required[Union[str, Parameter]]
    """Value corresponding to a single IPv4 address (eg., 123.1.2.3) or an IP range in CIDR format
    (eg., 123.1.2.3/24) to be allowed.
    """


class SearchNetworkRuleSet(TypedDict, total=False):
    bypass: Union[Parameter, Literal["AzurePortal", "AzureServices", "None"]]
    """Possible origins of inbound traffic that can bypass the rules defined in the 'ipRules' section."""
    ipRules: Union[Parameter, List[Union[SearchIpRule, Parameter]]]
    """A list of IP restriction rules that defines the inbound network(s) with allowing access to the search service
    endpoint. At the meantime, all other public IP networks are blocked by the firewall. These restriction rules
    are applied only when the 'publicNetworkAccess' of the search service is 'enabled'; otherwise, traffic over
    public interface is not allowed even with any public IP rules, and private endpoint connections would be the
    exclusive access method.
    """


class SearchIdentity(TypedDict, total=False):
    type: Required[Union[Literal["None", "SystemAssigned", "SystemAssigned,UserAssigned", "UserAssigned"], Parameter]]
    """The identity type."""
    userAssignedIdentities: Dict[Union[str, Parameter], Dict]
    """The set of user assigned identities associated with the resource."""


class SearchSku(TypedDict, total=False):
    name: Union[
        Literal["basic", "free", "standard", "standard2", "standard3", "storage_optimized_l1", "storage_optimized_l2"],
        Parameter,
    ]
    """The SKU of the search service. Valid values include: 'free': Shared service. 'basic': Dedicated service with
    up to 3 replicas. 'standard': Dedicated service with up to 12 partitions and 12 replicas. 'standard2': Similar
    to standard, but with more capacity per search unit. 'standard3': The largest Standard offering with up to 12
    partitions and 12 replicas (or up to 3 partitions with more indexes if you also set the hostingMode property to
    'highDensity'). 'storage_optimized_l1': Supports 1TB per partition, up to 12 partitions.
    'storage_optimized_l2': Supports 2TB per partition, up to 12 partitions.
    """


class SearchServiceResource(TypedDict, total=False):
    # TODO: Test different identity configurations - if this is a parameter, how does the merge work?
    identity: Union[SearchIdentity, Parameter]
    """The identity of the resource."""
    location: Union[str, Parameter]
    """The geo-location where the resource lives."""
    name: Union[str, Parameter]
    """The resource name."""
    properties: "SearchServiceProperties"  # type: ignore[name-defined]  # TODO
    """Properties of Cognitive Services account."""
    sku: Union[SearchSku, Parameter]
    """The SKU of the search service, which determines price tier and capacity limits. This property is required when
    creating a new search service.
    """
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Dictionary of tag names and values."""
