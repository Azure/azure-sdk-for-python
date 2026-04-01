# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import recorded_by_proxy
from preparer import TextTranslationPreparer
from test_helper import TestHelper
from testcase import TextTranslationTest


class TestTransliteration(TextTranslationTest, TestHelper):
    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_transliteration(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        input_text_elements = ["这里怎么一回事?"]
        response = client.transliterate(
            body=input_text_elements,
            language="zh-Hans",
            from_script="Hans",
            to_script="Latn",
        )

        assert response is not None
        assert response[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_multiple_inputs(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        input_text_elements = ["यहएककसौटीहैयहएककसौटीहै", "यहएककसौटीहै"]
        response = client.transliterate(
            body=input_text_elements,
            language="hi",
            from_script="Deva",
            to_script="Latn",
        )

        assert response is not None
        assert response[0].text is not None
        assert response[1].text is not None
