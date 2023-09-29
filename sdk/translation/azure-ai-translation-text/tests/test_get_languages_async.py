# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import recorded_by_proxy
from preparer import TextTranslationPreparer
from testcase import TextTranslationTest
import asyncio

class TestGetLanguagesAsync(TextTranslationTest):

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_all_scopes(self, **kwargs):
        async def test_all_scopes_async(**kwargs):
            endpoint = kwargs.get("text_translation_endpoint")
            client = self.create_async_getlanguage_client(endpoint)
            response = await client.get_languages()

            assert len(response.translation) > 0
            assert len(response.transliteration) > 0
            assert len(response.dictionary) > 0
        asyncio.run(test_all_scopes_async(**kwargs))

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_translation_scope(self, **kwargs):
        async def test_translation_scope_async(**kwargs):
            endpoint = kwargs.get("text_translation_endpoint")
            client = self.create_async_getlanguage_client(endpoint)
            response = await client.get_languages(scope="translation")

            assert len(response.translation) > 0
            translations = response.translation["af"]
            assert translations.dir is not None
            assert translations.name is not None
            assert translations.native_name is not None
        asyncio.run(test_translation_scope_async(**kwargs))

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_transliteration_scope(self, **kwargs):
        async def test_transliteration_scope_async(**kwargs):
            endpoint = kwargs.get("text_translation_endpoint")
            client = self.create_async_getlanguage_client(endpoint)
            response = await client.get_languages(scope="transliteration")

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
        asyncio.run(test_transliteration_scope_async(**kwargs))

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_transliteration_multiple_scripts(self, **kwargs):
        async def test_transliteration_multiple_scripts_async(**kwargs):            
            endpoint = kwargs.get("text_translation_endpoint")
            client = self.create_async_getlanguage_client(endpoint)
            response = await client.get_languages(scope="transliteration")

            assert len(response.transliteration) > 0
            transliterations = response.transliteration["zh-Hant"]
            assert transliterations.name is not None
            assert transliterations.native_name is not None
            assert transliterations.scripts is not None

            assert len(transliterations.scripts) > 1
            assert len(transliterations.scripts[0].to_scripts) > 1
            assert len(transliterations.scripts[1].to_scripts) > 1
        asyncio.run(test_transliteration_multiple_scripts_async(**kwargs))

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_dictionary_scope(self, **kwargs):    
        async def test_dictionary_scope_async(**kwargs):
            endpoint = kwargs.get("text_translation_endpoint")
            client = self.create_async_getlanguage_client(endpoint)
            response = await client.get_languages(scope="dictionary")

            assert len(response.dictionary) > 0
            dictionaries = response.dictionary["de"]
            assert dictionaries.name is not None
            assert dictionaries.native_name is not None

            assert len(dictionaries.translations) > 0
            assert dictionaries.translations[0].code is not None
            assert dictionaries.translations[0].dir is not None
            assert dictionaries.translations[0].name is not None
            assert dictionaries.translations[0].native_name is not None
        asyncio.run(test_dictionary_scope_async(**kwargs))

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_dictionary_multiple_translations(self, **kwargs):
        async def test_dictionary_multiple_translations_async(**kwargs):
            endpoint = kwargs.get("text_translation_endpoint")
            client = self.create_async_getlanguage_client(endpoint)
            response = await client.get_languages(scope="dictionary")

            assert len(response.dictionary) > 0
            dictionaries = response.dictionary["en"]
            assert dictionaries.name is not None
            assert dictionaries.native_name is not None

            assert len(dictionaries.translations) > 1
            assert dictionaries.translations[0].code is not None
            assert dictionaries.translations[0].dir is not None
            assert dictionaries.translations[0].name is not None
            assert dictionaries.translations[0].native_name is not None
        asyncio.run(test_dictionary_multiple_translations_async(**kwargs))

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_with_culture(self, **kwargs):
        async def test_with_culture_async(**kwargs):
            endpoint = kwargs.get("text_translation_endpoint")
            client = self.create_async_getlanguage_client(endpoint)
            response = await client.get_languages(accept_language="es")

            assert len(response.translation.items()) > 0
            assert len(response.transliteration.items()) > 0
            assert len(response.dictionary.items()) > 0
            translations = response.translation["en"]
            assert translations.dir is not None
            assert translations.name is not None
            assert translations.native_name is not None
        asyncio.run(test_with_culture_async(**kwargs))
