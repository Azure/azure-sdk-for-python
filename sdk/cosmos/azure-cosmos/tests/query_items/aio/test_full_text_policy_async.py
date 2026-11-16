# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-backend copies of the legacy async multi-language full-text query tests.

Source: tests/test_full_text_policy_async.py. Only the two originals that call
``query_items`` are copied; their markers, policies, queries and assertions are
unchanged. Each test owns a fresh database created through an async key-auth
client pinned to ``_backend="rust"``, so container create/replace, item writes
and the full-text ``query_items`` calls all run on the Rust driver. The owned
database is deleted in async cleanup.
"""

import os
import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient


@pytest.mark.cosmosSearchQuery
class TestFullTextPolicyAsync(unittest.IsolatedAsyncioTestCase):
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

    async def asyncSetUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        await self.client.__aenter__()
        self.addAsyncCleanup(self.client.close)
        self.test_db = await self.client.create_database("query_items_full_text_async_" + uuid.uuid4().hex)
        self.addAsyncCleanup(self._delete_owned_database)

    async def _delete_owned_database(self):
        try:
            await self.client.delete_database(self.test_db.id)
        except exceptions.CosmosResourceNotFoundError:
            pass

    # Skipped upstream until the testing pipeline supports full-text multi-language.
    @pytest.mark.skip(reason="environment-gap: the original is skipped until the testing pipeline "
                             "supports full-text multi-language; pt-BR and pt-PT items tie under "
                             "TOP 1 ORDER BY RANK.")
    async def test_default_language_fallback_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_full_text_policy_async.py::TestFullTextPolicyAsync.test_default_language_fallback_async
        full_text_policy = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {"path": "/abstract"}
            ]
        }
        container = await self.test_db.create_container(
            id='full_text_container' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy
        )
        try:
            for language_code in self.supported_languages.values():
                updated_policy = {
                    "defaultLanguage": language_code,
                    "fullTextPaths": [
                        {"path": "/abstract"}
                    ]
                }
                replaced_container = await self.test_db.replace_container(
                    container=container.id,
                    partition_key=PartitionKey(path="/id"),
                    full_text_policy=updated_policy
                )
                properties = await replaced_container.read()
                assert properties["fullTextPolicy"]["defaultLanguage"] == updated_policy["defaultLanguage"]
                assert properties["fullTextPolicy"]["fullTextPaths"] == updated_policy["fullTextPaths"]
                item = {
                    "id": str(uuid.uuid4()),
                    "abstract": self.language_abstracts[language_code],
                }
                await container.create_item(body=item)
                query = (
                    f"SELECT TOP 1 * FROM c WHERE FullTextContains(c.abstract, '{self.search_terms[language_code]}') "
                    f"ORDER BY RANK FullTextScore(c.abstract, '{self.search_terms[language_code]}')"
                )
                results = [result async for result in container.query_items(query)]
                assert len(results) > 0
                assert any(result["abstract"] == item["abstract"] for result in results)
        finally:
            await self.test_db.delete_container(container.id)

    async def test_multi_path_multi_language_policy_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_full_text_policy_async.py::TestFullTextPolicyAsync.test_multi_path_multi_language_policy_async
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
        container = await self.test_db.create_container(
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
                await container.create_item(body=item)
            # Verify the fullTextPolicy has the correct language for each path
            properties = await container.read()
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
                results = [result async for result in container.query_items(query)]
                assert len(results) > 0
                assert results[0][f"abstract_{suffix}"] == self.language_abstracts[lang_code]
        finally:
            await self.test_db.delete_container(container.id)


if __name__ == '__main__':
    unittest.main()
