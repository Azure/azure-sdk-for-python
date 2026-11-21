# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""``DatabaseProxy.read`` on Rust keeps the service's handling of conditional reads."""
from __future__ import annotations

import os
import uuid

import pytest
from azure.core import MatchConditions

from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from common._rust_checks import run_on_rust


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


@pytest.fixture(scope="module")
def readable_database_id():
    database_id = "rust_read_db_" + uuid.uuid4().hex[:12]
    with _rust_client() as client:
        try:
            client.create_database(database_id)
            yield database_id
        finally:
            try:
                client.delete_database(database_id)
            except CosmosResourceNotFoundError:
                pass


def test_read_database_with_stale_if_match_returns_database_rust(readable_database_id):
    """The service does not enforce If-Match on a database read, so a stale etag still returns the database."""
    with _rust_client() as client:
        database = client.get_database_client(readable_database_id)
        properties = run_on_rust(
            client, lambda: database.read(etag='"stale-version"', match_condition=MatchConditions.IfNotModified),
        )

    assert properties["id"] == readable_database_id
    assert properties["_etag"] != '"stale-version"'
