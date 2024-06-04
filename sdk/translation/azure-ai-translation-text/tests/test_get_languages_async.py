# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils.aio import recorded_by_proxy_async
from preparer import TextTranslationPreparer
from testcase import TextTranslationTest


class TestGetLanguagesAsync(TextTranslationTest):
    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_all_scopes(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        client = self.create_async_getlanguage_client(endpoint)
        async with client:
            response = await client.get_supported_languages()

        assert len(response.translation) > 0
        assert len(response.transliteration) > 0
        assert len(response.dictionary) > 0

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_translation_scope(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        client = self.create_async_getlanguage_client(endpoint)
        async with client:
            response = await client.get_supported_languages(scope="translation")

        assert len(response.translation) > 0
        translations = response.translation["af"]
        assert translations.dir is not None
        assert translations.name is not None
        assert translations.native_name is not None

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_transliteration_scope(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        client = self.create_async_getlanguage_client(endpoint)
        async with client:
            response = await client.get_supported_languages(scope="transliteration")

        assert len(response.transliteration) > 0
        transliterations = response.transliteration["be"]
        assert transliterations.name is not None
        assert transliterations.native_name is not None
        assert transliterations.scripts is not None

        assert len(transliterations.scripts) > 0
        assert transliterations.scripts[0].name is not None
        assert transliterations.scripts[0].native_name is not None
        assert transliterations.scripts[0].code is not None
        assert transliterations.scripts[0].dir is not None
        assert transliterations.scripts[0].to_scripts is not None

        assert len(transliterations.scripts[0].to_scripts) > 0
        assert transliterations.scripts[0].to_scripts[0].name is not None
        assert transliterations.scripts[0].to_scripts[0].native_name is not None
        assert transliterations.scripts[0].to_scripts[0].code is not None
        assert transliterations.scripts[0].to_scripts[0].dir is not None

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_transliteration_multiple_scripts(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        client = self.create_async_getlanguage_client(endpoint)
        async with client:
            response = await client.get_supported_languages(scope="transliteration")

        assert len(response.transliteration) > 0
        transliterations = response.transliteration["zh-Hant"]
        assert transliterations.name is not None
        assert transliterations.native_name is not None
        assert transliterations.scripts is not None

        assert len(transliterations.scripts) > 1
        assert len(transliterations.scripts[0].to_scripts) > 1
        assert len(transliterations.scripts[1].to_scripts) > 1

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_dictionary_scope(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        client = self.create_async_getlanguage_client(endpoint)
        async with client:
            response = await client.get_supported_languages(scope="dictionary")

        assert len(response.dictionary) > 0
        dictionaries = response.dictionary["de"]
        assert dictionaries.name is not None
        assert dictionaries.native_name is not None

        assert len(dictionaries.translations) > 0
        assert dictionaries.translations[0].code is not None
        assert dictionaries.translations[0].dir is not None
        assert dictionaries.translations[0].name is not None
        assert dictionaries.translations[0].native_name is not None

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_dictionary_multiple_translations(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        client = self.create_async_getlanguage_client(endpoint)
        async with client:
            response = await client.get_supported_languages(scope="dictionary")

        assert len(response.dictionary) > 0
        dictionaries = response.dictionary["en"]
        assert dictionaries.name is not None
        assert dictionaries.native_name is not None

        assert len(dictionaries.translations) > 1
        assert dictionaries.translations[0].code is not None
        assert dictionaries.translations[0].dir is not None
        assert dictionaries.translations[0].name is not None
        assert dictionaries.translations[0].native_name is not None

    @TextTranslationPreparer()
    @recorded_by_proxy_async
    async def test_with_culture(self, **kwargs):
        endpoint = kwargs.get("translation_text_endpoint")
        client = self.create_async_getlanguage_client(endpoint)
        async with client:
            response = await client.get_supported_languages(accept_language="es")

        assert len(response.translation.items()) > 0
        assert len(response.transliteration.items()) > 0
        assert len(response.dictionary.items()) > 0
        translations = response.translation["en"]
        assert translations.dir is not None
        assert translations.name is not None
        assert translations.native_name is not None
