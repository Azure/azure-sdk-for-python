# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import recorded_by_proxy
from azure.ai.translation.text.models import InputTextItem
from preparer import TextTranslationPreparer
from testcase import TextTranslationTest

class TestDictionaryLookup(TextTranslationTest):

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_single_input_element(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        source_language = "en"
        target_language = "es"
        input_text_elements = [InputTextItem(text="fly")]

        response = client.lookup_dictionary_entries(
            content=input_text_elements, from_parameter=source_language, to=target_language)
        assert response is not None
        assert response[0].normalized_source == "fly"
        assert response[0].display_source == "fly"

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_multiple_input_elements(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        source_language = "en"
        target_language = "es"
        input_text_elements = [InputTextItem(
            text="fly"), InputTextItem(text="fox")]

        response = client.lookup_dictionary_entries(
            content=input_text_elements, from_parameter=source_language, to=target_language)
        assert response is not None
        assert len(response) == 2
        assert response[0].normalized_source == "fly"
        assert response[0].display_source == "fly"
        assert response[1].normalized_source == "fox"
        assert response[1].display_source == "fox"