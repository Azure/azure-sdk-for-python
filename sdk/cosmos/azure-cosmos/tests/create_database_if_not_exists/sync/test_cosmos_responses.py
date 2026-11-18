# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Legacy response assertions and new get-or-create regressions using Rust."""
from contextlib import ExitStack
import os
import unittest
import uuid
from unittest.mock import patch

import pytest

from azure.cosmos import CosmosClient, exceptions


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestCosmosResponses(unittest.TestCase):
    def setUp(self):
        self.client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust"
        )
        self.addCleanup(self.client.close)

    def test_create_database_if_not_exists_creation_race_returns_winner_rust(self):
        """New test, not copied from legacy: recover a real conflict without changing the winner."""
        # Source: (new) Real creation conflict returns the winner without changing its throughput.
        self._exercise_creation_race(delete_winner=False)

    def test_create_database_if_not_exists_creation_race_missing_winner_rust(self):
        """New test, not copied from legacy: propagate a failed follow-up read without creating again."""
        # Source: (new) A deleted race winner propagates the final read failure without another create.
        self._exercise_creation_race(delete_winner=True)

    def _exercise_creation_race(self, *, delete_winner):
        database_id = "responses_race_" + str(uuid.uuid4())
        responses, hooks, winner = [], [], []

        def hook(headers, properties):
            hooks.append((dict(headers), dict(properties)))
            properties["id"] = "hook-only"

        with CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust"
        ) as competitor, ExitStack() as stack:
            for connection in (self.client.client_connection, competitor.client_connection):
                assert "pipeline_client" not in vars(connection)
                for method in ("_setup", "GetDatabaseAccount", "ReadDatabase", "CreateDatabase"):
                    stack.enter_context(patch.object(
                        connection, method, side_effect=AssertionError("legacy request executed"),
                    ))

            def after_response(operation, status, headers):
                responses.append((operation, status, dict(headers)))
                if operation == "read_database" and status == 404 and not winner:
                    _, properties = competitor.create_database(
                        database_id, offer_throughput=1000, return_properties=True,
                    )
                    winner.append(properties)
                elif operation == "create_database" and status == 409 and delete_winner:
                    competitor.delete_database(database_id)

            execute = self.client._adapter.execute

            def execute_with_competitor(prepared, *, deadline=None):
                # Interleave real service requests; do not synthesize the 404 or 409.
                try:
                    response = execute(prepared, deadline=deadline)
                except exceptions.CosmosHttpResponseError as error:
                    after_response(prepared.op, error.status_code, error.headers)
                    raise
                after_response(prepared.op, response.status_code, response.headers)
                return response

            stack.enter_context(patch.object(self.client._adapter, "execute", new=execute_with_competitor))
            try:
                options = dict(offer_throughput=2000, return_properties=True, response_hook=hook, timeout=30)
                if delete_winner:
                    with pytest.raises(exceptions.CosmosResourceNotFoundError) as caught:
                        self.client.create_database_if_not_exists(database_id, **options)
                    assert caught.value.status_code == 404
                    assert caught.value.headers["x-ms-activity-id"] == responses[-1][2]["x-ms-activity-id"]
                    assert hooks == []
                else:
                    database, properties = self.client.create_database_if_not_exists(database_id, **options)
                    assert database.id == properties["id"] == database_id
                    assert properties["_rid"] == winner[0]["_rid"]
                    assert len(hooks) == 1
                    assert hooks[0][1]["_rid"] == winner[0]["_rid"]
                    assert hooks[0][0]["x-ms-activity-id"] == responses[-1][2]["x-ms-activity-id"]
                    assert competitor.get_database_client(database_id).get_throughput().offer_throughput == 1000
                assert [(operation, status) for operation, status, _ in responses] == [
                    ("read_database", 404), ("create_database", 409),
                    ("read_database", 404 if delete_winner else 200),
                ]
                for connection in (self.client.client_connection, competitor.client_connection):
                    assert "pipeline_client" not in vars(connection)
            finally:
                try:
                    competitor.delete_database(database_id)
                except exceptions.CosmosResourceNotFoundError:
                    pass

    def test_create_database_if_not_exists_rejects_trailing_slash_before_read_rust(self):
        """Invalid names fail locally for both missing and existing databases."""
        # Source: (new) Reject trailing-slash IDs before Rust dispatch; preserve getter read compatibility.
        database_id = "responses_test" + str(uuid.uuid4())

        def reject_invalid_id():
            with patch.object(self.client._adapter, "execute", side_effect=AssertionError("request dispatched")):
                with pytest.raises(ValueError, match="Id contains illegal chars"):
                    self.client.create_database_if_not_exists(database_id + "/")

        reject_invalid_id()
        created = self.client.create_database_if_not_exists(database_id)
        try:
            assert created.id == database_id
            reject_invalid_id()
            assert self.client.get_database_client(database_id + "/").read()["id"] == database_id
        finally:
            self.client.delete_database(database_id)

    def test_create_database_if_not_exists_headers_rust(self):
        """First call creates the database and returns its id with populated headers.

        This is the create branch: nothing exists yet. The returned properties
        must carry the id that was asked for, and the headers must hold the
        request unit charge.
        """
        # Source: tests/test_cosmos_responses.py::TestCosmosResponses.test_create_database_if_not_exists_headers
        database_id = "responses_test" + str(uuid.uuid4())
        first_response = self.client.create_database_if_not_exists(id=database_id, return_properties=True)
        try:
            assert first_response[1]["id"] == database_id
            assert len(first_response[1].get_response_headers()) > 0
        finally:
            self.client.delete_database(database_id)

    def test_create_database_if_not_exists_headers_negative_rust(self):
        """Calls against an existing database return that same database, with headers.

        Despite the name, nothing fails here. "Negative" means the create was
        skipped: the database is made up front, then asked for twice more.

        The strongest check is on ``_rid``, the resource id the service assigns
        at creation time. Both responses must carry the same ``_rid`` as the
        database created up front, which proves the existing database was
        handed back rather than a fresh one quietly created in its place. The
        id alone could not tell those two apart.

        Headers must still be populated on this branch, since it reads rather
        than creates and is the one more likely to return them empty.
        """
        # Source: tests/test_cosmos_responses.py::TestCosmosResponses.test_create_database_if_not_exists_headers_negative
        database_id = "responses_test" + str(uuid.uuid4())
        _, existing = self.client.create_database(id=database_id, return_properties=True)
        try:
            first_response = self.client.create_database_if_not_exists(id=database_id, return_properties=True)
            second_response = self.client.create_database_if_not_exists(id=database_id, return_properties=True)
            assert first_response[1]["id"] == second_response[1]["id"] == database_id
            assert first_response[1]["_rid"] == second_response[1]["_rid"] == existing["_rid"]
            assert len(second_response[1].get_response_headers()) > 0
        finally:
            self.client.delete_database(database_id)
