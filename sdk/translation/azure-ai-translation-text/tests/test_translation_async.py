# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.translation.text.models import TextType, ProfanityAction, ProfanityMarker
from preparer import TextTranslationPreparer
from testcase import TextTranslationTest


class TestTranslationAsync(TextTranslationTest):
    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_translate(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_async_client(endpoint, apikey, region)

        source_language = "es"
        target_languages = ["cs"]
        input_text_elements = ["Hola mundo"]
        async with client:
            response = await client.translate(
                request_body=input_text_elements, target_languages=target_languages, source_language=source_language
            )

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].translations[0].to == "cs"
        assert response[0].translations[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_autodetect(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_async_client(endpoint, apikey, region)

        target_languages = ["cs"]
        input_text_elements = ["This is a test."]
        async with client:
            response = await client.translate(request_body=input_text_elements, target_languages=target_languages)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.confidence == 1
        assert response[0].translations[0].to == "cs"
        assert response[0].translations[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_no_translate_tag(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_async_client(endpoint, apikey, region)

        source_language = "zh-chs"
        target_languages = ["en"]
        input_text_elements = ["<span class=notranslate>今天是怎么回事是</span>非常可怕的"]
        async with client:
            response = await client.translate(
                request_body=input_text_elements,
                target_languages=target_languages,
                source_language=source_language,
                text_type=TextType.HTML,
            )

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert "今天是怎么回事是" in response[0].translations[0].text

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_dictionary_tag(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_async_client(endpoint, apikey, region)

        source_language = "en"
        target_languages = ["es"]
        input_text_elements = [
            'The word < mstrans:dictionary translation ="wordomatic">wordomatic</mstrans:dictionary> is a dictionary entry.'
        ]
        async with client:
            response = await client.translate(
                request_body=input_text_elements, target_languages=target_languages, source_language=source_language
            )

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].translations[0].to == "es"
        assert "wordomatic" in response[0].translations[0].text

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_transliteration(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_async_client(endpoint, apikey, region)

        source_language = "ar"
        target_languages = ["zh-Hans"]
        input_text_elements = ["hudha akhtabar."]
        async with client:
            response = await client.translate(
                request_body=input_text_elements,
                target_languages=target_languages,
                source_language=source_language,
                source_language_script="Latn",
                target_language_script="Latn",
            )

        assert len(response) == 1
        assert response[0].source_text is not None
        assert len(response[0].translations) == 1
        assert response[0].translations[0].to == "zh-Hans"
        assert response[0].translations[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_from_to_latin(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_async_client(endpoint, apikey, region)

        source_language = "hi"
        target_languages = ["ta"]
        input_text_elements = ["ap kaise ho"]
        async with client:
            response = await client.translate(
                request_body=input_text_elements,
                target_languages=target_languages,
                source_language=source_language,
                source_language_script="Latn",
                target_language_script="Latn",
            )

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].translations[0].text is not None
        assert "eppadi irukkiraai?" in response[0].translations[0].transliteration.text

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_multiple_input(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_async_client(endpoint, apikey, region)

        target_languages = ["cs"]
        input_text_elements = [
            "This is a test.",
            "Esto es una prueba.",
            "Dies ist ein Test.",
        ]
        async with client:
            response = await client.translate(request_body=input_text_elements, target_languages=target_languages)

        assert len(response) == 3
        assert response[0].detected_language.language == "en"
        assert response[1].detected_language.language == "es"
        assert response[2].detected_language.language == "de"
        assert response[0].detected_language.confidence == 1
        assert response[1].detected_language.confidence == 1
        assert response[2].detected_language.confidence == 1

        assert response[0].translations[0].text is not None
        assert response[1].translations[0].text is not None
        assert response[2].translations[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_multiple_target_languages(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_async_client(endpoint, apikey, region)

        target_languages = ["cs", "es", "de"]
        input_text_elements = ["This is a test."]
        async with client:
            response = await client.translate(request_body=input_text_elements, target_languages=target_languages)

        assert len(response) == 1
        assert len(response[0].translations) == 3
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.confidence == 1
        assert response[0].translations[0].text is not None
        assert response[0].translations[1].text is not None
        assert response[0].translations[2].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_different_texttypes(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_async_client(endpoint, apikey, region)

        target_languages = ["cs"]
        input_text_elements = ["<html><body>This <b>is</b> a test.</body></html>"]
        async with client:
            response = await client.translate(
                request_body=input_text_elements, target_languages=target_languages, text_type=TextType.HTML
            )

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.confidence == 1

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_profanity(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_async_client(endpoint, apikey, region)

        target_languages = ["zh-cn"]
        input_text_elements = ["shit this is fucking crazy"]
        async with client:
            response = await client.translate(
                request_body=input_text_elements,
                target_languages=target_languages,
                profanity_action=ProfanityAction.MARKED,
                profanity_marker=ProfanityMarker.ASTERISK,
            )

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.confidence == 1
        assert "***" in response[0].translations[0].text

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_alignment(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_async_client(endpoint, apikey, region)

        target_languages = ["cs"]
        input_text_elements = ["It is a beautiful morning"]
        async with client:
            response = await client.translate(
                request_body=input_text_elements, target_languages=target_languages, include_alignment=True
            )

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.confidence == 1
        assert response[0].translations[0].alignment.projections is not None

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_sentence_length(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_async_client(endpoint, apikey, region)

        target_languages = ["fr"]
        input_text_elements = [
            "La réponse se trouve dans la traduction automatique. La meilleure technologie de traduction automatique ne peut pas toujours fournir des traductions adaptées à un site ou des utilisateurs comme un être humain. Il suffit de copier et coller un extrait de code n'importe où."
        ]
        async with client:
            response = await client.translate(
                request_body=input_text_elements, target_languages=target_languages, include_sentence_length=True
            )

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "fr"
        assert response[0].detected_language.confidence == 1
        assert len(response[0].translations[0].sentence_boundaries.source_sentences_lengths) == 3
        assert len(response[0].translations[0].sentence_boundaries.translated_sentences_lengths) == 3

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_custom_endpoint(self, **kwargs):
        endpoint = kwargs.get("text_translation_custom_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_async_client(endpoint, apikey, region)

        target_languages = ["fr"]
        input_text_elements = ["It is a beautiful morning"]
        async with client:
            response = await client.translate(request_body=input_text_elements, target_languages=target_languages)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.confidence == 1

    @pytest.mark.live_test_only
    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_token(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_async_client_token(endpoint, apikey, region)

        target_languages = ["cs"]
        input_text_elements = ["This is a test."]
        async with client:
            response = await client.translate(request_body=input_text_elements, target_languages=target_languages)

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].detected_language.language == "en"
        assert response[0].detected_language.confidence == 1

    @pytest.mark.live_test_only
    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_translate_aad(self, **kwargs):
        aadRegion = "westus2"
        aadResourceId = kwargs.get("text_translation_aadresourceid")
        token_credential = self.get_mt_credential(True)
        client = self.create_async_text_translation_client_with_aad(token_credential, aadRegion, aadResourceId)

        source_language = "es"
        target_languages = ["cs"]
        input_text_elements = ["Hola mundo"]
        response = await client.translate(
            request_body=input_text_elements, target_languages=target_languages, source_language=source_language
        )

        assert len(response) == 1
        assert len(response[0].translations) == 1
        assert response[0].translations[0].to == "cs"
        assert response[0].translations[0].text is not None
