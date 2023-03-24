# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import AzureRecordedTestCase
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential

class TextTranslationTest(AzureRecordedTestCase):    
    def create_client(self, endpoint, apikey, region):
        credential = TranslatorCredential(apikey, region) 
        client = TextTranslationClient(endpoint=endpoint, credential=credential)
        return client
    
    def create_getlanguage_client(self, endpoint):
        client = TextTranslationClient(endpoint=endpoint, credential=None)
        return client  