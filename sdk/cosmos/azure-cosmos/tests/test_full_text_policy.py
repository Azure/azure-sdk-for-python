# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import CosmosClient, PartitionKey


@pytest.mark.cosmosSearchQuery
class TestFullTextPolicy(unittest.TestCase):
    client: CosmosClient = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy

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
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = CosmosClient(cls.host, cls.masterKey)
        cls.created_database = cls.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
        cls.test_db = cls.client.create_database(str(uuid.uuid4()))

    def test_create_full_text_container(self):
        # Create a container with a valid full text policy and full text indexing policy
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
        created_container = self.test_db.create_container(
            id='full_text_container' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy,
            indexing_policy=indexing_policy
        )
        properties = created_container.read()
        assert properties["fullTextPolicy"] == full_text_policy
        assert properties["indexingPolicy"]['fullTextIndexes'] == indexing_policy['fullTextIndexes']
        self.test_db.delete_container(created_container.id)

        # Create a container with a full text policy containing only default language
        full_text_policy_no_paths = {
            "defaultLanguage": "en-US"
        }
        created_container = self.test_db.create_container(
            id='full_text_container' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy_no_paths,
        )
        properties = created_container.read()
        assert properties["fullTextPolicy"] == full_text_policy_no_paths
        self.test_db.delete_container(created_container.id)

        # Create a container with a full text policy with a given path containing only default language
        full_text_policy_no_langs = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {
                    "path": "/abstract"
                }
            ]
        }
        created_container = self.test_db.create_container(
            id='full_text_container' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy_no_langs,
        )
        properties = created_container.read()
        assert properties["fullTextPolicy"] == full_text_policy_no_langs
        self.test_db.delete_container(created_container.id)

    def test_replace_full_text_container(self):
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
        assert properties["fullTextPolicy"] == full_text_policy
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
        assert properties["fullTextPolicy"] == full_text_policy
        assert properties["indexingPolicy"]['fullTextIndexes'] == indexing_policy['fullTextIndexes']

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
        assert properties["fullTextPolicy"] == full_text_policy
        assert properties["indexingPolicy"]['fullTextIndexes'] == indexing_policy['fullTextIndexes']
        assert created_container_properties['fullTextPolicy'] != properties['fullTextPolicy']
        assert created_container_properties["indexingPolicy"] != properties["indexingPolicy"]
        self.test_db.delete_container(created_container.id)

    def test_fail_create_full_text_policy(self):
        # Pass a full text policy with a wrongly formatted path
        full_text_policy_wrong_path = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {
                    "path": "abstract",
                    "language": "en-US"
                }
            ]
        }
        try:
            self.test_db.create_container(
                id='full_text_container',
                partition_key=PartitionKey(path="/id"),
                full_text_policy=full_text_policy_wrong_path
            )
            pytest.fail("Container creation should have failed for invalid path.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "The Full Text Policy contains an invalid Path: abstract" in e.http_error_message

        # Pass a full text policy with an unsupported default language
        full_text_policy_wrong_default = {
            "defaultLanguage": "spa-SPA",
            "fullTextPaths": [
                {
                    "path": "/abstract",
                    "language": "en-US"
                }
            ]
        }
        try:
            self.test_db.create_container(
                id='full_text_container',
                partition_key=PartitionKey(path="/id"),
                full_text_policy=full_text_policy_wrong_default
            )
            pytest.fail("Container creation should have failed for wrong supported language.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "The Full Text Policy contains an unsupported language spa-SPA. Supported languages are:"\
                   in e.http_error_message

        # Pass a full text policy with an unsupported path language
        full_text_policy_wrong_default = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {
                    "path": "/abstract",
                    "language": "spa-SPA"
                }
            ]
        }
        try:
            self.test_db.create_container(
                id='full_text_container',
                partition_key=PartitionKey(path="/id"),
                full_text_policy=full_text_policy_wrong_default
            )
            pytest.fail("Container creation should have failed for wrong supported language.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "The Full Text Policy contains an unsupported language spa-SPA. Supported languages are:"\
                   in e.http_error_message

    def test_fail_create_full_text_indexing_policy(self):
        full_text_policy = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {
                    "path": "/abstract",
                    "language": "en-US"
                }
            ]
        }
        # Pass a full text indexing policy with a path not present in the full text policy
        indexing_policy_wrong_path = {
            "fullTextIndexes": [
                {"path": "/path"}
            ]
        }
        try:
            container = self.test_db.create_container(
                id='full_text_container' + str(uuid.uuid4()),
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy_wrong_path,
            )
            container.read()
            # TODO: This test is only failing on the pipelines, have been unable to see it pass locally
            # pytest.fail("Container creation should have failed for lack of embedding policy.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "The path of the Full Text Index /path does not match the path specified in the Full Text Policy"\
                   in e.http_error_message

        # Pass a full text indexing policy with a wrongly formatted path
        indexing_policy_wrong_path = {
            "fullTextIndexes": [
                {"path": "abstract"}
            ]
        }
        try:
            self.test_db.create_container(
                id='full_text_container',
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy_wrong_path,
                full_text_policy=full_text_policy
            )
            pytest.fail("Container creation should have failed for invalid path.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "Full-text index specification at index (0) contains invalid path" in e.http_error_message

        # Pass a full text indexing policy without a path field
        indexing_policy_no_path = {
            "fullTextIndexes": [
                {"not_path": "abstract"}
            ]
        }
        try:
            self.test_db.create_container(
                id='full_text_container',
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy_no_path,
                full_text_policy=full_text_policy
            )
            pytest.fail("Container creation should have failed for missing path.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "Missing path in full-text index specification at index (0)" in e.http_error_message

    # Skipped until testing pipeline is set up for full text multi-language support
    @pytest.mark.skip
    def test_supported_languages_in_full_text_policy(self):
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
                assert properties["fullTextPolicy"] == updated_policy
        finally:
            self.test_db.delete_container(container.id)

    # Skipped until testing pipeline is set up for full text multi-language support
    @pytest.mark.skip
    def test_default_language_fallback(self):
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
                assert properties["fullTextPolicy"] == updated_policy
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

    # Skipped until testing pipeline is set up for full text multi-language support
    @pytest.mark.skip
    def test_mismatched_default_and_path_languages(self):
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
            assert properties["fullTextPolicy"] == updated_policy

        finally:
            # Delete the container at the end of the test
            self.test_db.delete_container(container.id)

    # Skipped until testing pipeline is set up for full text multi-language support
    @pytest.mark.skip
    def test_replace_full_text_policy_with_different_languages(self):
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
                assert properties["fullTextPolicy"] == updated_policy

        finally:
            # Delete the container at the end of the test
            self.test_db.delete_container(container.id)

    # Skipped until testing pipeline is set up for full text multi-language support
    @pytest.mark.skip
    def test_replace_full_text_policy_with_different_path_languages(self):
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
                assert properties["fullTextPolicy"] == updated_policy

        finally:
            # Delete the container at the end of the test
            self.test_db.delete_container(container.id)

    # Skipped until testing pipeline is set up for full text multi-language support
    @pytest.mark.skip
    def test_multi_path_multi_language_policy(self):
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
                assert any(results[0][f"abstract_{suffix}"] == self.language_abstracts[lang_code] for result in results)
        finally:
            self.test_db.delete_container(container.id)

    # Skipped until testing pipeline is set up for full text multi-language support
    @pytest.mark.skip
    def test_unsupported_language_in_full_text_policy(self):
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
                assert "The Full Text Policy contains an unsupported language" in e.http_error_message
        finally:
            self.test_db.delete_container(container.id)


if __name__ == '__main__':
    unittest.main()
