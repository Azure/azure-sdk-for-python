# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils.aio import recorded_by_proxy_async
from preparer import TextTranslationPreparer
from test_helper import TestHelper
from testcase import TextTranslationTest


class TestTransliterationAsync(TextTranslationTest, TestHelper):
    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_transliteration(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_async_client(endpoint, apikey, region)

        input_text_elements = ["这里怎么一回事?"]
        async with client:
            response = await client.transliterate(
                body=input_text_elements,
                language="zh-Hans",
                from_script="Hans",
                to_script="Latn",
            )

        assert response is not None
        assert response[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_multiple_inputs(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_async_client(endpoint, apikey, region)

        input_text_elements = ["यहएककसौटीहैयहएककसौटीहै", "यहएककसौटीहै"]
        async with client:
            response = await client.transliterate(
                body=input_text_elements,
                language="hi",
                from_script="Deva",
                to_script="Latn",
            )

        assert response is not None
        assert response[0].text is not None
        assert response[1].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_edit_distance(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_async_client(endpoint, apikey, region)

        input_text_elements = [
            "gujarat",
            "hadman",
            "hukkabar",
        ]
        async with client:
            response = await client.transliterate(
                body=input_text_elements,
                language="gu",
                from_script="Latn",
                to_script="Gujr",
            )

        assert response is not None
        assert response[0].text is not None
        assert response[1].text is not None
        assert response[2].text is not None

        expected_texts = ["ગુજરાત", "હદમાં", "હુક્કાબાર"]
        edit_distance_value = 0
        for i, expected_text in enumerate(expected_texts):
            edit_distance_value = edit_distance_value + self.edit_distance(expected_text, response[i].text)
        assert edit_distance_value < 6
