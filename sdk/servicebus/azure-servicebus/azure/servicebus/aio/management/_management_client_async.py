# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint:disable=protected-access
# pylint:disable=specify-parameter-names-in-call
import functools
from copy import copy
from typing import TYPE_CHECKING, Dict, Any, Union, cast
from xml.etree.ElementTree import ElementTree

from azure.core.async_paging import AsyncItemPaged
from azure.servicebus.aio.management._utils import extract_data_template, get_next_template
from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import HttpLoggingPolicy, DistributedTracingPolicy, ContentDecodePolicy, \
    RequestIdPolicy, AsyncBearerTokenCredentialPolicy
from azure.core.pipeline.transport import AioHttpTransport

from ...management._generated.models import QueueDescriptionFeed, TopicDescriptionEntry, \
    QueueDescriptionEntry, SubscriptionDescriptionFeed, SubscriptionDescriptionEntry, RuleDescriptionEntry, \
    RuleDescriptionFeed, NamespacePropertiesEntry, CreateTopicBody, CreateTopicBodyContent, \
    TopicDescriptionFeed, CreateSubscriptionBody, CreateSubscriptionBodyContent, CreateRuleBody, \
    CreateRuleBodyContent, CreateQueueBody, CreateQueueBodyContent, \
    QueueDescription as InternalQueueDescription, TopicDescription as InternalTopicDescription, \
    SubscriptionDescription as InternalSubscriptionDescription, RuleDescription as InternalRuleDescription, \
    NamespaceProperties

from ..._common.utils import parse_conn_str
from ..._common.constants import JWT_TOKEN_SCOPE
from ...aio._base_handler_async import ServiceBusSharedKeyCredential
from ...management._generated.aio._configuration_async import ServiceBusManagementClientConfiguration
from ...management._generated.aio._service_bus_management_client_async import ServiceBusManagementClient \
    as ServiceBusManagementClientImpl
from ...management import _constants as constants
from ._shared_key_policy_async import AsyncServiceBusSharedKeyCredentialPolicy
from ...management._models import QueueRuntimeInfo, QueueDescription, TopicDescription, TopicRuntimeInfo, \
    SubscriptionDescription, SubscriptionRuntimeInfo, RuleDescription
from ...management._xml_workaround_policy import ServiceBusXMLWorkaroundPolicy
from ...management._handle_response_error import _handle_response_error
from ...management._model_workaround import avoid_timedelta_overflow


if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential  # pylint:disable=ungrouped-imports


class ServiceBusManagementClient:  #pylint:disable=too-many-public-methods
    """Use this client to create, update, list, and delete resources of a ServiceBus namespace.

    :param str fully_qualified_namespace: The fully qualified host name for the Service Bus namespace.
    :param credential: To authenticate to manage the entities of the ServiceBus namespace.
    :type credential: Union[TokenCredential, ServiceBusSharedKeyCredential]
    """

    def __init__(self, fully_qualified_namespace, credential, **kwargs):
        # type: (str, Union[AsyncTokenCredential, ServiceBusSharedKeyCredential], Dict[str, Any]) -> None

        self.fully_qualified_namespace = fully_qualified_namespace
        self._credential = credential
        self._endpoint = "https://" + fully_qualified_namespace
        self._config = ServiceBusManagementClientConfiguration(self._endpoint, **kwargs)
        self._pipeline = self._build_pipeline()
        self._impl = ServiceBusManagementClientImpl(endpoint=fully_qualified_namespace, pipeline=self._pipeline)

    async def __aenter__(self) -> "ServiceBusManagementClient":
        await self._impl.__aenter__()
        return self

    async def __aexit__(self, *exc_details) -> None:
        await self._impl.__aexit__(*exc_details)

    def _build_pipeline(self, **kwargs):  # pylint: disable=no-self-use
        transport = kwargs.get('transport')
        policies = kwargs.get('policies')
        credential_policy = \
            AsyncServiceBusSharedKeyCredentialPolicy(self._endpoint, self._credential, "Authorization") \
            if isinstance(self._credential, ServiceBusSharedKeyCredential) \
            else AsyncBearerTokenCredentialPolicy(self._credential, JWT_TOKEN_SCOPE)
        if policies is None:  # [] is a valid policy list
            policies = [
                RequestIdPolicy(**kwargs),
                self._config.headers_policy,
                self._config.user_agent_policy,
                self._config.proxy_policy,
                ContentDecodePolicy(**kwargs),
                ServiceBusXMLWorkaroundPolicy(),
                self._config.redirect_policy,
                self._config.retry_policy,
                credential_policy,
                self._config.logging_policy,
                DistributedTracingPolicy(**kwargs),
                HttpLoggingPolicy(**kwargs),
            ]
        if not transport:
            transport = AioHttpTransport(**kwargs)
        return AsyncPipeline(transport, policies)

    @classmethod
    def from_connection_string(cls, conn_str, **kwargs):
        # type: (str, Any) -> ServiceBusManagementClient
        """Create a client from connection string.

        :param str conn_str: The connection string of the Service Bus Namespace.
        :rtype: ~azure.servicebus.management.aio.ServiceBusManagementClient
        """
        endpoint, shared_access_key_name, shared_access_key, _ = parse_conn_str(conn_str)
        if "//" in endpoint:
            endpoint = endpoint[endpoint.index("//")+2:]
        return cls(endpoint, ServiceBusSharedKeyCredential(shared_access_key_name, shared_access_key), **kwargs)

    async def _get_entity_element(self, entity_name, enrich=False, **kwargs):
        # type: (str, bool, Any) -> ElementTree

        with _handle_response_error():
            element = cast(
                ElementTree,
                await self._impl.entity.get(entity_name, enrich=enrich, api_version=constants.API_VERSION, **kwargs)
            )
        return element

    async def _get_subscription_element(self, topic_name, subscription_name, enrich=False, **kwargs):
        # type: (str, str, bool, Any) -> ElementTree

        with _handle_response_error():
            element = cast(
                ElementTree,
                await self._impl.subscription.get(
                    topic_name, subscription_name, enrich=enrich, api_version=constants.API_VERSION, **kwargs)
            )
        return element

    async def _get_rule_element(self, topic_name, subscription_name, rule_name, **kwargs):
        # type: (str, str, str, Any) -> ElementTree

        with _handle_response_error():
            element = cast(
                ElementTree,
                await self._impl.rule.get(
                    topic_name, subscription_name, rule_name, enrich=False, api_version=constants.API_VERSION, **kwargs)
            )
        return element

    async def get_queue(self, queue_name: str, **kwargs) -> QueueDescription:
        """Get a QueueDescription.

        :param str queue_name: The name of the queue.
        :rtype: ~azure.servicebus.management.QueueDescription
        """
        entry_ele = await self._get_entity_element(queue_name, **kwargs)
        entry = QueueDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError("Queue '{}' does not exist".format(queue_name))
        queue_description = QueueDescription._from_internal_entity(
            entry.content.queue_description)
        queue_description.name = queue_name
        return queue_description

    async def get_queue_runtime_info(self, queue_name: str, **kwargs) -> QueueRuntimeInfo:
        """Get the runtime information of a queue.

        :param str queue_name: The name of the queue.
        :rtype: ~azure.servicebus.management.QueueRuntimeInfo
        """
        entry_ele = await self._get_entity_element(queue_name, **kwargs)
        entry = QueueDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError("Queue {} does not exist".format(queue_name))
        runtime_info = QueueRuntimeInfo._from_internal_entity(
            entry.content.queue_description)
        runtime_info.name = queue_name
        return runtime_info

    async def create_queue(self, queue: Union[str, QueueDescription], **kwargs) -> QueueDescription:
        """Create a queue.

        :param queue: The queue name or a `QueueDescription` instance. When it's a str, it will be the name
         of the created queue. Other properties of the created queue will have default values decided by the
         ServiceBus. Use a `QueueDescription` if you want to set queue properties other than the queue name.
        :type queue: Union[str, ~azure.servicebus.management.QueueDescription]
        :rtype: ~azure.servicebus.management.QueueDescription
        """
        try:
            queue_name = queue.name  # type: ignore
            to_create = queue._to_internal_entity()  # type: ignore
        except AttributeError:
            queue_name = queue  # type: ignore
            to_create = InternalQueueDescription()  # Use an empty queue description.

        create_entity_body = CreateQueueBody(
            content=CreateQueueBodyContent(
                queue_description=to_create,  # type: ignore
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        with _handle_response_error():
            entry_ele = cast(
                ElementTree,
                await self._impl.entity.put(
                    queue_name,  # type: ignore
                    request_body, api_version=constants.API_VERSION, **kwargs)
            )

        entry = QueueDescriptionEntry.deserialize(entry_ele)
        result = QueueDescription._from_internal_entity(
            entry.content.queue_description)
        result.name = queue_name
        return result

    async def update_queue(self, queue_description: QueueDescription, **kwargs) -> None:
        """Update a queue.

        :param queue_description: The properties of this `QueueDescription` will be applied to the queue in
         ServiceBus. Only a portion of properties can be updated.
         Refer to https://docs.microsoft.com/en-us/rest/api/servicebus/update-queue.
        :type queue_description: ~azure.servicebus.management.QueueDescription
        :keyword timedelta default_message_time_to_live: The value you want to update to.
        :keyword timedelta lock_duration: The value you want to update to.
        :keyword bool dead_lettering_on_message_expiration: The value you want to update to.
        :keyword timedelta duplicate_detection_history_time_window: The value you want to update to.
        :keyword int max_delivery_count: The value you want to update to.
        :rtype: ~azure.servicebus.management.QueueDescription
        """

        if not isinstance(queue_description, QueueDescription):
            raise TypeError("queue_description must be of type QueueDescription")

        internal_description = queue_description._to_internal_entity()
        to_update = copy(internal_description)

        to_update.default_message_time_to_live = kwargs.get(
            "default_message_time_to_live") or queue_description.default_message_time_to_live
        to_update.lock_duration = kwargs.get("lock_duration") or queue_description.lock_duration
        to_update.dead_lettering_on_message_expiration = kwargs.get(
            "dead_lettering_on_message_expiration") or queue_description.dead_lettering_on_message_expiration
        to_update.duplicate_detection_history_time_window = kwargs.get(
            "duplicate_detection_history_time_window") or queue_description.duplicate_detection_history_time_window
        to_update.max_delivery_count = kwargs.get("max_delivery_count") or queue_description.max_delivery_count

        to_update.default_message_time_to_live = avoid_timedelta_overflow(to_update.default_message_time_to_live)
        to_update.auto_delete_on_idle = avoid_timedelta_overflow(to_update.auto_delete_on_idle)

        create_entity_body = CreateQueueBody(
            content=CreateQueueBodyContent(
                queue_description=to_update,
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        with _handle_response_error():
            await self._impl.entity.put(
                queue_description.name,  # type: ignore
                request_body,
                api_version=constants.API_VERSION,
                if_match="*",
                **kwargs
            )

    async def delete_queue(self, queue: Union[str, QueueDescription], **kwargs) -> None:
        """Delete a queue.

        :param Union[str, azure.servicebus.management.QueueDescription] queue: The name of the queue or
         a `QueueDescription` with name.
        :rtype: None
        """
        try:
            queue_name = queue.name  # type: ignore
        except AttributeError:
            queue_name = queue
        if not queue_name:
            raise ValueError("queue_name must not be None or empty")
        with _handle_response_error():
            await self._impl.entity.delete(queue_name, api_version=constants.API_VERSION, **kwargs)

    def list_queues(self, **kwargs) -> AsyncItemPaged[QueueDescription]:
        """List the queues of a ServiceBus namespace.

        :keyword int start_index: skip this number of queues.
        :keyword int max_page_size: max number of entities per page.
        :rtype: ItemPaged[~azure.servicebus.management.QueueDescription]
        """

        def entry_to_qd(entry):
            qd = QueueDescription._from_internal_entity(entry.content.queue_description)
            qd.name = entry.title
            return qd

        extract_data = functools.partial(
            extract_data_template, QueueDescriptionFeed, entry_to_qd
        )
        get_next = functools.partial(
            get_next_template, functools.partial(self._impl.list_entities, constants.ENTITY_TYPE_QUEUES), **kwargs
        )
        return AsyncItemPaged(
            get_next, extract_data)

    def list_queues_runtime_info(self, **kwargs) -> AsyncItemPaged[QueueRuntimeInfo]:
        """List the runtime info of the queues in a ServiceBus namespace.

        :keyword int start_index: skip this number of queues.
        :keyword int max_page_size: max number of entities per page.
         the ServiceBus namespace.
        :rtype: ItemPaged[~azure.servicebus.management.QueueRuntimeInfo]
        """

        def entry_to_qr(entry):
            qd = QueueRuntimeInfo._from_internal_entity(entry.content.queue_description)
            qd.name = entry.title
            return qd

        extract_data = functools.partial(
            extract_data_template, QueueDescriptionFeed, entry_to_qr
        )
        get_next = functools.partial(
            get_next_template, functools.partial(self._impl.list_entities, constants.ENTITY_TYPE_QUEUES), **kwargs
        )
        return AsyncItemPaged(
            get_next, extract_data)

    async def get_topic(self, topic_name: str, **kwargs) -> TopicDescription:
        """Get a TopicDescription.

        :param str topic_name: The name of the topic.
        :rtype: ~azure.servicebus.management.TopicDescription
        """
        entry_ele = await self._get_entity_element(topic_name, **kwargs)
        entry = TopicDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError("Topic '{}' does not exist".format(topic_name))
        topic_description = TopicDescription._from_internal_entity(entry.content.topic_description)
        topic_description.name = topic_name
        return topic_description

    async def get_topic_runtime_info(self, topic_name: str, **kwargs) -> TopicRuntimeInfo:
        """Get a TopicRuntimeInfo

        :param str topic_name: The name of the topic.
        :rtype: ~azure.servicebus.management.TopicRuntimeInfo
        """
        entry_ele = await self._get_entity_element(topic_name, **kwargs)
        entry = TopicDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError("Topic {} does not exist".format(topic_name))
        topic_description = TopicRuntimeInfo._from_internal_entity(entry.content.topic_description)
        topic_description.name = topic_name
        return topic_description

    async def create_topic(self, topic: Union[str, TopicDescription], **kwargs) -> TopicDescription:
        """Create a topic.

        :param Union[str, ~azure.servicebus.management.TopicDescription] topic: The topic name or a `TopicDescription`
         instance. When it's a str, it will be the name of the created topic. Other properties of the created topic
         will have default values decided by the ServiceBus.
         Use a `TopicDescription` if you want to set queue properties other than the queue name.
        :rtype: ~azure.servicebus.management.TopicDescription
        """
        try:
            topic_name = topic.name  # type: ignore
            to_create = topic._to_internal_entity()  # type: ignore
        except AttributeError:
            topic_name = topic  # type: ignore
            to_create = InternalTopicDescription()  # Use an empty topic description.

        create_entity_body = CreateTopicBody(
            content=CreateTopicBodyContent(
                topic_description=to_create,  # type: ignore
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        with _handle_response_error():
            entry_ele = cast(
                ElementTree,
                await self._impl.entity.put(
                    topic_name,  # type: ignore
                    request_body, api_version=constants.API_VERSION, **kwargs)
            )
        entry = TopicDescriptionEntry.deserialize(entry_ele)
        result = TopicDescription._from_internal_entity(entry.content.topic_description)
        result.name = topic_name
        return result

    async def update_topic(self, topic_description: TopicDescription, **kwargs) -> None:
        """Update a topic.

        Before calling this method, you should use `get_topic` to get a `TopicDescription` instance, then use the
        keyword arguments to update the properties you want to update.
        Only a portion of properties can be updated.
        Refer to https://docs.microsoft.com/en-us/rest/api/servicebus/update-topic.

        :param ~azure.servicebus.management.TopicDescription topic_description: The topic to be updated.
        :keyword timedelta default_message_time_to_live: The value you want to update to.
        :keyword timedelta duplicate_detection_history_time_window: The value you want to update to.
        :rtype: None
        """

        if not isinstance(topic_description, TopicDescription):
            raise TypeError("topic_description must be of type TopicDescription")

        internal_description = topic_description._to_internal_entity()
        to_update = copy(internal_description)

        to_update.default_message_time_to_live = kwargs.get(
            "default_message_time_to_live") or topic_description.default_message_time_to_live
        to_update.duplicate_detection_history_time_window = kwargs.get(
            "duplicate_detection_history_time_window") or topic_description.duplicate_detection_history_time_window

        to_update.default_message_time_to_live = avoid_timedelta_overflow(to_update.default_message_time_to_live)
        to_update.auto_delete_on_idle = avoid_timedelta_overflow(to_update.auto_delete_on_idle)

        create_entity_body = CreateTopicBody(
            content=CreateTopicBodyContent(
                topic_description=to_update,
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        with _handle_response_error():
            await self._impl.entity.put(
                topic_description.name,  # type: ignore
                request_body,
                api_version=constants.API_VERSION,
                if_match="*",
                **kwargs
            )

    async def delete_topic(self, topic: Union[str, TopicDescription], **kwargs) -> None:
        """Delete a topic.

        :param Union[str, TopicDescription] topic:
        :rtype: None
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic
        await self._impl.entity.delete(topic_name, api_version=constants.API_VERSION, **kwargs)

    def list_topics(self, **kwargs) -> AsyncItemPaged[TopicDescription]:
        """List the topics of a ServiceBus namespace.

        :keyword int start_index: skip this number of topics.
        :keyword int max_page_size: max number of entities per page.
        :rtype: ItemPaged[~azure.servicebus.management.TopicDescription]
        """
        def entry_to_topic(entry):
            topic = TopicDescription._from_internal_entity(entry.content.topic_description)
            topic.name = entry.title
            return topic

        extract_data = functools.partial(
            extract_data_template, TopicDescriptionFeed, entry_to_topic
        )
        get_next = functools.partial(
            get_next_template, functools.partial(self._impl.list_entities, constants.ENTITY_TYPE_TOPICS), **kwargs
        )
        return AsyncItemPaged(
            get_next, extract_data)

    def list_topics_runtime_info(self, **kwargs) -> AsyncItemPaged[TopicRuntimeInfo]:
        """List the topics runtime info of a ServiceBus namespace.

        :keyword int start_index: skip this number of queues.
        :keyword int max_page_size: max number of entities per page.
        :rtype: ItemPaged[~azure.servicebus.management.TopicRuntimeInfo]
        """
        def entry_to_topic(entry):
            topic = TopicRuntimeInfo._from_internal_entity(entry.content.topic_description)
            topic.name = entry.title
            return topic

        extract_data = functools.partial(
            extract_data_template, TopicDescriptionFeed, entry_to_topic
        )
        get_next = functools.partial(
            get_next_template, functools.partial(self._impl.list_entities, constants.ENTITY_TYPE_TOPICS), **kwargs
        )
        return AsyncItemPaged(
            get_next, extract_data)

    async def get_subscription(
            self, topic: Union[str, TopicDescription], subscription_name: str, **kwargs
    ) -> SubscriptionDescription:
        """Get a topic subscription.

        :param Union[str, TopicDescription] topic: The topic that owns the subscription.
        :param str subscription_name: name of the subscription.
        :rtype: ~azure.servicebus.management.SubscriptionDescription
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic
        entry_ele = await self._get_subscription_element(topic_name, subscription_name, **kwargs)
        entry = SubscriptionDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError(
                "Subscription('Topic: {}, Subscription: {}') does not exist".format(subscription_name, topic_name))
        subscription = SubscriptionDescription._from_internal_entity(entry.content.subscription_description)
        subscription.name = entry.title
        return subscription

    async def get_subscription_runtime_info(
            self, topic: Union[str, TopicDescription], subscription_name: str, **kwargs
    ) -> SubscriptionRuntimeInfo:
        """Get a topic subscription runtime info.

        :param Union[str, TopicDescription] topic: The topic that owns the subscription.
        :param str subscription_name: name of the subscription.
        :rtype: ~azure.servicebus.management.SubscriptionRuntimeInfo
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic
        entry_ele = await self._get_subscription_element(topic_name, subscription_name, **kwargs)
        entry = SubscriptionDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError(
                "Subscription('Topic: {}, Subscription: {}') does not exist".format(subscription_name, topic_name))
        subscription = SubscriptionRuntimeInfo._from_internal_entity(entry.content.subscription_description)
        subscription.name = entry.title
        return subscription

    async def create_subscription(
            self, topic: Union[str, TopicDescription], subscription: Union[str, SubscriptionDescription], **kwargs
    ) -> SubscriptionDescription:
        """

        :param Union[str, TopicDescription] topic: The topic that will own the to-be-created subscription.
        :param Union[str, ~azure.servicebus.management.SubscriptionDescription] subscription: The subscription name or a
        `SubscriptionDescription` instance. When it's a str, it will be the name of the created subscription.
         Other properties of the created subscription will have default values decided by the ServiceBus.
        :rtype:  ~azure.servicebus.management.SubscriptionDescription
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic
        try:
            subscription_name = subscription.name  # type: ignore
            to_create = subscription._to_internal_entity()  # type: ignore
        except AttributeError:
            subscription_name = subscription  # type: ignore
            to_create = InternalSubscriptionDescription()  # Use an empty queue description.

        create_entity_body = CreateSubscriptionBody(
            content=CreateSubscriptionBodyContent(
                subscription_description=to_create,  # type: ignore
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        with _handle_response_error():
            entry_ele = cast(
                ElementTree,
                await self._impl.subscription.put(
                    topic_name,
                    subscription_name,  # type: ignore
                    request_body, api_version=constants.API_VERSION, **kwargs)
            )

        entry = SubscriptionDescriptionEntry.deserialize(entry_ele)
        result = SubscriptionDescription._from_internal_entity(entry.content.subscription_description)
        result.name = subscription_name
        return result

    async def update_subscription(
            self, topic: Union[str, TopicDescription], subscription_description: SubscriptionDescription, **kwargs
    ) -> None:
        """Update a subscription.

        Before calling this method, you should use `get_subscription` to get a `SubscriptionDescription` instance,
        then update the related attributes and call this method.
        Only a portion of properties can be updated.
        Refer to TODO: to add the doc link that describes what can be updated.

        :param Union[str, TopicDescription] topic: The topic that owns the subscription.
        :param ~azure.servicebus.management.SubscriptionDescription subscription: The subscription to be updated.
        :rtype: None
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic
        if not isinstance(subscription_description, SubscriptionDescription):
            raise TypeError("subscription_description must be of type SubscriptionDescription")

        internal_description = subscription_description._to_internal_entity()
        to_update = copy(internal_description)

        to_update.default_message_time_to_live = avoid_timedelta_overflow(to_update.default_message_time_to_live)
        to_update.auto_delete_on_idle = avoid_timedelta_overflow(to_update.auto_delete_on_idle)

        create_entity_body = CreateSubscriptionBody(
            content=CreateSubscriptionBodyContent(
                subscription_description=to_update,
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        with _handle_response_error():
            await self._impl.subscription.put(
                topic_name,
                subscription_description.name,
                request_body,
                api_version=constants.API_VERSION,
                if_match="*",
                **kwargs
            )

    async def delete_subscription(
            self, topic: Union[str, TopicDescription], subscription: Union[str, SubscriptionDescription], **kwargs
    ) -> None:
        """Delete a topic subscription.

        :param Union[str, TopicDescription] topic: The topic that owns the subscription.
        :param Union[str, SubscriptionDescription] subscription: The subscription to be deleted.
        :rtype: None
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic
        try:
            subscription_name = subscription.name  # type: ignore
        except AttributeError:
            subscription_name = subscription
        await self._impl.subscription.delete(topic_name, subscription_name, api_version=constants.API_VERSION, **kwargs)

    def list_subscriptions(
            self, topic: Union[str, TopicDescription], **kwargs) -> AsyncItemPaged[SubscriptionDescription]:
        """List the subscriptions of a ServiceBus Topic.

        :param Union[str, ~azure.servicebus.management.TopicDescription] topic: The topic that owns the subscription.
        :keyword int start_index: skip this number of queues.
        :keyword int max_page_size: max number of entities per page.
        :rtype: ItemPaged[~azure.servicebus.management.SubscriptionDescription]
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic

        def entry_to_subscription(entry):
            subscription = SubscriptionDescription._from_internal_entity(entry.content.subscription_description)
            subscription.name = entry.title
            return subscription

        extract_data = functools.partial(
            extract_data_template, SubscriptionDescriptionFeed, entry_to_subscription
        )
        get_next = functools.partial(
            get_next_template, functools.partial(self._impl.list_subscriptions, topic_name), **kwargs
        )
        return AsyncItemPaged(
            get_next, extract_data)

    def list_subscriptions_runtime_info(
            self, topic: Union[str, TopicDescription], **kwargs) -> AsyncItemPaged[SubscriptionRuntimeInfo]:
        """List the subscriptions of a ServiceBus Topic Runtime Information.

        :param Union[str, TopicDescription] topic: The topic that owns the subscription.
        :keyword int start_index: skip this number of queues.
        :keyword int max_page_size: max number of entities per page.
        :rtype: ItemPaged[~azure.servicebus.management.SubscriptionRuntimeInfo]
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic

        def entry_to_subscription(entry):
            subscription = SubscriptionRuntimeInfo._from_internal_entity(entry.content.subscription_description)
            subscription.name = entry.title
            return subscription

        extract_data = functools.partial(
            extract_data_template, SubscriptionDescriptionFeed, entry_to_subscription
        )
        get_next = functools.partial(
            get_next_template, functools.partial(self._impl.list_subscriptions, topic_name), **kwargs
        )
        return AsyncItemPaged(
            get_next, extract_data)

    async def get_rule(
            self, topic: Union[str, TopicDescription], subscription: Union[str, SubscriptionDescription],
            rule_name: str, **kwargs) -> RuleDescription:
        """Get a topic subscription rule

        :param Union[str, TopicDescription] topic: The topic that owns the subscription.
        :param Union[str, SubscriptionDescription] subscription: The subscription that owns the rule.
        :param str rule_name: Name of the rule.
        :rtype: ~azure.servicebus.management.RuleDescription
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic
        try:
            subscription_name = subscription.name  # type: ignore
        except AttributeError:
            subscription_name = subscription
        entry_ele = await self._get_rule_element(topic_name, subscription_name, rule_name, **kwargs)
        entry = RuleDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError(
                "Rule('Topic: {}, Subscription: {}, Rule {}') does not exist".format(
                    subscription_name, topic_name, rule_name))
        rule_description = RuleDescription._from_internal_entity(entry.content.rule_description)
        return rule_description

    async def create_rule(
            self, topic: Union[str, TopicDescription], subscription: Union[str, SubscriptionDescription],
            rule: Union[str, RuleDescription], **kwargs) -> RuleDescription:
        """Create a subscription of a topic.

        :param Union[str, TopicDescription] topic: The topic that will own the to-be-created subscription rule.
        :param Union[str, SubscriptionDescription] subscription: The subscription that will own the to-be-created rule.
        :param Union[str, ~azure.servicebus.management.RuleDescription] rule: The rule name or a
        `RuleDescription` instance. When it's a str, it will be the name of the created rule.
         Other properties of the created rule will have default values decided by the ServiceBus
        :rtype: ~azure.servicebus.management.RuleDescription
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic
        try:
            subscription_name = subscription.name  # type: ignore
        except AttributeError:
            subscription_name = subscription
        try:
            rule_name = rule.name  # type: ignore
            to_create = rule._to_internal_entity()  # type: ignore
        except AttributeError:
            rule_name = rule
            to_create = InternalRuleDescription()  # Use an empty queue description.

        create_entity_body = CreateRuleBody(
            content=CreateRuleBodyContent(
                rule_description=to_create,  # type: ignore
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        with _handle_response_error():
            entry_ele = await self._impl.rule.put(
                topic_name,
                subscription_name,  # type: ignore
                rule_name,
                request_body, api_version=constants.API_VERSION, **kwargs)
        entry = RuleDescriptionEntry.deserialize(entry_ele)
        result = entry.content.rule_description
        return result

    async def update_rule(
            self, topic: Union[str, TopicDescription], subscription: Union[str, SubscriptionDescription],
            rule_description: RuleDescription, **kwargs) -> None:
        """Update a rule.

        Before calling this method, you should use `get_rule` to get a `RuleDescription` instance,
        then update the related attributes and call this method.
        Only a portion of properties can be updated.
        Refer to TODO: to add the doc link that describes what can be updated.

        :param Union[str, TopicDescription] topic: The topic that owns the subscription.
        :param Union[str, SubscriptionDescription] subscription: The subscription that owns this rule.
        :param ~azure.servicebus.management.RuleDescription rule_description: The rule to be updated.
        :rtype: None
        """

        if not isinstance(rule_description, RuleDescription):
            raise TypeError("rule_description must be of type RuleDescription")

        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic
        try:
            subscription_name = subscription.name  # type: ignore
        except AttributeError:
            subscription_name = subscription

        internal_description = rule_description._to_internal_entity()
        to_update = copy(internal_description)

        create_entity_body = CreateRuleBody(
            content=CreateRuleBodyContent(
                rule_description=to_update,
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        with _handle_response_error():
            await self._impl.rule.put(
                topic_name,
                subscription_name,
                rule_description.name,
                request_body,
                api_version=constants.API_VERSION,
                if_match="*",
                **kwargs
            )

    async def delete_rule(
            self, topic: Union[str, TopicDescription], subscription: Union[str, SubscriptionDescription],
            rule: Union[str, RuleDescription], **kwargs) -> None:
        """Delete a topic subscription rule.

        :param Union[str, TopicDescription] topic: The topic that owns the subscription.
        :param Union[str, SubscriptionDescription] subscription: The subscription that owns the topic.
        :param Union[str, RuleDescription] rule: The to-be-deleted rule.
        :rtype: None
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic
        try:
            subscription_name = subscription.name  # type: ignore
        except AttributeError:
            subscription_name = subscription
        try:
            rule_name = rule.name  # type: ignore
        except AttributeError:
            rule_name = rule
        await self._impl.rule.delete(
            topic_name, subscription_name, rule_name, api_version=constants.API_VERSION, **kwargs)

    def list_rules(
            self, topic: Union[str, TopicDescription], subscription: Union[str, RuleDescription], **kwargs
    ) -> AsyncItemPaged[RuleDescription]:
        """List the rules of a topic subscription.

        :param Union[str, TopicDescription] topic: The topic that owns the subscription.
        :param Union[str, SubscriptionDescription] subscription: The subscription that owns the rules.
        :keyword int start_index: skip this number of rules.
        :keyword int max_page_size: max number of entities per page.
        :rtype: ItemPaged[~azure.servicebus.management.RuleDescription]
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic
        try:
            subscription_name = subscription.name  # type: ignore
        except AttributeError:
            subscription_name = subscription

        def entry_to_rule(entry):
            rule = entry.content.rule_description
            return RuleDescription._from_internal_entity(rule)

        extract_data = functools.partial(
            extract_data_template, RuleDescriptionFeed, entry_to_rule
        )
        get_next = functools.partial(
            get_next_template, functools.partial(self._impl.list_rules, topic_name, subscription_name), **kwargs
        )
        return AsyncItemPaged(
            get_next, extract_data)

    async def get_namespace_properties(self, **kwargs) -> NamespaceProperties:
        """Get the namespace properties

        :rtype: NamespaceProperties
        """
        entry_el = await self._impl.namespace.get(api_version=constants.API_VERSION, **kwargs)
        namespace_entry = NamespacePropertiesEntry.deserialize(entry_el)
        return namespace_entry.content.namespace_properties

    async def close(self) -> None:
        await self._impl.close()
