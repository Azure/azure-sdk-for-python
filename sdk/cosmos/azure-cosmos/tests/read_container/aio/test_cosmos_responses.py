# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Main's async container-response header assertion, with a Rust data client."""

import uuid

import pytest
from azure.cosmos import PartitionKey
from read_container._container_setup import AsyncContainerReadCase


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestCosmosResponsesAsync(AsyncContainerReadCase):
    async def test_container_read_headers_async_rust(self):
        # Source: tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_container_read_headers_async
        container = await self.test_database.create_container(id="responses_test" + str(uuid.uuid4()),
                                                             partition_key=PartitionKey(path="/company"))
        first_response = await container.read()
        assert len(first_response.get_response_headers()) > 0
