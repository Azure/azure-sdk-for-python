# coding=utf-8
from azure.ai.contentsafety.aio import BlocklistClient, ContentSafetyClient
from devtools_testutils import AzureRecordedTestCase


class ContentSafetyClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(ContentSafetyClient, is_async=True)
        return self.create_client_from_credential(
            ContentSafetyClient,
            credential=credential,
            endpoint=endpoint,
        )


class BlocklistClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(BlocklistClient, is_async=True)
        return self.create_client_from_credential(
            BlocklistClient,
            credential=credential,
            endpoint=endpoint,
        )
