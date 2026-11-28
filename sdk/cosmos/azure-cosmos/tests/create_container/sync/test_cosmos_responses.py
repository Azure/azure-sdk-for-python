# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing legacy create-container return-shape checks, re-run on the Rust engine.

Why this file exists: ``create_container`` returns two different things
depending on one argument. By default it returns a ``ContainerProxy`` -- the
object you go on to read and write items through. With ``return_properties``
set, it returns a pair, and the second half of that pair carries the response
headers, which is where a customer reads how many request units the create
cost. Code written against either shape breaks if the other one comes back, so
both shapes have to survive the move to Rust.

What it does: two real legacy tests copied from ``tests/test_cosmos_responses.py``,
changed in one place -- the client is built with ``_backend="rust"``.
``test_create_container_headers`` asks for properties and checks the headers
are not empty. ``test_create_container_returns_container_proxy`` does not ask,
and checks a ``ContainerProxy`` came back.

This file runs on Rust only and reuses assertions the team already trusts.

Self-contained: it creates and deletes its own database, so it shares no state
with any other test. The class name and method names match the source (apart from the
method's ``_rust`` suffix), so the
two test IDs differ by path and method suffix.

Run with::

    pytest --noconftest tests/create_container/sync/test_cosmos_responses.py -v
"""

import unittest
import uuid

import pytest

from azure.cosmos import ContainerProxy
from azure.cosmos.partition_key import PartitionKey
from create_container._setup import SyncCreationCase


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestCosmosResponses(SyncCreationCase):

    def test_create_container_headers_rust(self):
        """With ``return_properties=True``, the response headers come back populated.

        The second half of the returned pair is what a customer reads the
        request unit charge from, so it must not be empty.
        """
        # Source: tests/test_cosmos_responses.py::TestCosmosResponses.test_create_container_headers
        first_response = self.test_database.create_container(
            id="responses_test" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/company"),
            return_properties=True,
        )
        assert len(first_response[1].get_response_headers()) > 0

    def test_create_container_returns_container_proxy_rust(self):
        """Without ``return_properties``, the plain ``ContainerProxy`` comes back.

        This is the default and by far the common case: callers chain straight
        into reading and writing items. Returning the pair here instead would
        break every existing caller.
        """
        # Source: tests/test_cosmos_responses.py::TestCosmosResponses.test_create_container_returns_container_proxy
        first_response = self.test_database.create_container(
            id="responses_test" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/company"),
        )
        assert isinstance(first_response, ContainerProxy)


if __name__ == "__main__":
    unittest.main()
