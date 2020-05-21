import sys
import inspect
from typing import TYPE_CHECKING, Dict, Any, Union
from xml.etree import ElementTree

from azure.servicebus import ServiceBusSharedKeyCredential
from azure.servicebus._control_client2._generated import models
from azure.servicebus._control_client2._generated.models import CreateEntityBody, CreateEntityBodyContent, \
    QueueDescription
from ._generated._service_bus_management_client import ServiceBusManagementClient as ServiceBusManagementClientImpl

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

# workaround for issue https://github.com/Azure/azure-sdk-for-python/issues/11568
# clsmembers = inspect.getmembers(models, inspect.isclass)
# for _, clazz in clsmembers:
#     if hasattr(clazz, "_xml_map"):
#         ns = clazz._xml_map['ns']
#         if hasattr(clazz, "_attribute_map"):
#             for mps in clazz._attribute_map.values():
#                 if 'xml' not in mps:
#                     mps['xml'] = {'ns': ns}
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
        self._impl = ServiceBusManagementClientImpl(endpoint=fully_qualified_namespace)

    @classmethod
    def from_connection_string(cls, connection_string):
        # type: (str) -> ServiceBusManagementClient
        """

        :param str connection_string:
        :return:
        """

    def get_queue(self, queue_name):
        # type: (str) -> QueueDescription
        sas_token = self._credential.get_token(self._endpoint + "/" + queue_name)
        custom_headers = {"Authorization": sas_token.token.decode("utf-8")}
        et = self._impl.queue.get(queue_name, headers=custom_headers)
        content_ele = et.find("{http://www.w3.org/2005/Atom}content")
        qc_ele = content_ele.find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}QueueDescription")
        qc = QueueDescription.deserialize(qc_ele)
        return qc

    def create_queue(self, queue_name, queue_description=QueueDescription()):
        # type: (str, "QueueDescription") -> QueueDescription
        """Create a queue"""
        sas_token = self._credential.get_token(self._endpoint + "/" + queue_name)
        custom_headers = {"Authorization": sas_token.token.decode("utf-8")}
        create_entity_body = CreateEntityBody(
            content=CreateEntityBodyContent(
                entity=queue_description
            )
        )
        request_body = create_entity_body.serialize(is_xml=True)
        et = self._impl.queue.create(queue_name, request_body, headers=custom_headers)
        content_ele = et.find("{http://www.w3.org/2005/Atom}content")
        qc_ele = content_ele.find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}QueueDescription")
        qc = QueueDescription.deserialize(qc_ele)
        return qc
