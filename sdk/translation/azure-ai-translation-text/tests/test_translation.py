# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from devtools_testutils import recorded_by_proxy
from azure.ai.translation.text.models import (
    TranslateInputItem,
    TranslationTarget,
    TextType,
    ProfanityAction,
    ProfanityMarker,
)
from preparer import TextTranslationPreparer
from testcase import TextTranslationTest


class TestTranslation(TextTranslationTest):
    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_translate(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        from_language = "es"
        to_language = ["cs"]
        input_text_elements = ["Hola mundo"]
        response = client.translate(body=input_text_elements, to_language=to_language, from_language=from_language)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].translations[0].language == "cs"
        assert response[0].translations[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_autodetect(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        to_language = ["cs"]
        input_text_elements = ["This is a test."]
        response = client.translate(body=input_text_elements, to_language=to_language)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language is not None
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1
        assert response[0].translations[0].language == "cs"
        assert response[0].translations[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_translate_using_llm(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        input_text_element = TranslateInputItem(
            text="Hola mundo", targets=[TranslationTarget(language="cs", deployment_name="gpt-4o-mini")], language="es"
        )
        response = client.translate(body=[input_text_element])

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].translations[0].language == "cs"
        assert response[0].translations[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_no_translate_tag(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        input_text_element = TranslateInputItem(
            text="<span class=notranslate>今天是怎么回事是</span>非常可怕的",
            targets=[TranslationTarget(language="en")],
            language="zh-chs",
            text_type=TextType.HTML,
        )
        response = client.translate(body=[input_text_element])

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert "今天是怎么回事是" in response[0].translations[0].text

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_transliteration(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        input_text_element = TranslateInputItem(
            text="hudha akhtabar.",
            targets=[TranslationTarget(language="zh-Hans", script="Latn")],
            language="ar",
            script="Latn",
        )
        response = client.translate(body=[input_text_element])

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].translations[0].language == "zh-Hans"
        assert response[0].translations[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_multiple_input(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        to_language = ["cs"]
        input_text_elements = [
            "This is a test.",
            "Esto es una prueba.",
            "Dies ist ein Test.",
        ]
        response = client.translate(body=input_text_elements, to_language=to_language)

        assert len(response) == 3
        assert response[0].detected_language is not None
        assert response[1].detected_language is not None
        assert response[2].detected_language is not None
        assert response[0].detected_language.language == "en"
        assert response[1].detected_language.language == "es"
        assert response[2].detected_language.language == "de"
        assert response[0].detected_language.score == 1
        assert response[1].detected_language.score == 1
        assert response[2].detected_language.score == 1

        assert response[0].translations[0].text is not None
        assert response[1].translations[0].text is not None
        assert response[2].translations[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_multiple_target_languages(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        to_language = ["cs", "es", "de"]
        input_text_element = TranslateInputItem(
            text="This is a test.", targets=[TranslationTarget(language=lang) for lang in to_language]
        )
        response = client.translate(body=[input_text_element])

        assert len(response) == 1
        assert len(response[0].translations) == 3
        assert response[0].detected_language is not None
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1
        assert response[0].translations[0].text is not None
        assert response[0].translations[1].text is not None
        assert response[0].translations[2].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_different_texttypes(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        to_language = ["cs"]
        input_text_element = TranslateInputItem(
            text="<html><body>This <b>is</b> a test.</body></html>",
            targets=[TranslationTarget(language=lang) for lang in to_language],
            text_type=TextType.HTML,
        )
        response = client.translate(body=[input_text_element])

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language is not None
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_profanity(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        input_text_element = TranslateInputItem(
            text="shit this is fucking crazy",
            targets=[
                TranslationTarget(
                    language="zh-cn", profanity_action=ProfanityAction.MARKED, profanity_marker=ProfanityMarker.ASTERISK
                )
            ],
        )
        response = client.translate(body=[input_text_element])

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language is not None
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score > 0.5
        assert (
            "***" in response[0].translations[0].text
        )  # Created bug: https://machinetranslation.visualstudio.com/MachineTranslation/_workitems/edit/164493

    @pytest.mark.live_test_only
    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_token(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client_token(endpoint, apikey, region, "https://api.microsofttranslator.com/")

        to_language = ["cs"]
        input_text_elements = ["This is a test."]
        response = client.translate(body=input_text_elements, to_language=to_language)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language is not None
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1

    @pytest.mark.skip
    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_translate_aad(self, **kwargs):
        aadRegion = "westus2"
        aadResourceId = kwargs.get("text_translation_resource_id")
        token_credential = self.get_mt_credential(False)
        client = self.create_text_translation_client_with_aad(token_credential, aadRegion, aadResourceId)

        from_language = "es"
        to_language = ["cs"]
        input_text_elements = ["Hola mundo"]
        response = client.translate(body=input_text_elements, to_language=to_language, from_language=from_language)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].translations[0].language == "cs"
        assert response[0].translations[0].text is not None

    @pytest.mark.skip
    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_translate_aad_custom(self, **kwargs):
        endpoint = kwargs.get("text_translation_custom_endpoint")
        token_credential = self.get_mt_credential(False)
        client = self.create_text_translation_client_custom_with_aad(token_credential, endpoint=endpoint)

        from_language = "es"
        to_language = ["cs"]
        input_text_elements = ["Hola mundo"]
        response = client.translate(body=input_text_elements, to_language=to_language, from_language=from_language)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].translations[0].language == "cs"
        assert response[0].translations[0].text is not None
