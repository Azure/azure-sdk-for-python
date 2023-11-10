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
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_async_client(endpoint, apikey, region)

        source_language = "en"
        target_language = "es"
        input_text_elements = [DictionaryExampleTextItem(text="fly", translation="volar")]

        async with client:
            response = await client.lookup_dictionary_examples(
                request_body=input_text_elements, from_parameter=source_language, to=target_language
            )
        assert response is not None
        assert response[0].normalized_source == "fly"
        assert response[0].normalized_target == "volar"

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_multiple_input_elements(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_async_client(endpoint, apikey, region)

        source_language = "en"
        target_language = "es"
        input_text_elements = [
            DictionaryExampleTextItem(text="fly", translation="volar"),
            DictionaryExampleTextItem(text="beef", translation="came"),
        ]

        async with client:
            response = await client.lookup_dictionary_examples(
                request_body=input_text_elements, from_parameter=source_language, to=target_language
            )
        assert response is not None
        assert len(response) == 2
        assert response[0].normalized_source == "fly"
        assert response[0].normalized_target == "volar"
        assert response[1].normalized_source == "beef"
        assert response[1].normalized_target == "came"
