# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=line-too-long

from enum import Enum
from functools import partial
from typing import IO, ClassVar, List, Optional, Dict, Literal, TypedDict
from dataclasses import field, dataclass

from ._roles import RoleAssignment
from ._resource import (
    Output,
    UniqueName,
    _serialize_resource,
    Resource,
    LocatedResource,
    generate_symbol,
    _UNSET,
    _SKIP,
    GuidName,
    PrincipalId,
    resolve_value,
    BicepBool,
    BicepInt,
    BicepStr
)


class ServiceBusRoleAssignments(Enum):
    DATA_OWNER = "090c5cfd-751d-490a-894a-3ce6f1109419"
    DATA_RECEIVER = "4f6d3b9b-027b-4f4c-9142-0e5a2a2247e0"
    DATA_SENDER = "69a216fc-b8fb-44d8-bc22-1f3c2cd27a39"


class Identity(TypedDict, total=False):
    # Required
    type: Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned','UserAssigned']
    userAssignedIdentities: Dict[BicepStr, BicepStr]


class ServiceBusSku(TypedDict, total=False):
    capacity: BicepInt
    # Required
    name: Literal['Basic', 'Premium', 'Standard']
    # Required
    tier: Literal['Basic', 'Premium', 'Standard']


class UserAssignedIdentityProperties(TypedDict, total=False):
    userAssignedIdentity: BicepStr


class KeyVaultProperties(TypedDict, total=False):
    identity: UserAssignedIdentityProperties
    keyName: BicepStr
    keyVaultUri: BicepStr
    keyVersion: BicepStr


class ServiceBusEncryption(TypedDict, total=False):
    # Required
    keySource: Literal['Microsoft.KeyVault']
    keyVaultProperties: List[KeyVaultProperties]
    requireInfrastructureEncryption: BicepBool


class NamespaceReplicaLocation(TypedDict, total=False):
    clusterArmId: BicepStr
    locationName: BicepStr
    roleType: Literal['Primary', 'Secondary']


class GeoDataReplicationProperties(TypedDict, total=False):
    locations: List[NamespaceReplicaLocation]
    maxReplicationLagDurationInSeconds: BicepInt


class PrivateEndpoint(TypedDict):
    # Required
    id: BicepStr


class PrivateEndpointConnectionProperties(TypedDict):
    # Required
    privateEndpoint: PrivateEndpoint
    # privateLinkServiceConnectionState	Details about the state of the connection.	ConnectionState
    # provisioningState	Provisioning state of the Private Endpoint Connection.	'Canceled','Creating','Deleting','Failed','Succeeded','Updating'


class PrivateEndpointConnection(TypedDict):
    # Required
    properties: PrivateEndpointConnectionProperties


class AuthorizationRuleProperties(TypedDict):
    # Required
    rights: List[Literal['Listen', 'Manage', 'Send']]


@dataclass(kw_only=True)
class AuthorizationRule(Resource):
    _resource: ClassVar[Literal['Microsoft.ServiceBus/namespaces/AuthorizationRules']] = 'Microsoft.ServiceBus/namespaces/AuthorizationRules'
    _version: ClassVar[str] = '2021-11-01'
    _symbolicname: str = field(default_factory=partial(generate_symbol, "sbar"), init=False, repr=False)
    name: BicepStr = field(default_factory=partial(UniqueName, prefix="cm_sb_auth_rule_", length=50), metadata={'rest': 'name'})
    properties: AuthorizationRuleProperties = field(metadata={'rest': 'properties'})


class ClientAffineProperties(TypedDict, total=False):
    clientId: BicepStr
    isDurable: BicepBool
    isShared: BicepBool


class SubscriptionProperties(TypedDict, total=False):
    autoDeleteOnIdle: BicepStr
    clientAffineProperties: ClientAffineProperties
    deadLetteringOnFilterEvaluationExceptions: BicepBool
    deadLetteringOnMessageExpiration: BicepBool
    defaultMessageTimeToLive: BicepStr
    duplicateDetectionHistoryTimeWindow: BicepStr
    enableBatchedOperations: BicepBool
    forwardDeadLetteredMessagesTo: BicepStr
    forwardTo: BicepStr
    isClientAffine: BicepBool
    lockDuration: BicepStr
    maxDeliveryCount: BicepInt
    requiresSession: BicepBool
    status: Literal['Active', 'Creating', 'Deleting', 'Disabled', 'ReceiveDisabled', 'Renaming', 'Restoring', 'SendDisabled', 'Unknown']


@dataclass(kw_only=True)
class TopicSubsciprtion(Resource):
    _resource: ClassVar[Literal['Microsoft.ServiceBus/namespaces/topics/subscriptions']] = 'Microsoft.ServiceBus/namespaces/topics/subscriptions'
    _version: ClassVar[str] = '2021-11-01'
    _symbolicname: str = field(default_factory=partial(generate_symbol, "sbsub"), init=False, repr=False)
    name: BicepStr = field(default_factory=partial(UniqueName, prefix="cm_sb_subscription_", length=50), metadata={'rest': 'name'})
    properties: SubscriptionProperties = field(metadata={'rest': 'properties'})


class TopicProperties(TypedDict, total=False):
    autoDeleteOnIdle: BicepStr
    defaultMessageTimeToLive: BicepStr
    duplicateDetectionHistoryTimeWindow: BicepStr
    enableBatchedOperations: BicepBool
    enableExpress: BicepBool
    enablePartitioning: BicepBool
    maxMessageSizeInKilobytes: BicepInt
    maxSizeInMegabytes: BicepInt
    requiresDuplicateDetection: BicepBool
    status: Literal['Active', 'Creating', 'Deleting', 'Disabled', 'ReceiveDisabled', 'Renaming', 'Restoring', 'SendDisabled', 'Unknown']
    supportOrdering: BicepBool


@dataclass(kw_only=True)
class ServiceBusTopic(Resource):
    _resource: ClassVar[Literal['Microsoft.ServiceBus/namespaces/topics']] = 'Microsoft.ServiceBus/namespaces/topics'
    _version: ClassVar[str] = '2021-11-01'
    _symbolicname: str = field(default_factory=partial(generate_symbol, "sbtp"), init=False, repr=False)
    name: BicepStr = field(default_factory=partial(UniqueName, prefix="cm_sb_topic_", length=50), metadata={'rest': 'name'})
    properties: Optional[TopicProperties] = field(metadata={'rest': 'properties'})
    subscriptions: List[TopicSubsciprtion] = field(default_factory=list, metadata={'rest': _SKIP})

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        _serialize_resource(bicep, self)
        for sub in self.subscriptions:
            sub.parent = self
            self._outputs.update(sub.write(bicep))
        return self._outputs


class ServiceBusNamespaceProperties(TypedDict, total=False):
    alternateName: BicepStr
    disableLocalAuth: BicepBool
    encryption: ServiceBusEncryption
    geoDataReplication: GeoDataReplicationProperties
    minimumTlsVersion: Literal['1.1', '1.2']
    premiumMessagingPartitions: BicepInt
    privateEndpointConnections: List[PrivateEndpointConnection]
    publicNetworkAccess: Literal['Disabled', 'Enabled', 'SecuredByPerimeter']
    zoneRedundant: BicepBool


@dataclass(kw_only=True)
class ServiceBusNamespace(LocatedResource):
    sku: ServiceBusSku = field(metadata={'rest': 'sku'})
    identity: Optional[Identity] = field(default=_UNSET, metadata={'rest': 'identity'})
    properties: Optional[ServiceBusNamespaceProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    topics: List[ServiceBusTopic] = field(default_factory=list, metadata={'rest': _SKIP})
    auth_rules: List[AuthorizationRule] = field(default_factory=list, metadata={'rest': _SKIP})
    roles: List[RoleAssignment] = field(default_factory=list, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.ServiceBus/namespaces']] = 'Microsoft.ServiceBus/namespaces'
    _version: ClassVar[str] = '2017-04-01'
    _symbolicname: str = field(default_factory=partial(generate_symbol, "sbns"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        _serialize_resource(bicep, self)

        for rule in self.auth_rules:
            rule.parent = self
            self._outputs.update(rule.write(bicep))
        for role in self.roles:
            role.name = GuidName(self, PrincipalId(), role.properties['roleDefinitionId'])
            role.scope = self
            self._outputs.update(role.write(bicep))
        for topic in self.topics:
            topic.parent = self
            self._outputs.update(topic.write(bicep))

        if self._fname:
            output_prefix = self._fname.title()
        else:
            output_prefix = ""
        output_prefix = "ServiceBus" + output_prefix
        self._outputs[output_prefix + "Id"] = Output(f"{self._symbolicname}.id")
        self._outputs[output_prefix + "Name"] = Output(f"{self._symbolicname}.name")
        self._outputs[output_prefix + "Endpoint"] = Output(f"{self._symbolicname}.properties.serviceBusEndpoint")
        for key, value in self._outputs.items():
            bicep.write(f"output {key} string = {resolve_value(value)}\n")
        bicep.write("\n")
        return self._outputs
