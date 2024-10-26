# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=name-too-long, line-too-long

from typing import IO, ClassVar, Dict, List, Optional, Literal, TypedDict, Union
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
    # Required
    type: Literal['SystemAssigned', 'UserAssigned']
    userAssignedIdentity: BicepStr


class StorageBlobDeadLetterDestinationProperties(TypedDict):
    # Required
    blobContainerName: BicepStr
    # Required
    resourceId: BicepStr


class StorageBlobDeadLetterDestination(TypedDict):
    # Required
    endpointType: Literal['StorageBlob']
    # Required
    properties: StorageBlobDeadLetterDestinationProperties


class DeadLetterWithResourceIdentity(TypedDict):
    # Required
    deadLetterDestination: StorageBlobDeadLetterDestination
    # Required
    identity: EventSubscriptionIdentity


class DynamicDeliveryAttributeMappingProperties(TypedDict):
    # Required
    sourceField: BicepStr


class DynamicDeliveryAttributeMapping(TypedDict):
    # Required
    type: Literal['Dynamic']
    # Required
    properties: DynamicDeliveryAttributeMappingProperties


class StaticDeliveryAttributeMappingProperties(TypedDict):
    # Required
    isSecret: BicepBool
    # Required
    value: BicepStr


class StaticDeliveryAttributeMapping(TypedDict):
    # Required
    type: Literal['Static']
    # Required
    properties: StaticDeliveryAttributeMappingProperties


AttributeMapping = Union[
    DynamicDeliveryAttributeMapping,
    StaticDeliveryAttributeMapping
]


class AzureFunctionEventSubscriptionDestinationProperties(TypedDict, total=False):
    deliveryAttributeMappings: List[AttributeMapping]
    maxEventsPerBatch: BicepInt
    preferredBatchSizeInKilobytes: BicepInt
    # Required
    resourceId: BicepStr


class AzureFunctionEventSubscriptionDestination(TypedDict):
    # Required
    endpointType: Literal['AzureFunction']
    # Required
    properties: AzureFunctionEventSubscriptionDestinationProperties


class EventHubEventSubscriptionDestinationProperties(TypedDict, total=False):
    deliveryAttributeMappings: List[AttributeMapping]
    # Required
    resourceId: BicepStr


class EventHubEventSubscriptionDestination(TypedDict):
    # Required
    endpointType: Literal['EventHub']
    # Required
    properties: EventHubEventSubscriptionDestinationProperties


class HybridConnectionEventSubscriptionDestinationProperties(TypedDict, total=False):
    deliveryAttributeMappings: List[AttributeMapping]
    # Required
    resourceId: BicepStr


class HybridConnectionEventSubscriptionDestination(TypedDict):
    # Required
    endpointType: Literal['HybridConnection']
    # Required
    properties: HybridConnectionEventSubscriptionDestinationProperties


class MonitorAlertEventSubscriptionDestinationProperties(TypedDict, total=False):
    actionGroups: List[BicepStr]
    description: BicepStr
    # Required
    severity: Literal['Sev0', 'Sev1', 'Sev2', 'Sev3', 'Sev4']


class MonitorAlertEventSubscriptionDestination(TypedDict):
    # Required
    endpointType: Literal['MonitorAlert']
    # Required
    properties: MonitorAlertEventSubscriptionDestinationProperties


class NamespaceTopicEventSubscriptionDestinationProperties(TypedDict):
    # Required
    resourceId: BicepStr


class NamespaceTopicEventSubscriptionDestination(TypedDict):
    # Required
    endpointType: Literal['NamespaceTopic']
    # Required
    properties: NamespaceTopicEventSubscriptionDestinationProperties


class PartnerEventSubscriptionDestinationProperties(TypedDict):
    # Required
    resourceId: BicepStr


class PartnerEventSubscriptionDestination(TypedDict):
    # Required
    endpointType: Literal['PartnerDestination']
    # Required
    properties: PartnerEventSubscriptionDestinationProperties


class ServiceBusQueueEventSubscriptionDestinationProperties(TypedDict, total=False):
    deliveryAttributeMappings: List[AttributeMapping]
    # Required
    resourceId: BicepStr


class ServiceBusQueueEventSubscriptionDestination(TypedDict):
    # Required
    endpointType: Literal['ServiceBusQueue']
    # Required
    properties: ServiceBusQueueEventSubscriptionDestinationProperties


class ServiceBusTopicEventSubscriptionDestinationProperties(TypedDict, total=False):
    deliveryAttributeMappings: List[AttributeMapping]
    # Required
    resourceId: BicepStr


class ServiceBusTopicEventSubscriptionDestination(TypedDict):
    # Required
    endpointType: Literal['ServiceBusTopic']
    # Required
    properties: ServiceBusTopicEventSubscriptionDestinationProperties


class StorageQueueEventSubscriptionDestinationProperties(TypedDict, total=False):
    # Required
    resourceId: BicepStr
    # Required
    queueName: BicepStr
    queueMessageTimeToLiveInSeconds: BicepInt


class StorageQueueEventSubscriptionDestination(TypedDict):
    # Required
    endpointType: Literal['StorageQueue']
    # Required
    properties: StorageQueueEventSubscriptionDestinationProperties


class WebHookEventSubscriptionDestinationProperties(TypedDict, total=False):
    # Required
    azureActiveDirectoryApplicationIdOrUri: BicepStr
    azureActiveDirectoryTenantId: BicepStr
    deliveryAttributeMappings: List[AttributeMapping]
    endpointUrl: BicepStr
    maxEventsPerBatch: BicepInt
    minimumTlsVersionAllowed: Literal['1.0', '1.1', '1.2']
    preferredBatchSizeInKilobytes: BicepInt


class WebHookEventSubscriptionDestination(TypedDict):
    # Required
    endpointType: Literal['WebHook']
    # Required
    properties: WebHookEventSubscriptionDestinationProperties


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


class DeliveryWithResourceIdentity(TypedDict):
    # Required
    destination: DestinationTypes
    # Required
    identity: EventSubscriptionIdentity


class BoolEqualsAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['BoolEquals']
    # Required
    value: BicepBool


class IsNotNullAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['IsNotNull']


class IsNullOrUndefinedAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['IsNullOrUndefined']


class NumberGreaterThanAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['NumberGreaterThan']
    # Required
    value: BicepInt


class NumberGreaterThanOrEqualsAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['NumberGreaterThanOrEquals']
    value: BicepInt


class NumberInAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['NumberIn']
    # Required
    values: List[BicepInt]


class NumberInRangeAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['NumberInRange']
    # Required
    values: List[List[BicepInt]]


class NumberLessThanAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['NumberLessThan']
    # Required
    value: BicepInt


class NumberLessThanOrEqualsAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['NumberLessThanOrEquals']
    # Required
    value: BicepInt


class NumberNotInAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['NumberNotIn']
    # Required
    values: List[BicepInt]


class NumberNotInRangeAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['NumberNotInRange']
    # Required
    values: List[List[BicepInt]]


class StringBeginsWithAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['StringBeginsWith']
    # Required
    values: List[BicepStr]


class StringContainsAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['StringContains']
    # Required
    values: List[BicepStr]


class StringEndsWithAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['StringEndsWith']
    # Required
    values: List[BicepStr]


class StringInAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['StringIn']
    # Required
    values: List[BicepStr]


class StringNotBeginsWithAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['StringNotBeginsWith']
    # Required
    values: List[BicepStr]


class StringNotContainsAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['StringNotContains']
    # Required
    values: List[BicepStr]


class StringNotEndsWithAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['StringNotEndsWith']
    # Required
    values: List[BicepStr]


class StringNotInAdvancedFilter(TypedDict):
    # Required
    operatorType: Literal['StringNotIn']
    # Required
    values: List[BicepStr]


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
    # Required
    includedEventTypes: List[BicepStr]
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
    # Required
    eventDeliverySchema: Literal['CloudEventSchemaV1_0', 'CustomInputSchema', 'EventGridSchema']
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
    # Required
    type: Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned', 'UserAssigned']
    userAssignedIdentities: UserAssignedIdentities


class SystemTopicProperties(TypedDict):
    # Required
    source: BicepStr
    # Required
    topicType: BicepStr


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
