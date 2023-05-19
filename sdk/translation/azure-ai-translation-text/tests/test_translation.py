# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from devtools_testutils import recorded_by_proxy
from azure.ai.translation.text.models import InputTextItem, TextType, ProfanityAction, ProfanityMarker
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

        source_language = "es"
        target_languages = ["cs"]
        input_text_elements = [InputTextItem(text="Hola mundo")]
        response = client.translate(
            content=input_text_elements, to=target_languages, from_parameter=source_language)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].translations[0].to == "cs"
        assert response[0].translations[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_autodetect(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        target_languages = ["cs"]
        input_text_elements = [InputTextItem(text="This is a test.")]
        response = client.translate(
            content=input_text_elements, to=target_languages)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1
        assert response[0].translations[0].to == "cs"
        assert response[0].translations[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_no_translate_tag(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        source_language = "zh-chs"
        target_languages = ["en"]
        input_text_elements = [InputTextItem(
            text="<span class=notranslate>今天是怎么回事是</span>非常可怕的")]
        response = client.translate(content=input_text_elements,
                                    to=target_languages,
                                    from_parameter=source_language,
                                    text_type=TextType.HTML)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert "今天是怎么回事是" in response[0].translations[0].text

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_dictionary_tag(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        source_language = "en"
        target_languages = ["es"]
        input_text_elements = [InputTextItem(
            text="The word < mstrans:dictionary translation =\"wordomatic\">wordomatic</mstrans:dictionary> is a dictionary entry.")]
        response = client.translate(
            content=input_text_elements,
            to=target_languages,
            from_parameter=source_language)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].translations[0].to == "es"
        assert "wordomatic" in response[0].translations[0].text

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_transliteration(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        source_language = "ar"
        target_languages = ["zh-Hans"]
        input_text_elements = [InputTextItem(text="hudha akhtabar.")]
        response = client.translate(content=input_text_elements,
                                    to=target_languages,
                                    from_parameter=source_language,
                                    from_script="Latn",
                                    to_script="Latn")

        assert len(response) == 1
        assert response[0].source_text is not None
        assert len(response[0].translations) == 1
        assert response[0].translations[0].to == "zh-Hans"
        assert response[0].translations[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_from_to_latin(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        source_language = "hi"
        target_languages = ["ta"]
        input_text_elements = [InputTextItem(text="ap kaise ho")]
        response = client.translate(content=input_text_elements,
                                    to=target_languages,
                                    from_parameter=source_language,
                                    from_script="Latn",
                                    to_script="Latn")

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].translations[0].text is not None
        assert "eppadi irukkiraai?" in response[0].translations[0].transliteration.text

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_multiple_input(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        target_languages = ["cs"]
        input_text_elements = [InputTextItem(text="This is a test."), InputTextItem(
            text="Esto es una prueba."), InputTextItem(text="Dies ist ein Test.")]
        response = client.translate(
            content=input_text_elements, to=target_languages)

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
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        target_languages = ["cs", "es", "de"]
        input_text_elements = [InputTextItem(text="This is a test.")]
        response = client.translate(
            content=input_text_elements, to=target_languages)

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
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        target_languages = ["cs"]
        input_text_elements = [InputTextItem(
            text="<html><body>This <b>is</b> a test.</body></html>")]
        response = client.translate(
            content=input_text_elements, to=target_languages, text_type=TextType.HTML)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_profanity(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        target_languages = ["zh-cn"]
        input_text_elements = [InputTextItem(
            text="shit this is fucking crazy")]
        response = client.translate(content=input_text_elements,
                                    to=target_languages,
                                    profanity_action=ProfanityAction.MARKED,
                                    profanity_marker=ProfanityMarker.ASTERISK)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1
        assert "***" in response[0].translations[0].text

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_alignment(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        target_languages = ["cs"]
        input_text_elements = [InputTextItem(text="It is a beautiful morning")]
        response = client.translate(
            content=input_text_elements, to=target_languages, include_alignment=True)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1
        assert response[0].translations[0].alignment.proj is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_sentence_length(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        target_languages = ["fr"]
        input_text_elements = [InputTextItem(
            text="La réponse se trouve dans la traduction automatique. La meilleure technologie de traduction automatique ne peut pas toujours fournir des traductions adaptées à un site ou des utilisateurs comme un être humain. Il suffit de copier et coller un extrait de code n'importe où.")]
        response = client.translate(
            content=input_text_elements, 
            to=target_languages, 
            include_sentence_length=True)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "fr"
        assert response[0].detected_language.score == 1
        assert len(response[0].translations[0].sent_len.src_sent_len) == 3
        assert len(response[0].translations[0].sent_len.trans_sent_len) == 3

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_custom_endpoint(self, **kwargs):
        endpoint = kwargs.get("text_translation_custom_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        target_languages = ["fr"]
        input_text_elements = [InputTextItem(text="It is a beautiful morning")]
        response = client.translate(
            content=input_text_elements, 
            to=target_languages)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1

    @pytest.mark.live_test_only
    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_token(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client_token(endpoint, apikey, region)

        target_languages = ["cs"]
        input_text_elements = [InputTextItem(text="This is a test.")]
        response = client.translate(
            content=input_text_elements, to=target_languages)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.score == 1
