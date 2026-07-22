# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Live sync parity tests for ``CosmosClient.create_database``."""
from __future__ import annotations

import os
import uuid

from common._parity_helpers import (
    run_on_both_backends,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

from azure.cosmos import CosmosClient, ThroughputProperties


pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


def _database_id(label):
    return "parity_create_db_{}_{}".format(label, uuid.uuid4().hex[:12])


def _cleanup(database_ids):
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    try:
        for database_id in database_ids:
            try:
                client.delete_database(database_id)
            except Exception:  # pylint: disable=broad-except
                pass
    finally:
        client.close()


def _run_case(label, call):
    database_ids = []

    def _do(client):
        database_id = _database_id(label)
        database_ids.append(database_id)
        return call(client, database_id)

    try:
        return run_on_both_backends(_do, description=label)
    finally:
        _cleanup(database_ids)


def test_create_database_baseline_properties():
    """Minimal create returns the same customer-visible database document."""

    def _call(client, database_id):
        _proxy, properties = client.create_database(database_id, return_properties=True)
        return dict(properties)

    _run_case("create_database baseline", _call).assert_functional_parity()


def test_create_database_manual_throughput():
    """Manual database throughput is created and read back identically."""

    def _call(client, database_id):
        database = client.create_database(database_id, offer_throughput=1000)
        throughput = database.get_throughput()
        return {"id": database.id, "offer_throughput": throughput.offer_throughput}

    _run_case("create_database manual throughput", _call).assert_functional_parity()


def test_create_database_autoscale_zero_increment():
    """Autoscale max throughput and an explicit zero increment survive the request."""

    def _call(client, database_id):
        database = client.create_database(
            database_id,
            offer_throughput=ThroughputProperties(
                auto_scale_max_throughput=5000,
                auto_scale_increment_percent=0,
            ),
        )
        throughput = database.get_throughput()
        return {
            "id": database.id,
            "auto_scale_max_throughput": throughput.auto_scale_max_throughput,
            "auto_scale_increment_percent": throughput.auto_scale_increment_percent,
        }

    _run_case("create_database autoscale increment zero", _call).assert_functional_parity()


def test_create_database_options_and_response_hook():
    """Throughput bucket, initial headers and response hook work on both backends."""

    def _call(client, database_id):
        hook_calls = []
        _proxy, properties = client.create_database(
            database_id,
            throughput_bucket=1,
            initial_headers={"x-ms-cosmos-throughput-bucket": "1"},
            return_properties=True,
            response_hook=lambda headers, body: hook_calls.append((dict(headers), body)),
        )
        return {
            "database_id_matches": properties["id"] == database_id,
            "hook_count": len(hook_calls),
            "hook_body_id_matches": hook_calls[0][1]["id"] == properties["id"],
            "request_charge_present": "x-ms-request-charge" in {
                key.lower() for key in hook_calls[0][0]
            },
        }

    _run_case("create_database options and response hook", _call).assert_functional_parity()


def test_create_database_duplicate_maps_409():
    """Creating the same database twice raises the same typed 409 exception."""

    def _call(client, database_id):
        client.create_database(database_id)
        return client.create_database(database_id)

    _run_case(
        "create_database duplicate 409", _call
    ).assert_functional_exception_parity()
