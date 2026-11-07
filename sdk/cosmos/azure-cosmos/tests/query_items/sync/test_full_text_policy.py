# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-backend copies of the legacy multi-language full-text query tests.

Source: tests/test_full_text_policy.py. Only the two originals that call
``query_items`` are copied; their markers, policies, queries and assertions are
unchanged. The class owns a fresh database created through a key-auth client
pinned to ``_backend="rust"``, so container create/replace, item writes and the
full-text ``query_items`` calls all run on the Rust driver. The owned database
is deleted in class teardown.
"""

import os
import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
from azure.cosmos import CosmosClient, PartitionKey


@pytest.mark.cosmosSearchQuery
class TestFullTextPolicy(unittest.TestCase):
    client: CosmosClient = None

    # Centralized dictionaries for all tests
    supported_languages = {
        "EnglishUS": "en-US",
        "FrenchFR": "fr-FR",
        "GermanDE": "de-DE",
        "ItalianIT": "it-IT",
        "PortugueseBR": "pt-BR",
        "PortuguesePT": "pt-PT",
        "SpanishES": "es-ES",
    }
    language_abstracts = {
        "en-US": "This is a test in English.",
        "fr-FR": "Ceci est une démonstration en français.",  # cspell:ignore Ceci démonstration français
        "de-DE": "Dies ist ein Beispiel auf Deutsch.",  # cspell:ignore Dies Beispiel Deutsch
        "it-IT": "Questo è un esempio in italiano.",  # cspell:ignore Questo esempio italiano
        "pt-BR": "Este é um exemplo em português do Brasil.",  # cspell:ignore Este exemplo português Brasil
        "pt-PT": "Este é um exemplo em português de Portugal.",  # cspell:ignore Este exemplo português Portugal
        "es-ES": "Esta es una demostración en español.",  # cspell:ignore Esta demostración español
    }
    search_terms = {
        "en-US": "English",
        "fr-FR": "démonstration",  # cspell:ignore démonstration
        "de-DE": "Beispiel",  # cspell:ignore Beispiel
        "it-IT": "esempio",  # cspell:ignore esempio
        "pt-BR": "exemplo",  # cspell:ignore exemplo
        "pt-PT": "exemplo",  # cspell:ignore exemplo
        "es-ES": "demostración",  # cspell:ignore demostración
    }

    @classmethod
    def setUpClass(cls):
        cls.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        cls.addClassCleanup(cls.client.close)
        cls.test_db = cls.client.create_database("query_items_full_text_" + uuid.uuid4().hex)
        cls.addClassCleanup(cls._delete_owned_database)

    @classmethod
    def _delete_owned_database(cls):
        try:
            cls.client.delete_database(cls.test_db.id)
        except exceptions.CosmosResourceNotFoundError:
            pass

    # Skipped upstream until the testing pipeline supports full-text multi-language.
    @pytest.mark.skip(reason="environment-gap: the original is skipped until the testing pipeline "
                             "supports full-text multi-language; pt-BR and pt-PT items tie under "
                             "TOP 1 ORDER BY RANK.")
    def test_default_language_fallback_rust(self):
        # Source: tests/test_full_text_policy.py::TestFullTextPolicy.test_default_language_fallback
        # Use centralized dictionaries
        full_text_policy = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {"path": "/abstract"}
            ]
        }
        container = self.test_db.create_container(
            id='full_text_container' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy
        )
        try:
            for language_code in self.supported_languages.values():
                # Replace the container's full text policy for each language
                updated_policy = {
                    "defaultLanguage": language_code,
                    "fullTextPaths": [
                        {"path": "/abstract"}
                    ]
                }
                replaced_container = self.test_db.replace_container(
                    container=container.id,
                    partition_key=PartitionKey(path="/id"),
                    full_text_policy=updated_policy
                )
                properties = replaced_container.read()
                assert properties["fullTextPolicy"]["defaultLanguage"] == updated_policy["defaultLanguage"]
                assert properties["fullTextPolicy"]["fullTextPaths"] == updated_policy["fullTextPaths"]
                # Insert and verify item
                item = {
                    "id": str(uuid.uuid4()),
                    "abstract": self.language_abstracts[language_code],
                }
                container.create_item(body=item)
                query = (
                    f"SELECT TOP 1 * FROM c WHERE FullTextContains(c.abstract, '{self.search_terms[language_code]}') "
                    f"ORDER BY RANK FullTextScore(c.abstract, '{self.search_terms[language_code]}')"
                )
                results = list(container.query_items(query, enable_cross_partition_query=True))
                assert len(results) > 0
                assert any(result["abstract"] == item["abstract"] for result in results)
        finally:
            self.test_db.delete_container(container.id)

    def test_multi_path_multi_language_policy_rust(self):
        # Source: tests/test_full_text_policy.py::TestFullTextPolicy.test_multi_path_multi_language_policy
        # Create a container with a different language in each path
        full_text_paths_multi = []
        for lang_code in self.supported_languages.values():
            # Use a unique, valid suffix for each language (replace '-' with '_')
            suffix = lang_code.replace('-', '_').lower()
            full_text_paths_multi.append({
                "path": f"/abstract_{suffix}",
                "language": lang_code
            })
        full_text_policy_multi = {
            "defaultLanguage": "en-US",
            "fullTextPaths": full_text_paths_multi
        }
        container = self.test_db.create_container(
            id='full_text_container_multi_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy_multi
        )
        try:
            # Insert one item per language, each with its own path
            for lang_code in self.supported_languages.values():
                suffix = lang_code.replace('-', '_').lower()
                item = {
                    "id": str(uuid.uuid4()),
                    f"abstract_{suffix}": self.language_abstracts[lang_code],
                }
                container.create_item(body=item)
            # Verify the fullTextPolicy has the correct language for each path
            properties = container.read()
            for path_entry in properties["fullTextPolicy"]["fullTextPaths"]:
                lang = path_entry["language"]
                suffix = lang.replace('-', '_').lower()
                assert path_entry["path"] == f"/abstract_{suffix}"
                assert lang in self.language_abstracts
            # Perform a full-text search for each language
            for lang_code in self.supported_languages.values():
                suffix = lang_code.replace('-', '_').lower()
                query = (
                    f"SELECT TOP 1 * FROM c WHERE FullTextContains(c.abstract_{suffix}, "
                    f"'{self.search_terms[lang_code]}') "
                    f"ORDER BY RANK FullTextScore(c.abstract_{suffix}, "
                    f"'{self.search_terms[lang_code]}')"
                )
                results = list(container.query_items(query, enable_cross_partition_query=True))
                assert len(results) > 0
                assert results[0][f"abstract_{suffix}"] == self.language_abstracts[lang_code]
        finally:
            self.test_db.delete_container(container.id)


if __name__ == '__main__':
    unittest.main()
