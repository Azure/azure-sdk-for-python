# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Unchanged legacy policy-replacement methods with isolated Rust setup."""

import uuid
import pytest
from azure.cosmos import PartitionKey, exceptions
from azure.cosmos import CosmosClient
from replace_container._legacy_setup import SyncReplacementCase

@pytest.mark.cosmosEmulator
class TestFullTextPolicy(SyncReplacementCase):
    def _create_key_client(self):
        return CosmosClient(self.host, self.key, _backend="rust", read_timeout=30)

    def test_replace_full_text_container(self):
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
