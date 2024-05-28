# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils.aio import recorded_by_proxy_async
from preparer import TextTranslationPreparer
from testcase import TextTranslationTest


class TestBreakSentenceAsync(TextTranslationTest):
    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_autodetect(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_async_client(endpoint, apikey, region)
        input_text_elements = ["Hello world"]

        async with client:
            response = await client.find_sentence_boundaries(body=input_text_elements)
        assert response is not None
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score > 0.9
        assert response[0].sent_len[0] == 11

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_with_language(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_async_client(endpoint, apikey, region)

        input_text_elements = [
            "รวบรวมแผ่นคำตอบ ระยะเวลาของโครงการ วิธีเลือกชายในฝัน หมายเลขซีเรียลของระเบียน วันที่สิ้นสุดของโครงการเมื่อเสร็จสมบูรณ์ ปีที่มีการรวบรวม ทุกคนมีวัฒนธรรมและวิธีคิดเหมือนกัน ได้รับโทษจำคุกตลอดชีวิตใน ฉันลดได้ถึง 55 ปอนด์ได้อย่างไร  ฉันคิดว่าใครๆ ก็ต้องการกำหนดเมนูอาหารส่วนบุคคล"
        ]

        async with client:
            response = await client.find_sentence_boundaries(body=input_text_elements, language="th")
        assert response is not None
        expected_lengths = [78, 41, 110, 46]
        for i, expected_length in enumerate(expected_lengths):
            assert expected_length == response[0].sent_len[i]

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_with_language_script(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_async_client(endpoint, apikey, region)

        input_text_elements = ["zhè shì gè cè shì。"]

        async with client:
            response = await client.find_sentence_boundaries(
                body=input_text_elements, language="zh-Hans", script="Latn"
            )
        assert response is not None
        assert response[0].sent_len[0] == 18

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_with_multiple_languages(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_async_client(endpoint, apikey, region)

        input_text_elements = [
            "hello world",
            "العالم هو مكان مثير جدا للاهتمام",
        ]

        async with client:
            response = await client.find_sentence_boundaries(body=input_text_elements)
        assert response is not None
        assert response[0].detected_language.language == "en"
        assert response[1].detected_language.language == "ar"
        assert response[0].sent_len[0] == 11
        assert response[1].sent_len[0] == 32
