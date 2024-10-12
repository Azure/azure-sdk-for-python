# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=name-too-long, line-too-long

from typing import IO, ClassVar, Dict, List, Optional, Literal, Required, TypedDict, Union
from dataclasses import dataclass, field

from ._identity import UserAssignedIdentities
from ._resource import (
    Resource,
    LocatedResource,
    UniqueName,
    generate_symbol,
    _serialize_resource,
    _UNSET,
    _SKIP,
    BicepInt,
    BicepBool,
    BicepStr
)


class EventSubscriptionIdentity(TypedDict, total=False):
    type: Required[Literal['SystemAssigned', 'UserAssigned']]
    userAssignedIdentity: BicepStr


class StorageBlobDeadLetterDestinationProperties(TypedDict, total=False):
    blobContainerName: Required[BicepStr]
    resourceId: Required[BicepStr]


class StorageBlobDeadLetterDestination(TypedDict, total=False):
    endpointType: Required[Literal['StorageBlob']]
    properties: Required[StorageBlobDeadLetterDestinationProperties]


class DeadLetterWithResourceIdentity(TypedDict, total=False):
    deadLetterDestination: Required[StorageBlobDeadLetterDestination]
    identity: Required[EventSubscriptionIdentity]


class DynamicDeliveryAttributeMappingProperties(TypedDict, total=False):
    sourceField: Required[BicepStr]


class DynamicDeliveryAttributeMapping(TypedDict, total=False):
    type: Required[Literal['Dynamic']]
    properties: Required[DynamicDeliveryAttributeMappingProperties]


class StaticDeliveryAttributeMappingProperties(TypedDict, total=False):
    isSecret: Required[BicepBool]
    value: Required[BicepStr]


class StaticDeliveryAttributeMapping(TypedDict, total=False):
    type: Required[Literal['Static']]
    properties: Required[StaticDeliveryAttributeMappingProperties]


AttributeMapping = Union[
    DynamicDeliveryAttributeMapping,
    StaticDeliveryAttributeMapping
]


class AzureFunctionEventSubscriptionDestinationProperties(TypedDict, total=False):
    deliveryAttributeMappings: List[AttributeMapping]
    maxEventsPerBatch: BicepInt
    preferredBatchSizeInKilobytes: BicepInt
    resourceId: Required[BicepStr]


class AzureFunctionEventSubscriptionDestination(TypedDict, total=False):
    endpointType: Required[Literal['AzureFunction']]
    properties: Required[AzureFunctionEventSubscriptionDestinationProperties]


class EventHubEventSubscriptionDestinationProperties(TypedDict, total=False):
    deliveryAttributeMappings: List[AttributeMapping]
    resourceId: Required[BicepStr]


class EventHubEventSubscriptionDestination(TypedDict, total=False):
    endpointType: Required[Literal['EventHub']]
    properties: Required[EventHubEventSubscriptionDestinationProperties]


class HybridConnectionEventSubscriptionDestinationProperties(TypedDict, total=False):
    deliveryAttributeMappings: List[AttributeMapping]
    resourceId: Required[BicepStr]


class HybridConnectionEventSubscriptionDestination(TypedDict, total=False):
    endpointType: Required[Literal['HybridConnection']]
    properties: Required[HybridConnectionEventSubscriptionDestinationProperties]


class MonitorAlertEventSubscriptionDestinationProperties(TypedDict, total=False):
    actionGroups: List[BicepStr]
    description: BicepStr
    severity: Required[Literal['Sev0', 'Sev1', 'Sev2', 'Sev3', 'Sev4']]


class MonitorAlertEventSubscriptionDestination(TypedDict, total=False):
    endpointType: Required[Literal['MonitorAlert']]
    properties: Required[MonitorAlertEventSubscriptionDestinationProperties]


class NamespaceTopicEventSubscriptionDestinationProperties(TypedDict, total=False):
    resourceId: Required[BicepStr]


class NamespaceTopicEventSubscriptionDestination(TypedDict, total=False):
    endpointType: Required[Literal['NamespaceTopic']]
    properties: Required[NamespaceTopicEventSubscriptionDestinationProperties]


class PartnerEventSubscriptionDestinationProperties(TypedDict, total=False):
    resourceId: Required[BicepStr]


class PartnerEventSubscriptionDestination(TypedDict, total=False):
    endpointType: Required[Literal['PartnerDestination']]
    properties: Required[PartnerEventSubscriptionDestinationProperties]


class ServiceBusQueueEventSubscriptionDestinationProperties(TypedDict, total=False):
    deliveryAttributeMappings: List[AttributeMapping]
    resourceId: Required[BicepStr]


class ServiceBusQueueEventSubscriptionDestination(TypedDict, total=False):
    endpointType: Required[Literal['ServiceBusQueue']]
    properties: Required[ServiceBusQueueEventSubscriptionDestinationProperties]


class ServiceBusTopicEventSubscriptionDestinationProperties(TypedDict, total=False):
    deliveryAttributeMappings: List[AttributeMapping]
    resourceId: Required[BicepStr]


class ServiceBusTopicEventSubscriptionDestination(TypedDict, total=False):
    endpointType: Required[Literal['ServiceBusTopic']]
    properties: Required[ServiceBusTopicEventSubscriptionDestinationProperties]


class StorageQueueEventSubscriptionDestinationProperties(TypedDict, total=False):
    resourceId: Required[BicepStr]
    queueName: Required[BicepStr]
    queueMessageTimeToLiveInSeconds: BicepInt


class StorageQueueEventSubscriptionDestination(TypedDict, total=False):
    endpointType: Required[Literal['StorageQueue']]
    properties: Required[StorageQueueEventSubscriptionDestinationProperties]


class WebHookEventSubscriptionDestinationProperties(TypedDict, total=False):
    azureActiveDirectoryApplicationIdOrUri: Required[BicepStr]
    azureActiveDirectoryTenantId: BicepStr
    deliveryAttributeMappings: List[AttributeMapping]
    endpointUrl: BicepStr
    maxEventsPerBatch: BicepInt
    minimumTlsVersionAllowed: Literal['1.0', '1.1', '1.2']
    preferredBatchSizeInKilobytes: BicepInt


class WebHookEventSubscriptionDestination(TypedDict, total=False):
    endpointType: Required[Literal['WebHook']]
    properties: Required[WebHookEventSubscriptionDestinationProperties]


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


class DeliveryWithResourceIdentity(TypedDict, total=False):
    destination: Required[DestinationTypes]
    identity: Required[EventSubscriptionIdentity]


class BoolEqualsAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['BoolEquals']]
    value: Required[BicepBool]


class IsNotNullAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['IsNotNull']]


class IsNullOrUndefinedAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['IsNullOrUndefined']]


class NumberGreaterThanAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['NumberGreaterThan']]
    value: Required[BicepInt]


class NumberGreaterThanOrEqualsAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['NumberGreaterThanOrEquals']]
    value: Required[BicepInt]


class NumberInAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['NumberIn']]
    values: Required[List[BicepInt]]


class NumberInRangeAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['NumberInRange']]
    values: Required[List[List[BicepInt]]]


class NumberLessThanAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['NumberLessThan']]
    value: Required[BicepInt]


class NumberLessThanOrEqualsAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['NumberLessThanOrEquals']]
    value: Required[BicepInt]


class NumberNotInAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['NumberNotIn']]
    values: Required[List[BicepInt]]


class NumberNotInRangeAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['NumberNotInRange']]
    values: Required[List[List[BicepInt]]]


class StringBeginsWithAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['StringBeginsWith']]
    values: Required[List[BicepStr]]


class StringContainsAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['StringContains']]
    values: Required[List[BicepStr]]


class StringEndsWithAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['StringEndsWith']]
    values: Required[List[BicepStr]]


class StringInAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['StringIn']]
    values: Required[List[BicepStr]]


class StringNotBeginsWithAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['StringNotBeginsWith']]
    values: Required[List[BicepStr]]


class StringNotContainsAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['StringNotContains']]
    values: Required[List[BicepStr]]


class StringNotEndsWithAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['StringNotEndsWith']]
    values: Required[List[BicepStr]]


class StringNotInAdvancedFilter(TypedDict, total=False):
    operatorType: Required[Literal['StringNotIn']]
    values: Required[List[BicepStr]]


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


class EventSubscriptionFilter(TypedDict, total=False):
    advancedFilters: List[FilterTypes]
    enableAdvancedFilteringOnArrays: BicepBool
    includedEventTypes: Required[List[BicepStr]]
    isSubjectCaseSensitive: BicepBool
    subjectBeginsWith: BicepStr
    subjectEndsWith: BicepStr


class RetryPolicy(TypedDict, total=False):
    eventTimeToLiveInMinutes: BicepInt
    maxDeliveryAttempts: BicepInt


class EventSubscriptionProperties(TypedDict, total=False):
    deadLetterDestination: StorageBlobDeadLetterDestination
    deadLetterWithResourceIdentity: DeadLetterWithResourceIdentity
    deliveryWithResourceIdentity: DeliveryWithResourceIdentity
    destination: DestinationTypes
    eventDeliverySchema: Required[Literal['CloudEventSchemaV1_0', 'CustomInputSchema', 'EventGridSchema']]
    expirationTimeUtc: BicepStr
    filter: EventSubscriptionFilter
    labels: List[BicepStr]
    retryPolicy: RetryPolicy


@dataclass(kw_only=True)
class EventSubscription(Resource):
    properties: Optional[EventSubscriptionProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    name: BicepStr = field(default_factory=lambda: UniqueName(prefix="cmegsub", length=24), metadata={'rest': 'name'})
    _resource: ClassVar[Literal['Microsoft.EventGrid/systemTopics/eventSubscriptions']] = 'Microsoft.EventGrid/systemTopics/eventSubscriptions'
    _version: ClassVar[str] = '2022-06-15'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("egsub"), init=False, repr=False)


class IdentityInfo(TypedDict, total=False):
    principalId: BicepStr
    tenantId: BicepStr
    type: Required[Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned', 'UserAssigned']]
    userAssignedIdentities: UserAssignedIdentities


class SystemTopicProperties(TypedDict, total=False):
    source: Required[BicepStr]
    topicType: Required[BicepStr]


@dataclass(kw_only=True)
class SystemTopics(LocatedResource):
    identity: Optional[IdentityInfo] = field(default=_UNSET, metadata={'rest': 'identity'})
    properties: Optional[SystemTopicProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    subscriptions: List[EventSubscription] = field(default_factory=list, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.EventGrid/systemTopics']] = 'Microsoft.EventGrid/systemTopics'
    _version: ClassVar[str] = '2022-06-15'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("egst"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        _serialize_resource(bicep, self)
        for sub in self.subscriptions:
            sub.parent = self
            self._outputs.update(sub.write(bicep))
        return self._outputs
