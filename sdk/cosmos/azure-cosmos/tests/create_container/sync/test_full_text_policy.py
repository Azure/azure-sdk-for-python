# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Creation assertions copied from main e1c0306c77b2: test_full_text_policy.py."""

import uuid
import pytest
from azure.cosmos import PartitionKey
from azure.cosmos import exceptions
import re
from create_container._setup import SyncCreationCase


@pytest.mark.cosmosSearchQuery
class TestFullTextPolicy(SyncCreationCase):

    def test_create_full_text_container_rust(self):
        full_text_policy = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [{"path": "/abstract", "language": "en-US"}],
        }
        indexing_policy = {"fullTextIndexes": [{"path": "/abstract"}]}
        created_container = self.test_db.create_container(
            id="full_text_container" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy,
            indexing_policy=indexing_policy,
        )
        properties = created_container.read()
        assert (
            properties["fullTextPolicy"]["defaultLanguage"]
            == full_text_policy["defaultLanguage"]
        )
        assert (
            properties["fullTextPolicy"]["fullTextPaths"]
            == full_text_policy["fullTextPaths"]
        )
        assert (
            properties["indexingPolicy"]["fullTextIndexes"]
            == indexing_policy["fullTextIndexes"]
        )
        self.test_db.delete_container(created_container.id)
        full_text_policy_no_paths = {"defaultLanguage": "en-US"}
        created_container = self.test_db.create_container(
            id="full_text_container" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy_no_paths,
        )
        properties = created_container.read()
        assert (
            properties["fullTextPolicy"]["defaultLanguage"]
            == full_text_policy_no_paths["defaultLanguage"]
        )
        self.test_db.delete_container(created_container.id)
        full_text_policy_no_langs = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [{"path": "/abstract"}],
        }
        created_container = self.test_db.create_container(
            id="full_text_container" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy_no_langs,
        )
        properties = created_container.read()
        assert (
            properties["fullTextPolicy"]["defaultLanguage"]
            == full_text_policy_no_langs["defaultLanguage"]
        )
        assert (
            properties["fullTextPolicy"]["fullTextPaths"]
            == full_text_policy_no_langs["fullTextPaths"]
        )
        self.test_db.delete_container(created_container.id)

    def test_fail_create_full_text_policy_rust(self):
        full_text_policy_wrong_path = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [{"path": "abstract", "language": "en-US"}],
        }
        try:
            self.test_db.create_container(
                id="full_text_container",
                partition_key=PartitionKey(path="/id"),
                full_text_policy=full_text_policy_wrong_path,
            )
            pytest.fail("Container creation should have failed for invalid path.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert re.search(
                "the full.text policy contains an invalid path.*abstract",
                e.http_error_message,
                re.IGNORECASE,
            )
        full_text_policy_wrong_default = {
            "defaultLanguage": "spa-SPA",
            "fullTextPaths": [{"path": "/abstract", "language": "en-US"}],
        }
        try:
            self.test_db.create_container(
                id="full_text_container",
                partition_key=PartitionKey(path="/id"),
                full_text_policy=full_text_policy_wrong_default,
            )
            pytest.fail(
                "Container creation should have failed for wrong supported language."
            )
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
        full_text_policy_wrong_default = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [{"path": "/abstract", "language": "spa-SPA"}],
        }
        try:
            self.test_db.create_container(
                id="full_text_container",
                partition_key=PartitionKey(path="/id"),
                full_text_policy=full_text_policy_wrong_default,
            )
            pytest.fail(
                "Container creation should have failed for wrong supported language."
            )
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400

    def test_fail_create_full_text_indexing_policy_rust(self):
        full_text_policy = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [{"path": "/abstract", "language": "en-US"}],
        }
        indexing_policy_wrong_path = {"fullTextIndexes": [{"path": "/path"}]}
        try:
            container = self.test_db.create_container(
                id="full_text_container" + str(uuid.uuid4()),
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy_wrong_path,
            )
            container.read()
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
        indexing_policy_wrong_path = {"fullTextIndexes": [{"path": "abstract"}]}
        try:
            self.test_db.create_container(
                id="full_text_container",
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy_wrong_path,
                full_text_policy=full_text_policy,
            )
            pytest.fail("Container creation should have failed for invalid path.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
        indexing_policy_no_path = {"fullTextIndexes": [{"not_path": "abstract"}]}
        try:
            self.test_db.create_container(
                id="full_text_container",
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy_no_path,
                full_text_policy=full_text_policy,
            )
            pytest.fail("Container creation should have failed for missing path.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
