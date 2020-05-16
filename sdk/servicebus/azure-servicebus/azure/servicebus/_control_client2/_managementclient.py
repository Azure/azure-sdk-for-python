from typing import TYPE_CHECKING, Dict, Any, Union

from azure.servicebus import ServiceBusSharedKeyCredential
from azure.servicebus._control_client2._generated.models import CreateQueueBody, CreateQueueBodyContent, \
    QueueDescription, CreateQueueBodyAuthor

from ._generated._service_bus_management_client import ServiceBusManagementClient as ServiceBusManagementClientImpl

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
        self._impl = ServiceBusManagementClientImpl(endpoint=fully_qualified_namespace)

    @classmethod
    def from_connection_string(cls, connection_string):
        # type: (str) -> ServiceBusManagementClient
        """

        :param str connection_string:
        :return:
        """

    def create_queue(self, queue_name=None, queue_description=None):
        # type: (str, "QueueDescription") -> None
        """Create a queue"""
        sas_token = self._credential.get_token(self._endpoint + "/" + queue_name)
        custom_headers = {"Authorization": sas_token.token.decode("utf-8")}
        body = CreateQueueBody(author=CreateQueueBodyAuthor(), content=CreateQueueBodyContent(type="application/xml", queue_description=QueueDescription()))
        response = self._impl.queue.create(queue_name, body, headers=custom_headers)
        print(type(response), response)

    def create_rule(self, topic_path, subscription_name, rule_description):
        # type: (str, str, "RuleDescription") -> None
        """

        :param topic_path:
        :param subscription_name:
        :param rule_description:
        :return:
        """

    def create_subscription(self, topic_path, subscription_name, subscription_description, default_rule):
        # type: (str, str, "SubscriptionDescription", "RuleDescription") -> None
        """

        :param topic_path:
        :param subscription_name:
        :param subscription_description:
        :param default_rule:
        :return:
        """
