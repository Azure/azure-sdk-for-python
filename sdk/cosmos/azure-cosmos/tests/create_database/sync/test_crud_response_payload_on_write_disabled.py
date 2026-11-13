# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Legacy database-ID validation with response payload suppression enabled."""

import unittest

import pytest

from config import clients
from config.settings import unique_database_id


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestCRUDOperationsResponsePayloadOnWriteDisabled(unittest.TestCase):
    def setUp(self):
        self.key_client = clients.create_setup_client(_backend="rust", no_response_on_write=True)
        self.addCleanup(self.key_client.close)

    def test_id_validation_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_id_validation
        try:
            self.key_client.create_database(id="id_with_space ")
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual("Id ends with a space or newline.", e.args[0])

        try:
            self.key_client.create_database(id="id_with_illegal/_char")
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual("Id contains illegal chars.", e.args[0])

        try:
            self.key_client.create_database(id="id_with_illegal\\_char")
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual("Id contains illegal chars.", e.args[0])

        try:
            self.key_client.create_database(id="id_with_illegal?_char")
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual("Id contains illegal chars.", e.args[0])

        try:
            self.key_client.create_database(id="id_with_illegal#_char")
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual("Id contains illegal chars.", e.args[0])

        db = self.key_client.create_database(id=" " + unique_database_id("id-begin-space"))
        self.addCleanup(self.key_client.delete_database, db.id)
        self.assertTrue(True)
