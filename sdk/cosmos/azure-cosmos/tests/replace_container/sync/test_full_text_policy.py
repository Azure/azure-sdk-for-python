# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Unchanged legacy policy-replacement methods with isolated Rust setup."""

import re
import uuid
import pytest
from azure.cosmos import PartitionKey, exceptions
from azure.cosmos import CosmosClient
from replace_container._container_setup import SyncReplacementCase

@pytest.mark.cosmosSearchQuery
class TestFullTextPolicy(SyncReplacementCase):
    def _create_key_client(self):
        return CosmosClient(self.host, self.key, _backend="rust")

    def test_replace_full_text_container_rust(self):
        """Replace can both add a full text policy and change an existing one.

        Two rounds. First a container with no full text settings is replaced so
        it gains a policy and matching full text indexes. Then a container
        created with them already in place is replaced with the path changed to
        ``/new_path``.

        Each round checks the new values arrived and also that the result
        differs from what was there before. That second check is what stops the
        test passing when a replace quietly ignores the request and leaves the
        old settings in place.

        As with vector search, the policy and the indexes live in different
        parts of the definition and have to move together.
        """
        # Source: tests/test_full_text_policy.py::TestFullTextPolicy.test_replace_full_text_container
        # Replace a container without a full text policy and full text indexing policy

        created_container = self.test_db.create_container(
            id='full_text_container' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id")
        )
        created_container_properties = created_container.read()
        full_text_policy = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {
                    "path": "/abstract",
                    "language": "en-US"
                }
            ]
        }
        indexing_policy = {
            "fullTextIndexes": [
                {"path": "/abstract"}
            ]
        }

        # Replace the container with new policies
        replaced_container = self.test_db.replace_container(
            container=created_container.id,
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy,
            indexing_policy=indexing_policy
        )
        properties = replaced_container.read()
        assert properties["fullTextPolicy"]["defaultLanguage"] == full_text_policy["defaultLanguage"]
        assert properties["fullTextPolicy"]["fullTextPaths"] == full_text_policy["fullTextPaths"]
        assert properties["indexingPolicy"]['fullTextIndexes'] == indexing_policy['fullTextIndexes']
        assert created_container_properties['indexingPolicy'] != properties['indexingPolicy']
        self.test_db.delete_container(created_container.id)

        # Replace a container with a valid full text policy and full text indexing policy
        created_container = self.test_db.create_container(
            id='full_text_container' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy,
            indexing_policy=indexing_policy
        )
        created_container_properties = created_container.read()
        assert created_container_properties["fullTextPolicy"]["defaultLanguage"] == full_text_policy["defaultLanguage"]
        assert created_container_properties["fullTextPolicy"]["fullTextPaths"] == full_text_policy["fullTextPaths"]
        assert created_container_properties["indexingPolicy"]['fullTextIndexes'] == indexing_policy['fullTextIndexes']

        # Replace the container with new policies
        full_text_policy['fullTextPaths'][0]['path'] = "/new_path"
        indexing_policy['fullTextIndexes'][0]['path'] = "/new_path"
        replaced_container = self.test_db.replace_container(
            container=created_container.id,
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy,
            indexing_policy=indexing_policy
        )
        properties = replaced_container.read()
        assert properties["fullTextPolicy"]["defaultLanguage"] == full_text_policy["defaultLanguage"]
        assert properties["fullTextPolicy"]["fullTextPaths"] == full_text_policy["fullTextPaths"]
        assert properties["indexingPolicy"]['fullTextIndexes'] == indexing_policy['fullTextIndexes']
        assert created_container_properties['fullTextPolicy'] != properties['fullTextPolicy']
        assert created_container_properties["indexingPolicy"] != properties["indexingPolicy"]
        self.test_db.delete_container(created_container.id)

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

    @pytest.mark.skip(reason="environment-gap: the original main test is skipped; retain its disabled status.")
    def test_supported_languages_in_full_text_policy_rust(self):
        # Source: tests/test_full_text_policy.py::TestFullTextPolicy.test_supported_languages_in_full_text_policy
        # Create the container with English as the default language
        full_text_policy = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {"path": "/abstract", "language": "en-US"}
            ]
        }
        container = self.test_db.create_container(
            id='full_text_container' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy
        )
        try:
            for lang in self.supported_languages.values():
                updated_policy = {
                    "defaultLanguage": lang,
                    "fullTextPaths": [
                        {"path": "/abstract", "language": lang}
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
        finally:
            self.test_db.delete_container(container.id)

    @pytest.mark.skip(reason="environment-gap: the original main test is skipped; retain its disabled status.")
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

    @pytest.mark.skip(reason="environment-gap: the original main test is skipped; retain its disabled status.")
    def test_mismatched_default_and_path_languages_rust(self):
        # Source: tests/test_full_text_policy.py::TestFullTextPolicy.test_mismatched_default_and_path_languages
        # Create the initial container with English as the default language
        full_text_policy = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {
                    "path": "/abstract",
                    "language": "en-US"
                }
            ]
        }
        container = self.test_db.create_container(
            id='full_text_container' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy
        )

        try:
            # Update the full text policy with mismatched default and path languages
            updated_policy = {
                "defaultLanguage": "en-US",
                "fullTextPaths": [
                    {
                        "path": "/abstract",
                        "language": "fr-FR"
                    }
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

        finally:
            # Delete the container at the end of the test
            self.test_db.delete_container(container.id)

    @pytest.mark.skip(reason="environment-gap: the original main test is skipped; retain its disabled status.")
    def test_replace_full_text_policy_with_different_languages_rust(self):
        # Source: tests/test_full_text_policy.py::TestFullTextPolicy.test_replace_full_text_policy_with_different_languages
        # Create the initial container with English as the default language
        full_text_policy = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {
                    "path": "/abstract",
                    "language": "en-US"
                }
            ]
        }
        container = self.test_db.create_container(
            id='full_text_container' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy
        )

        try:
            # Replace the full text policy with each supported language
            for language in self.supported_languages.values():
                updated_policy = {
                    "defaultLanguage": language,
                    "fullTextPaths": [
                        {
                            "path": "/abstract",
                            "language": language
                        }
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

        finally:
            # Delete the container at the end of the test
            self.test_db.delete_container(container.id)

    @pytest.mark.skip(reason="environment-gap: the original main test is skipped; retain its disabled status.")
    def test_replace_full_text_policy_with_different_path_languages_rust(self):
        # Source: tests/test_full_text_policy.py::TestFullTextPolicy.test_replace_full_text_policy_with_different_path_languages
        # Create the initial container with English as the default language
        full_text_policy = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {
                    "path": "/abstract",
                    "language": "en-US"
                }
            ]
        }
        container = self.test_db.create_container(
            id='full_text_container' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy
        )

        try:
            # Replace the full text policy with each supported path language
            for language in self.supported_languages.values():
                updated_policy = {
                    "defaultLanguage": "en-US",  # Keep default language as English
                    "fullTextPaths": [
                        {
                            "path": "/abstract",
                            "language": language
                        }
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

        finally:
            # Delete the container at the end of the test
            self.test_db.delete_container(container.id)

    @pytest.mark.skip(reason="environment-gap: the original main test is skipped; retain its disabled status.")
    def test_unsupported_language_in_full_text_policy_rust(self):
        # Source: tests/test_full_text_policy.py::TestFullTextPolicy.test_unsupported_language_in_full_text_policy
        # Create the container with English as the default language
        full_text_policy = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {
                    "path": "/abstract",
                    "language": "en-US"
                }
            ]
        }
        container = self.test_db.create_container(
            id='full_text_container' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy
        )
        try:
            # Replace the full-text policy with an unsupported language
            updated_policy = {
                "defaultLanguage": "en-US",
                "fullTextPaths": [
                    {
                        "path": "/abstract",
                        "language": "unsupported-LANG"
                    }
                ]
            }
            try:
                self.test_db.replace_container(
                    container=container.id,
                    partition_key=PartitionKey(path="/id"),
                    full_text_policy=updated_policy
                )
                pytest.fail("Container replacement should have failed for unsupported language.")
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 400
                assert re.search(
                        r"the full.text policy contains an unsupported language",
                        e.http_error_message, re.IGNORECASE)
        finally:
            self.test_db.delete_container(container.id)
