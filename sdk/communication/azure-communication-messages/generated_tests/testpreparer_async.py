# coding=utf-8
from azure.communication.messages.aio import MessageTemplateClient, NotificationMessagesClient
from devtools_testutils import AzureRecordedTestCase


class NotificationMessagesClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(NotificationMessagesClient, is_async=True)
        return self.create_client_from_credential(
            NotificationMessagesClient,
            credential=credential,
            endpoint=endpoint,
        )


class MessageTemplateClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(MessageTemplateClient, is_async=True)
        return self.create_client_from_credential(
            MessageTemplateClient,
            credential=credential,
            endpoint=endpoint,
        )
