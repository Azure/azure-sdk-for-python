# coding=utf-8
from azure.eventgrid.aio import EventGridConsumerClient, EventGridPublisherClient
from devtools_testutils import AzureRecordedTestCase


class EventGridPublisherClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(EventGridPublisherClient, is_async=True)
        return self.create_client_from_credential(
            EventGridPublisherClient,
            credential=credential,
            endpoint=endpoint,
        )


class EventGridConsumerClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(EventGridConsumerClient, is_async=True)
        return self.create_client_from_credential(
            EventGridConsumerClient,
            credential=credential,
            endpoint=endpoint,
        )
