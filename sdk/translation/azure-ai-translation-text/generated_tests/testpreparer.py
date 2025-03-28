# coding=utf-8
from azure.ai.translation.text import TextTranslationClient
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
import functools


class TextTranslationClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(TextTranslationClient)
        return self.create_client_from_credential(
            TextTranslationClient,
            credential=credential,
            endpoint=endpoint,
        )


TextTranslationPreparer = functools.partial(
    PowerShellPreparer, "texttranslation", texttranslation_endpoint="https://fake_texttranslation_endpoint.com"
)
