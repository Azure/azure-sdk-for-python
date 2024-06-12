# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.translation.text.models import DictionaryExampleTextItem
from preparer import TextTranslationPreparer
from testcase import TextTranslationTest


class TestDictionaryExamplesAsync(TextTranslationTest):
    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_single_input_element(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_async_client(endpoint, apikey, region)

        from_language = "en"
        to_language = "es"
        input_text_elements = [DictionaryExampleTextItem(text="fly", translation="volar")]

        async with client:
            response = await client.lookup_dictionary_examples(
                body=input_text_elements, from_language=from_language, to_language=to_language
            )
        assert response is not None
        assert response[0].normalized_source == "fly"
        assert response[0].normalized_target == "volar"

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_multiple_input_elements(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_async_client(endpoint, apikey, region)

        from_language = "en"
        to_language = "es"
        input_text_elements = [
            DictionaryExampleTextItem(text="fly", translation="volar"),
            DictionaryExampleTextItem(text="beef", translation="came"),
        ]

        async with client:
            response = await client.lookup_dictionary_examples(
                body=input_text_elements, from_language=from_language, to_language=to_language
            )
        assert response is not None
        assert len(response) == 2
        assert response[0].normalized_source == "fly"
        assert response[0].normalized_target == "volar"
        assert response[1].normalized_source == "beef"
        assert response[1].normalized_target == "came"
