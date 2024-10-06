# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from enum import Enum
from typing import IO, ClassVar, List, Optional, Dict, Literal
from dataclasses import field

from .roles import RoleAssignment
from ._resource import (
    UniqueName,
    _serialize_resource,
    Resource,
    LocatedResource,
    dataclass_model,
    generate_symbol,
    _UNSET,
    _SKIP,
    GuidName,
    PrincipalId
)


class ServiceBusRoleAssignments(Enum):
    DATA_OWNER = "090c5cfd-751d-490a-894a-3ce6f1109419"
    DATA_RECEIVER = "4f6d3b9b-027b-4f4c-9142-0e5a2a2247e0"
    DATA_SENDER = "69a216fc-b8fb-44d8-bc22-1f3c2cd27a39"


@dataclass_model
class Identity:
    type: Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned','UserAssigned'] = field(metadata={'rest': 'type'})
    user_assigned_identities: Optional[Dict[str, str]] = field(default=_UNSET, metadata={'rest': 'userAssignedIdentities'})


@dataclass_model
class ServiceBusSku:
    capacity: Optional[int] = field(default=_UNSET, metadata={'rest': 'capacity'})
    name: Literal['Basic', 'Premium', 'Standard'] = field(metadata={'rest': 'name'})
    tier: Literal['Basic', 'Premium', 'Standard'] = field(metadata={'rest': 'tier'})


@dataclass_model
class UserAssignedIdentityProperties:
    user_assigned_identity: Optional[str] = field(default=_UNSET, metadata={'rest': 'userAssignedIdentity'})


@dataclass_model
class KeyVaultProperties:
    identity: Optional[UserAssignedIdentityProperties] = field(default=_UNSET, metadata={'rest': 'identity'})
    key_name: Optional[str] = field(default=_UNSET, metadata={'rest': 'keyName'})
    keyvault_uri: Optional[str] = field(default=_UNSET, metadata={'rest': 'keyVaultUri'})
    key_version: Optional[str] = field(default=_UNSET, metadata={'rest': 'keyVersion'})


@dataclass_model
class ServiceBusEncryption:
    key_source: Literal['Microsoft.KeyVault'] = field(default='Microsoft.KeyVault', metadata={'rest': 'keySource'})
    keyvault_properties: Optional[List[KeyVaultProperties]] = field(default=_UNSET, metadata={'rest': 'keyVaultProperties'})
    require_infrastructure_encryption: Optional[bool] = field(default=_UNSET, metadata={'rest': 'requireInfrastructureEncryption'})


@dataclass_model
class NamespaceReplicaLocation:
    cluster_arm_id: Optional[str] = field(default=_UNSET, metadata={'rest': 'clusterArmId'})
    location_name: Optional[str] = field(default=_UNSET, metadata={'rest': 'locationName'})
    roleType: Optional[Literal['Primary', 'Secondary']] = field(default=_UNSET, metadata={'rest': 'roleType'})


@dataclass_model
class GeoDataReplicationProperties:
    locations: Optional[List[NamespaceReplicaLocation]] = field(metadata={'rest': 'locations'})
    max_replication_lag_duration_in_seconds: Optional[int] = field(metadata={'rest': 'maxReplicationLagDurationInSeconds'})


@dataclass_model
class PrivateEndpoint:
    id: str = field(metadata={'rest': 'id'})


@dataclass_model
class PrivateEndpointConnectionProperties:
    private_endpoint: PrivateEndpoint = field(metadata={'rest': 'privateEndpoint'})
    # privateLinkServiceConnectionState	Details about the state of the connection.	ConnectionState
    # provisioningState	Provisioning state of the Private Endpoint Connection.	'Canceled','Creating','Deleting','Failed','Succeeded','Updating'


@dataclass_model
class PrivateEndpointConnection:
    properties: PrivateEndpointConnectionProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class AuthorizationRuleProperties:
    rights: List[Literal['Listen', 'Manage', 'Send']] = field(metadata={'rest': 'rights'})


@dataclass_model
class AuthorizationRule(Resource):
    _resource: ClassVar[Literal['Microsoft.ServiceBus/namespaces/AuthorizationRules']] = 'Microsoft.ServiceBus/namespaces/AuthorizationRules'
    _version: ClassVar[str] = '2021-11-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("sbar"), init=False, repr=False)
    name: str = field(default_factory=lambda: UniqueName(prefix="cm_sb_auth_rule-", length=50), metadata={'rest': 'name'})
    properties: AuthorizationRuleProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class ClientAffineProperties:
    client_id: Optional[str] = field(default=_UNSET, metadata={'rest': 'clientId'})
    is_durable: Optional[bool] = field(default=_UNSET, metadata={'rest': 'isDurable'})
    is_shared: Optional[bool] = field(default=_UNSET, metadata={'rest': 'isShared'})


@dataclass_model
class SubscriptionProperties:
    auto_delete_on_idle: Optional[str] = field(default=_UNSET, metadata={'rest': 'autoDeleteOnIdle'})
    client_affine_properties: Optional[ClientAffineProperties] = field(default=_UNSET, metadata={'rest': 'clientAffineProperties'})
    dead_lettering_on_filter_evaluation_exceptions: Optional[bool] = field(default=_UNSET, metadata={'rest': 'deadLetteringOnFilterEvaluationExceptions'})
    dead_lettering_on_message_expiration: Optional[bool] = field(default=_UNSET, metadata={'rest': 'deadLetteringOnMessageExpiration'})
    default_message_time_to_live: Optional[str] = field(default=_UNSET, metadata={'rest': 'defaultMessageTimeToLive'})
    duplicate_detection_history_time_window: Optional[str] = field(default=_UNSET, metadata={'rest': 'duplicateDetectionHistoryTimeWindow'})
    enable_batched_operations: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enableBatchedOperations'})
    forward_dead_lettered_messages_to: Optional[str] = field(default=_UNSET, metadata={'rest': 'forwardDeadLetteredMessagesTo'})
    forward_to: Optional[str] = field(default=_UNSET, metadata={'rest': 'forwardTo'})
    is_client_affine: Optional[bool] = field(default=_UNSET, metadata={'rest': 'isClientAffine'})
    lock_duration: Optional[str] = field(default=_UNSET, metadata={'rest': 'lockDuration'})
    max_delivery_count: Optional[int] = field(default=_UNSET, metadata={'rest': 'maxDeliveryCount'})
    requires_session: Optional[bool] = field(default=_UNSET, metadata={'rest': 'requiresSession'})
    status: Optional[Literal['Active', 'Creating', 'Deleting', 'Disabled', 'ReceiveDisabled', 'Renaming', 'Restoring', 'SendDisabled', 'Unknown']] = field(default=_UNSET, metadata={'rest': 'status'})


@dataclass_model
class TopicSubsciprtion(Resource):
    _resource: ClassVar[Literal['Microsoft.ServiceBus/namespaces/topics/subscriptions']] = 'Microsoft.ServiceBus/namespaces/topics/subscriptions'
    _version: ClassVar[str] = '2021-11-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("sbsub"), init=False, repr=False)
    name: str = field(default_factory=lambda: UniqueName(prefix="cm_sb_subscription-", length=50), metadata={'rest': 'name'})
    properties: SubscriptionProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class TopicProperties:
    auto_delete_on_idle: Optional[str] = field(default=_UNSET, metadata={'rest': 'autoDeleteOnIdle'})
    default_message_time_to_live: Optional[str] = field(default=_UNSET, metadata={'rest': 'defaultMessageTimeToLive'})
    duplicate_detection_history_time_window: Optional[str] = field(default=_UNSET, metadata={'rest': 'duplicateDetectionHistoryTimeWindow'})
    enable_batched_operations: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enableBatchedOperations'})
    enable_express: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enableExpress'})
    enable_partitioning: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enablePartitioning'})
    max_message_size_in_kilobytes: Optional[int] = field(default=_UNSET, metadata={'rest': 'maxMessageSizeInKilobytes'})
    max_size_in_megabytes: Optional[int] = field(default=_UNSET, metadata={'rest': 'maxSizeInMegabytes'})
    requires_duplicate_detection: Optional[bool] = field(default=_UNSET, metadata={'rest': 'requiresDuplicateDetection'})
    status: Optional[Literal['Active', 'Creating', 'Deleting', 'Disabled', 'ReceiveDisabled', 'Renaming', 'Restoring', 'SendDisabled', 'Unknown']] = field(default=_UNSET, metadata={'rest': 'status'})
    support_ordering: Optional[bool] = field(default=_UNSET, metadata={'rest': 'supportOrdering'})


@dataclass_model
class ServiceBusTopic(Resource):
    _resource: ClassVar[Literal['Microsoft.ServiceBus/namespaces/topics']] = 'Microsoft.ServiceBus/namespaces/topics'
    _version: ClassVar[str] = '2021-11-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("sbtp"), init=False, repr=False)
    name: str = field(default_factory=lambda: UniqueName(prefix="cm_sb_topic-", length=50), metadata={'rest': 'name'})
    properties: Optional[TopicProperties] = field(metadata={'rest': 'properties'})
    subscriptions: List[TopicSubsciprtion] = field(default_factory=list, metadata={'rest': _SKIP})

    def write(self, bicep: IO[str]) -> None:
        _serialize_resource(bicep, self)

        for sub in self.subscriptions:
            sub._parent = self
            sub.write(bicep)

@dataclass_model
class ServiceBusNamespaceProperties:
    alternate_name: Optional[str] = field(default=_UNSET, metadata={'rest': 'alternateName'})
    disable_local_auth: Optional[bool] = field(default=_UNSET, metadata={'rest': 'disableLocalAuth'})
    encryption: Optional[ServiceBusEncryption] = field(default=_UNSET, metadata={'rest': 'encryption'})
    geo_data_replication: Optional[GeoDataReplicationProperties] = field(default=_UNSET, metadata={'rest': 'geoDataReplication'})
    minimum_tls_version: Optional[Literal['1.1', '1.2']] = field(default=_UNSET, metadata={'rest': 'minimumTlsVersion'})
    premium_messaging_partitions: Optional[int] = field(default=_UNSET, metadata={'rest': 'premiumMessagingPartitions'})
    private_endpoint_connections: Optional[List[PrivateEndpointConnection]] = field(default=_UNSET, metadata={'rest': 'privateEndpointConnections'})
    public_network_access: Optional[Literal['Disabled', 'Enabled', 'SecuredByPerimeter']] = field(default=_UNSET, metadata={'rest': 'publicNetworkAccess'})
    zone_redundant: Optional[bool] = field(default=_UNSET, metadata={'rest': 'zoneRedundant'})


@dataclass_model
class ServiceBusNamespace(LocatedResource):
    sku: ServiceBusSku = field(metadata={'rest': 'sku'})
    identity: Optional[Identity] = field(default=_UNSET, metadata={'rest': 'identity'})
    properties: Optional[ServiceBusNamespaceProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    topics: List[ServiceBusTopic] = field(default_factory=list, metadata={'rest': _SKIP})
    auth_rules: List[AuthorizationRule] = field(default_factory=list, metadata={'rest': _SKIP})
    roles: List[RoleAssignment] = field(default_factory=list, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.ServiceBus/namespaces']] = 'Microsoft.ServiceBus/namespaces'
    _version: ClassVar[str] = '2017-04-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("sbns"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> None:
        _serialize_resource(bicep, self)

        for rule in self.auth_rules:
            rule._parent = self
            rule.write(bicep)
        for role in self.roles:
            role.name = GuidName(self, PrincipalId(), role.properties.role_definition_id)
            role._scope = self
            role.write(bicep)
        for topic in self.topics:
            topic._parent = self
            topic.write(bicep)

        if self._fname:
            output_prefix = self._fname.title()
        else:
            output_prefix = ""
        output_prefix = "ServiceBus" + output_prefix
        self._outputs.append(output_prefix + 'Id')
        bicep.write(f"output {output_prefix}Id string = {self._symbolicname}.id\n")
        self._outputs.append(output_prefix + 'Name')
        bicep.write(f"output {output_prefix}Name string = {self._symbolicname}.name\n")
        self._outputs.append(output_prefix + 'Endpoint')
        bicep.write(f"output {output_prefix}Endpoint string = {self._symbolicname}.properties.serviceBusEndpoint\n\n")
