# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 ``test_offer_methods`` check, re-run on the rust engine.

Why this file exists: ``get_throughput`` hands the customer an object whose
type name changed over time. The class was renamed from ``Offer`` to
``ThroughputProperties``, but the old ``Offer`` name was kept as an alias so
customer code written years ago (``isinstance(result, Offer)``) still works.
Old code depending on that alias must not break when a resource is read
through the new rust engine.

What it does: it is the real v4 test copied verbatim from
``tests/test_backwards_compatibility.py``, changed in exactly one place --
the client is built with ``_backend="rust"`` -- so the same assertions now
run against the rust path. It checks that ``get_throughput`` still returns an
object that is BOTH named ``ThroughputProperties`` AND an instance of
``Offer``. Without this copy, a rust return-type regression (a customer
unpacking the wrong object) would slip through.

This is NOT the side-by-side parity comparison. The parity tests
(``read_offer/sync/test_read_offer_parity.py``) run the same call on both
engines and diff the numbers. This file runs on rust only; the core-python
side of the contract is already guaranteed by the original test in
``tests/``. Together: parity catches value drift (wrong RU/s), this catches
contract drift (wrong return type) by reusing a check the team already
trusts.

Self-contained: builds its own database + container in ``setUp`` and deletes
them in ``tearDown``. The class name and method name match the source so the
two test IDs differ only by path. The database is created with shared
throughput and the container with dedicated throughput, because
``get_throughput`` only returns an offer when the resource owns one.

Run with::

    pytest --noconftest tests/read_offer/sync/legacy/test_backwards_compatibility.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, Offer, PartitionKey


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestBackwardsCompatibility(unittest.TestCase):

    def setUp(self) -> None:
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        self._db_id = "legacy_read_offer_bwc_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.databaseForTest = self.client.create_database(self._db_id, offer_throughput=400)
        self.containerForTest = self.databaseForTest.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400,
        )

    def tearDown(self) -> None:
        try:
            self.client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass

    def test_offer_methods(self):
        # Source: tests/test_backwards_compatibility.py::TestBackwardsCompatibility.test_offer_methods
        database_offer = self.databaseForTest.get_throughput()
        container_offer = self.containerForTest.get_throughput()

        self.assertTrue("ThroughputProperties" in str(type(database_offer)))
        self.assertTrue("ThroughputProperties" in str(type(container_offer)))

        self.assertTrue(isinstance(database_offer, Offer))
        self.assertTrue(isinstance(container_offer, Offer))


if __name__ == "__main__":
    unittest.main()
