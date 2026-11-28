# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""A bodyless successful create returns a proxy and reads properties only on request."""

import uuid

import pytest
from azure.core import MatchConditions
from azure.cosmos import PartitionKey
from create_container._setup import AsyncCreationCase


@pytest.mark.cosmosLong
class TestConditionalCreationAsync(AsyncCreationCase):
    async def test_if_missing_bodyless_creation_outcome_async_rust(self):
        for return_properties in (False, True):
            with self.subTest(return_properties=return_properties):
                container_id = "conditional_" + uuid.uuid4().hex
                hook_bodies = []
                result = await self.test_db.create_container(
                    container_id,
                    PartitionKey("/pk"),
                    match_condition=MatchConditions.IfMissing,
                    return_properties=return_properties,
                    response_hook=lambda _headers, body: hook_bodies.append(body),
                )
                container = result[0] if return_properties else result
                assert container.id == container_id
                if return_properties:
                    assert result[1]["id"] == container_id
                    assert result[1]["partitionKey"]["paths"] == ["/pk"]
                    assert result[1].get_response_headers()["x-ms-request-charge"]
                assert hook_bodies == [{}]
                persisted = await self.test_db.get_container_client(container_id).read()
                assert persisted["id"] == container_id
                assert persisted["partitionKey"]["paths"] == ["/pk"]
