# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import recorded_by_proxy, AzureRecordedTestCase, PowerShellPreparer
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from tests.preparer import TextTranslationPreparer
from tests.testcase import TextTranslationTest
    
# Write your tests
class TestTranslation(TextTranslationTest):

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_translator_translate(self, **kwargs):      
        endpoint = kwargs.get("texttranslation_endpoint")
        apikey = kwargs.get("texttranslation_apikey")
        region = kwargs.get("texttranslation_region")
        client = self.create_client(endpoint, apikey, region)

        source_language = "en"
        target_languages = ["cs"]
        input_text_elements = [ InputTextItem(text = "This is a test") ]
        response = client.translate(content = input_text_elements, to = target_languages, from_parameter = source_language)
        
        translation = response[0] if response else None
        if translation:
            for translated_text in translation.translations:
                assert translated_text.to == "cs"