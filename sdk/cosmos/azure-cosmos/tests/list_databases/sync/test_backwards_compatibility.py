# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Listing assertions adapted from the legacy session-token compatibility test."""

import unittest
import uuid

import pytest

from config import resources, settings
from azure.cosmos import CosmosClient


@pytest.mark.cosmosEmulator
class TestBackwardsCompatibility(unittest.TestCase):
    configs = settings.TestSettings

    @classmethod
    def setUpClass(cls):
        cls.client = CosmosClient(cls.configs.host, cls.configs.masterKey, _backend="rust")

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

    def test_list_databases_session_token_compatibility_rust(self):
        """Reject the removed listing option and still list this test's database."""
        # Source: tests/test_backwards_compatibility.py::TestBackwardsCompatibility.test_session_token_compatibility
        database = self.client.create_database(settings.unique_database_id("backcompat-list"))
        self.addCleanup(resources.try_delete_database_with_id, self.client, database.id)
        for token in (str(uuid.uuid4()), None):
            with self.subTest(session_token=token):
                with pytest.raises(
                    TypeError, match=r"list_databases\(\) does not support the 'session_token' option"
                ):
                    self.client.list_databases(session_token=token)
        database_ids = {db["id"] for db in self.client.list_databases()}
        assert database.id in database_ids
