# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Live sync parity tests for ``DatabaseProxy.read``.

What a customer does here: ``client.get_database_client("tenant").read()`` to
get a database's properties back as a dict.

Why these tests exist: a customer can build a client on either engine -- the
newer rust engine or the older core-python one -- and the same call must behave
the same on both. These tests run each scenario twice, once per engine, against
a real account and compare the results. A unit test with fakes cannot do that,
because the thing being checked is what the service actually sends back.

Three scenarios, matching what customers do with this call:

* baseline -- the properties dict is identical on both engines. Customers read
  ``id`` and ``_rid`` out of it directly, so a difference here is a broken
  application, not a cosmetic one.
* options and callbacks -- a custom header, a ``session_token`` that this method
  ignores by design, and a ``response_hook``. Each must be treated the same way
  on both engines, including the hook firing once with real response headers.
* missing database -- the same typed not-found exception on both. Customers
  catch that exception by type to decide whether to create the database.

``assert_functional_parity`` deliberately allows one known difference: the rust
engine reports a smaller set of response headers today. That gap is tracked
separately and still printed in the report; it is not a behavior difference.

These need a real account (the emulator counts) and the rust binding built, so
they skip when either is missing.
"""
from __future__ import annotations

import os
import uuid

import pytest

from common._parity_helpers import (
    run_on_both_backends,
    run_target_operation,
    skip_unless_emulator,
    skip_unless_rust_binding,
)
from azure.cosmos import CosmosClient


pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture(scope="module")
def readable_database_id():
    database_id = "parity_read_db_" + uuid.uuid4().hex[:12]
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    client.create_database(database_id)
    try:
        yield database_id
    finally:
        try:
            client.delete_database(database_id)
        finally:
            client.close()


def test_read_database_baseline_properties(readable_database_id):
    """Both backends return the same stable database properties."""

    def _call(client):
        database = client.get_database_client(readable_database_id)
        properties = run_target_operation(client, database.read)
        return {
            key: properties.get(key)
            for key in ("id", "_rid", "_self", "_etag", "_colls", "_users")
        }

    run_on_both_backends(
        _call,
        description="read_database baseline properties",
    ).assert_functional_parity()


def test_read_database_options_and_response_hook(readable_database_id):
    """Initial headers, ignored session tokens and response hooks retain parity."""

    def _call(client):
        hook_calls = []
        database = client.get_database_client(readable_database_id)
        with pytest.warns(DeprecationWarning, match="session_token"):
            properties = run_target_operation(
                client,
                lambda: database.read(
                    initial_headers={"x-ms-cosmos-throughput-bucket": "1"},
                    session_token="ignored",
                    response_hook=lambda headers, body: hook_calls.append(
                        (dict(headers), dict(body))
                    ),
                ),
            )
        return {
            "database_id_matches": properties["id"] == readable_database_id,
            "hook_count": len(hook_calls),
            "hook_database_id_matches": hook_calls[0][1]["id"] == readable_database_id,
            "request_charge_present": "x-ms-request-charge" in {
                key.lower() for key in hook_calls[0][0]
            },
        }

    run_on_both_backends(
        _call,
        description="read_database options and response hook",
        request_kwargs={
            "initial_headers": {"x-ms-cosmos-throughput-bucket": "1"},
            "session_token": "ignored",
            "response_hook": "<callable>",
        },
    ).assert_functional_parity()


def test_read_database_missing_maps_404():
    """A missing database raises the same typed 404 exception."""
    database_id = "parity_missing_read_db_" + uuid.uuid4().hex

    def _call(client):
        database = client.get_database_client(database_id)
        return run_target_operation(client, database.read)

    run_on_both_backends(
        _call,
        description="read_database missing 404",
    ).assert_functional_exception_parity()
