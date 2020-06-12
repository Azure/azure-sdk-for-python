# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import functools
import xml
from copy import copy
from typing import TYPE_CHECKING, Dict, Any, Union, cast
from xml.etree.ElementTree import ElementTree

import six
from azure.core.paging import ItemPaged
from azure.servicebus.management._generated.models import QueueDescriptionFeed, TopicDescription, TopicDescriptionEntry, \
    QueueDescriptionEntry, SubscriptionDescriptionFeed, SubscriptionDescriptionEntry, RuleDescriptionEntry, \
    RuleDescriptionFeed, RuleDescription
from azure.servicebus.management._utils import extract_data_template, get_next_template
from azure.servicebus.management._xml_workaround_policy import ServiceBusXMLWorkaroundPolicy
from msrest.exceptions import ValidationError
from azure.core.exceptions import raise_with_traceback
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import HttpLoggingPolicy, DistributedTracingPolicy, ContentDecodePolicy, \
    RequestIdPolicy, BearerTokenCredentialPolicy
from azure.core.pipeline.transport import RequestsTransport

from .._common.constants import JWT_TOKEN_SCOPE
from .._common.utils import parse_conn_str
from .._base_handler import ServiceBusSharedKeyCredential
from ._shared_key_policy import ServiceBusSharedKeyCredentialPolicy
from ._generated._configuration import ServiceBusManagementClientConfiguration
from ._generated.models import CreateQueueBody, CreateQueueBodyContent, \
    QueueDescription as InternalQueueDescription
from ._generated._service_bus_management_client import ServiceBusManagementClient as ServiceBusManagementClientImpl
from ._model_workaround import QUEUE_DESCRIPTION_SERIALIZE_ATTRIBUTES, avoid_timedelta_overflow
from . import _constants as constants
from ._models import QueueRuntimeInfo, QueueDescription
from ._handle_response_error import _handle_response_error

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # pylint:disable=ungrouped-imports


class ServiceBusManagementClient:
    """Use this client to create, update, list, and delete resources of a ServiceBus namespace.

    :param str fully_qualified_namespace: The fully qualified host name for the Service Bus namespace.
    :param credential: To authenticate to manage the entities of the ServiceBus namespace.
    :type credential: Union[TokenCredential, ServiceBusSharedKeyCredential]
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

    def _get_entity_element(self, entity_name, **kwargs):
        # type: (str, Any) -> ElementTree

        with _handle_response_error():
            element = cast(
                ElementTree,
                self._impl.entity.get(entity_name, enrich=False, api_version=constants.API_VERSION, **kwargs)
            )
        return element

    def _get_subscription_element(self, topic_name, subscription_name, **kwargs):
        # type: (str, str, Any) -> ElementTree

        with _handle_response_error():
            element = cast(
                ElementTree,
                self._impl.subscription.get(topic_name, subscription_name, enrich=False, api_version=constants.API_VERSION, **kwargs)
            )
        return element

    def _get_rule_element(self, topic_name, subscription_name, rule_name, **kwargs):
        # type: (str, str, str, Any) -> ElementTree

        with _handle_response_error():
            element = cast(
                ElementTree,
                self._impl.rule.get(topic_name, subscription_name, rule_name, enrich=False, api_version=constants.API_VERSION, **kwargs)
            )
        return element

    def get_queue(self, queue_name, **kwargs):
        # type: (str, Any) -> QueueDescription
        """Get a QueueDescription.

        :param str queue_name: The name of the queue.
        :rtype: ~azure.servicebus.management.QueueDescription
        """
        entry_ele = self._get_entity_element(queue_name, **kwargs)
        entry = QueueDescriptionEntry.deserialize(entry_ele)
        queue_description = QueueDescription._from_internal_entity(entry.content.queue_description)
        queue_description.queue_name = queue_name
        return queue_description

    def get_queue_runtime_info(self, queue_name, **kwargs):
        # type: (str, Any) -> QueueRuntimeInfo
        """Get the runtime information of a queue.

        :param str queue_name: The name of the queue.
        :rtype: ~azure.servicebus.management.QueueRuntimeInfo
        """
        entry_ele = self._get_entity_element(queue_name, **kwargs)
        entry = QueueDescriptionEntry.deserialize(entry_ele)
        runtime_info = QueueRuntimeInfo._from_internal_entity(entry.content.queue_description)
        runtime_info.queue_name = queue_name
        return runtime_info

    def create_queue(self, queue, **kwargs):
        # type: (Union[str, QueueDescription], Any) -> QueueDescription
        """Create a queue.

        :param queue: The queue name or a `QueueDescription` instance. When it's a str, it will be the name
         of the created queue. Other properties of the created queue will have default values decided by the
         ServiceBus. Use a `QueueDescription` if you want to set queue properties other than the queue name.
        :type queue: Union[str, QueueDescription]
        :rtype: ~azure.servicebus.management.QueueDescription
        """
        try:
            queue_name = queue.queue_name  # type: ignore
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
        try:
            with _handle_response_error():
                entry_ele = cast(
                    ElementTree,
                    self._impl.entity.put(
                        queue_name,  # type: ignore
                        request_body, api_version=constants.API_VERSION, **kwargs)
                )
        except ValidationError:
            # post-hoc try to give a somewhat-justifiable failure reason.
            if isinstance(queue, (six.string_types, QueueDescription)):
                raise_with_traceback(
                    ValueError,
                    message="queue must be a non-empty str or a QueueDescription with non-empty str queue_name")
            raise_with_traceback(
                TypeError,
                message="queue must be a non-empty str or a QueueDescription with non-empty str queue_name")

        entry = QueueDescriptionEntry.deserialize(entry_ele)
        result = QueueDescription._from_internal_entity(entry.content.queue_description)
        result.queue_name = queue_name
        return result

    def update_queue(self, queue_description, **kwargs):
        # type: (QueueDescription, Any) -> QueueDescription
        """Update a queue.

        :param queue_description: The properties of this `QueueDescription` will be applied to the queue in
         ServiceBus. Only a portion of properties can be updated.
         Refer to https://docs.microsoft.com/en-us/rest/api/servicebus/update-queue.
        :type queue_description: ~azure.servicebus.management.QueueDescription
        :rtype: ~azure.servicebus.management.QueueDescription
        """

        if not isinstance(queue_description, QueueDescription):
            raise TypeError("queue_description must be of type QueueDescription")

        internal_description = queue_description._to_internal_entity()
        to_update = copy(internal_description)  # pylint:disable=protected-access

        for attr in QUEUE_DESCRIPTION_SERIALIZE_ATTRIBUTES:
            setattr(to_update, attr, getattr(internal_description, attr, None))
        to_update.default_message_time_to_live = avoid_timedelta_overflow(to_update.default_message_time_to_live)
        to_update.auto_delete_on_idle = avoid_timedelta_overflow(to_update.auto_delete_on_idle)

        create_entity_body = CreateQueueBody(
            content=CreateQueueBodyContent(
                queue_description=to_update,
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        with _handle_response_error():
            try:
                entry_ele = cast(
                    ElementTree,
                    self._impl.entity.put(
                        queue_description.queue_name,  # type: ignore
                        request_body,
                        api_version=constants.API_VERSION,
                        if_match="*",
                        **kwargs
                    )
                )
            except ValidationError:
                # post-hoc try to give a somewhat-justifiable failure reason.
                raise_with_traceback(
                    ValueError,
                    message="queue_description must be a QueueDescription with valid fields, "
                            "including non-empty string queue name")
        entry = QueueDescriptionEntry.deserialize(entry_ele)
        result = QueueDescription._from_internal_entity(entry.content.queue_description)
        result.queue_name = queue_description.queue_name
        return result

    def delete_queue(self, queue_name, **kwargs):
        # type: (str, Any) -> None
        """Delete a queue.

        :param str queue_name: The name of the queue.
        :rtype: None
        """

        if not queue_name:
            raise ValueError("queue_name must not be None or empty")
        with _handle_response_error():
            self._impl.entity.delete(queue_name, api_version=constants.API_VERSION, **kwargs)

    def list_queues(self, **kwargs):
        # type: (Any) -> ItemPaged[QueueDescription]
        """List the queues of a ServiceBus namespace.

        :keyword int start_index: skip this number of queues.
        :keyword int max_count: return at most this number of queues if there are more than this number in
         the ServiceBus namespace.
        :rtype: List[~azure.servicebus.management.QueueDescription]
        """

        def entry_to_qd(entry):
            qd = QueueDescription._from_internal_entity(entry.content.queue_description)
            qd.queue_name = entry.title
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
        """List the runtime info of the queues in a ServiceBus namespace.

        :keyword int start_index: skip this number of queues.
        :keyword int max_count: return at most this number of queues if there are more than this number in
         the ServiceBus namespace.
        :rtype: List[~azure.servicebus.management.QueueRuntimeInfo]
        """

        def entry_to_qr(entry):
            qd = QueueRuntimeInfo._from_internal_entity(entry.content.queue_description)
            qd.queue_name = entry.title
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
        """Get a TopicDescription.

        :param str queue_name: The name of the queue.
        :rtype: ~azure.servicebus.management.TopicDescription
        """
        entry_ele = self._get_entity_element(topic_name, **kwargs)
        entry = TopicDescriptionEntry.deserialize(entry_ele)
        topic_description = entry.content.topic_description
        # TODO: wrap it in external TopicDescription and set name
        return topic_description

    def get_topic_runtime_info(self, topic_name, **kwargs):
        pass

    def create_topic(self, topic, **kwargs):
        pass

    def update_topic(self, topic, **kwargs):
        pass

    def delete_topic(self, topic_name, **kwargs):
        pass

    def list_topics(self, topic_name, **kwargs):
        pass

    def list_topics_runtime_info(self, topic_name, **kwargs):
        pass

    def get_subscription(self, topic_name, subscription_name, **kwargs):
        self._impl.subscription.get()
        entry_ele = self._get_subscription_element("{}/Subscriptions/{}".format(topic_name, subscription_name), **kwargs)
        subscription = SubscriptionDescriptionEntry.deserialize(entry_ele)
        print(subscription)

    def get_subscription_runtime_info(self, topic_name, subscription_name, **kwargs):
        pass

    def create_subscriptiono(self, subscription, **kwargs):
        pass

    def update_subscription(self, subscription, **kwargs):
        pass

    def delete_subscription(self, topic_name, subscription_name, **kwargs):
        pass

    def list_subscriptions(self, topic_name, **kwargs):
        def entry_to_rule(entry):
            rule = entry.content.subscription_description
            # TODO: convert to external SubscriptionDescription
            return rule

        extract_data = functools.partial(
            extract_data_template, SubscriptionDescriptionFeed, entry_to_rule
        )
        get_next = functools.partial(
            get_next_template, functools.partial(self._impl.list_subscriptions, topic_name), **kwargs
        )
        return ItemPaged(
            get_next, extract_data)

    def list_subscriptions_runtime_info(self, topic_name, **kwargs):
        pass

    def get_rule(self, topic_name, subscription_name, rule_name, **kwargs):
        entry_ele = self._get_rule_element(topic_name, subscription_name, rule_name, **kwargs)
        rule = RuleDescriptionEntry.deserialize(entry_ele)
        print(rule)

    def get_rule_runtime_info(self, topic_name, subscription_name, rule_name, **kwargs):
        pass

    def create_rule(self, rule, **kwargs):
        pass

    def update_rule(self, rule, **kwargs):
        pass

    def delete_rule(self, topic_name, subscription_name, rule_name, **kwargs):
        pass

    def list_rules(self, topic_name, subscription_name, **kwargs):
        def entry_to_rule(entry):
            rule = entry.content.rule_description
            # TODO: convert to external RuleDescription
            return rule

        extract_data = functools.partial(
            extract_data_template, RuleDescriptionFeed, entry_to_rule
        )
        get_next = functools.partial(
            get_next_template, functools.partial(self._impl.list_rules, topic_name, subscription_name), **kwargs
        )
        return ItemPaged(
            get_next, extract_data)

    def list_rules_runtime_info(self, topic_name, subscription_name, **kwargs):
        pass

    def get_management_properties(self):
        pass

    # TODO: discuss whether we need API xxx_exists in Python. It's easy to tell by get_xxx(), which
    # raises ResourceNotExists