# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import recorded_by_proxy
from preparer import TextTranslationPreparer
from testcase import TextTranslationTest


class TestGetLanguages(TextTranslationTest):
    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_all_scopes(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        client = self.create_getlanguage_client(endpoint)
        response = client.get_supported_languages()

        assert response.translation
        assert response.transliteration
        assert response.models

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_translation_scope(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        client = self.create_getlanguage_client(endpoint)
        response = client.get_supported_languages(scope="translation")

        assert response.translation
        translations = response.translation["af"]
        assert translations.dir is not None
        assert translations.name is not None
        assert translations.native_name is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_transliteration_scope(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        client = self.create_getlanguage_client(endpoint)
        response = client.get_supported_languages(scope="transliteration")

        assert response.transliteration
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
    @recorded_by_proxy
    def test_transliteration_multiple_scripts(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        client = self.create_getlanguage_client(endpoint)
        response = client.get_supported_languages(scope="transliteration")

        assert response.transliteration
        transliterations = response.transliteration["zh-Hant"]
        assert transliterations.name is not None
        assert transliterations.native_name is not None
        assert transliterations.scripts is not None

        assert len(transliterations.scripts) > 1
        assert len(transliterations.scripts[0].to_scripts) > 1
        assert len(transliterations.scripts[1].to_scripts) > 1

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_models_scope(self, **kwargs):
        endpoint = kwargs.get("text_translation_endpoint")
        client = self.create_getlanguage_client(endpoint)
        response = client.get_supported_languages(scope="models")

        assert response.models
        assert len(response.models) > 0
