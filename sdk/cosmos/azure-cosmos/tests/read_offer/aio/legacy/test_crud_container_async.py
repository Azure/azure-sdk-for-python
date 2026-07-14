# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 ``test_offer_read_and_query_async`` check, re-run on the rust engine.

Why this file exists: when a customer reads a container's throughput, the SDK
returns an offer document, and one field on it -- ``resource`` -- is the link
that ties the offer back to the container it belongs to. Tools and dashboards
rely on that link (plus ``id`` / ``_rid`` / ``_self``) to know *which*
container a throughput number is for. If the rust engine returned an offer
body with a wrong or missing ``resource`` link, a customer could attribute
RU/s to the wrong container, and code reading those fields would break.

What it does: it is the real v4 test copied verbatim from
``tests/test_crud_container_async.py``, changed in exactly one place -- the
client is built with ``_backend="rust"`` -- so the same assertions now run
against the rust path. It reads the offer, then checks the offer body has
non-null ``id`` / ``_rid`` / ``_self`` / ``resource``, that ``_self``
contains the offer ``id``, and that ``resource`` points back at this
container's link. Without this copy, an offer-body regression on the rust
engine would slip through.

This is NOT the side-by-side parity comparison. The parity tests
(``read_offer/aio/test_read_offer_parity_async.py``) run the same call on both
engines and diff the numbers. This file runs on rust only; the core-python
side of the contract is already guaranteed by the original test in
``tests/``. Together: parity catches value drift (wrong RU/s), this catches
contract drift (wrong offer body) by reusing a check the team already trusts.

Self-contained: builds its own database + container in ``asyncSetUp`` and
deletes them in ``asyncTearDown``. The class name and method name match the
source so the two test IDs differ only by path. The container is created with
dedicated throughput because ``get_throughput`` only returns an offer when the
container owns one.

Run with::

    pytest --noconftest tests/read_offer/aio/legacy/test_crud_container_async.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestCRUDContainerOperationsAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        await self.client.__aenter__()
        self._db_id = "legacy_read_offer_async_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.database = await self.client.create_database(self._db_id)
        self.container = await self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400,
        )

    async def asyncTearDown(self):
        try:
            await self.client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass
        await self.client.close()

    def __validate_offer_response_body(self, offer, expected_coll_link, expected_offer_type):
        assert offer.properties['id'] is not None
        assert offer.properties.get('_rid') is not None
        assert offer.properties.get('_self') is not None
        assert offer.properties.get('resource') is not None
        assert offer.properties['_self'].find(offer.properties['id']) != -1
        assert expected_coll_link.strip('/') == offer.properties['resource'].strip('/')
        if expected_offer_type:
            assert expected_offer_type == offer.properties.get('offerType')

    async def test_offer_read_and_query_async(self):
        # Source: tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_offer_read_and_query_async
        collection = self.container
        # Read the offer.
        expected_offer = await collection.get_throughput()
        collection_properties = await collection.read()
        self.__validate_offer_response_body(expected_offer, collection_properties.get('_self'), None)


if __name__ == "__main__":
    unittest.main()
