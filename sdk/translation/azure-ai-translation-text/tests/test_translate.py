import functools
import pytest

from devtools_testutils import recorded_by_proxy, AzureRecordedTestCase, PowerShellPreparer
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem

TextTranslationPreparer = functools.partial(
    PowerShellPreparer, 'texttranslation',
    texttranslation_endpoint="https://fakeEndpoint.cognitive.microsofttranslator.com",
    texttranslation_apiKey="fakeapikey",
    texttranslation_region="fakeregion",
)

class TextTranslationTest(AzureRecordedTestCase):    
    def create_client(self, endpoint, apiKey, region):        
        credential = TranslatorCredential(apiKey, region) 
        client = self.create_client_from_credential(TextTranslationClient, credential=credential, endpoint=endpoint)
        return client   
    
# Write your tests
class TestTranslation(TextTranslationTest): 
    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_translator_translate(self,  **kwargs):
        endpoint = kwargs.get("texttranslation_endpoint")
        apiKey = kwargs.get("texttranslation_apiKey")
        region = kwargs.get("texttranslation_region")
        client = self.create_client(endpoint, apiKey, region)

        source_language = "en"
        target_languages = ["cs"]
        input_text_elements = [ InputTextItem(text = "This is a test") ]
        response = client.translate(content = input_text_elements, to = target_languages, from_parameter = source_language)
        
        translation = response[0] if response else None
        if translation:
            for translated_text in translation.translations:
                assert translated_text.to == "cs"