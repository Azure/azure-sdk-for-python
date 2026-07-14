# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 ``test_offer_read_and_query`` check, re-run on the rust engine.

Why this file exists: when a customer reads a container's throughput, the SDK
returns an offer document, and one field on it -- ``resource`` -- is the link
that ties the offer back to the container it belongs to. Tools and dashboards
rely on that link (plus ``id`` / ``_rid`` / ``_self``) to know *which*
container a throughput number is for. If the rust engine returned an offer
body with a wrong or missing ``resource`` link, a customer could attribute
RU/s to the wrong container, and code reading those fields would break.

What it does: it is the real v4 test copied verbatim from
``tests/test_crud_container.py``, changed in exactly one place -- the client
is built with ``_backend="rust"`` -- so the same assertions now run against
the rust path. It reads the offer, then checks the offer body has non-null
``id`` / ``_rid`` / ``_self`` / ``resource``, that ``_self`` contains the
offer ``id``, and that ``resource`` points back at this container's link.
Without this copy, an offer-body regression on the rust engine would slip
through.

This is NOT the side-by-side parity comparison. The parity tests
(``read_offer/sync/test_read_offer_parity.py``) run the same call on both
engines and diff the numbers. This file runs on rust only; the core-python
side of the contract is already guaranteed by the original test in
``tests/``. Together: parity catches value drift (wrong RU/s), this catches
contract drift (wrong offer body) by reusing a check the team already trusts.

Self-contained: builds its own database + container in ``setUp`` and deletes
them in ``tearDown``. The class name and method name match the source so the
two test IDs differ only by path. The container is created with dedicated
throughput because ``get_throughput`` only returns an offer when the
container owns one.

Run with::

    pytest --noconftest tests/read_offer/sync/legacy/test_crud_container.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestCRUDContainerOperations(unittest.TestCase):

    def setUp(self) -> None:
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        self._db_id = "legacy_read_offer_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.database = self.client.create_database(self._db_id)
        self.container = self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400,
        )

    def tearDown(self) -> None:
        try:
            self.client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass

    def __ValidateOfferResponseBody(self, offer, expected_coll_link, expected_offer_type):
        self.assertIsNotNone(offer.properties['id'], 'Id cannot be null.')
        self.assertIsNotNone(offer.properties.get('_rid'), 'Resource Id (Rid) cannot be null.')
        self.assertIsNotNone(offer.properties.get('_self'), 'Self Link cannot be null.')
        self.assertIsNotNone(offer.properties.get('resource'), 'Resource Link cannot be null.')
        self.assertTrue(offer.properties['_self'].find(offer.properties['id']) != -1,
                        'Offer id not contained in offer self link.')
        self.assertEqual(expected_coll_link.strip('/'), offer.properties['resource'].strip('/'))
        if (expected_offer_type):
            self.assertEqual(expected_offer_type, offer.properties.get('offerType'))

    def test_offer_read_and_query(self):
        # Source: tests/test_crud_container.py::TestCRUDContainerOperations.test_offer_read_and_query
        collection = self.container
        # Read the offer.
        expected_offer = collection.get_throughput()
        collection_properties = collection.read()
        self.__ValidateOfferResponseBody(expected_offer, collection_properties.get('_self'), None)


if __name__ == "__main__":
    unittest.main()
