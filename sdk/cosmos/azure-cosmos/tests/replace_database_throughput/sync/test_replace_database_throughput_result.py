# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Database ``replace_throughput`` on Rust stores the new shared throughput and reports it faithfully."""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient
from common._rust_checks import run_on_rust
from common.throughput_fixtures import owned_database


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


@pytest.fixture
def database_id():
    """A database with 1000 RU/s of shared throughput, deleted after the test."""
    with _rust_client() as client:
        with owned_database(client, "rust_repl_db_" + uuid.uuid4().hex, offer_throughput=1000) as database:
            yield database.id


def test_replace_database_throughput_hook_cannot_change_result_rust(database_id):
    """The hook runs once; editing its headers or offer body changes neither the returned nor stored 2000 RU/s."""
    calls = []

    def hook(headers, offer):
        calls.append(offer["content"]["offerThroughput"])
        headers.clear()
        offer["content"]["offerThroughput"] = 999

    with _rust_client() as client:
        database = client.get_database_client(database_id)
        updated = run_on_rust(client, lambda: database.replace_throughput(2000, response_hook=hook))

        assert calls == [2000]
        assert updated.offer_throughput == 2000
        assert updated.properties["content"]["offerThroughput"] == 2000
        assert updated.get_response_headers()
        assert database.get_throughput().offer_throughput == 2000


def test_replace_database_throughput_persists_new_value_rust(database_id):
    """After replacing shared throughput, a later get_throughput returns the new 3000 RU/s."""
    with _rust_client() as client:
        database = client.get_database_client(database_id)
        run_on_rust(client, lambda: database.replace_throughput(3000))

    with _rust_client() as reader:
        persisted = reader.get_database_client(database_id).get_throughput()

    assert persisted.offer_throughput == 3000
    assert persisted.auto_scale_max_throughput is None
