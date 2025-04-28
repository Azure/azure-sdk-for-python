# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import Dict, Literal, Union
from typing_extensions import Required, TypedDict

from ..._bicep.expressions import Parameter


VERSION = "2024-05-01"


class ConfigStoreIdentity(TypedDict, total=False):
    type: Required[Union[Literal["None", "SystemAssigned", "SystemAssigned,UserAssigned", "UserAssigned"], Parameter]]
    """The type of managed identity used. The type 'SystemAssigned, UserAssigned' includes both an implicitly created identity and a set of user-assigned identities. The type 'None' will remove any identities."""
    userAssignedIdentities: Dict[Union[str, Parameter], Dict]
    """The list of user-assigned identities associated with the resource. The user-assigned identity dictionary keys will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'."""


class ConfigStoreSku(TypedDict, total=False):
    name: Union[Literal["Free", "Standard"], Parameter]
    """The SKU name of the configuration store."""


class ConfigStoreProperties(TypedDict, total=False):
    createMode: Union[Literal["Default", "Recover"], Parameter]
    """Indicates whether the configuration store need to be recovered."""
    dataPlaneProxy: Union["DataPlaneProxyProperties", Parameter]  # type: ignore[name-defined]  # TODO
    """Property specifying the configuration of data plane proxy for Azure Resource Manager (ARM)."""
    disableLocalAuth: Union[bool, Parameter]
    """Disables all authentication methods other than AAD authentication."""
    enablePurgeProtection: Union[bool, Parameter]
    """Property specifying whether protection against purge is enabled for this configuration store."""
    encryption: Union["EncryptionProperties", Parameter]  # type: ignore[name-defined]  # TODO
    """The encryption settings of the configuration store."""
    publicNetworkAccess: Union[Literal["Disabled", "Enabled"], Parameter]
    """Control permission for data plane traffic coming from public networks while private endpoint is enabled."""
    softDeleteRetentionInDays: Union[int, Parameter]
    """The amount of time in days that the configuration store will be retained when it is soft deleted."""


class ConfigStoreResource(TypedDict, total=False):
    identity: Union[ConfigStoreIdentity, Parameter]
    """The identity of the resource."""
    location: Union[str, Parameter]
    """The geo-location where the resource lives."""
    name: Union[str, Parameter]
    """The resource name."""
    sku: Union[ConfigStoreSku, Parameter]
    """The sku of the configuration store."""
    properties: "ConfigStoreProperties"
    """Properties of the configuration store."""
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Dictionary of tag names and values."""
