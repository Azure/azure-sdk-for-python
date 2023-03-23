import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem

TextTranslationPreparer = functools.partial(
    PowerShellPreparer, 'texttranslation',
    texttranslation_endpoint="fake.cognitive.microsofttranslator.com",
    texttranslation_apiKey="fakeapikey1234",
    texttranslation_region="fakeregion",
)

class TextTranslationTest(AzureRecordedTestCase):    
    def create_client(self, endpoint, apiKey, region):        
        credential = TranslatorCredential(apiKey, region)        
        client = self.create_client_from_credential(TextTranslationClient, credential=credential, endpoint=endpoint)
        return client   
    
# Write your tests
class TestTextTranslation(TextTranslationTest):   

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_translation_basic(self, texttranslation_endpoint, texttranslation_apiKey, texttranslation_region):
        client = self.create_client(texttranslation_endpoint, texttranslation_apiKey, texttranslation_region)
        assert client is not None