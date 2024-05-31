# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from devtools_testutils import recorded_by_proxy
from azure.ai.translation.text.models import TextType, ProfanityAction, ProfanityMarker
from preparer import TextTranslationPreparer
from testcase import TextTranslationTest


class TestTranslation(TextTranslationTest):
    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_translate(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_client(endpoint, apikey, region)

        from_language = "es"
        to_language = ["cs"]
        input_text_elements = ["Hola mundo"]
        response = client.translate(body=input_text_elements, to_language=to_language, from_language=from_language)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].translations[0].to == "cs"
        assert response[0].translations[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_autodetect(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_client(endpoint, apikey, region)

        to_language = ["cs"]
        input_text_elements = ["This is a test."]
        response = client.translate(body=input_text_elements, to_language=to_language)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1
        assert response[0].translations[0].to == "cs"
        assert response[0].translations[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_no_translate_tag(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_client(endpoint, apikey, region)

        from_language = "zh-chs"
        to_language = ["en"]
        input_text_elements = ["<span class=notranslate>今天是怎么回事是</span>非常可怕的"]
        response = client.translate(
            body=input_text_elements,
            to_language=to_language,
            from_language=from_language,
            text_type=TextType.HTML,
        )

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert "今天是怎么回事是" in response[0].translations[0].text

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_dictionary_tag(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_client(endpoint, apikey, region)

        from_language = "en"
        to_language = ["es"]
        input_text_elements = [
            'The word < mstrans:dictionary translation ="wordomatic">wordomatic</mstrans:dictionary> is a dictionary entry.'
        ]
        response = client.translate(body=input_text_elements, to_language=to_language, from_language=from_language)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].translations[0].to == "es"
        assert "wordomatic" in response[0].translations[0].text

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_transliteration(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_client(endpoint, apikey, region)

        from_language = "ar"
        to_language = ["zh-Hans"]
        input_text_elements = ["hudha akhtabar."]
        response = client.translate(
            body=input_text_elements,
            to_language=to_language,
            from_language=from_language,
            from_script="Latn",
            to_script="Latn",
        )

        assert len(response) == 1
        assert response[0].source_text is not None
        assert len(response[0].translations) == 1
        assert response[0].translations[0].to == "zh-Hans"
        assert response[0].translations[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_from_to_latin(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_client(endpoint, apikey, region)

        from_language = "hi"
        to_language = ["ta"]
        input_text_elements = ["ap kaise ho"]
        response = client.translate(
            body=input_text_elements,
            to_language=to_language,
            from_language=from_language,
            from_script="Latn",
            to_script="Latn",
        )

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].translations[0].text is not None
        assert "eppadi irukkiraai?" in response[0].translations[0].transliteration.text

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_multiple_input(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_client(endpoint, apikey, region)

        to_language = ["cs"]
        input_text_elements = [
            "This is a test.",
            "Esto es una prueba.",
            "Dies ist ein Test.",
        ]
        response = client.translate(body=input_text_elements, to_language=to_language)

        assert len(response) == 3
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
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_client(endpoint, apikey, region)

        to_language = ["cs", "es", "de"]
        input_text_elements = ["This is a test."]
        response = client.translate(body=input_text_elements, to_language=to_language)

        assert len(response) == 1
        assert len(response[0].translations) == 3
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1
        assert response[0].translations[0].text is not None
        assert response[0].translations[1].text is not None
        assert response[0].translations[2].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_different_texttypes(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_client(endpoint, apikey, region)

        to_language = ["cs"]
        input_text_elements = ["<html><body>This <b>is</b> a test.</body></html>"]
        response = client.translate(body=input_text_elements, to_language=to_language, text_type=TextType.HTML)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_profanity(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_client(endpoint, apikey, region)

        to_language = ["zh-cn"]
        input_text_elements = ["shit this is fucking crazy"]
        response = client.translate(
            body=input_text_elements,
            to_language=to_language,
            profanity_action=ProfanityAction.MARKED,
            profanity_marker=ProfanityMarker.ASTERISK,
        )

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1
        assert "***" in response[0].translations[0].text

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_alignment(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_client(endpoint, apikey, region)

        to_language = ["cs"]
        input_text_elements = ["It is a beautiful morning"]
        response = client.translate(body=input_text_elements, to_language=to_language, include_alignment=True)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1
        assert response[0].translations[0].alignment.proj is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_sentence_length(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_client(endpoint, apikey, region)

        to_language = ["fr"]
        input_text_elements = [
            "La réponse se trouve dans la traduction automatique. La meilleure technologie de traduction automatique ne peut pas toujours fournir des traductions adaptées à un site ou des utilisateurs comme un être humain. Il suffit de copier et coller un extrait de code n'importe où."
        ]
        response = client.translate(body=input_text_elements, to_language=to_language, include_sentence_length=True)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "fr"
        assert response[0].detected_language.score == 1
        assert len(response[0].translations[0].sent_len.src_sent_len) == 3
        assert len(response[0].translations[0].sent_len.trans_sent_len) == 3

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_custom_endpoint(self, **kwargs):
        endpoint = kwargs.get("translation_text_custom_endpoint")
        apikey = kwargs.get("translation_text_custom_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_client(endpoint, apikey, region)

        to_language = ["fr"]
        input_text_elements = ["It is a beautiful morning"]
        response = client.translate(body=input_text_elements, to_language=to_language)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1

    @pytest.mark.live_test_only
    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_token(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        apikey = kwargs.get("translation_text_apikey")
        region = kwargs.get("translation_text_region")
        client = self.create_client_token(endpoint, apikey, region)

        to_language = ["cs"]
        input_text_elements = ["This is a test."]
        response = client.translate(body=input_text_elements, to_language=to_language)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1

    @pytest.mark.skip
    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_translate_aad(self, **kwargs):
        aadRegion = "westus2"
        aadResourceId = kwargs.get("translation_text_resource_id")
        token_credential = self.get_mt_credential(False)
        client = self.create_text_translation_client_with_aad(token_credential, aadRegion, aadResourceId)

        from_language = "es"
        to_language = ["cs"]
        input_text_elements = ["Hola mundo"]
        response = client.translate(body=input_text_elements, to_language=to_language, from_language=from_language)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].translations[0].to == "cs"
        assert response[0].translations[0].text is not None
