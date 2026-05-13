# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``_helpers/_request_prep.py`` â—” no network, no Cosmos emulator.

These tests exercise the *composition* of the five wire-prep helpers
(B1 options, B2 container rid, B3 auto-id, B4 PK wire, B5 body wire)
into a single ``PreparedRequest``. Each individual helper has its
own dedicated test module; this module covers only the joining logic
and the round-trips that depend on more than one helper.
"""
import json
import re
import unittest
import uuid

from azure.cosmos._backend.base import PreparedRequest
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._request_prep import build_create_item_prepared
from azure.cosmos.partition_key import _Empty, _Undefined

_UUID4_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


class TestHappyPathComposition(unittest.TestCase):
    """The common case: simple body, scalar PK, all kwargs known."""

    def test_returns_prepared_request_and_id(self):
        prepared, item_id = build_create_item_prepared(
            container_link="dbs/db/colls/orders",
            body={"id": "order-42", "pk": "customerA", "total": 99.5},
            partition_key_value="customerA",
            container_rid="rid-orders-1",
            kwargs={"pre_trigger_include": "validateOrder"},
        )

        # The PreparedRequest is the immutable backend-facing shape.
        self.assertIsInstance(prepared, PreparedRequest)

        # The container link passes straight through.
        self.assertEqual(prepared.container_link, "dbs/db/colls/orders")

        # The item id is what the body had.
        self.assertEqual(item_id, "order-42")

        # Body bytes are the compact-JSON form (B5).
        self.assertEqual(
            prepared.body_bytes,
            b'{"id":"order-42","pk":"customerA","total":99.5}',
        )

        # PK header is the wire shape (B4) â—” single string value.
        self.assertEqual(prepared.partition_key_header, '["customerA"]')

        # The B1 kwarg shortcut landed in headers under the
        # internal-option-key name.
        self.assertEqual(prepared.headers["preTriggerInclude"], "validateOrder")

        # B2 stamped the rid into the headers map under the constant
        # key the rest of the SDK reads.
        self.assertEqual(
            prepared.headers[Constants.ContainerRID],
            "rid-orders-1",
        )

    def test_kwargs_dict_is_consumed_by_compose_step(self):
        # B1 pops every recognised key out of the kwargs dict the
        # caller passed in â—” so the caller can forward the remaining
        # kwargs to azure-core without double-handling.
        kwargs = {
            "pre_trigger_include": "validateOrder",
            "priority": "High",
            "extra_unknown": "left-alone",
        }
        build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            kwargs=kwargs,
        )
        # Recognised kwargs are gone.
        self.assertNotIn("pre_trigger_include", kwargs)
        self.assertNotIn("priority", kwargs)
        # Unrecognised survive.
        self.assertEqual(kwargs, {"extra_unknown": "left-alone"})

    def test_body_bytes_are_json_round_trippable(self):
        # Sanity check on B5 composition: the bytes the helper
        # produced parse back into the dict the body now carries
        # (after auto-id mutation, when applicable).
        body = {"v": 1}  # No id â—” B3 will mint one.
        prepared, item_id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body=body,
            partition_key_value="pk",
            container_rid="rid",
        )
        round_tripped = json.loads(prepared.body_bytes)
        self.assertEqual(round_tripped, body)
        self.assertEqual(round_tripped["id"], item_id)


class TestAutoIdGeneration(unittest.TestCase):
    """B3 (auto-id) interaction with the prep helper."""

    def test_missing_id_mints_uuid_and_writes_into_body(self):
        body = {"total": 99.5}
        prepared, item_id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body=body,
            partition_key_value="pk",
            container_rid="rid",
        )
        # The minted id is in body, the return tuple, and the bytes.
        self.assertRegex(item_id, _UUID4_PATTERN)
        self.assertEqual(body["id"], item_id)
        self.assertIn(f'"id":"{item_id}"', prepared.body_bytes.decode())

    def test_disabled_id_generation_leaves_body_without_id(self):
        # The customer asked us not to mint. We emit an empty string
        # for the item_id so the return type stays str.
        body = {"total": 99.5}
        prepared, item_id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body=body,
            partition_key_value="pk",
            container_rid="rid",
            enable_automatic_id_generation=False,
        )
        self.assertEqual(item_id, "")
        self.assertNotIn("id", body)
        # Body bytes also lack the id field â—” what the legacy path does.
        self.assertNotIn(b'"id"', prepared.body_bytes)

    def test_disable_flag_lands_in_options(self):
        # disableAutomaticIdGeneration is the negation of the kwarg;
        # the legacy path writes both forms. Make sure the helper
        # writes the same option-key the legacy GetHeaders consumer
        # reads.
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            enable_automatic_id_generation=False,
        )
        self.assertTrue(prepared.headers["disableAutomaticIdGeneration"])

    def test_enabled_flag_lands_in_options(self):
        # And the True default also lands explicitly.
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            enable_automatic_id_generation=True,
        )
        self.assertFalse(prepared.headers["disableAutomaticIdGeneration"])


class TestPartitionKeyShapes(unittest.TestCase):
    """B4 (PK wire serialization) interaction."""

    def test_scalar_pk_renders_as_one_element_array(self):
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value=42,
            container_rid="rid",
        )
        self.assertEqual(prepared.partition_key_header, "[42]")

    def test_hierarchical_pk_renders_in_order(self):
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value=["t1", "r1"],
            container_rid="rid",
        )
        self.assertEqual(prepared.partition_key_header, '["t1","r1"]')

    def test_undefined_pk_renders_reserved_shape(self):
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value=_Undefined(),
            container_rid="rid",
        )
        self.assertEqual(prepared.partition_key_header, "[{}]")

    def test_empty_pk_renders_reserved_shape(self):
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value=_Empty(),
            container_rid="rid",
        )
        self.assertEqual(prepared.partition_key_header, "[]")


class TestContainerRidOptional(unittest.TestCase):
    """B2 (container rid) interaction â—” including the None-skip path."""

    def test_none_rid_skips_stamping(self):
        # A test fixture / future caller may not have a rid. The
        # helper does not invent one; it skips stamping entirely.
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid=None,
        )
        self.assertNotIn(Constants.ContainerRID, prepared.headers)

    def test_supplied_rid_lands_in_headers_under_constant_key(self):
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid-abc",
        )
        self.assertEqual(prepared.headers[Constants.ContainerRID], "rid-abc")


class TestIndexingDirective(unittest.TestCase):
    """``indexing_directive`` is not a kwarg-shortcut; it lands directly."""

    def test_indexing_directive_lands_when_supplied(self):
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            indexing_directive=1,
        )
        self.assertEqual(prepared.headers["indexingDirective"], 1)

    def test_indexing_directive_omitted_when_not_supplied(self):
        # Default is None â—” no key added.
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
        )
        self.assertNotIn("indexingDirective", prepared.headers)


class TestPreparedRequestImmutability(unittest.TestCase):
    """The returned ``PreparedRequest`` is frozen; the caller cannot mutate it."""

    def test_assigning_to_field_raises(self):
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
        )
        # frozen=True dataclasses raise on attribute assignment.
        with self.assertRaises(Exception):
            prepared.container_link = "dbs/db/colls/other"  # type: ignore[misc]


class TestRoundTripWithMintedId(unittest.TestCase):
    """End-to-end: minted id is consistent across body, bytes, and return."""

    def test_minted_id_appears_identically_in_three_places(self):
        body = {"pk": "customerA", "total": 99.5}
        prepared, item_id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body=body,
            partition_key_value="customerA",
            container_rid="rid",
        )
        # 1. Returned by the helper.
        self.assertIsInstance(item_id, str)
        # 2. Written into the body dict.
        self.assertEqual(body["id"], item_id)
        # 3. Present in the serialized bytes.
        decoded = json.loads(prepared.body_bytes)
        self.assertEqual(decoded["id"], item_id)
        # And the value is a UUID4.
        self.assertEqual(uuid.UUID(item_id).version, 4)


if __name__ == "__main__":
    unittest.main()
