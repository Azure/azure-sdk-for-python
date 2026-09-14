# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Unchanged v4 policy-replacement methods with isolated Rust setup."""

import uuid
import pytest
from azure.cosmos import PartitionKey, exceptions
from azure.cosmos import CosmosClient
from replace_container._legacy_setup import SyncReplacementCase

class TestFullTextPolicy(SyncReplacementCase):
    def _create_key_client(self):
        return CosmosClient(self.host, self.key, _backend="rust", read_timeout=30)

    def test_replace_full_text_container(self):
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
