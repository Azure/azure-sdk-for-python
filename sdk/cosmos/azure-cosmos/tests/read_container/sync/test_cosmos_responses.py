# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Main's container-response header assertion, with a Rust data client."""

import uuid

import pytest
from azure.cosmos import PartitionKey
from read_container._container_setup import SyncContainerReadCase


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestCosmosResponses(SyncContainerReadCase):
    def test_container_read_headers_rust(self):
        # Source: tests/test_cosmos_responses.py::TestCosmosResponses.test_container_read_headers
        container = self.test_database.create_container(id="responses_test" + str(uuid.uuid4()),
                                                       partition_key=PartitionKey(path="/company"))
        first_response = container.read()
        assert len(first_response.get_response_headers()) > 0
