# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint:disable=protected-access
# pylint:disable=specify-parameter-names-in-call
# pylint:disable=too-many-lines
import functools
from typing import TYPE_CHECKING, Any, Union, cast, Mapping
from xml.etree.ElementTree import ElementTree

from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import (
    HttpLoggingPolicy,
    DistributedTracingPolicy,
    ContentDecodePolicy,
    RequestIdPolicy,
    AsyncBearerTokenCredentialPolicy,
)
from azure.core.pipeline.transport import AioHttpTransport

from ...management._generated.models import (
    QueueDescriptionFeed,
    TopicDescriptionEntry,
    QueueDescriptionEntry,
    SubscriptionDescriptionFeed,
    SubscriptionDescriptionEntry,
    RuleDescriptionEntry,
    RuleDescriptionFeed,
    NamespacePropertiesEntry,
    CreateTopicBody,
    CreateTopicBodyContent,
    TopicDescriptionFeed,
    CreateSubscriptionBody,
    CreateSubscriptionBodyContent,
    CreateRuleBody,
    CreateRuleBodyContent,
    CreateQueueBody,
    CreateQueueBodyContent,
)

from ..._base_handler import _parse_conn_str
from ..._common.constants import (
    JWT_TOKEN_SCOPE,
    SUPPLEMENTARY_AUTHORIZATION_HEADER,
    DEAD_LETTER_SUPPLEMENTARY_AUTHORIZATION_HEADER,
)
from ...aio._base_handler_async import (
    ServiceBusSharedKeyCredential,
    ServiceBusSASTokenCredential,
)
from ...management._generated.aio._configuration_async import (
    ServiceBusManagementClientConfiguration,
)
from ...management._generated.aio._service_bus_management_client_async import (
    ServiceBusManagementClient as ServiceBusManagementClientImpl,
)
from ...management import _constants as constants
from ._shared_key_policy_async import AsyncServiceBusSharedKeyCredentialPolicy
from ...management._models import (
    QueueRuntimeProperties,
    QueueProperties,
    TopicProperties,
    TopicRuntimeProperties,
    SubscriptionProperties,
    SubscriptionRuntimeProperties,
    RuleProperties,
    NamespaceProperties,
    TrueRuleFilter,
)
from ...management._xml_workaround_policy import ServiceBusXMLWorkaroundPolicy
from ...management._handle_response_error import _handle_response_error
from ...management._model_workaround import avoid_timedelta_overflow
from ._utils import extract_data_template, extract_rule_data_template, get_next_template
from ...management._utils import (
    deserialize_rule_key_values,
    serialize_rule_key_values,
    create_properties_from_dict_if_needed,
    _validate_entity_name_type,
    _validate_topic_and_subscription_types,
    _validate_topic_subscription_and_rule_types,
)

if TYPE_CHECKING:
    from azure.core.credentials_async import (
        AsyncTokenCredential,
    )  # pylint:disable=ungrouped-imports


class ServiceBusAdministrationClient:  # pylint:disable=too-many-public-methods
    """Use this client to create, update, list, and delete resources of a ServiceBus namespace.

    :param str fully_qualified_namespace: The fully qualified host name for the Service Bus namespace.
    :param credential: To authenticate to manage the entities of the ServiceBus namespace.
    :type credential: AsyncTokenCredential
    """

    def __init__(
        self,
        fully_qualified_namespace: str,
        credential: "AsyncTokenCredential",
        **kwargs: Any
    ) -> None:

        self.fully_qualified_namespace = fully_qualified_namespace
        self._credential = credential
        self._endpoint = "https://" + fully_qualified_namespace
        self._config = ServiceBusManagementClientConfiguration(self._endpoint, **kwargs)
        self._pipeline = self._build_pipeline()
        self._impl = ServiceBusManagementClientImpl(
            endpoint=fully_qualified_namespace, pipeline=self._pipeline
        )

    async def __aenter__(self) -> "ServiceBusAdministrationClient":
        await self._impl.__aenter__()
        return self

    async def __aexit__(self, *exc_details) -> None:
        await self._impl.__aexit__(*exc_details)

    def _build_pipeline(self, **kwargs):  # pylint: disable=no-self-use
        transport = kwargs.get("transport")
        policies = kwargs.get("policies")
        credential_policy = (
            AsyncServiceBusSharedKeyCredentialPolicy(
                self._endpoint, self._credential, "Authorization"
            )
            if isinstance(self._credential, ServiceBusSharedKeyCredential)
            else AsyncBearerTokenCredentialPolicy(self._credential, JWT_TOKEN_SCOPE)
        )
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

    async def _get_entity_element(self, entity_name, enrich=False, **kwargs):
        # type: (str, bool, Any) -> ElementTree
        _validate_entity_name_type(entity_name)

        with _handle_response_error():
            element = cast(
                ElementTree,
                await self._impl.entity.get(
                    entity_name,
                    enrich=enrich,
                    api_version=constants.API_VERSION,
                    **kwargs
                ),
            )
        return element

    async def _get_subscription_element(
        self, topic_name, subscription_name, enrich=False, **kwargs
    ):
        # type: (str, str, bool, Any) -> ElementTree
        _validate_topic_and_subscription_types(topic_name, subscription_name)

        with _handle_response_error():
            element = cast(
                ElementTree,
                await self._impl.subscription.get(
                    topic_name,
                    subscription_name,
                    enrich=enrich,
                    api_version=constants.API_VERSION,
                    **kwargs
                ),
            )
        return element

    async def _get_rule_element(
        self, topic_name, subscription_name, rule_name, **kwargs
    ):
        # type: (str, str, str, Any) -> ElementTree
        _validate_topic_subscription_and_rule_types(
            topic_name, subscription_name, rule_name
        )

        with _handle_response_error():
            element = cast(
                ElementTree,
                await self._impl.rule.get(
                    topic_name,
                    subscription_name,
                    rule_name,
                    enrich=False,
                    api_version=constants.API_VERSION,
                    **kwargs
                ),
            )
        return element

    async def _create_forward_to_header_tokens(self, entity, kwargs):
        """forward_to requires providing a bearer token in headers for the referenced entity."""
        kwargs["headers"] = kwargs.get("headers", {})

        async def _populate_header_within_kwargs(uri, header):
            token = (await self._credential.get_token(uri)).token.decode()
            if not isinstance(
                self._credential,
                (ServiceBusSASTokenCredential, ServiceBusSharedKeyCredential),
            ):
                token = "Bearer {}".format(token)
            kwargs["headers"][header] = token

        if entity.forward_to:
            await _populate_header_within_kwargs(
                entity.forward_to, SUPPLEMENTARY_AUTHORIZATION_HEADER
            )
        if entity.forward_dead_lettered_messages_to:
            await _populate_header_within_kwargs(
                entity.forward_dead_lettered_messages_to,
                DEAD_LETTER_SUPPLEMENTARY_AUTHORIZATION_HEADER,
            )

    @classmethod
    def from_connection_string(
        cls, conn_str: str, **kwargs: Any
    ) -> "ServiceBusAdministrationClient":
        """Create a client from connection string.

        :param str conn_str: The connection string of the Service Bus Namespace.
        :rtype: ~azure.servicebus.management.aio.ServiceBusAdministrationClient
        """
        (
            endpoint,
            shared_access_key_name,
            shared_access_key,
            _,
            token,
            token_expiry,
        ) = _parse_conn_str(conn_str)
        if token and token_expiry:
            credential = ServiceBusSASTokenCredential(token, token_expiry)
        elif shared_access_key_name and shared_access_key:
            credential = ServiceBusSharedKeyCredential(shared_access_key_name, shared_access_key)  # type: ignore
        if "//" in endpoint:
            endpoint = endpoint[endpoint.index("//") + 2 :]
        return cls(endpoint, credential, **kwargs)  # type: ignore

    async def get_queue(self, queue_name: str, **kwargs) -> QueueProperties:
        """Get the properties of a queue.

        :param str queue_name: The name of the queue.
        :rtype: ~azure.servicebus.management.QueueProperties
        """
        entry_ele = await self._get_entity_element(queue_name, **kwargs)
        entry = QueueDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError("Queue '{}' does not exist".format(queue_name))
        queue_description = QueueProperties._from_internal_entity(
            queue_name, entry.content.queue_description
        )
        return queue_description

    async def get_queue_runtime_properties(
        self, queue_name: str, **kwargs
    ) -> QueueRuntimeProperties:
        """Get the runtime information of a queue.

        :param str queue_name: The name of the queue.
        :rtype: ~azure.servicebus.management.QueueRuntimeProperties
        """
        entry_ele = await self._get_entity_element(queue_name, **kwargs)
        entry = QueueDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError("Queue {} does not exist".format(queue_name))
        runtime_properties = QueueRuntimeProperties._from_internal_entity(
            queue_name, entry.content.queue_description
        )
        return runtime_properties

    async def create_queue(self, queue_name: str, **kwargs) -> QueueProperties:
        """Create a queue.

        :param queue_name: Name of the queue.
        :type queue_name: str
        :keyword authorization_rules: Authorization rules for resource.
        :type authorization_rules: list[~azure.servicebus.management.AuthorizationRule]
        :keyword auto_delete_on_idle: ISO 8601 timeSpan idle interval after which the queue is
         automatically deleted. The minimum duration is 5 minutes.
        :type auto_delete_on_idle: ~datetime.timedelta
        :keyword dead_lettering_on_message_expiration: A value that indicates whether this queue has dead
         letter support when a message expires.
        :type dead_lettering_on_message_expiration: bool
        :keyword default_message_time_to_live: ISO 8601 default message timespan to live value. This is
         the duration after which the message expires, starting from when the message is sent to Service
         Bus. This is the default value used when TimeToLive is not set on a message itself.
        :type default_message_time_to_live: ~datetime.timedelta
        :keyword duplicate_detection_history_time_window: ISO 8601 timeSpan structure that defines the
         duration of the duplicate detection history. The default value is 10 minutes.
        :type duplicate_detection_history_time_window: ~datetime.timedelta
        :keyword enable_batched_operations: Value that indicates whether server-side batched operations
         are enabled.
        :type enable_batched_operations: bool
        :keyword enable_express: A value that indicates whether Express Entities are enabled. An express
         queue holds a message in memory temporarily before writing it to persistent storage.
        :type enable_express: bool
        :keyword enable_partitioning: A value that indicates whether the queue is to be partitioned
         across multiple message brokers.
        :type enable_partitioning: bool
        :keyword lock_duration: ISO 8601 timespan duration of a peek-lock; that is, the amount of time
         that the message is locked for other receivers. The maximum value for LockDuration is 5
         minutes; the default value is 1 minute.
        :type lock_duration: ~datetime.timedelta
        :keyword max_delivery_count: The maximum delivery count. A message is automatically deadlettered
         after this number of deliveries. Default value is 10.
        :type max_delivery_count: int
        :keyword max_size_in_megabytes: The maximum size of the queue in megabytes, which is the size of
         memory allocated for the queue.
        :type max_size_in_megabytes: int
        :keyword requires_duplicate_detection: A value indicating if this queue requires duplicate
         detection.
        :type requires_duplicate_detection: bool
        :keyword requires_session: A value that indicates whether the queue supports the concept of
         sessions.
        :type requires_session: bool
        :keyword forward_to: The name of the recipient entity to which all the messages sent to the queue
         are forwarded to.
        :type forward_to: str
        :keyword user_metadata: Custom metdata that user can associate with the description. Max length
         is 1024 chars.
        :type user_metadata: str
        :keyword forward_dead_lettered_messages_to: The name of the recipient entity to which all the
         dead-lettered messages of this subscription are forwarded to.
        :type forward_dead_lettered_messages_to: str

        :rtype: ~azure.servicebus.management.QueueProperties
        """
        queue = QueueProperties(
            queue_name,
            authorization_rules=kwargs.pop("authorization_rules", None),
            auto_delete_on_idle=kwargs.pop("auto_delete_on_idle", None),
            dead_lettering_on_message_expiration=kwargs.pop(
                "dead_lettering_on_message_expiration", None
            ),
            default_message_time_to_live=kwargs.pop(
                "default_message_time_to_live", None
            ),
            duplicate_detection_history_time_window=kwargs.pop(
                "duplicate_detection_history_time_window", None
            ),
            availability_status=None,
            enable_batched_operations=kwargs.pop("enable_batched_operations", None),
            enable_express=kwargs.pop("enable_express", None),
            enable_partitioning=kwargs.pop("enable_partitioning", None),
            lock_duration=kwargs.pop("lock_duration", None),
            max_delivery_count=kwargs.pop("max_delivery_count", None),
            max_size_in_megabytes=kwargs.pop("max_size_in_megabytes", None),
            requires_duplicate_detection=kwargs.pop(
                "requires_duplicate_detection", None
            ),
            requires_session=kwargs.pop("requires_session", None),
            status=kwargs.pop("status", None),
            forward_to=kwargs.pop("forward_to", None),
            forward_dead_lettered_messages_to=kwargs.pop(
                "forward_dead_lettered_messages_to", None
            ),
            user_metadata=kwargs.pop("user_metadata", None),
        )
        to_create = queue._to_internal_entity()
        create_entity_body = CreateQueueBody(
            content=CreateQueueBodyContent(
                queue_description=to_create,  # type: ignore
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        await self._create_forward_to_header_tokens(queue, kwargs)
        with _handle_response_error():
            entry_ele = cast(
                ElementTree,
                await self._impl.entity.put(
                    queue_name,  # type: ignore
                    request_body,
                    api_version=constants.API_VERSION,
                    **kwargs
                ),
            )

        entry = QueueDescriptionEntry.deserialize(entry_ele)
        result = QueueProperties._from_internal_entity(
            queue_name, entry.content.queue_description
        )
        return result

    async def update_queue(self, queue: Union[QueueProperties, Mapping[str, Any]], **kwargs) -> None:
        """Update a queue.

        Before calling this method, you should use `get_queue`, `create_queue` or `list_queues` to get a
        `QueueProperties` instance, then update the properties. Only a portion of properties can
        be updated. Refer to https://docs.microsoft.com/en-us/rest/api/servicebus/update-queue.

        :param queue: The queue that is returned from `get_queue`, `create_queue` or `list_queues` and
         has the updated properties.
        :type queue: ~azure.servicebus.management.QueueProperties
        :rtype: None
        """

        queue = create_properties_from_dict_if_needed(queue, QueueProperties)
        to_update = queue._to_internal_entity()

        to_update.default_message_time_to_live = avoid_timedelta_overflow(
            to_update.default_message_time_to_live
        )
        to_update.auto_delete_on_idle = avoid_timedelta_overflow(
            to_update.auto_delete_on_idle
        )

        create_entity_body = CreateQueueBody(
            content=CreateQueueBodyContent(
                queue_description=to_update,
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        await self._create_forward_to_header_tokens(queue, kwargs)
        with _handle_response_error():
            await self._impl.entity.put(
                queue.name,  # type: ignore
                request_body,
                api_version=constants.API_VERSION,
                if_match="*",
                **kwargs
            )

    async def delete_queue(self, queue_name: str, **kwargs) -> None:
        """Delete a queue.

        :param str queue_name: The name of the queue or
         a `QueueProperties` with name.
        :rtype: None
        """
        _validate_entity_name_type(queue_name)

        if not queue_name:
            raise ValueError("queue_name must not be None or empty")
        with _handle_response_error():
            await self._impl.entity.delete(
                queue_name, api_version=constants.API_VERSION, **kwargs
            )

    def list_queues(self, **kwargs: Any) -> AsyncItemPaged[QueueProperties]:
        """List the queues of a ServiceBus namespace.

        :returns: An iterable (auto-paging) response of QueueProperties.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.servicebus.management.QueueProperties]
        """

        def entry_to_qd(entry):
            qd = QueueProperties._from_internal_entity(
                entry.title, entry.content.queue_description
            )
            return qd

        extract_data = functools.partial(
            extract_data_template, QueueDescriptionFeed, entry_to_qd
        )
        get_next = functools.partial(
            get_next_template,
            functools.partial(self._impl.list_entities, constants.ENTITY_TYPE_QUEUES),
            **kwargs
        )
        return AsyncItemPaged(get_next, extract_data)

    def list_queues_runtime_properties(
        self, **kwargs: Any
    ) -> AsyncItemPaged[QueueRuntimeProperties]:
        """List the runtime information of the queues in a ServiceBus namespace.

        :returns: An iterable (auto-paging) response of QueueRuntimeProperties.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.servicebus.management.QueueRuntimeProperties]
        """

        def entry_to_qr(entry):
            qd = QueueRuntimeProperties._from_internal_entity(
                entry.title, entry.content.queue_description
            )
            return qd

        extract_data = functools.partial(
            extract_data_template, QueueDescriptionFeed, entry_to_qr
        )
        get_next = functools.partial(
            get_next_template,
            functools.partial(self._impl.list_entities, constants.ENTITY_TYPE_QUEUES),
            **kwargs
        )
        return AsyncItemPaged(get_next, extract_data)

    async def get_topic(self, topic_name: str, **kwargs) -> TopicProperties:
        """Get the properties of a topic.

        :param str topic_name: The name of the topic.
        :rtype: ~azure.servicebus.management.TopicDescription
        """
        entry_ele = await self._get_entity_element(topic_name, **kwargs)
        entry = TopicDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError("Topic '{}' does not exist".format(topic_name))
        topic_description = TopicProperties._from_internal_entity(
            topic_name, entry.content.topic_description
        )
        return topic_description

    async def get_topic_runtime_properties(
        self, topic_name: str, **kwargs
    ) -> TopicRuntimeProperties:
        """Get the runtime information of a topic.

        :param str topic_name: The name of the topic.
        :rtype: ~azure.servicebus.management.TopicRuntimeProperties
        """
        entry_ele = await self._get_entity_element(topic_name, **kwargs)
        entry = TopicDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError("Topic {} does not exist".format(topic_name))
        topic_description = TopicRuntimeProperties._from_internal_entity(
            topic_name, entry.content.topic_description
        )
        return topic_description

    async def create_topic(self, topic_name: str, **kwargs) -> TopicProperties:
        """Create a topic.

        :param topic_name: Name of the topic.
        :type topic_name: str
        :keyword default_message_time_to_live: ISO 8601 default message timespan to live value. This is
         the duration after which the message expires, starting from when the message is sent to Service
         Bus. This is the default value used when TimeToLive is not set on a message itself.
        :type default_message_time_to_live: ~datetime.timedelta
        :keyword max_size_in_megabytes: The maximum size of the topic in megabytes, which is the size of
         memory allocated for the topic.
        :type max_size_in_megabytes: long
        :keyword requires_duplicate_detection: A value indicating if this topic requires duplicate
         detection.
        :type requires_duplicate_detection: bool
        :keyword duplicate_detection_history_time_window: ISO 8601 timeSpan structure that defines the
         duration of the duplicate detection history. The default value is 10 minutes.
        :type duplicate_detection_history_time_window: ~datetime.timedelta
        :keyword enable_batched_operations: Value that indicates whether server-side batched operations
         are enabled.
        :type enable_batched_operations: bool
        :keyword size_in_bytes: The size of the topic, in bytes.
        :type size_in_bytes: int
        :keyword filtering_messages_before_publishing: Filter messages before publishing.
        :type filtering_messages_before_publishing: bool
        :keyword authorization_rules: Authorization rules for resource.
        :type authorization_rules:
         list[~azure.servicebus.management.AuthorizationRule]
        :keyword support_ordering: A value that indicates whether the topic supports ordering.
        :type support_ordering: bool
        :keyword auto_delete_on_idle: ISO 8601 timeSpan idle interval after which the topic is
         automatically deleted. The minimum duration is 5 minutes.
        :type auto_delete_on_idle: ~datetime.timedelta
        :keyword enable_partitioning: A value that indicates whether the topic is to be partitioned
         across multiple message brokers.
        :type enable_partitioning: bool
        :keyword enable_express: A value that indicates whether Express Entities are enabled. An express
         queue holds a message in memory temporarily before writing it to persistent storage.
        :type enable_express: bool
        :keyword user_metadata: Metadata associated with the topic.
        :type user_metadata: str

        :rtype: ~azure.servicebus.management.TopicProperties
        """

        topic = TopicProperties(
            topic_name,
            default_message_time_to_live=kwargs.pop(
                "default_message_time_to_live", None
            ),
            max_size_in_megabytes=kwargs.pop("max_size_in_megabytes", None),
            requires_duplicate_detection=kwargs.pop(
                "requires_duplicate_detection", None
            ),
            duplicate_detection_history_time_window=kwargs.pop(
                "duplicate_detection_history_time_window", None
            ),
            enable_batched_operations=kwargs.pop("enable_batched_operations", None),
            size_in_bytes=kwargs.pop("size_in_bytes", None),
            authorization_rules=kwargs.pop("authorization_rules", None),
            status=kwargs.pop("status", None),
            support_ordering=kwargs.pop("support_ordering", None),
            auto_delete_on_idle=kwargs.pop("auto_delete_on_idle", None),
            enable_partitioning=kwargs.pop("enable_partitioning", None),
            availability_status=None,
            enable_express=kwargs.pop("enable_express", None),
            user_metadata=kwargs.pop("user_metadata", None),
        )
        to_create = topic._to_internal_entity()

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
                    request_body,
                    api_version=constants.API_VERSION,
                    **kwargs
                ),
            )
        entry = TopicDescriptionEntry.deserialize(entry_ele)
        result = TopicProperties._from_internal_entity(
            topic_name, entry.content.topic_description
        )
        return result

    async def update_topic(self, topic: Union[TopicProperties, Mapping[str, Any]], **kwargs) -> None:
        """Update a topic.

        Before calling this method, you should use `get_topic`, `create_topic` or `list_topics` to get a
        `TopicProperties` instance, then update the properties. Only a portion of properties can be updated.
        Refer to https://docs.microsoft.com/en-us/rest/api/servicebus/update-topic.

        :param topic: The topic that is returned from `get_topic`, `create_topic`, or `list_topics`
         and has the updated properties.
        :type topic: ~azure.servicebus.management.TopicProperties
        :rtype: None
        """

        topic = create_properties_from_dict_if_needed(topic, TopicProperties)
        to_update = topic._to_internal_entity()

        to_update.default_message_time_to_live = avoid_timedelta_overflow(
            to_update.default_message_time_to_live
        )
        to_update.auto_delete_on_idle = avoid_timedelta_overflow(
            to_update.auto_delete_on_idle
        )

        create_entity_body = CreateTopicBody(
            content=CreateTopicBodyContent(
                topic_description=to_update,
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        with _handle_response_error():
            await self._impl.entity.put(
                topic.name,  # type: ignore
                request_body,
                api_version=constants.API_VERSION,
                if_match="*",
                **kwargs
            )

    async def delete_topic(self, topic_name: str, **kwargs) -> None:
        """Delete a topic.

        :param str topic_name: The topic to be deleted.
        :rtype: None
        """
        _validate_entity_name_type(topic_name)

        await self._impl.entity.delete(
            topic_name, api_version=constants.API_VERSION, **kwargs
        )

    def list_topics(self, **kwargs: Any) -> AsyncItemPaged[TopicProperties]:
        """List the topics of a ServiceBus namespace.

        :returns: An iterable (auto-paging) response of TopicProperties.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.servicebus.management.TopicProperties]
        """

        def entry_to_topic(entry):
            topic = TopicProperties._from_internal_entity(
                entry.title, entry.content.topic_description
            )
            return topic

        extract_data = functools.partial(
            extract_data_template, TopicDescriptionFeed, entry_to_topic
        )
        get_next = functools.partial(
            get_next_template,
            functools.partial(self._impl.list_entities, constants.ENTITY_TYPE_TOPICS),
            **kwargs
        )
        return AsyncItemPaged(get_next, extract_data)

    def list_topics_runtime_properties(
        self, **kwargs: Any
    ) -> AsyncItemPaged[TopicRuntimeProperties]:
        """List the topics runtime information of a ServiceBus namespace.

        :returns: An iterable (auto-paging) response of TopicRuntimeProperties.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.servicebus.management.TopicRuntimeProperties]
        """

        def entry_to_topic(entry):
            topic = TopicRuntimeProperties._from_internal_entity(
                entry.title, entry.content.topic_description
            )
            return topic

        extract_data = functools.partial(
            extract_data_template, TopicDescriptionFeed, entry_to_topic
        )
        get_next = functools.partial(
            get_next_template,
            functools.partial(self._impl.list_entities, constants.ENTITY_TYPE_TOPICS),
            **kwargs
        )
        return AsyncItemPaged(get_next, extract_data)

    async def get_subscription(
        self, topic_name: str, subscription_name: str, **kwargs
    ) -> SubscriptionProperties:
        """Get the properties of a topic subscription.

        :param str topic_name: The topic that owns the subscription.
        :param str subscription_name: name of the subscription.
        :rtype: ~azure.servicebus.management.SubscriptionProperties
        """
        entry_ele = await self._get_subscription_element(
            topic_name, subscription_name, **kwargs
        )
        entry = SubscriptionDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError(
                "Subscription('Topic: {}, Subscription: {}') does not exist".format(
                    subscription_name, topic_name
                )
            )
        subscription = SubscriptionProperties._from_internal_entity(
            entry.title, entry.content.subscription_description
        )
        return subscription

    async def get_subscription_runtime_properties(
        self, topic_name: str, subscription_name: str, **kwargs
    ) -> SubscriptionRuntimeProperties:
        """Get a topic subscription runtime info.

        :param str topic_name: The topic that owns the subscription.
        :param str subscription_name: name of the subscription.
        :rtype: ~azure.servicebus.management.SubscriptionRuntimeProperties
        """
        entry_ele = await self._get_subscription_element(
            topic_name, subscription_name, **kwargs
        )
        entry = SubscriptionDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError(
                "Subscription('Topic: {}, Subscription: {}') does not exist".format(
                    subscription_name, topic_name
                )
            )
        subscription = SubscriptionRuntimeProperties._from_internal_entity(
            entry.title, entry.content.subscription_description
        )
        return subscription

    async def create_subscription(
        self, topic_name: str, subscription_name: str, **kwargs
    ) -> SubscriptionProperties:
        """Create a topic subscription.

        :param str topic_name: The topic that will own the
         to-be-created subscription.
        :param subscription_name: Name of the subscription.
        :type subscription_name: str
        :keyword lock_duration: ISO 8601 timespan duration of a peek-lock; that is, the amount of time
         that the message is locked for other receivers. The maximum value for LockDuration is 5
         minutes; the default value is 1 minute.
        :type lock_duration: ~datetime.timedelta
        :keyword requires_session: A value that indicates whether the queue supports the concept of
         sessions.
        :type requires_session: bool
        :keyword default_message_time_to_live: ISO 8601 default message timespan to live value. This is
         the duration after which the message expires, starting from when the message is sent to Service
         Bus. This is the default value used when TimeToLive is not set on a message itself.
        :type default_message_time_to_live: ~datetime.timedelta
        :keyword dead_lettering_on_message_expiration: A value that indicates whether this subscription
         has dead letter support when a message expires.
        :type dead_lettering_on_message_expiration: bool
        :keyword dead_lettering_on_filter_evaluation_exceptions: A value that indicates whether this
         subscription has dead letter support when a message expires.
        :type dead_lettering_on_filter_evaluation_exceptions: bool
        :keyword max_delivery_count: The maximum delivery count. A message is automatically deadlettered
         after this number of deliveries. Default value is 10.
        :type max_delivery_count: int
        :keyword enable_batched_operations: Value that indicates whether server-side batched operations
         are enabled.
        :type enable_batched_operations: bool
        :keyword forward_to: The name of the recipient entity to which all the messages sent to the
         subscription are forwarded to.
        :type forward_to: str
        :keyword user_metadata: Metadata associated with the subscription. Maximum number of characters
         is 1024.
        :type user_metadata: str
        :keyword forward_dead_lettered_messages_to: The name of the recipient entity to which all the
         messages sent to the subscription are forwarded to.
        :type forward_dead_lettered_messages_to: str
        :keyword auto_delete_on_idle: ISO 8601 timeSpan idle interval after which the subscription is
         automatically deleted. The minimum duration is 5 minutes.
        :type auto_delete_on_idle: ~datetime.timedelta
        :rtype:  ~azure.servicebus.management.SubscriptionProperties
        """
        _validate_entity_name_type(topic_name, display_name="topic_name")

        subscription = SubscriptionProperties(
            subscription_name,
            lock_duration=kwargs.pop("lock_duration", None),
            requires_session=kwargs.pop("requires_session", None),
            default_message_time_to_live=kwargs.pop(
                "default_message_time_to_live", None
            ),
            dead_lettering_on_message_expiration=kwargs.pop(
                "dead_lettering_on_message_expiration", None
            ),
            dead_lettering_on_filter_evaluation_exceptions=kwargs.pop(
                "dead_lettering_on_filter_evaluation_exceptions", None
            ),
            max_delivery_count=kwargs.pop("max_delivery_count", None),
            enable_batched_operations=kwargs.pop("enable_batched_operations", None),
            status=kwargs.pop("status", None),
            forward_to=kwargs.pop("forward_to", None),
            user_metadata=kwargs.pop("user_metadata", None),
            forward_dead_lettered_messages_to=kwargs.pop(
                "forward_dead_lettered_messages_to", None
            ),
            auto_delete_on_idle=kwargs.pop("auto_delete_on_idle", None),
            availability_status=None,
        )
        to_create = subscription._to_internal_entity()  # type: ignore  # pylint:disable=protected-access

        create_entity_body = CreateSubscriptionBody(
            content=CreateSubscriptionBodyContent(
                subscription_description=to_create,  # type: ignore
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        await self._create_forward_to_header_tokens(subscription, kwargs)
        with _handle_response_error():
            entry_ele = cast(
                ElementTree,
                await self._impl.subscription.put(
                    topic_name,
                    subscription_name,  # type: ignore
                    request_body,
                    api_version=constants.API_VERSION,
                    **kwargs
                ),
            )

        entry = SubscriptionDescriptionEntry.deserialize(entry_ele)
        result = SubscriptionProperties._from_internal_entity(
            subscription_name, entry.content.subscription_description
        )
        return result

    async def update_subscription(
        self, topic_name: str, subscription: Union[SubscriptionProperties, Mapping[str, Any]], **kwargs
    ) -> None:
        """Update a subscription.

        Before calling this method, you should use `get_subscription`, `update_subscription` or `list_subscription`
        to get a `SubscriptionProperties` instance, then update the properties.

        :param str topic_name: The topic that owns the subscription.
        :param ~azure.servicebus.management.SubscriptionProperties subscription: The subscription that is returned
         from `get_subscription`, `update_subscription` or `list_subscription` and has the updated properties.
        :rtype: None
        """

        _validate_entity_name_type(topic_name, display_name="topic_name")

        subscription = create_properties_from_dict_if_needed(subscription, SubscriptionProperties)
        to_update = subscription._to_internal_entity()

        to_update.default_message_time_to_live = avoid_timedelta_overflow(
            to_update.default_message_time_to_live
        )
        to_update.auto_delete_on_idle = avoid_timedelta_overflow(
            to_update.auto_delete_on_idle
        )

        create_entity_body = CreateSubscriptionBody(
            content=CreateSubscriptionBodyContent(
                subscription_description=to_update,
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        await self._create_forward_to_header_tokens(subscription, kwargs)
        with _handle_response_error():
            await self._impl.subscription.put(
                topic_name,
                subscription.name,
                request_body,
                api_version=constants.API_VERSION,
                if_match="*",
                **kwargs
            )

    async def delete_subscription(
        self, topic_name: str, subscription_name: str, **kwargs
    ) -> None:
        """Delete a topic subscription.

        :param str topic_name: The topic that owns the subscription.
        :param str subscription_name: The subscription
         to be deleted.
        :rtype: None
        """
        _validate_topic_and_subscription_types(topic_name, subscription_name)

        await self._impl.subscription.delete(
            topic_name, subscription_name, api_version=constants.API_VERSION, **kwargs
        )

    def list_subscriptions(
        self, topic_name: str, **kwargs: Any
    ) -> AsyncItemPaged[SubscriptionProperties]:
        """List the subscriptions of a ServiceBus Topic.

        :param str topic_name: The topic that owns the subscription.
        :returns: An iterable (auto-paging) response of SubscriptionProperties.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.servicebus.management.SubscriptionProperties]
        """
        _validate_entity_name_type(topic_name)

        def entry_to_subscription(entry):
            subscription = SubscriptionProperties._from_internal_entity(
                entry.title, entry.content.subscription_description
            )
            return subscription

        extract_data = functools.partial(
            extract_data_template, SubscriptionDescriptionFeed, entry_to_subscription
        )
        get_next = functools.partial(
            get_next_template,
            functools.partial(self._impl.list_subscriptions, topic_name),
            **kwargs
        )
        return AsyncItemPaged(get_next, extract_data)

    def list_subscriptions_runtime_properties(
        self, topic_name: str, **kwargs: Any
    ) -> AsyncItemPaged[SubscriptionRuntimeProperties]:
        """List the subscriptions runtime information of a ServiceBus.

        :param str topic_name: The topic that owns the subscription.
        :returns: An iterable (auto-paging) response of SubscriptionRuntimeProperties.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.servicebus.management.SubscriptionRuntimeProperties]
        """
        _validate_entity_name_type(topic_name)

        def entry_to_subscription(entry):
            subscription = SubscriptionRuntimeProperties._from_internal_entity(
                entry.title, entry.content.subscription_description
            )
            return subscription

        extract_data = functools.partial(
            extract_data_template, SubscriptionDescriptionFeed, entry_to_subscription
        )
        get_next = functools.partial(
            get_next_template,
            functools.partial(self._impl.list_subscriptions, topic_name),
            **kwargs
        )
        return AsyncItemPaged(get_next, extract_data)

    async def get_rule(
        self, topic_name: str, subscription_name: str, rule_name: str, **kwargs
    ) -> RuleProperties:
        """Get the properties of a topic subscription rule.

        :param str topic_name: The topic that owns the subscription.
        :param str subscription_name: The subscription that
         owns the rule.
        :param str rule_name: Name of the rule.
        :rtype: ~azure.servicebus.management.RuleProperties
        """
        entry_ele = await self._get_rule_element(
            topic_name, subscription_name, rule_name, **kwargs
        )
        entry = RuleDescriptionEntry.deserialize(entry_ele)
        if not entry.content:
            raise ResourceNotFoundError(
                "Rule('Topic: {}, Subscription: {}, Rule {}') does not exist".format(
                    subscription_name, topic_name, rule_name
                )
            )
        rule_description = RuleProperties._from_internal_entity(
            rule_name, entry.content.rule_description
        )
        deserialize_rule_key_values(
            entry_ele, rule_description
        )  # to remove after #3535 is released.
        return rule_description

    async def create_rule(
        self, topic_name: str, subscription_name: str, rule_name: str, **kwargs
    ) -> RuleProperties:
        """Create a rule for a topic subscription.

        :param str topic_name: The topic that will own the
         to-be-created subscription rule.
        :param str subscription_name: The subscription that
         will own the to-be-created rule.
        :param rule_name: Name of the rule.
        :type rule_name: str
        :keyword filter: The filter of the rule. The default value is ~azure.servicebus.management.TrueRuleFilter
        :type filter: Union[~azure.servicebus.management.CorrelationRuleFilter,
         ~azure.servicebus.management.SqlRuleFilter]
        :keyword action: The action of the rule.
        :type action: Optional[~azure.servicebus.management.SqlRuleAction]

        :rtype: ~azure.servicebus.management.RuleProperties
        """
        _validate_topic_and_subscription_types(topic_name, subscription_name)

        rule = RuleProperties(
            rule_name,
            filter=kwargs.pop("filter", TrueRuleFilter()),
            action=kwargs.pop("action", None),
            created_at_utc=None,
        )
        to_create = rule._to_internal_entity()

        create_entity_body = CreateRuleBody(
            content=CreateRuleBodyContent(
                rule_description=to_create,  # type: ignore
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        serialize_rule_key_values(request_body, rule)
        with _handle_response_error():
            entry_ele = await self._impl.rule.put(
                topic_name,
                subscription_name,  # type: ignore
                rule_name,
                request_body,
                api_version=constants.API_VERSION,
                **kwargs
            )
        entry = RuleDescriptionEntry.deserialize(entry_ele)
        result = RuleProperties._from_internal_entity(
            rule_name, entry.content.rule_description
        )
        deserialize_rule_key_values(
            entry_ele, result
        )  # to remove after #3535 is released.
        return result

    async def update_rule(
        self, topic_name: str, subscription_name: str, rule: Union[RuleProperties, Mapping[str, Any]], **kwargs
    ) -> None:
        """Update a rule.

        Before calling this method, you should use `get_rule`, `create_rule` or `list_rules` to get a `RuleProperties`
        instance, then update the properties.

        :param str topic_name: The topic that owns the subscription.
        :param str subscription_name: The subscription that
         owns this rule.
        :param rule: The rule that is returned from `get_rule`,
         `create_rule`, or `list_rules` and has the updated properties.
        :type rule: ~azure.servicebus.management.RuleProperties
        :rtype: None
        """
        _validate_topic_and_subscription_types(topic_name, subscription_name)

        rule = create_properties_from_dict_if_needed(rule, RuleProperties)
        to_update = rule._to_internal_entity()

        create_entity_body = CreateRuleBody(
            content=CreateRuleBodyContent(
                rule_description=to_update,
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        serialize_rule_key_values(request_body, rule)
        with _handle_response_error():
            await self._impl.rule.put(
                topic_name,
                subscription_name,
                rule.name,
                request_body,
                api_version=constants.API_VERSION,
                if_match="*",
                **kwargs
            )

    async def delete_rule(
        self, topic_name: str, subscription_name: str, rule_name: str, **kwargs
    ) -> None:
        """Delete a topic subscription rule.

        :param str topic_name: The topic that owns the subscription.
        :param str subscription_name: The subscription that
         owns the topic.
        :param str rule_name: The to-be-deleted rule.
        :rtype: None
        """
        _validate_topic_subscription_and_rule_types(
            topic_name, subscription_name, rule_name
        )

        await self._impl.rule.delete(
            topic_name,
            subscription_name,
            rule_name,
            api_version=constants.API_VERSION,
            **kwargs
        )

    def list_rules(
        self, topic_name: str, subscription_name: str, **kwargs: Any
    ) -> AsyncItemPaged[RuleProperties]:
        """List the rules of a topic subscription.

        :param str topic_name: The topic that owns the subscription.
        :param str subscription_name: The subscription that
         owns the rules.
        :returns: An iterable (auto-paging) response of RuleProperties.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.servicebus.management.RuleProperties]
        """
        _validate_topic_and_subscription_types(topic_name, subscription_name)

        def entry_to_rule(ele, entry):
            """
            `ele` will be removed after #3535 is released.
            """
            rule = entry.content.rule_description
            rule_description = RuleProperties._from_internal_entity(entry.title, rule)
            deserialize_rule_key_values(
                ele, rule_description
            )  # to remove after #3535 is released.
            return rule_description

        extract_data = functools.partial(
            extract_rule_data_template, RuleDescriptionFeed, entry_to_rule
        )
        get_next = functools.partial(
            get_next_template,
            functools.partial(self._impl.list_rules, topic_name, subscription_name),
            **kwargs
        )
        return AsyncItemPaged(get_next, extract_data)

    async def get_namespace_properties(self, **kwargs) -> NamespaceProperties:
        """Get the namespace properties

        :rtype: ~azure.servicebus.management.NamespaceProperties
        """
        entry_el = await self._impl.namespace.get(
            api_version=constants.API_VERSION, **kwargs
        )
        namespace_entry = NamespacePropertiesEntry.deserialize(entry_el)
        return NamespaceProperties._from_internal_entity(
            namespace_entry.title, namespace_entry.content.namespace_properties
        )

    async def close(self) -> None:
        await self._impl.close()
