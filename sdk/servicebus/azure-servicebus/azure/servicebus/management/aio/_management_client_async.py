# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from copy import copy
from typing import TYPE_CHECKING, Dict, Any, Union, List, Type, cast
from xml.etree.ElementTree import ElementTree, Element

from msrest.exceptions import ValidationError
from msrest.serialization import Model
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import HttpLoggingPolicy, DistributedTracingPolicy, ContentDecodePolicy, \
    RequestIdPolicy, AsyncBearerTokenCredentialPolicy
from azure.core.pipeline.transport import AioHttpTransport

from ..._common.utils import parse_conn_str
from ..._common.constants import JWT_TOKEN_SCOPE
from ...aio._base_handler_async import ServiceBusSharedKeyCredential
from .._generated.aio._configuration_async import ServiceBusManagementClientConfiguration
from .._generated.models import CreateQueueBody, CreateQueueBodyContent, \
    QueueDescription, QueueRuntimeInfo
from .._generated.aio._service_bus_management_client_async import ServiceBusManagementClient \
    as ServiceBusManagementClientImpl
from .. import _constants as constants
from .._management_client import _convert_xml_to_object, _handle_response_error
from .._model_workaround import QUEUE_UPDATE_SERIALIZE_ATTRIBUTES, avoid_timedelta_overflow
from ._shared_key_policy_async import AsyncServiceBusSharedKeyCredentialPolicy


if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential  # pylint:disable=ungrouped-imports


class ServiceBusManagementClient:
    """Use this client to create, update, list, and delete resources of a ServiceBus namespace

    :param str fully_qualified_namespace:
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
    def from_connection_string(cls, connection_string, **kwargs):
        # type: (str, Any) -> ServiceBusManagementClient
        """Create a client from connection string

        :param str connection_string: The connection string of the Service Bus Namespace
        """
        endpoint, shared_access_key_name, shared_access_key, _ = parse_conn_str(connection_string)
        if "//" in endpoint:
            endpoint = endpoint[endpoint.index("//")+2:]
        return cls(endpoint, ServiceBusSharedKeyCredential(shared_access_key_name, shared_access_key), **kwargs)

    async def _get_queue_object(self, queue_name, clazz):
        # type: (str, Type[Model]) -> Union[QueueDescription, QueueRuntimeInfo]
        if not queue_name:
            raise ValueError("queue_name must be a non-empty str")
        with _handle_response_error():
            et = cast(
                ElementTree,
                await self._impl.queue.get(queue_name, enrich=False, api_version=constants.API_VERSION)
            )
        return _convert_xml_to_object(queue_name, et, clazz)

    async def _list_queues(self, skip, max_count, clazz):
        # type: (int, int, Type[Model]) -> Union[List[QueueDescription], List[QueueRuntimeInfo]]
        with _handle_response_error():
            et = cast(
                ElementTree,
                await self._impl.list_entities(
                    entity_type="queues", skip=skip, top=max_count, api_version=constants.API_VERSION
                )
            )
        entries = et.findall(constants.ENTRY_TAG)
        queues = []
        for entry in entries:
            entity_name = entry.find(constants.TITLE_TAG).text  # type: ignore
            queue_description = _convert_xml_to_object(
                entity_name,   # type: ignore
                cast(Element, entry),
                clazz
            )
            queues.append(queue_description)
        return queues

    async def get_queue(self, queue_name):
        # type: (str) -> QueueDescription
        """Get a QueueDescription

        :param str queue_name: The name of the queue
        """
        return await self._get_queue_object(queue_name, QueueDescription)

    async def get_queue_runtime_info(self, queue_name):
        # type: (str) -> QueueRuntimeInfo
        """Get the runtime information of a queue

        :param str queue_name: The name of the queue
        """
        return await self._get_queue_object(queue_name, QueueRuntimeInfo)

    async def create_queue(self, queue):
        # type: (Union[str, QueueDescription]) -> QueueDescription
        """Create a queue

        :param queue: The queue name or a `QueueDescription` instance. When it's a str, it will be the name
         of the created queue. Other properties of the created queue will have default values decided by the
         ServiceBus. Use a `QueueDesceiption` if you want to set queue properties other than the queue name.
        :type queue: Union[str, QueueDescription].
        :returns: `QueueDescription` returned from ServiceBus.
        """
        try:
            queue_name = queue.queue_name  # type: ignore
            to_create = copy(queue)  # type: ignore
            to_create.queue_name = None  # type: ignore
        except AttributeError:
            queue_name = queue  # type: ignore
            to_create = QueueDescription()  # Use an empty queue description.

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
                    await self._impl.queue.put(
                        queue_name, request_body, api_version=constants.API_VERSION  # type: ignore
                    )
                )
        except ValidationError as e:
            # post-hoc try to give a somewhat-justifiable failure reason.
            if isinstance(queue, str) or (isinstance(queue, QueueDescription) and isinstance(queue.queue_name, str)):
                raise ValueError("queue must be a non-empty str or a QueueDescription with non-empty str queue_name", e)
            raise TypeError("queue must be a non-empty str or a QueueDescription with non-empty str queue_name", e)

        return _convert_xml_to_object(queue_name, et, QueueDescription)  # type: ignore

    async def update_queue(self, queue_description):
        # type: (QueueDescription) -> QueueDescription
        """Update a queue
        :param queue_description: The properties of this `QueueDescription` will be applied to the queue in
         ServiceBus. Only a portion of properties can be updated.
         Refer to https://docs.microsoft.com/en-us/rest/api/servicebus/update-queue.
        :type queue_description: ~azure.servicebus.management.QueueDescription
        :returns: ~azure.servicebus.management.QueueDescription returned from ServiceBus.
        """

        if not queue_description.queue_name:
            raise ValueError("queue_description must have a non-empty queue_name")

        to_update = QueueDescription()

        for attr in QUEUE_UPDATE_SERIALIZE_ATTRIBUTES:
            setattr(to_update, attr, getattr(queue_description, attr, None))
        to_update.default_message_time_to_live = avoid_timedelta_overflow(to_update.default_message_time_to_live)
        to_update.auto_delete_on_idle = avoid_timedelta_overflow(to_update.auto_delete_on_idle)

        create_entity_body = CreateQueueBody(
            content=CreateQueueBodyContent(
                queue_description=to_update
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        with _handle_response_error():
            et = cast(
                ElementTree,
                await self._impl.queue.put(
                    queue_description.queue_name, request_body, api_version=constants.API_VERSION, if_match="*"
                )
            )
        return _convert_xml_to_object(queue_description.queue_name, et, QueueDescription)

    async def delete_queue(self, queue_name):
        # type: (str) -> None
        """Delete a queue

        :param str queue_name: The name of the queue
        """

        if not queue_name:
            raise ValueError("queue_name must not be None or empty")
        with _handle_response_error():
            await self._impl.queue.delete(queue_name, api_version=constants.API_VERSION)

    async def list_queues(self, skip=0, max_count=100):
        # type: (int, int) -> List[QueueDescription]
        """List the queues of a ServiceBus namespace

        :param int skip: skip this number of queues
        :param int max_count: return at most this number of queues if there are more than this number in
         the ServiceBus namespace
        """
        return await self._list_queues(skip, max_count, QueueDescription)

    async def list_queues_runtime_info(self, skip=0, max_count=100):
        # type: (int, int) -> List[QueueRuntimeInfo]
        """List the queues runtime info of a ServiceBus namespace

        :param int skip: skip this number of queues
        :param int max_count: return at most this number of queues if there are more than this number in
         the ServiceBus namespace
        """
        return await self._list_queues(skip, max_count, QueueRuntimeInfo)
