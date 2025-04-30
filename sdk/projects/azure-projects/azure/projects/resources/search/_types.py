# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long, name-too-long

from __future__ import annotations
from typing import TypedDict, Literal, Union, Any

from ..._bicep.expressions import Parameter
from .._extension import Identity


VERSION = "2024-06-01-Preview"


class SearchServiceDataPlaneAadOrApiKeyAuthOption(TypedDict, total=False):
    aadAuthFailureMode: Union[Literal["http403", "http401WithBearerChallenge"], Parameter]
    """Describes what response the data plane API of a search service would send for requests that failed authentication."""


class SearchServiceDataPlaneAuthOptions(TypedDict, total=False):
    aadOrApiKey: Union[SearchServiceDataPlaneAadOrApiKeyAuthOption, Parameter]
    """Indicates that either the API key or an access token from a Microsoft Entra ID tenant can be used for authentication."""
    apiKeyOnly: Union[Any, Parameter]
    """Indicates that only the API key can be used for authentication."""


class SearchServiceEncryptionWithCmk(TypedDict, total=False):
    enforcement: Union[Literal["Disabled", "Unspecified", "Enabled"], Parameter]
    """Describes how a search service should enforce compliance if it finds objects that aren't encrypted with the customer-managed key."""


class SearchServiceIpRule(TypedDict, total=False):
    value: Union[str, Parameter]
    """Value corresponding to a single IPv4 address (eg., 123.1.2.3) or an IP range in CIDR format (eg., 123.1.2.3/24) to be allowed."""


class SearchServiceResource(TypedDict, total=False):
    identity: Union[Identity, Parameter]
    """The identity of the resource."""
    location: Union[str, Parameter]
    """The geo-location where the resource lives"""
    name: Union[str, Parameter]
    """The resource name"""
    properties: SearchServiceProperties
    """Properties of the search service."""
    sku: Union[SearchServiceSku, Parameter]
    """The SKU of the search service, which determines price tier and capacity limits. This property is required when creating a new search service."""
    tags: Union[dict[str, Union[str, Parameter]], Parameter]
    """Resource tags"""


class SearchServiceNetworkRuleSet(TypedDict, total=False):
    bypass: Union[Literal["AzurePortal", "None", "AzureServices"], Parameter]
    """Possible origins of inbound traffic that can bypass the rules defined in the 'ipRules' section."""
    ipRules: Union[list[SearchServiceIpRule], Parameter]
    """A list of IP restriction rules that defines the inbound network(s) with allowing access to the search service endpoint. At the meantime, all other public IP networks are blocked by the firewall. These restriction rules are applied only when the 'publicNetworkAccess' of the search service is 'enabled'; otherwise, traffic over public interface is not allowed even with any public IP rules, and private endpoint connections would be the exclusive access method."""


class SearchServiceProperties(TypedDict, total=False):
    authOptions: Union[SearchServiceDataPlaneAuthOptions, Parameter]
    """Defines the options for how the data plane API of a search service authenticates requests. This cannot be set if 'disableLocalAuth' is set to true."""
    computeType: Union[Literal["confidential", "default"], Parameter]
    """Configure this property to support the search service using either the default compute or Azure Confidential Compute."""
    disabledDataExfiltrationOptions: Union[Literal["All"], Parameter]
    """A list of data exfiltration scenarios that are explicitly disallowed for the search service. Currently, the only supported value is 'All' to disable all possible data export scenarios with more fine grained controls planned for the future."""
    disableLocalAuth: Union[bool, Parameter]
    """When set to true, calls to the search service will not be permitted to utilize API keys for authentication. This cannot be set to true if 'dataPlaneAuthOptions' are defined."""
    encryptionWithCmk: Union[SearchServiceEncryptionWithCmk, Parameter]
    """Specifies any policy regarding encryption of resources (such as indexes) using customer manager keys within a search service."""
    endpoint: Union[str, Parameter]
    """The endpoint of the Azure AI Search service."""
    hostingMode: Union[Literal["default", "highDensity"], Parameter]
    """Applicable only for the standard3 SKU. You can set this property to enable up to 3 high density partitions that allow up to 1000 indexes, which is much higher than the maximum indexes allowed for any other SKU. For the standard3 SKU, the value is either 'default' or 'highDensity'. For all other SKUs, this value must be 'default'."""
    networkRuleSet: Union[SearchServiceNetworkRuleSet, Parameter]
    """Network specific rules that determine how the Azure AI Search service may be reached."""
    partitionCount: Union[int, Parameter]
    """The number of partitions in the search service; if specified, it can be 1, 2, 3, 4, 6, or 12. Values greater than 1 are only valid for standard SKUs. For 'standard3' services with hostingMode set to 'highDensity', the allowed values are between 1 and 3."""
    publicNetworkAccess: Union[Literal["disabled", "enabled"], Parameter]
    """This value can be set to 'enabled' to avoid breaking changes on existing customer resources and templates. If set to 'disabled', traffic over public interface is not allowed, and private endpoint connections would be the exclusive access method."""
    replicaCount: Union[int, Parameter]
    """The number of replicas in the search service. If specified, it must be a value between 1 and 12 inclusive for standard SKUs or between 1 and 3 inclusive for basic SKU."""
    semanticSearch: Union[Literal["free", "disabled", "standard"], Parameter]
    """Sets options that control the availability of semantic search. This configuration is only possible for certain Azure AI Search SKUs in certain locations."""


class SearchServiceSku(TypedDict, total=False):
    name: Union[
        Literal["storage_optimized_l1", "free", "storage_optimized_l2", "basic", "standard3", "standard", "standard2"],
        Parameter,
    ]
    """The SKU of the search service. Valid values include: 'free': Shared service. 'basic': Dedicated service with up to 3 replicas. 'standard': Dedicated service with up to 12 partitions and 12 replicas. 'standard2': Similar to standard, but with more capacity per search unit. 'standard3': The largest Standard offering with up to 12 partitions and 12 replicas (or up to 3 partitions with more indexes if you also set the hostingMode property to 'highDensity'). 'storage_optimized_l1': Supports 1TB per partition, up to 12 partitions. 'storage_optimized_l2': Supports 2TB per partition, up to 12 partitions.'"""
