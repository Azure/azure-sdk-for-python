import inspect
from typing import TYPE_CHECKING, Dict, Any, Union

from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import HttpLoggingPolicy, DistributedTracingPolicy, ContentDecodePolicy, \
    RequestIdPolicy, BearerTokenCredentialPolicy
from azure.core.pipeline.transport import RequestsTransport
from azure.servicebus import ServiceBusSharedKeyCredential
from azure.servicebus._control_client2._generated import models
from azure.servicebus._control_client2._generated._configuration import ServiceBusManagementClientConfiguration
from azure.servicebus._control_client2._generated.models import CreateEntityBody, CreateEntityBodyContent, \
    QueueDescription
from azure.servicebus._control_client2._shared_key_policy import ServiceBusSharedKeyCredentialPolicy
from .._common.constants import JWT_TOKEN_SCOPE

from .._common.utils import parse_conn_str
from ._generated._service_bus_management_client import ServiceBusManagementClient as ServiceBusManagementClientImpl
from . import constants

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

# workaround for issue https://github.com/Azure/azure-sdk-for-python/issues/11568
clsmembers = inspect.getmembers(models, inspect.isclass)
for _, clazz in clsmembers:
    if hasattr(clazz, "_xml_map"):
        ns = clazz._xml_map['ns']
        if hasattr(clazz, "_attribute_map"):
            for mps in clazz._attribute_map.values():
                if 'xml' not in mps:
                    mps['xml'] = {'ns': ns}
# end of workaround


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
        et = self._impl.queue.get(queue_name, enrich=False, api_version=constants.API_VERSION)
        content_ele = et.find("{http://www.w3.org/2005/Atom}content")
        qc_ele = content_ele.find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}QueueDescription")
        qc = QueueDescription.deserialize(qc_ele)
        return qc

    def create_queue(self, queue_name, queue_description=QueueDescription()):
        # type: (str, "QueueDescription") -> QueueDescription
        """Create a queue"""
        create_entity_body = CreateEntityBody(
            content=CreateEntityBodyContent(
                entity=queue_description
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        et = self._impl.queue.create(queue_name, request_body)
        content_ele = et.find("{http://www.w3.org/2005/Atom}content")
        qc_ele = content_ele.find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}QueueDescription")
        qc = QueueDescription.deserialize(qc_ele)
        return qc
