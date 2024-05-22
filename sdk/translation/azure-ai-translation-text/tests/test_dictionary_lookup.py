# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import recorded_by_proxy
from preparer import TextTranslationPreparer
from testcase import TextTranslationTest


class TestDictionaryLookup(TextTranslationTest):
    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_single_input_element(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_client(endpoint, apikey, region)

        from_language = "en"
        to_language = "es"
        input_text_elements = ["fly"]

        response = client.lookup_dictionary_entries(
            body=input_text_elements, from_language=from_language, to_language=to_language
        )
        assert response is not None
        assert response[0].normalized_source == "fly"
        assert response[0].display_source == "fly"

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_multiple_input_elements(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_client(endpoint, apikey, region)

        from_language = "en"
        to_language = "es"
        input_text_elements = ["fly", "fox"]

        response = client.lookup_dictionary_entries(
            body=input_text_elements, from_language=from_language, to_language=to_language
        )
        assert response is not None
        assert len(response) == 2
        assert response[0].normalized_source == "fly"
        assert response[0].display_source == "fly"
        assert response[1].normalized_source == "fox"
        assert response[1].display_source == "fox"
