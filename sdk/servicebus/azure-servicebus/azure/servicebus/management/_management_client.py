# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint:disable=protected-access
# pylint:disable=specify-parameter-names-in-call
import functools
from typing import TYPE_CHECKING, Dict, Any, Union, cast
from xml.etree.ElementTree import ElementTree

from azure.core.paging import ItemPaged
from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import HttpLoggingPolicy, DistributedTracingPolicy, ContentDecodePolicy, \
    RequestIdPolicy, BearerTokenCredentialPolicy
from azure.core.pipeline.transport import RequestsTransport

from ._generated.models import QueueDescriptionFeed, TopicDescriptionEntry, \
    QueueDescriptionEntry, SubscriptionDescriptionFeed, SubscriptionDescriptionEntry, RuleDescriptionEntry, \
    RuleDescriptionFeed, NamespacePropertiesEntry, CreateTopicBody, CreateTopicBodyContent, \
    TopicDescriptionFeed, CreateSubscriptionBody, CreateSubscriptionBodyContent, CreateRuleBody, \
    CreateRuleBodyContent, CreateQueueBody, CreateQueueBodyContent, \
    QueueDescription as InternalQueueDescription, TopicDescription as InternalTopicDescription, \
    SubscriptionDescription as InternalSubscriptionDescription, RuleDescription as InternalRuleDescription, \
    NamespaceProperties
from ._utils import extract_data_template, get_next_template
from ._xml_workaround_policy import ServiceBusXMLWorkaroundPolicy

from .._common.constants import JWT_TOKEN_SCOPE
from .._common.utils import parse_conn_str
from .._base_handler import ServiceBusSharedKeyCredential
from ._shared_key_policy import ServiceBusSharedKeyCredentialPolicy
from ._generated._configuration import ServiceBusManagementClientConfiguration
from ._generated._service_bus_management_client import ServiceBusManagementClient as ServiceBusManagementClientImpl
from ._model_workaround import avoid_timedelta_overflow
from . import _constants as constants
from ._models import QueueRuntimeInfo, QueueDescription, TopicDescription, TopicRuntimeInfo, \
    SubscriptionDescription, SubscriptionRuntimeInfo, RuleDescription
from ._handle_response_error import _handle_response_error

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # pylint:disable=ungrouped-imports


class ServiceBusManagementClient:  # pylint:disable=too-many-public-methods
    """Use this client to create, update, list, and delete resources of a ServiceBus namespace.

    :param str fully_qualified_namespace: The fully qualified host name for the Service Bus namespace.
    :param credential: To authenticate to manage the entities of the ServiceBus namespace.
    :type credential: Union[TokenCredential, azure.servicebus.ServiceBusSharedKeyCredential]
    """

    def __init__(self, fully_qualified_namespace, credential, **kwargs):
        # type: (str, Union[TokenCredential, ServiceBusSharedKeyCredential], Dict[str, Any]) -> None
        self.fully_qualified_namespace = fully_qualified_namespace
        self._credential = credential
        self._endpoint = "https://" + fully_qualified_namespace
        self._config = ServiceBusManagementClientConfiguration(self._endpoint, **kwargs)
        self._pipeline = self._build_pipeline()
        self._impl = ServiceBusManagementClientImpl(endpoint=fully_qualified_namespace, pipeline=self._pipeline)

    def __enter__(self):
        self._impl.__enter__()
        return self

    def __exit__(self, *exc_details):
        self._impl.__exit__(*exc_details)

    def _build_pipeline(self, **kwargs):  # pylint: disable=no-self-use
        transport = kwargs.get('transport')
        policies = kwargs.get('policies')
        credential_policy = ServiceBusSharedKeyCredentialPolicy(self._endpoint, self._credential, "Authorization") \
            if isinstance(self._credential, ServiceBusSharedKeyCredential) \
            else BearerTokenCredentialPolicy(self._credential, JWT_TOKEN_SCOPE)
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
            transport = RequestsTransport(**kwargs)
        return Pipeline(transport, policies)

    def _get_entity_element(self, entity_name, enrich=False, **kwargs):
        # type: (str, bool, Any) -> ElementTree

        with _handle_response_error():
            element = cast(
                ElementTree,
                self._impl.entity.get(entity_name, enrich=enrich, api_version=constants.API_VERSION, **kwargs)
            )
        return element

    def _get_subscription_element(self, topic_name, subscription_name, enrich=False, **kwargs):
        # type: (str, str, bool, Any) -> ElementTree

        with _handle_response_error():
            element = cast(
                ElementTree,
                self._impl.subscription.get(
                    topic_name, subscription_name, enrich=enrich, api_version=constants.API_VERSION, **kwargs)
            )
        return element

    def _get_rule_element(self, topic_name, subscription_name, rule_name, **kwargs):
        # type: (str, str, str, Any) -> ElementTree

        with _handle_response_error():
            element = cast(
                ElementTree,
                self._impl.rule.get(
                    topic_name, subscription_name, rule_name, enrich=False, api_version=constants.API_VERSION, **kwargs)
            )
        return element

    @classmethod
    def from_connection_string(cls, conn_str, **kwargs):
        # type: (str, Any) -> ServiceBusManagementClient
        """Create a client from connection string.

        :param str conn_str: The connection string of the Service Bus Namespace.
        :rtype: ~azure.servicebus.management.ServiceBusManagementClient
        """
        endpoint, shared_access_key_name, shared_access_key, _ = parse_conn_str(conn_str)
        if "//" in endpoint:
            endpoint = endpoint[endpoint.index("//") + 2:]
        return cls(endpoint, ServiceBusSharedKeyCredential(shared_access_key_name, shared_access_key), **kwargs)

    def get_queue(self, queue_name, **kwargs):
        # type: (str, Any) -> QueueDescription
        """Get the properties of a queue.

        :param str queue_name: The name of the queue.
        :rtype: ~azure.servicebus.management.QueueDescription
        """
        entry_ele = self._get_entity_element(queue_name, **kwargs)
        entry = QueueDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError("Queue '{}' does not exist".format(queue_name))
        queue_description = QueueDescription._from_internal_entity(queue_name, entry.content.queue_description)
        return queue_description

    def get_queue_runtime_info(self, queue_name, **kwargs):
        # type: (str, Any) -> QueueRuntimeInfo
        """Get the runtime information of a queue.

        :param str queue_name: The name of the queue.
        :rtype: ~azure.servicebus.management.QueueRuntimeInfo
        """
        entry_ele = self._get_entity_element(queue_name, **kwargs)
        entry = QueueDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError("Queue {} does not exist".format(queue_name))
        runtime_info = QueueRuntimeInfo._from_internal_entity(queue_name, entry.content.queue_description)
        return runtime_info

    def create_queue(self, queue, **kwargs):
        # type: (Union[str, QueueDescription], Any) -> QueueDescription
        """Create a queue.

        :param queue: The queue name or a `QueueDescription` instance. When it's a str, it will be the name
         of the created queue. Other properties of the created queue will have default values as defined by the
         service. Use a `QueueDescription` if you want to set queue properties other than the queue name.
        :type queue: Union[str, ~azure.servicebus.management.QueueDescription]
        :rtype: ~azure.servicebus.management.QueueDescription
        """
        try:
            queue_name = queue.name  # type: ignore
            to_create = queue._to_internal_entity()  # type: ignore  # pylint:disable=protected-access
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
                self._impl.entity.put(
                    queue_name,  # type: ignore
                    request_body, api_version=constants.API_VERSION, **kwargs)
            )

        entry = QueueDescriptionEntry.deserialize(entry_ele)
        result = QueueDescription._from_internal_entity(queue_name, entry.content.queue_description)
        return result

    def update_queue(self, queue, **kwargs):
        # type: (QueueDescription, Any) -> None
        """Update a queue.

        Before calling this method, you should use `get_queue` to get a `QueueDescription` instance, then use the
        keyword arguments to update the properties you want to update.
        Only a portion of properties can be updated.
        Refer to https://docs.microsoft.com/en-us/rest/api/servicebus/update-queue.

        :param queue: The queue to be updated.
        :type queue: ~azure.servicebus.management.QueueDescription
        :keyword timedelta default_message_time_to_live: The value you want to update to.
        :keyword timedelta lock_duration: The value you want to update to.
        :keyword bool dead_lettering_on_message_expiration: The value you want to update to.
        :keyword timedelta duplicate_detection_history_time_window: The value you want to update to.
        :keyword int max_delivery_count: The value you want to update to.
        :rtype: None
        """

        to_update = queue._to_internal_entity()

        to_update.default_message_time_to_live = kwargs.get(
            "default_message_time_to_live") or queue.default_message_time_to_live
        to_update.lock_duration = kwargs.get("lock_duration") or queue.lock_duration
        to_update.dead_lettering_on_message_expiration = kwargs.get(
            "dead_lettering_on_message_expiration") or queue.dead_lettering_on_message_expiration
        to_update.duplicate_detection_history_time_window = kwargs.get(
            "duplicate_detection_history_time_window") or queue.duplicate_detection_history_time_window
        to_update.max_delivery_count = kwargs.get("max_delivery_count") or queue.max_delivery_count

        to_update.default_message_time_to_live = avoid_timedelta_overflow(to_update.default_message_time_to_live)
        to_update.auto_delete_on_idle = avoid_timedelta_overflow(to_update.auto_delete_on_idle)

        create_entity_body = CreateQueueBody(
            content=CreateQueueBodyContent(
                queue_description=to_update,
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        with _handle_response_error():
            self._impl.entity.put(
                queue.name,  # type: ignore
                request_body,
                api_version=constants.API_VERSION,
                if_match="*",
                **kwargs
            )

    def delete_queue(self, queue, **kwargs):
        # type: (Union[str, QueueDescription], Any) -> None
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
            self._impl.entity.delete(
                queue_name,   # type: ignore
                api_version=constants.API_VERSION, **kwargs)

    def list_queues(self, **kwargs):
        # type: (Any) -> ItemPaged[QueueDescription]
        """List the queues of a ServiceBus namespace.

        :returns: An iterable (auto-paging) response of QueueDescription.
        :rtype: ~azure.core.paging.ItemPaged[~azure.servicebus.management.QueueDescription]
        """

        def entry_to_qd(entry):
            qd = QueueDescription._from_internal_entity(entry.title, entry.content.queue_description)
            return qd

        extract_data = functools.partial(
            extract_data_template, QueueDescriptionFeed, entry_to_qd
        )
        get_next = functools.partial(
            get_next_template, functools.partial(self._impl.list_entities, constants.ENTITY_TYPE_QUEUES), **kwargs
        )
        return ItemPaged(
            get_next, extract_data)

    def list_queues_runtime_info(self, **kwargs):
        # type: (Any) -> ItemPaged[QueueRuntimeInfo]
        """List the runtime information of the queues in a ServiceBus namespace.

        :returns: An iterable (auto-paging) response of QueueRuntimeInfo.
        :rtype: ~azure.core.paging.ItemPaged[~azure.servicebus.management.QueueRuntimeInfo]
        """

        def entry_to_qr(entry):
            qd = QueueRuntimeInfo._from_internal_entity(entry.title, entry.content.queue_description)
            return qd

        extract_data = functools.partial(
            extract_data_template, QueueDescriptionFeed, entry_to_qr
        )
        get_next = functools.partial(
            get_next_template, functools.partial(self._impl.list_entities, constants.ENTITY_TYPE_QUEUES), **kwargs
        )
        return ItemPaged(
            get_next, extract_data)

    def get_topic(self, topic_name, **kwargs):
        # type: (str, Any) -> TopicDescription
        """Get the properties of a topic.

        :param str topic_name: The name of the topic.
        :rtype: ~azure.servicebus.management.TopicDescription
        """
        entry_ele = self._get_entity_element(topic_name, **kwargs)
        entry = TopicDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError("Topic '{}' does not exist".format(topic_name))
        topic_description = TopicDescription._from_internal_entity(topic_name, entry.content.topic_description)
        return topic_description

    def get_topic_runtime_info(self, topic_name, **kwargs):
        # type: (str, Any) -> TopicRuntimeInfo
        """Get a the runtime information of a topic.

        :param str topic_name: The name of the topic.
        :rtype: ~azure.servicebus.management.TopicRuntimeInfo
        """
        entry_ele = self._get_entity_element(topic_name, **kwargs)
        entry = TopicDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError("Topic {} does not exist".format(topic_name))
        topic_description = TopicRuntimeInfo._from_internal_entity(topic_name, entry.content.topic_description)
        return topic_description

    def create_topic(self, topic, **kwargs):
        # type: (Union[str, TopicDescription], Any) -> TopicDescription
        """Create a topic.

        :param Union[str, ~azure.servicebus.management.TopicDescription] topic: The topic name or a `TopicDescription`
         instance. When it's a str, it will be the name of the created topic. Other properties of the created topic
         will have default values as defined by the service.
         Use a `TopicDescription` if you want to set queue properties other than the queue name.
        :rtype: ~azure.servicebus.management.TopicDescription
        """
        try:
            topic_name = topic.name  # type: ignore
            to_create = topic._to_internal_entity()  # type: ignore  # pylint:disable=protected-access
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
                self._impl.entity.put(
                    topic_name,  # type: ignore
                    request_body, api_version=constants.API_VERSION, **kwargs)
            )
        entry = TopicDescriptionEntry.deserialize(entry_ele)
        result = TopicDescription._from_internal_entity(topic_name, entry.content.topic_description)
        return result

    def update_topic(self, topic, **kwargs):
        # type: (TopicDescription, Any) -> None
        """Update a topic.

        Before calling this method, you should use `get_topic` to get a `TopicDescription` instance, then use the
        keyword arguments to update the properties you want to update.
        Only a portion of properties can be updated.
        Refer to https://docs.microsoft.com/en-us/rest/api/servicebus/update-topic.

        :param ~azure.servicebus.management.TopicDescription topic: The topic to be updated.
        :keyword timedelta default_message_time_to_live: The value you want to update to.
        :keyword timedelta duplicate_detection_history_time_window: The value you want to update to.
        :rtype: None
        """

        to_update = topic._to_internal_entity()

        to_update.default_message_time_to_live = kwargs.get(
            "default_message_time_to_live") or topic.default_message_time_to_live
        to_update.duplicate_detection_history_time_window = kwargs.get(
            "duplicate_detection_history_time_window") or topic.duplicate_detection_history_time_window

        to_update.default_message_time_to_live = avoid_timedelta_overflow(to_update.default_message_time_to_live)
        to_update.auto_delete_on_idle = avoid_timedelta_overflow(to_update.auto_delete_on_idle)

        create_entity_body = CreateTopicBody(
            content=CreateTopicBodyContent(
                topic_description=to_update,
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        with _handle_response_error():
            self._impl.entity.put(
                topic.name,  # type: ignore
                request_body,
                api_version=constants.API_VERSION,
                if_match="*",
                **kwargs
            )

    def delete_topic(self, topic, **kwargs):
        # type: (Union[str, TopicDescription], Any) -> None
        """Delete a topic.

        :param Union[str, ~azure.servicebus.management.TopicDescription] topic: The topic to be deleted.
        :rtype: None
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic
        self._impl.entity.delete(topic_name, api_version=constants.API_VERSION, **kwargs)

    def list_topics(self, **kwargs):
        # type: (Any) -> ItemPaged[TopicDescription]
        """List the topics of a ServiceBus namespace.

        :returns: An iterable (auto-paging) response of TopicDescription.
        :rtype: ~azure.core.paging.ItemPaged[~azure.servicebus.management.TopicDescription]
        """
        def entry_to_topic(entry):
            topic = TopicDescription._from_internal_entity(entry.title, entry.content.topic_description)
            return topic

        extract_data = functools.partial(
            extract_data_template, TopicDescriptionFeed, entry_to_topic
        )
        get_next = functools.partial(
            get_next_template, functools.partial(self._impl.list_entities, constants.ENTITY_TYPE_TOPICS), **kwargs
        )
        return ItemPaged(
            get_next, extract_data)

    def list_topics_runtime_info(self, **kwargs):
        # type: (Any) -> ItemPaged[TopicRuntimeInfo]
        """List the topics runtime information of a ServiceBus namespace.

        :returns: An iterable (auto-paging) response of TopicRuntimeInfo.
        :rtype: ~azure.core.paging.ItemPaged[~azure.servicebus.management.TopicRuntimeInfo]
        """
        def entry_to_topic(entry):
            topic = TopicRuntimeInfo._from_internal_entity(entry.title, entry.content.topic_description)
            return topic

        extract_data = functools.partial(
            extract_data_template, TopicDescriptionFeed, entry_to_topic
        )
        get_next = functools.partial(
            get_next_template, functools.partial(self._impl.list_entities, constants.ENTITY_TYPE_TOPICS), **kwargs
        )
        return ItemPaged(
            get_next, extract_data)

    def get_subscription(self, topic, subscription_name, **kwargs):
        # type: (Union[str, TopicDescription], str, Any) -> SubscriptionDescription
        """Get the properties of a topic subscription.

        :param Union[str, ~azure.servicebus.management.TopicDescription] topic: The topic that owns the subscription.
        :param str subscription_name: name of the subscription.
        :rtype: ~azure.servicebus.management.SubscriptionDescription
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic
        entry_ele = self._get_subscription_element(topic_name, subscription_name, **kwargs)
        entry = SubscriptionDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError(
                "Subscription('Topic: {}, Subscription: {}') does not exist".format(subscription_name, topic_name))
        subscription = SubscriptionDescription._from_internal_entity(
            entry.title, entry.content.subscription_description)
        return subscription

    def get_subscription_runtime_info(self, topic, subscription_name, **kwargs):
        # type: (Union[str, TopicDescription], str, Any) -> SubscriptionRuntimeInfo
        """Get a topic subscription runtime info.

        :param Union[str, ~azure.servicebus.management.TopicDescription] topic: The topic that owns the subscription.
        :param str subscription_name: name of the subscription.
        :rtype: ~azure.servicebus.management.SubscriptionRuntimeInfo
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic
        entry_ele = self._get_subscription_element(topic_name, subscription_name, **kwargs)
        entry = SubscriptionDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError(
                "Subscription('Topic: {}, Subscription: {}') does not exist".format(subscription_name, topic_name))
        subscription = SubscriptionRuntimeInfo._from_internal_entity(
            entry.title, entry.content.subscription_description)
        return subscription

    def create_subscription(self, topic, subscription, **kwargs):
        # type: (Union[str, TopicDescription], Union[str, SubscriptionDescription], Any) -> SubscriptionDescription
        """Create a topic subscription.

        :param Union[str, ~azure.servicebus.management.TopicDescription] topic: The topic that will own the
         to-be-created subscription.
        :param Union[str, ~azure.servicebus.management.SubscriptionDescription] subscription: The subscription name or a
        `SubscriptionDescription` instance. When it's a str, it will be the name of the created subscription.
         Other properties of the created subscription will have default values as defined by the service.
        :rtype:  ~azure.servicebus.management.SubscriptionDescription
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic
        try:
            subscription_name = subscription.name  # type: ignore
            to_create = subscription._to_internal_entity()  # type: ignore  # pylint:disable=protected-access
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
                self._impl.subscription.put(
                    topic_name,
                    subscription_name,  # type: ignore
                    request_body, api_version=constants.API_VERSION, **kwargs)
            )

        entry = SubscriptionDescriptionEntry.deserialize(entry_ele)
        result = SubscriptionDescription._from_internal_entity(
            subscription_name, entry.content.subscription_description)
        return result

    def update_subscription(self, topic, subscription, **kwargs):
        # type: (Union[str, TopicDescription], SubscriptionDescription, Any) -> None
        """Update a subscription.

        Before calling this method, you should use `get_subscription` to get a `SubscriptionDescription` instance,
        then update the related attributes and call this method.
        Only a portion of properties can be updated.

        :param Union[str, ~azure.servicebus.management.TopicDescription] topic: The topic that owns the subscription.
        :param ~azure.servicebus.management.SubscriptionDescription subscription: The subscription to be updated.
        :rtype: None
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic

        to_update = subscription._to_internal_entity()

        to_update.default_message_time_to_live = avoid_timedelta_overflow(to_update.default_message_time_to_live)
        to_update.auto_delete_on_idle = avoid_timedelta_overflow(to_update.auto_delete_on_idle)

        create_entity_body = CreateSubscriptionBody(
            content=CreateSubscriptionBodyContent(
                subscription_description=to_update,
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        with _handle_response_error():
            self._impl.subscription.put(
                topic_name,
                subscription.name,
                request_body,
                api_version=constants.API_VERSION,
                if_match="*",
                **kwargs
            )

    def delete_subscription(self, topic, subscription, **kwargs):
        # type: (Union[str, TopicDescription], Union[str, SubscriptionDescription], Any) -> None
        """Delete a topic subscription.

        :param Union[str, ~azure.servicebus.management.TopicDescription] topic: The topic that owns the subscription.
        :param Union[str, ~azure.servicebus.management.SubscriptionDescription] subscription: The subscription to
         be deleted.
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
        self._impl.subscription.delete(topic_name, subscription_name, api_version=constants.API_VERSION, **kwargs)

    def list_subscriptions(self, topic, **kwargs):
        # type: (Union[str, TopicDescription], Any) -> ItemPaged[SubscriptionDescription]
        """List the subscriptions of a ServiceBus Topic.

        :param Union[str, ~azure.servicebus.management.TopicDescription] topic: The topic that owns the subscription.
        :returns: An iterable (auto-paging) response of SubscriptionDescription.
        :rtype: ~azure.core.paging.ItemPaged[~azure.servicebus.management.SubscriptionDescription]
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic

        def entry_to_subscription(entry):
            subscription = SubscriptionDescription._from_internal_entity(
                entry.title, entry.content.subscription_description)
            return subscription

        extract_data = functools.partial(
            extract_data_template, SubscriptionDescriptionFeed, entry_to_subscription
        )
        get_next = functools.partial(
            get_next_template, functools.partial(self._impl.list_subscriptions, topic_name), **kwargs
        )
        return ItemPaged(
            get_next, extract_data)

    def list_subscriptions_runtime_info(self, topic, **kwargs):
        # type: (Union[str, TopicDescription], Any) -> ItemPaged[SubscriptionRuntimeInfo]
        """List the subscriptions runtime information of a ServiceBus Topic.

        :param Union[str, ~azure.servicebus.management.TopicDescription] topic: The topic that owns the subscription.
        :returns: An iterable (auto-paging) response of SubscriptionRuntimeInfo.
        :rtype: ~azure.core.paging.ItemPaged[~azure.servicebus.management.SubscriptionRuntimeInfo]
        """
        try:
            topic_name = topic.name  # type: ignore
        except AttributeError:
            topic_name = topic

        def entry_to_subscription(entry):
            subscription = SubscriptionRuntimeInfo._from_internal_entity(
                entry.title, entry.content.subscription_description)
            return subscription

        extract_data = functools.partial(
            extract_data_template, SubscriptionDescriptionFeed, entry_to_subscription
        )
        get_next = functools.partial(
            get_next_template, functools.partial(self._impl.list_subscriptions, topic_name), **kwargs
        )
        return ItemPaged(
            get_next, extract_data)

    def get_rule(self, topic, subscription, rule_name, **kwargs):
        # type: (Union[str, TopicDescription], Union[str, SubscriptionDescription], str, Any) -> RuleDescription
        """Get the properties of a topic subscription rule.

        :param Union[str, ~azure.servicebus.management.TopicDescription] topic: The topic that owns the subscription.
        :param Union[str, ~azure.servicebus.management.SubscriptionDescription] subscription: The subscription that
         owns the rule.
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
        entry_ele = self._get_rule_element(topic_name, subscription_name, rule_name, **kwargs)
        entry = RuleDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError(
                "Rule('Topic: {}, Subscription: {}, Rule {}') does not exist".format(
                    subscription_name, topic_name, rule_name))
        rule_description = RuleDescription._from_internal_entity(rule_name, entry.content.rule_description)
        return rule_description

    def create_rule(self, topic, subscription, rule, **kwargs):
        # type: (Union[str, TopicDescription], Union[str, SubscriptionDescription], RuleDescription, Any) -> RuleDescription  # pylint:disable=line-too-long
        """Create a rule for a topic subscription.

        :param Union[str, ~azure.servicebus.management.TopicDescription] topic: The topic that will own the
         to-be-created subscription rule.
        :param Union[str, ~azure.servicebus.management.SubscriptionDescription] subscription: The subscription that
         will own the to-be-created rule.
        :param azure.servicebus.management.RuleDescription rule: The rule to be created.
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
        rule_name = rule.name
        to_create = rule._to_internal_entity()

        create_entity_body = CreateRuleBody(
            content=CreateRuleBodyContent(
                rule_description=to_create,  # type: ignore
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        with _handle_response_error():
            entry_ele = self._impl.rule.put(
                topic_name,
                subscription_name,  # type: ignore
                rule_name,
                request_body, api_version=constants.API_VERSION, **kwargs)
        entry = RuleDescriptionEntry.deserialize(entry_ele)
        result = entry.content.rule_description
        return result

    def update_rule(self, topic, subscription, rule, **kwargs):
        # type: (Union[str, TopicDescription], Union[str, SubscriptionDescription], RuleDescription, Any) -> None
        """Update a rule.

        Before calling this method, you should use `get_rule` to get a `RuleDescription` instance,
        then update the related attributes and call this method.
        Only a portion of properties can be updated.

        :param Union[str, ~azure.servicebus.management.TopicDescription] topic: The topic that owns the subscription.
        :param Union[str, ~azure.servicebus.management.SubscriptionDescription] subscription: The subscription that
         owns this rule.
        :param ~azure.servicebus.management.RuleDescription rule: The rule to be updated.
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

        to_update = rule._to_internal_entity()

        create_entity_body = CreateRuleBody(
            content=CreateRuleBodyContent(
                rule_description=to_update,
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        with _handle_response_error():
            self._impl.rule.put(
                topic_name,
                subscription_name,
                rule.name,
                request_body,
                api_version=constants.API_VERSION,
                if_match="*",
                **kwargs
            )

    def delete_rule(self, topic, subscription, rule, **kwargs):
        # type: (Union[str, TopicDescription], Union[str, SubscriptionDescription], Union[str, RuleDescription], Any) -> None  # pylint:disable=line-too-long
        """Delete a topic subscription rule.

        :param Union[str, ~azure.servicebus.management.TopicDescription] topic: The topic that owns the subscription.
        :param Union[str, ~azure.servicebus.management.SubscriptionDescription] subscription: The subscription that
         owns the topic.
        :param Union[str, ~azure.servicebus.management.RuleDescription] rule: The to-be-deleted rule.
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
        self._impl.rule.delete(topic_name, subscription_name, rule_name, api_version=constants.API_VERSION, **kwargs)

    def list_rules(self, topic, subscription, **kwargs):
        # type: (Union[str, TopicDescription], Union[str, SubscriptionDescription], Any) -> ItemPaged[RuleDescription]
        """List the rules of a topic subscription.

        :param Union[str, ~azure.servicebus.management.TopicDescription] topic: The topic that owns the subscription.
        :param Union[str, ~azure.servicebus.management.SubscriptionDescription] subscription: The subscription that
         owns the rules.
        :returns: An iterable (auto-paging) response of RuleDescription.
        :rtype: ~azure.core.paging.ItemPaged[~azure.servicebus.management.RuleDescription]
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
            return RuleDescription._from_internal_entity(entry.title, rule)

        extract_data = functools.partial(
            extract_data_template, RuleDescriptionFeed, entry_to_rule
        )
        get_next = functools.partial(
            get_next_template, functools.partial(self._impl.list_rules, topic_name, subscription_name), **kwargs
        )
        return ItemPaged(
            get_next, extract_data)

    def get_namespace_properties(self, **kwargs):
        # type: (Any) -> NamespaceProperties
        """Get the namespace properties

        :rtype: ~azure.servicebus.management.NamespaceProperties
        """
        entry_el = self._impl.namespace.get(api_version=constants.API_VERSION, **kwargs)
        namespace_entry = NamespacePropertiesEntry.deserialize(entry_el)
        return namespace_entry.content.namespace_properties

    def close(self):
        # type: () -> None
        self._impl.close()
