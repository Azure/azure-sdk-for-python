# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``_helpers/_request_prep.py`` — no network, no Cosmos emulator.

``build_create_item_prepared`` is the one function that takes a
customer ``create_item`` call and assembles everything the backend
needs to send the request. It glues together five smaller helpers:

* **B1 options** — turn customer kwargs (``pre_trigger_include=…``,
  ``priority=…``, …) into the internal option-key dict.
* **B2 container rid** — stamp the immutable container resource id
  into the headers under ``Constants.ContainerRID`` (so the service
  notices a recreated-container mismatch).
* **B3 auto-id** — mint a UUID4 ``id`` if the body has none and
  generation is enabled.
* **B4 PK request-byte** — turn the partition-key value into the JSON-array
  string the ``x-ms-documentdb-partitionkey`` header expects.
* **B5 body request-byte** — serialise the body dict into the exact compact
  JSON bytes that go on the network.

Each helper has its own dedicated test module that covers its
behaviour in isolation. *This* file covers only the **composition** —
that the prep function calls the right helpers in the right order
and assembles the result into a ``PreparedRequest`` whose fields
line up. It also covers the round-trips that span more than one
helper (e.g. minted id appears identically in the body, the bytes,
and the return value).

Pure in-process; runs in milliseconds.
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
    """The common case: simple body, scalar PK, all kwargs known.

    These three tests prove the prep function returns a fully-formed
    ``PreparedRequest``, that the kwargs dict is consumed (so the
    caller doesn't double-forward), and that the body bytes round-trip
    cleanly back to the dict the body now carries.
    """

    def test_returns_prepared_request_and_id(self):
        """Happy-path call → ``PreparedRequest`` with every field correctly populated by the five helpers."""
        prepared, item_id = build_create_item_prepared(
            container_link="dbs/db/colls/orders",
            body={"id": "order-42", "pk": "customerA", "total": 99.5},
            partition_key_value="customerA",
            container_rid="rid-orders-1",
            kwargs={"pre_trigger_include": "validateOrder"},
        )

        # Immutable backend-facing shape.
        self.assertIsInstance(prepared, PreparedRequest)
        # Container link passes straight through.
        self.assertEqual(prepared.container_link, "dbs/db/colls/orders")
        # Item id comes from the body (not minted; the body had one).
        self.assertEqual(item_id, "order-42")
        # B5: body bytes are the compact-JSON form.
        self.assertEqual(
            prepared.body_bytes,
            b'{"id":"order-42","pk":"customerA","total":99.5}',
        )
        # B4: PK header is the byte shape — single string value.
        self.assertEqual(prepared.partition_key_header, '["customerA"]')
        # B1: kwarg shortcut landed under the internal-option-key name.
        self.assertEqual(prepared.headers["preTriggerInclude"], "validateOrder")
        # B2: rid stamped into headers under the constant key the SDK reads.
        self.assertEqual(prepared.headers[Constants.ContainerRID], "rid-orders-1")

    def test_kwargs_dict_is_consumed_by_compose_step(self):
        """B1 pops every recognised kwarg out of the input dict so the caller doesn't double-forward to azure-core."""
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
        self.assertNotIn("pre_trigger_include", kwargs)
        self.assertNotIn("priority", kwargs)
        # Unrecognised survive.
        self.assertEqual(kwargs, {"extra_unknown": "left-alone"})

    def test_body_bytes_are_json_round_trippable(self):
        """The serialised body bytes parse back into the (post-auto-id) dict the body now carries."""
        body = {"v": 1}  # No id — B3 will mint one.
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
    """B3 (auto-id) interaction with the prep helper.

    Covers the four cases of the auto-id contract through the prep
    pipeline: missing id minted, generation disabled, and the two
    values of the ``disableAutomaticIdGeneration`` option flag.
    """

    def test_missing_id_mints_uuid_and_writes_into_body(self):
        """No id on the body → B3 mints a UUID4, writes it into the body, returns it, and embeds it in the bytes."""
        body = {"total": 99.5}
        prepared, item_id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body=body,
            partition_key_value="pk",
            container_rid="rid",
        )
        self.assertRegex(item_id, _UUID4_PATTERN)
        self.assertEqual(body["id"], item_id)
        self.assertIn(f'"id":"{item_id}"', prepared.body_bytes.decode())

    def test_disabled_id_generation_leaves_body_without_id(self):
        """``enable_automatic_id_generation=False`` → no id minted; body stays bare; ``item_id`` is empty string."""
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
        self.assertNotIn(b'"id"', prepared.body_bytes)

    def test_disable_flag_lands_in_options(self):
        """``enable_automatic_id_generation=False`` → header ``disableAutomaticIdGeneration`` is True (legacy parity)."""
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            enable_automatic_id_generation=False,
        )
        self.assertTrue(prepared.headers["disableAutomaticIdGeneration"])

    def test_enabled_flag_lands_in_options(self):
        """``enable_automatic_id_generation=True`` → header ``disableAutomaticIdGeneration`` is False (explicit)."""
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            enable_automatic_id_generation=True,
        )
        self.assertFalse(prepared.headers["disableAutomaticIdGeneration"])


class TestPartitionKeyShapes(unittest.TestCase):
    """B4 (PK request-byte serialization) interaction with the prep helper.

    Smoke-tests the four PK shapes through the composition: scalar,
    hierarchical, ``_Undefined`` sentinel, ``_Empty`` sentinel.
    Exhaustive coverage of each shape lives in
    ``test_pk_wire_unit.py``.
    """

    def test_scalar_pk_renders_as_one_element_array(self):
        """Scalar integer PK → ``"[42]"`` in the partition-key header."""
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value=42,
            container_rid="rid",
        )
        self.assertEqual(prepared.partition_key_header, "[42]")

    def test_hierarchical_pk_renders_in_order(self):
        """Hierarchical PK list → JSON array in the supplied order."""
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value=["t1", "r1"],
            container_rid="rid",
        )
        self.assertEqual(prepared.partition_key_header, '["t1","r1"]')

    def test_undefined_pk_renders_reserved_shape(self):
        """``_Undefined`` PK → reserved ``"[{}]"`` shape."""
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value=_Undefined(),
            container_rid="rid",
        )
        self.assertEqual(prepared.partition_key_header, "[{}]")

    def test_empty_pk_renders_reserved_shape(self):
        """``_Empty`` PK → reserved ``"[]"`` shape (legacy partitionless container)."""
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value=_Empty(),
            container_rid="rid",
        )
        self.assertEqual(prepared.partition_key_header, "[]")


class TestContainerRidOptional(unittest.TestCase):
    """B2 (container rid) interaction — including the None-skip path.

    The prep helper accepts ``container_rid=None`` and skips
    stamping rather than inventing a value. That's how a test
    fixture (or a future caller that doesn't have a rid yet) can
    drive the prep without violating the helper's "never invent
    state" rule.
    """

    def test_none_rid_skips_stamping(self):
        """``container_rid=None`` → ``Constants.ContainerRID`` is not in the headers map."""
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid=None,
        )
        self.assertNotIn(Constants.ContainerRID, prepared.headers)

    def test_supplied_rid_lands_in_headers_under_constant_key(self):
        """A supplied rid lands in the headers under ``Constants.ContainerRID``."""
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid-abc",
        )
        self.assertEqual(prepared.headers[Constants.ContainerRID], "rid-abc")


class TestIndexingDirective(unittest.TestCase):
    """``indexing_directive`` is a direct option (not a kwarg shortcut).

    Unlike the B1 kwarg shortcuts (which translate snake_case →
    camelCase via the COMMON_OPTIONS table), ``indexing_directive``
    flows through as its own explicit prep parameter and lands under
    ``"indexingDirective"`` only when supplied.
    """

    def test_indexing_directive_lands_when_supplied(self):
        """A supplied ``indexing_directive=N`` lands in headers as ``"indexingDirective"``."""
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            indexing_directive=1,
        )
        self.assertEqual(prepared.headers["indexingDirective"], 1)

    def test_indexing_directive_omitted_when_not_supplied(self):
        """Default (``None``) → no ``"indexingDirective"`` key in the headers."""
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
        )
        self.assertNotIn("indexingDirective", prepared.headers)


class TestPreparedRequestImmutability(unittest.TestCase):
    """The returned ``PreparedRequest`` is a frozen dataclass; the caller cannot mutate it."""

    def test_assigning_to_field_raises(self):
        """Assigning to any field on the returned ``PreparedRequest`` raises (frozen dataclass)."""
        prepared, _id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
        )
        with self.assertRaises(Exception):  # FrozenInstanceError
            prepared.container_link = "dbs/db/colls/other"  # type: ignore[misc]


class TestRoundTripWithMintedId(unittest.TestCase):
    """End-to-end: a minted id appears identically in three places.

    The auto-id contract only works if the same string ends up in the
    body dict, the serialised bytes, and the helper's return value.
    Drift between any two of those would produce duplicate documents
    on retry. This test covers all three to the same value.
    """

    def test_minted_id_appears_identically_in_three_places(self):
        """Minted UUID4 id appears in body dict, serialised bytes, and return value — all the same string."""
        body = {"pk": "customerA", "total": 99.5}
        prepared, item_id = build_create_item_prepared(
            container_link="dbs/db/colls/c",
            body=body,
            partition_key_value="customerA",
            container_rid="rid",
        )
        self.assertIsInstance(item_id, str)
        self.assertEqual(body["id"], item_id)
        decoded = json.loads(prepared.body_bytes)
        self.assertEqual(decoded["id"], item_id)
        self.assertEqual(uuid.UUID(item_id).version, 4)


if __name__ == "__main__":
    unittest.main()
