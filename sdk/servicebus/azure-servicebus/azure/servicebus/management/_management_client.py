# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from copy import copy
from contextlib import contextmanager
from typing import TYPE_CHECKING, Dict, Any, Union, List, cast, Tuple
from xml.etree.ElementTree import ElementTree, Element

import six
from msrest.exceptions import ValidationError
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError, raise_with_traceback
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


if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # pylint:disable=ungrouped-imports


@contextmanager
def _handle_response_error():
    try:
        yield
    except HttpResponseError as response_error:
        try:
            new_response_error = HttpResponseError(
                message=response_error.model.detail,
                response=response_error.response,
                model=response_error.model
            )
        except AttributeError:
            new_response_error = response_error
        raise new_response_error


def _convert_xml_to_object(queue_name, et):
    # type: (str, Union[Element, ElementTree]) -> InternalQueueDescription
    content_ele = cast(ElementTree, et).find(constants.CONTENT_TAG)
    if not content_ele:
        raise ResourceNotFoundError("Queue '{}' does not exist".format(queue_name))
    qc_ele = content_ele.find(constants.QUEUE_DESCRIPTION_TAG)
    obj = InternalQueueDescription.deserialize(qc_ele)

    return obj


class ServiceBusManagementClient:
    """Use this client to create, update, list, and delete resources of a ServiceBus namespace

    :param str fully_qualified_namespace:
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
    def from_connection_string(cls, connection_string, **kwargs):
        # type: (str, Any) -> ServiceBusManagementClient
        """Create a client from connection string

        :param str connection_string: The connection string of the Service Bus Namespace
        """
        endpoint, shared_access_key_name, shared_access_key, _ = parse_conn_str(connection_string)
        if "//" in endpoint:
            endpoint = endpoint[endpoint.index("//")+2:]
        return cls(endpoint, ServiceBusSharedKeyCredential(shared_access_key_name, shared_access_key), **kwargs)

    def _get_queue_object(self, queue_name, **kwargs):
        # type: (str, Any) -> InternalQueueDescription

        if not queue_name:
            raise ValueError("queue_name must be a non-empty str")

        with _handle_response_error():
            et = cast(
                ElementTree,
                self._impl.queue.get(queue_name, enrich=False, api_version=constants.API_VERSION, **kwargs)
            )
        return _convert_xml_to_object(queue_name, et)

    def _list_queues(self, skip, max_count, **kwargs):
        # type: (int, int, Any) -> List[Tuple[str, InternalQueueDescription]]
        with _handle_response_error():
            et = cast(
                ElementTree,
                self._impl.list_entities(
                    entity_type=constants.ENTITY_TYPE_QUEUES, skip=skip, top=max_count,
                    api_version=constants.API_VERSION, **kwargs
                )
            )
        entries = et.findall(constants.ENTRY_TAG)
        queues = []
        for entry in entries:
            entity_name = entry.find(constants.TITLE_TAG).text  # type: ignore
            internal_object = _convert_xml_to_object(
                entity_name,   # type: ignore
                cast(Element, entry)
            )
            queues.append((entity_name, internal_object))
        return queues   # type: ignore

    def get_queue(self, queue_name, **kwargs):
        # type: (str, Any) -> QueueDescription
        """Get a QueueDescription

        :param str queue_name: The name of the queue
        """
        queue_description = QueueDescription._from_internal_entity(  # pylint:disable=protected-access
            self._get_queue_object(queue_name, **kwargs)
        )
        queue_description.queue_name = queue_name
        return queue_description

    def get_queue_runtime_info(self, queue_name, **kwargs):
        # type: (str, Any) -> QueueRuntimeInfo
        """Get the runtime information of a queue

        :param str queue_name: The name of the queue
        """
        runtime_info = QueueRuntimeInfo._from_internal_entity(  # pylint:disable=protected-access
            self._get_queue_object(queue_name, **kwargs)
        )
        runtime_info.queue_name = queue_name
        return runtime_info

    def create_queue(self, queue, **kwargs):
        # type: (Union[str, QueueDescription], Any) -> QueueDescription
        """Create a queue

        :param queue: The queue name or a `QueueDescription` instance. When it's a str, it will be the name
         of the created queue. Other properties of the created queue will have default values decided by the
         ServiceBus. Use a `QueueDesceiption` if you want to set queue properties other than the queue name.
        :type queue: Union[str, QueueDescription].
        :returns: ~azure.servicebus.management.QueueDescription returned from ServiceBus.
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
                et = cast(
                    ElementTree,
                    self._impl.queue.put(
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

        result = QueueDescription._from_internal_entity(  # pylint:disable=protected-access
                _convert_xml_to_object(queue_name, et)
        )
        result.queue_name = queue_name
        return result

    def update_queue(self, queue_description, **kwargs):
        # type: (QueueDescription, Any) -> QueueDescription
        """Update a queue

        :param queue_description: The properties of this `QueueDescription` will be applied to the queue in
         ServiceBus. Only a portion of properties can be updated.
         Refer to https://docs.microsoft.com/en-us/rest/api/servicebus/update-queue.
        :type queue_description: ~azure.servicebus.management.QueueDescription
        :returns: ~azure.servicebus.management.QueueDescription returned from ServiceBus.
        """

        if not isinstance(queue_description, QueueDescription):
            raise TypeError("queue_description must be of type QueueDescription")

        to_update = copy(queue_description._to_internal_entity())  # pylint:disable=protected-access

        for attr in QUEUE_DESCRIPTION_SERIALIZE_ATTRIBUTES:
            setattr(to_update, attr, getattr(queue_description, attr, None))
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
                et = cast(
                    ElementTree,
                    self._impl.queue.put(
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
        result = QueueDescription._from_internal_entity(  # pylint:disable=protected-access
            _convert_xml_to_object(queue_description.queue_name, et)
        )
        result.queue_name = queue_description.queue_name
        return result

    def delete_queue(self, queue_name, **kwargs):
        # type: (str, Any) -> None
        """Delete a queue

        :param str queue_name: The name of the queue
        """

        if not queue_name:
            raise ValueError("queue_name must not be None or empty")
        with _handle_response_error():
            self._impl.queue.delete(queue_name, api_version=constants.API_VERSION, **kwargs)

    def list_queues(self, skip=0, max_count=100, **kwargs):
        # type: (int, int, Any) -> List[QueueDescription]
        """List the queues of a ServiceBus namespace

        :param int skip: skip this number of queues
        :param int max_count: return at most this number of queues if there are more than this number in
         the ServiceBus namespace
        """
        result = []  # type: List[QueueDescription]
        internal_queues = self._list_queues(skip, max_count, **kwargs)
        for queue_name, internal_queue in internal_queues:
            qd = QueueDescription._from_internal_entity(internal_queue)  # pylint:disable=protected-access
            qd.queue_name = queue_name
            result.append(qd)
        return result

    def list_queues_runtime_info(self, skip=0, max_count=100, **kwargs):
        # type: (int, int, Any) -> List[QueueRuntimeInfo]
        """List the queues runtime info of a ServiceBus namespace

        :param int skip: skip this number of queues
        :param int max_count: return at most this number of queues if there are more than this number in
         the ServiceBus namespace
        """
        result = []  # type: List[QueueRuntimeInfo]
        internal_queues = self._list_queues(skip, max_count, **kwargs)
        for queue_name, internal_queue in internal_queues:
            runtime_info = QueueRuntimeInfo._from_internal_entity(internal_queue)  # pylint:disable=protected-access
            runtime_info.queue_name = queue_name
            result.append(runtime_info)
        return result
