# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original async replacement response-header assertion, with Rust and owned setup."""

import uuid

from azure.cosmos.aio import CosmosClient
from azure.cosmos.partition_key import PartitionKey
from replace_container._legacy_setup import AsyncReplacementCase


class TestCosmosResponsesAsync(AsyncReplacementCase):
    def _create_key_client(self):
        return CosmosClient(self.host, self.key, _backend="rust", read_timeout=30)

    async def test_replace_container_headers_async(self):
        """``replace_container`` with ``return_properties`` returns populated headers.

        The same return-shape rule as create, on the replace path: the second
        half of the returned pair carries the response headers a customer reads
        the request unit charge from, and it must not be empty.
        """
        # Source: tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_replace_container_headers_async
        first_response = await self.test_database.create_container_if_not_exists(id="responses_test" + str(uuid.uuid4()),
                                                        partition_key=PartitionKey(path="/company"))
        second_response = await self.test_database.replace_container(first_response.id,
                                                               partition_key=PartitionKey(path="/company"), return_properties=True)
        assert len(second_response[1].get_response_headers()) > 0
