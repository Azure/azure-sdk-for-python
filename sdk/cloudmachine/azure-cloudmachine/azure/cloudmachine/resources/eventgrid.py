# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import IO, ClassVar, List, Optional, Literal, Union
from dataclasses import field

from .identity import UserAssignedIdentities
from ._resource import (
    Resource,
    LocatedResource,
    UniqueName,
    ResourceId,
    dataclass_model,
    generate_symbol,
    _serialize_resource,
    _UNSET,
    _SKIP,
)

@dataclass_model
class EventSubscriptionIdentity:
    type: Literal['SystemAssigned', 'UserAssigned'] = field(metadata={'rest': 'type'})
    user_assigned_identity: Optional[Union[str, ResourceId]] = field(default=_UNSET, metadata={'rest': 'userAssignedIdentity'})


@dataclass_model
class StorageBlobDeadLetterDestinationProperties:
    blob_container_name: str = field(metadata={'rest': 'blobContainerName'})
    resource_id: Union[str, ResourceId] = field(metadata={'rest': 'resourceId'})


@dataclass_model
class StorageBlobDeadLetterDestination:
    endpoint_type: Literal['StorageBlob'] = field(default='StorageBlob', init=False, metadata={'rest': 'endpointType'})
    properties: StorageBlobDeadLetterDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class DeadLetterWithResourceIdentity:
    dead_letter_destination: StorageBlobDeadLetterDestination = field(metadata={'rest': 'deadLetterDestination'})
    identity: EventSubscriptionIdentity = field(metadata={'rest': 'identity'})


@dataclass_model
class DynamicDeliveryAttributeMappingProperties:
    source_field: str = field(metadata={'rest': 'sourceField'})


@dataclass_model
class DynamicDeliveryAttributeMapping:
    type: Literal['Dynamic'] = field(default='Dynamic', init=False, metadata={'rest': 'type'})
    properties: DynamicDeliveryAttributeMappingProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class StaticDeliveryAttributeMappingProperties:
    is_secret: bool = field(metadata={'rest': 'isSecret'})
    value: str = field(metadata={'rest': 'value'})


@dataclass_model
class StaticDeliveryAttributeMapping:
    type: Literal['Static'] = field(default='Static', init=False, metadata={'rest': 'type'})
    properties: StaticDeliveryAttributeMappingProperties = field(metadata={'rest': 'properties'})


AttributeMapping = Union[
    DynamicDeliveryAttributeMapping,
    StaticDeliveryAttributeMapping
]

@dataclass_model
class AzureFunctionEventSubscriptionDestinationProperties:
    delivery_attribute_mappings: Optional[List[AttributeMapping]] = field(default=_UNSET, metadata={'rest': 'deliveryAttributeMappings'})
    max_events_per_batch: Optional[int] = field(default=_UNSET, metadata={'rest': 'maxEventsPerBatch'})
    preferred_batch_size_in_kilobytes: Optional[int] = field(default=_UNSET, metadata={'rest': 'preferredBatchSizeInKilobytes'})
    resource_id: Union[str, ResourceId] = field(metadata={'rest': 'resourceId'})


@dataclass_model
class AzureFunctionEventSubscriptionDestination:
    endpoint_type: Literal['AzureFunction'] = field(default='AzureFunction', init=False, metadata={'rest': 'endpointType'})
    properties: AzureFunctionEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class EventHubEventSubscriptionDestinationProperties:
    delivery_attribute_mappings: Optional[List[AttributeMapping]] = field(default=_UNSET, metadata={'rest': 'deliveryAttributeMappings'})
    resource_id: Union[str, ResourceId] = field(metadata={'rest': 'resourceId'})


@dataclass_model
class EventHubEventSubscriptionDestination:
    endpoint_type: Literal['EventHub'] = field(default='EventHub', init=False, metadata={'rest': 'endpointType'})
    properties: EventHubEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class HybridConnectionEventSubscriptionDestinationProperties:
    delivery_attribute_mappings: Optional[List[AttributeMapping]] = field(default=_UNSET, metadata={'rest': 'deliveryAttributeMappings'})
    resource_id: Union[str, ResourceId] = field(metadata={'rest': 'resourceId'})


@dataclass_model
class HybridConnectionEventSubscriptionDestination:
    endpoint_type: Literal['HybridConnection'] = field(default='HybridConnection', init=False, metadata={'rest': 'endpointType'})
    properties: HybridConnectionEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class MonitorAlertEventSubscriptionDestinationProperties:
    action_groups: Optional[List[Union[str, ResourceId]]] = field(default=_UNSET, metadata={'rest': 'actionGroups'})
    description: Optional[str] = field(default=_UNSET, metadata={'rest': 'description'})
    severity: Literal['Sev0', 'Sev1', 'Sev2', 'Sev3', 'Sev4'] = field(metadata={'rest': 'severity'})


@dataclass_model
class MonitorAlertEventSubscriptionDestination:
    endpoint_type: Literal['MonitorAlert'] = field(default='MonitorAlert', init=False, metadata={'rest': 'endpointType'})
    properties: MonitorAlertEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class NamespaceTopicEventSubscriptionDestinationProperties:
    resource_id: Union[str, ResourceId] = field(metadata={'rest': 'resourceId'})


@dataclass_model
class NamespaceTopicEventSubscriptionDestination:
    endpoint_type: Literal['NamespaceTopic'] = field(default='NamespaceTopic', init=False, metadata={'rest': 'endpointType'})
    properties: NamespaceTopicEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class PartnerEventSubscriptionDestinationProperties:
    resource_id: Union[str, ResourceId] = field(metadata={'rest': 'resourceId'})


@dataclass_model
class PartnerEventSubscriptionDestination:
    endpoint_type: Literal['PartnerDestination'] = field(default='PartnerDestination', init=False, metadata={'rest': 'endpointType'})
    properties: PartnerEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class ServiceBusQueueEventSubscriptionDestinationProperties:
    delivery_attribute_mappings: Optional[List[AttributeMapping]] = field(default=_UNSET, metadata={'rest': 'deliveryAttributeMappings'})
    resource_id: Union[str, ResourceId] = field(metadata={'rest': 'resourceId'})


@dataclass_model
class ServiceBusQueueEventSubscriptionDestination:
    endpoint_type: Literal['ServiceBusQueue'] = field(default='ServiceBusQueue', init=False, metadata={'rest': 'endpointType'})
    properties: ServiceBusQueueEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class ServiceBusTopicEventSubscriptionDestinationProperties:
    delivery_attribute_mappings: Optional[List[AttributeMapping]] = field(default=_UNSET, metadata={'rest': 'deliveryAttributeMappings'})
    resource_id: Union[str, ResourceId] = field(metadata={'rest': 'resourceId'})


@dataclass_model
class ServiceBusTopicEventSubscriptionDestination:
    endpoint_type: Literal['ServiceBusTopic'] = field(default='ServiceBusTopic', init=False, metadata={'rest': 'endpointType'})
    properties: ServiceBusTopicEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class StorageQueueEventSubscriptionDestinationProperties:
    resource_id: Union[str, ResourceId] = field(metadata={'rest': 'resourceId'})
    queue_name: str = field(metadata={'rest': 'queueName'})
    queue_message_time_to_live_in_seconds: Optional[int] = field(default=_UNSET, metadata={'rest': 'queueMessageTimeToLiveInSeconds'})


@dataclass_model
class StorageQueueEventSubscriptionDestination:
    endpoint_type: Literal['StorageQueue'] = field(default='StorageQueue', init=False, metadata={'rest': 'endpointType'})
    properties: StorageQueueEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class WebHookEventSubscriptionDestinationProperties:
    azure_active_directory_application_id_or_uri: Optional[str] = field(metadata={'rest': 'azureActiveDirectoryApplicationIdOrUri'})
    azure_active_directory_tenant_id: Optional[str] = field(default=_UNSET, metadata={'rest': 'azureActiveDirectoryTenantId'})
    delivery_attribute_mappings: Optional[List[AttributeMapping]] = field(default=_UNSET, metadata={'rest': 'deliveryAttributeMappings'})
    endpoint_url: Optional[str] = field(default=_UNSET, metadata={'rest': 'endpointUrl'})
    max_events_per_batch: Optional[int] = field(default=_UNSET, metadata={'rest': 'maxEventsPerBatch'})
    minimum_tls_version_allowed: Optional[Literal['1.0', '1.1', '1.2']] = field(default=_UNSET, metadata={'rest': 'minimumTlsVersionAllowed'})
    preferred_batch_size_in_kilobytes: Optional[int] = field(default=_UNSET, metadata={'rest': 'preferredBatchSizeInKilobytes'})

@dataclass_model
class WebHookEventSubscriptionDestination:
    endpoint_type: Literal['WebHook'] = field(default='WebHook', init=False, metadata={'rest': 'endpointType'})
    properties: WebHookEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


DestinationTypes = Union[
    PartnerEventSubscriptionDestination,
    WebHookEventSubscriptionDestination,
    EventHubEventSubscriptionDestination,
    MonitorAlertEventSubscriptionDestination,
    StorageQueueEventSubscriptionDestination,
    AzureFunctionEventSubscriptionDestination,
    NamespaceTopicEventSubscriptionDestination,
    ServiceBusQueueEventSubscriptionDestination,
    ServiceBusTopicEventSubscriptionDestination,
    HybridConnectionEventSubscriptionDestination
]

@dataclass_model
class DeliveryWithResourceIdentity:
    destination: DestinationTypes = field(metadata={'rest': 'destination'})
    identity: EventSubscriptionIdentity = field(metadata={'rest': 'identity'})


@dataclass_model
class BoolEqualsAdvancedFilter:
    operator_type: Literal['BoolEquals'] = field(default='BoolEquals', init=False, metadata={'rest': 'operatorType'})
    value: bool = field(metadata={'rest': 'value'})


@dataclass_model
class IsNotNullAdvancedFilter:
    operator_type: Literal['IsNotNull'] = field(default='IsNotNull', init=False, metadata={'rest': 'operatorType'})


@dataclass_model
class IsNullOrUndefinedAdvancedFilter:
    operator_type: Literal['IsNullOrUndefined'] = field(default='IsNullOrUndefined', init=False, metadata={'rest': 'operatorType'})


@dataclass_model
class NumberGreaterThanAdvancedFilter:
    operator_type: Literal['NumberGreaterThan'] = field(default='NumberGreaterThan', init=False, metadata={'rest': 'operatorType'})
    value: int = field(metadata={'rest': 'value'})


@dataclass_model
class NumberGreaterThanOrEqualsAdvancedFilter:
    operator_type: Literal['NumberGreaterThanOrEquals'] = field(default='NumberGreaterThanOrEquals', init=False, metadata={'rest': 'operatorType'})
    value: int = field(metadata={'rest': 'value'})


@dataclass_model
class NumberInAdvancedFilter:
    operator_type: Literal['NumberIn'] = field(default='NumberIn', init=False, metadata={'rest': 'operatorType'})
    values: List[int] = field(metadata={'rest': 'value'})


@dataclass_model
class NumberInRangeAdvancedFilter:
    operator_type: Literal['NumberInRange'] = field(default='NumberInRange', init=False, metadata={'rest': 'operatorType'})
    values: List[List[int]] = field(metadata={'rest': 'values'})


@dataclass_model
class NumberLessThanAdvancedFilter:
    operator_type: Literal['NumberLessThan'] = field(default='NumberLessThan', init=False, metadata={'rest': 'operatorType'})
    value: int = field(metadata={'rest': 'value'})


@dataclass_model
class NumberLessThanOrEqualsAdvancedFilter:
    operator_type: Literal['NumberLessThanOrEquals'] = field(default='NumberLessThanOrEquals', init=False, metadata={'rest': 'operatorType'})
    value: int = field(metadata={'rest': 'value'})


@dataclass_model
class NumberNotInAdvancedFilter:
    operator_type: Literal['NumberNotIn'] = field(default='NumberNotIn', init=False, metadata={'rest': 'operatorType'})
    values: List[int] = field(metadata={'rest': 'value'})


@dataclass_model
class NumberNotInRangeAdvancedFilter:
    operator_type: Literal['NumberNotInRange'] = field(default='NumberNotInRange', init=False, metadata={'rest': 'operatorType'})
    values: List[List[int]] = field(metadata={'rest': 'values'})


@dataclass_model
class StringBeginsWithAdvancedFilter:
    operator_type: Literal['StringBeginsWith'] = field(default='StringBeginsWith', init=False, metadata={'rest': 'operatorType'})
    values: List[str] = field(metadata={'rest': 'values'})


@dataclass_model
class StringContainsAdvancedFilter:
    operator_type: Literal['StringContains'] = field(default='StringContains', init=False, metadata={'rest': 'operatorType'})
    values: List[str] = field(metadata={'rest': 'values'})


@dataclass_model
class StringEndsWithAdvancedFilter:
    operator_type: Literal['StringEndsWith'] = field(default='StringEndsWith', init=False, metadata={'rest': 'operatorType'})
    values: List[str] = field(metadata={'rest': 'values'})


@dataclass_model
class StringInAdvancedFilter:
    operator_type: Literal['StringIn'] = field(default='StringIn', init=False, metadata={'rest': 'operatorType'})
    values: List[str] = field(metadata={'rest': 'values'})


@dataclass_model
class StringNotBeginsWithAdvancedFilter:
    operator_type: Literal['StringNotBeginsWith'] = field(default='StringNotBeginsWith', init=False, metadata={'rest': 'operatorType'})
    values: List[str] = field(metadata={'rest': 'values'})


@dataclass_model
class StringNotContainsAdvancedFilter:
    operator_type: Literal['StringNotContains'] = field(default='StringNotContains', init=False, metadata={'rest': 'operatorType'})
    values: List[str] = field(metadata={'rest': 'values'})


@dataclass_model
class StringNotEndsWithAdvancedFilter:
    operator_type: Literal['StringNotEndsWith'] = field(default='StringNotEndsWith', init=False, metadata={'rest': 'operatorType'})
    values: List[str] = field(metadata={'rest': 'values'})


@dataclass_model
class StringNotInAdvancedFilter:
    operator_type: Literal['StringNotIn'] = field(default='StringNotIn', init=False, metadata={'rest': 'operatorType'})
    values: List[str] = field(metadata={'rest': 'values'})


FilterTypes = Union[
    NumberInAdvancedFilter,
    StringInAdvancedFilter,
    IsNotNullAdvancedFilter,
    BoolEqualsAdvancedFilter,
    NumberNotInAdvancedFilter,
    StringNotInAdvancedFilter,
    NumberInRangeAdvancedFilter,
    NumberLessThanAdvancedFilter,
    StringContainsAdvancedFilter,
    StringEndsWithAdvancedFilter,
    NumberNotInRangeAdvancedFilter,
    StringBeginsWithAdvancedFilter,
    IsNullOrUndefinedAdvancedFilter,
    NumberGreaterThanAdvancedFilter,
    StringNotContainsAdvancedFilter,
    StringNotEndsWithAdvancedFilter,
    StringNotBeginsWithAdvancedFilter,
    NumberLessThanOrEqualsAdvancedFilter,
    NumberGreaterThanOrEqualsAdvancedFilter
]

@dataclass_model
class EventSubscriptionFilter:
    advanced_filters: Optional[List[FilterTypes]] = field(default=_UNSET, metadata={'rest': 'advancedFilters'})
    enable_advanced_filtering_on_arrays: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enableAdvancedFilteringOnArrays'})
    included_event_types: Optional[List[str]] = field(metadata={'rest': 'includedEventTypes'})
    is_subject_case_sensitive: Optional[bool] = field(default=_UNSET, metadata={'rest': 'isSubjectCaseSensitive'})
    subject_begins_with: Optional[str] = field(default=_UNSET, metadata={'rest': 'subjectBeginsWith'})
    subject_ends_with: Optional[str] = field(default=_UNSET, metadata={'rest': 'subjectEndsWith'})


@dataclass_model
class RetryPolicy:
    event_time_to_live_in_minutes: Optional[int] = field(default=_UNSET, metadata={'rest': 'eventTimeToLiveInMinutes'})
    max_delivery_attempts: Optional[int] = field(default=_UNSET, metadata={'rest': 'maxDeliveryAttempts'})


@dataclass_model
class EventSubscriptionProperties:
    dead_letter_destination: Optional[StorageBlobDeadLetterDestination] = field(default=_UNSET, metadata={'rest': 'deadLetterDestination'})
    dead_letter_with_resource_identity: Optional[DeadLetterWithResourceIdentity] = field(default=_UNSET, metadata={'rest': 'deadLetterWithResourceIdentity'})
    delivery_with_resource_identity: Optional[DeliveryWithResourceIdentity] = field(default=_UNSET, metadata={'rest': 'deliveryWithResourceIdentity'})
    destination: Optional[DestinationTypes] = field(default=_UNSET, metadata={'rest': 'destination'})
    event_delivery_schema: Literal['CloudEventSchemaV1_0', 'CustomInputSchema', 'EventGridSchema'] = field(metadata={'rest': 'eventDeliverySchema'})
    expiration_time_utc: Optional[str] = field(default=_UNSET, metadata={'rest': 'expirationTimeUtc'})
    filter: Optional[EventSubscriptionFilter] = field(default=_UNSET, metadata={'rest': 'filter'})
    labels: Optional[List[str]] = field(default=_UNSET, metadata={'rest': 'labels'})
    retry_policy: Optional[RetryPolicy] = field(default=_UNSET, metadata={'rest': 'retryPolicy'})


@dataclass_model
class EventSubscription(Resource):
    properties: Optional[EventSubscriptionProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    name: str = field(default_factory=lambda: UniqueName(prefix="cmegsub", length=24), metadata={'rest': 'name'})
    _resource: ClassVar[Literal['Microsoft.EventGrid/systemTopics/eventSubscriptions']] = 'Microsoft.EventGrid/systemTopics/eventSubscriptions'
    _version: ClassVar[str] = '2022-06-15'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("egsub"), init=False, repr=False)


@dataclass_model
class IdentityInfo:
    principal_id: str = field(default=_UNSET, metadata={'rest': 'identity'})
    tenant_id: str = field(default=_UNSET, metadata={'rest': 'tenantId'})
    type: Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned', 'UserAssigned'] = field(metadata={'rest': 'type'})
    user_assigned_identities: Optional[UserAssignedIdentities] = field(default=_UNSET, metadata={'rest': 'userAssignedIdentities'})


@dataclass_model
class SystemTopicProperties:
    source: str = field(metadata={'rest': 'source'})
    topic_type: str = field(metadata={'rest': 'topicType'})


@dataclass_model
class SystemTopics(LocatedResource):
    identity: Optional[IdentityInfo] = field(default=_UNSET, metadata={'rest': 'identity'})
    properties: Optional[SystemTopicProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    subscriptions: List[EventSubscription] = field(default_factory=list, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.EventGrid/systemTopics']] = 'Microsoft.EventGrid/systemTopics'
    _version: ClassVar[str] = '2022-06-15'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("egst"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> None:
        _serialize_resource(bicep, self)
        for sub in self.subscriptions:
            sub._parent = self
            sub.write(bicep)
