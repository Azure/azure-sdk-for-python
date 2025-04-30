# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long, name-too-long

from __future__ import annotations
from typing import TypedDict, Literal, Union

from ..._bicep.expressions import Parameter
from .._extension import Identity


VERSION = "2024-05-01"


class ConfigurationStoreProperties(TypedDict, total=False):
    createMode: Union[Literal["Recover", "Default"], Parameter]
    """Indicates whether the configuration store need to be recovered."""
    dataPlaneProxy: Union[ConfigurationStoreDataPlaneProxyProperties, Parameter]
    """Property specifying the configuration of data plane proxy for Azure Resource Manager (ARM)."""
    disableLocalAuth: Union[bool, Parameter]
    """Disables all authentication methods other than AAD authentication."""
    enablePurgeProtection: Union[bool, Parameter]
    """Property specifying whether protection against purge is enabled for this configuration store."""
    encryption: Union[ConfigurationStoreEncryptionProperties, Parameter]
    """The encryption settings of the configuration store."""
    publicNetworkAccess: Union[Literal["Disabled", "Enabled"], Parameter]
    """Control permission for data plane traffic coming from public networks while private endpoint is enabled."""
    softDeleteRetentionInDays: Union[int, Parameter]
    """The amount of time in days that the configuration store will be retained when it is soft deleted."""


class ConfigurationStoreDataPlaneProxyProperties(TypedDict, total=False):
    authenticationMode: Union[Literal["Pass-through", "Local"], Parameter]
    """The data plane proxy authentication mode. This property manages the authentication mode of request to the data plane resources."""
    privateLinkDelegation: Union[Literal["Disabled", "Enabled"], Parameter]
    """The data plane proxy private link delegation. This property manages if a request from delegated Azure Resource Manager (ARM) private link is allowed when the data plane resource requires private link."""


class ConfigurationStoreEncryptionProperties(TypedDict, total=False):
    keyVaultProperties: Union[ConfigurationStoreKeyVaultProperties, Parameter]
    """Key vault properties."""


class ConfigurationStoreKeyVaultProperties(TypedDict, total=False):
    identityClientId: Union[str, Parameter]
    """The client id of the identity which will be used to access key vault."""
    keyIdentifier: Union[str, Parameter]
    """The URI of the key vault key used to encrypt data."""


class ConfigurationStoreResource(TypedDict, total=False):
    identity: Union[Identity, Parameter]
    """The managed identity information, if configured."""
    location: Union[str, Parameter]
    """The geo-location where the resource lives"""
    name: Union[str, Parameter]
    """The resource name"""
    properties: ConfigurationStoreProperties
    """The properties of a configuration store."""
    sku: Union[ConfigurationStoreSku, Parameter]
    """The sku of the configuration store."""
    tags: Union[dict[str, Union[str, Parameter]], Parameter]
    """Resource tags"""


class ConfigurationStoreSku(TypedDict, total=False):
    name: Union[str, Parameter]
    """The SKU name of the configuration store."""
