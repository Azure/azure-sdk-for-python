# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from copy import copy
from typing import TYPE_CHECKING, Dict, Any, Union, List

from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import HttpLoggingPolicy, DistributedTracingPolicy, ContentDecodePolicy, \
    RequestIdPolicy, BearerTokenCredentialPolicy
from azure.core.pipeline.transport import RequestsTransport
from azure.servicebus import ServiceBusSharedKeyCredential
from .._common.constants import JWT_TOKEN_SCOPE
from ._shared_key_policy import ServiceBusSharedKeyCredentialPolicy
from ._generated._configuration import ServiceBusManagementClientConfiguration
from ._generated.models import CreateQueueBody, CreateQueueBodyContent, \
    QueueDescription, QueueRuntimeInfo


from .._common.utils import parse_conn_str
from ._generated._service_bus_management_client import ServiceBusManagementClient as ServiceBusManagementClientImpl
from . import _constants as constants

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class ServiceBusManagementClient:

    def __init__(self, fully_qualified_namespace, credential, **kwargs):
        # type: (str, Union[TokenCredential, ServiceBusSharedKeyCredential], Dict[str, Any]) -> None
        """

        :param fully_qualified_namespace:
        :param kwargs:
        """
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
    def from_connection_string(cls, connection_string):
        # type: (str) -> ServiceBusManagementClient
        """

        :param str connection_string:
        :return:
        """
        endpoint, shared_access_key_name, shared_access_key, _ = parse_conn_str(connection_string)
        if "//" in endpoint:
            endpoint = endpoint[endpoint.index("//")+2:]
        return cls(endpoint, ServiceBusSharedKeyCredential(shared_access_key_name, shared_access_key))

    def get_queue(self, queue_name):
        # type: (str) -> QueueDescription
        et = self._impl.queue.get(
            queue_name,
            enrich=False,
            api_version=constants.API_VERSION, headers={"If-Match": "*"}
        )
        content_ele = et.find(constants.CONTENT_TAG)
        if not content_ele:
            raise ResourceNotFoundError("Queue '{}' does not exist".format(queue_name))
        qc_ele = content_ele.find(constants.QUEUE_DESCRIPTION_TAG)
        qc = QueueDescription.deserialize(qc_ele)
        qc.queue_name = queue_name
        return qc

    def get_queue_metrics(self, queue_name):
        # type: (str) -> QueueRuntimeInfo
        et = self._impl.queue.get(queue_name, enrich=True, api_version=constants.API_VERSION)
        content_ele = et.find(constants.CONTENT_TAG)
        if not content_ele:
            raise ResourceNotFoundError("Queue '{}' does not exist".format(queue_name))
        qc_ele = content_ele.find(constants.QUEUE_DESCRIPTION_TAG)
        qc = QueueRuntimeInfo.deserialize(qc_ele)
        qc.queue_name = queue_name
        return qc

    def create_queue(self, queue):
        # type: (Union[str, QueueDescription]) -> QueueDescription
        """Create a queue"""
        if isinstance(queue, str):
            queue_name = queue
            queue_description = QueueDescription()  # Use an emtpy queue description.
        else:
            queue_name = queue.queue_name
            queue_description = copy(queue)
            queue_description.queue_name = None
            queue_description.created_at = None
            if not queue_description.authorization_rules:
                queue_description.authorization_rules = None
        create_entity_body = CreateQueueBody(
            content=CreateQueueBodyContent(
                queue_description=queue_description,
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        et = self._impl.queue.put(queue_name, request_body, api_version=constants.API_VERSION)
        content_ele = et.find(constants.CONTENT_TAG)
        qc_ele = content_ele.find(constants.QUEUE_DESCRIPTION_TAG)
        qc = QueueDescription.deserialize(qc_ele)
        qc.queue_name = queue_name
        return qc

    def update_queue(self, queue_description):
        # type: (QueueDescription) -> QueueDescription
        """Update a queue"""

        to_update = copy(queue_description)
        to_update.queue_name = None
        create_entity_body = CreateQueueBody(
            content=CreateQueueBodyContent(
                queue_description=to_update
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        et = self._impl.queue.put(
            queue_description.queue_name,
            request_body,
            api_version=constants.API_VERSION,
            if_match="*"
        )
        content_ele = et.find(constants.CONTENT_TAG)
        qc_ele = content_ele.find(
            constants.QUEUE_DESCRIPTION_TAG)
        qc = QueueDescription.deserialize(qc_ele)
        qc.queue_name = queue_description.queue_name
        return qc

    def delete_queue(self, queue_name):
        # type: (str) -> None
        """Create a queue"""
        self._impl.queue.delete(queue_name, api_version=constants.API_VERSION)

    def list_queues(self, skip=0, max_count=100):
        # type: (int, int) -> List[QueueDescription]
        et = self._impl.list_entities(entity_type="queues", skip=skip, top=max_count, api_version=constants.API_VERSION)
        entries = et.findall(constants.ENTRY_TAG)
        queue_descriptions = []
        for entry in entries:
            entity_name = entry.find(constants.TITLE_TAG).text
            print(entity_name)
            qc_ele = entry.find(constants.CONTENT_TAG).find(constants.QUEUE_DESCRIPTION_TAG)
            queue_description = QueueDescription.deserialize(qc_ele)
            queue_description.queue_name = entity_name
            queue_descriptions.append(queue_description)
        return queue_descriptions
