# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import recorded_by_proxy
from azure.ai.translation.text.models import InputTextItem
from preparer import TextTranslationPreparer
from test_helper import TestHelper
from testcase import TextTranslationTest
import asyncio

class TestTransliterationAsync(TextTranslationTest, TestHelper):

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_transliteration(self, **kwargs):
        async def test_transliteration_async(**kwargs):
            endpoint = kwargs.get("text_translation_endpoint")
            apikey = kwargs.get("text_translation_apikey")
            region = kwargs.get("text_translation_region")
            client = self.create_async_client(endpoint, apikey, region)

            input_text_elements = [InputTextItem(text="这里怎么一回事?")]
            response = await client.transliterate(
                content=input_text_elements, language="zh-Hans", from_script="Hans", to_script="Latn")

            assert response is not None
            assert response[0].text is not None
        asyncio.run(test_transliteration_async(**kwargs))

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_multiple_inputs(self, **kwargs):
        async def test_multiple_inputs_async(**kwargs):
            endpoint = kwargs.get("text_translation_endpoint")
            apikey = kwargs.get("text_translation_apikey")
            region = kwargs.get("text_translation_region")
            client = self.create_async_client(endpoint, apikey, region)

            input_text_elements = [InputTextItem(
                text="यहएककसौटीहैयहएककसौटीहै"), InputTextItem(text="यहएककसौटीहै")]
            response = await client.transliterate(
                content=input_text_elements, language="hi", from_script="Deva", to_script="Latn")

            assert response is not None
            assert response[0].text is not None
            assert response[1].text is not None
        asyncio.run(test_multiple_inputs_async(**kwargs))

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_edit_distance(self, **kwargs):
        async def test_edit_distance_async(**kwargs):
            endpoint = kwargs.get("text_translation_endpoint")
            apikey = kwargs.get("text_translation_apikey")
            region = kwargs.get("text_translation_region")
            client = self.create_async_client(endpoint, apikey, region)

            input_text_elements = [InputTextItem(text="gujarat"), InputTextItem(
                text="hadman"), InputTextItem(text="hukkabar")]
            response = await client.transliterate(
                content=input_text_elements, language="gu", from_script="Latn", to_script="Gujr")

            assert response is not None
            assert response[0].text is not None
            assert response[1].text is not None
            assert response[2].text is not None

            expected_texts = ["ગુજરાત", "હદમાં", "હુક્કાબાર"]
            edit_distance_value = 0
            for i, expected_text in enumerate(expected_texts):
                edit_distance_value = edit_distance_value + \
                    self.edit_distance(expected_text, response[i].text)
            assert edit_distance_value < 6
        asyncio.run(test_edit_distance_async(**kwargs))
