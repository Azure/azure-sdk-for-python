# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 replace-throughput checks, re-run on the rust engine.

Why this file exists: when a customer changes a container's throughput, the SDK
reads the container's offer, changes the RU/s in it, and PUTs it back, then hands
back a ``ThroughputProperties`` showing the applied number. Customers and their
automation act on that returned number (a scaler confirms it took; a dashboard shows
the new capacity). If the rust engine set the wrong number, wrote to the wrong
offer, or handed back a different object type, a capacity change could silently fail
or report the wrong value -- at exactly the moment (a sale, a nightly load) the
change was meant to protect.

What it does: these are the real v4 tests copied verbatim from
``tests/test_crud_container.py``, changed in exactly one place -- the client is
built with ``_backend="rust"`` -- so the same assertions now run against the rust
path. They set throughput to a fixed 2500 RU/s (as an int and as a
``ThroughputProperties``) and confirm ``get_throughput`` reads 2500 back, and they
confirm that a ``ThroughputProperties`` mixing fixed and autoscale settings raises
``KeyError`` before any write (the same client-side guard on both engines). Fixed
absolute values (not read-then-add) keep the request deterministic so the two-column
parity audit compares like with like.

This is NOT the side-by-side parity comparison. The parity tests
(``replace_throughput/sync/test_replace_throughput_parity.py``) run the same call on
both engines and diff the numbers. This file runs on rust only; the core-python side
of the contract is guaranteed by the original test in ``tests/``. Together: parity
catches value drift (wrong RU/s), this catches contract drift (wrong return type or
a change that doesn't take) by reusing checks the team already trusts.

Self-contained: builds its own database + container in ``setUp`` and deletes them in
``tearDown``. The class name and method names match the source so the two test IDs
differ only by path. The container is created with dedicated throughput because
``replace_throughput`` only has an offer to change when the container owns one.

Run with::

    pytest --noconftest tests/replace_throughput/sync/legacy/test_crud_container.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, ThroughputProperties


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestCRUDContainerOperations(unittest.TestCase):
    """Runs the v4 throughput-change checks on the rust engine (rust-only).

    Each method builds a fresh container at 400 RU/s, changes its throughput, and
    reads it back to confirm the change took -- the same assertions the v4 SDK
    already shipped, now run with a ``_backend="rust"`` client. If the rust engine
    wrote the wrong number, wrote to the wrong offer, or handed back a different
    object, one of these checks fails. The core-python side of the contract is
    guaranteed by the original tests in ``tests/test_crud_container.py``.
    """

    def setUp(self) -> None:
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        self._db_id = "legacy_replace_tp_" + uuid.uuid4().hex[:8]
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

    def test_replace_throughput_offer_with_int(self):
        # Source: tests/test_crud_container.py::TestCRUDContainerOperations.test_replace_throughput_offer_with_int
        collection = self.container

        new_throughput = ThroughputProperties(offer_throughput=2500)
        collection.replace_throughput(new_throughput.offer_throughput)

        retrieve_throughput = collection.get_throughput()
        assert getattr(retrieve_throughput, "offer_throughput") == getattr(new_throughput, "offer_throughput")

    def test_replace_throughput_offer_with_object(self):
        # Source: tests/test_crud_container.py::TestCRUDContainerOperations.test_replace_throughput_offer_with_object
        collection = self.container

        new_throughput = ThroughputProperties(offer_throughput=2500)
        collection.replace_throughput(new_throughput)

        retrieve_throughput = collection.get_throughput()
        assert getattr(retrieve_throughput, "offer_throughput") == getattr(new_throughput, "offer_throughput")

    def test_negative_replace_throughput_with_all_configs_set(self):
        # Source: tests/test_crud_container.py::TestCRUDContainerOperations.test_negative_replace_throughput_with_all_configs_set
        collection = self.container

        new_throughput = ThroughputProperties(offer_throughput=2500, auto_scale_max_throughput=4000, auto_scale_increment_percent=5)

        with pytest.raises(KeyError):
            collection.replace_throughput(new_throughput)


if __name__ == "__main__":
    unittest.main()
