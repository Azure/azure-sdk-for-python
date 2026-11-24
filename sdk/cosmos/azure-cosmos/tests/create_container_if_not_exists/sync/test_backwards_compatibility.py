# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Isolate this API's conditional assertions from main 57f59d5d4851."""

import uuid

import pytest
from azure.core import MatchConditions
from azure.cosmos import PartitionKey
from config.clients import create_setup_client
from create_container._setup import SyncCreationCase


@pytest.mark.cosmosEmulator
class TestBackwardsCompatibility(SyncCreationCase):
    def _create_client(self):
        return create_setup_client(_backend="rust")

    def test_etag_match_condition_compatibility_rust(self):
        # Source: tests/test_backwards_compatibility.py::TestBackwardsCompatibility.test_etag_match_condition_compatibility
        container2 = self.databaseForTest.create_container_if_not_exists(
            str(uuid.uuid4()),
            PartitionKey(path="/pk"),
            etag=str(uuid.uuid4()),
            match_condition=MatchConditions.IfNotModified,
        )
        assert container2 is not None
        container2_read = container2.read()
        assert container2_read is not None
