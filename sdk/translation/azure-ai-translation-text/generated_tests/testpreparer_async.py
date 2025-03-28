# coding=utf-8
from azure.ai.translation.text.aio import TextTranslationClient
from devtools_testutils import AzureRecordedTestCase


class TextTranslationClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(TextTranslationClient, is_async=True)
        return self.create_client_from_credential(
            TextTranslationClient,
            credential=credential,
            endpoint=endpoint,
        )
