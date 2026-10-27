# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Own replacement-test databases through setup, assertions and cleanup."""

from contextlib import ExitStack
import os
import uuid

import pytest

from common.throughput_fixtures import owned_database, owned_database_async

from azure.cosmos import CosmosClient


__all__ = ["owned_database", "owned_database_async", "database_per_backend"]


@pytest.fixture
def database_per_backend():
    """Isolate writes by backend; share only the target of missing-offer rejections."""
    with ExitStack() as cleanup:
        client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        cleanup.callback(client.close)

        def make(offer_throughput):
            created = {}
            backends = ("core-python",) if offer_throughput is None else ("core-python", "rust")
            for backend in backends:
                database_id = "parity_repl_db_" + uuid.uuid4().hex
                cleanup.enter_context(owned_database(client, database_id, offer_throughput=offer_throughput))
                created[backend] = database_id
            if offer_throughput is None:
                created["rust"] = created["core-python"]
            return created

        yield make
