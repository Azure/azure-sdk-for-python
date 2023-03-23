import functools
import pytest

from devtools_testutils import recorded_by_proxy
from tests.test_translate import TextTranslationPreparer, TextTranslationTest
    
# Write your tests
class TestGetLanguages(TextTranslationTest): 
    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_translation_getLanguages(self, **kwargs):
        endpoint = kwargs.get("texttranslation_endpoint")
        apiKey = kwargs.get("texttranslation_apiKey")
        region = kwargs.get("texttranslation_region")

        client = self.create_client(endpoint, apiKey, region)
        response = client.get_languages()
        assert len(response.translation) > 0