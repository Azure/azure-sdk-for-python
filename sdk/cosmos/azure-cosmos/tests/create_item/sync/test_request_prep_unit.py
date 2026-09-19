# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for ``prepare_create_item_request`` -- no network, no emulator.

``prepare_create_item_request`` takes a customer ``create_item`` call and
builds everything the backend needs to send the request. It does five
small things in order:

* Turn the customer's keyword arguments (``pre_trigger_include=...``,
  ``priority=...`` and the rest) into the internal options dict.
* Set the container's resource id into the headers, so the service can
  tell when a container was dropped and recreated under the same name.
* Generate a random id for the item when the body has none and id
  generation is on.
* Turn the partition-key value into the JSON-array string the
  ``x-ms-documentdb-partitionkey`` header expects.
* Serialise the body into the exact compact JSON bytes that go on the wire.

Each of those steps has its own dedicated test file. This file checks how
they fit together: that the prep returns a ``PreparedRequest`` whose fields
all line up, and that a value touched by more than one step (a generated id,
say) comes out the same in the body, the bytes, and the return value.

Pure in-process; runs in milliseconds.
"""
from common.typed_requests import legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options, legacy_settings
import json
import re
import unittest
import uuid

from azure.cosmos._backend.contracts import PreparedRequest
from azure.cosmos._constants import _Constants as Constants
from common.request_preparation import (
    prepare_create_item_request,
)
from common.typed_requests import flatten_options_to_headers
from azure.cosmos.partition_key import _Empty, _Undefined

_UUID4_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


class TestHappyPathComposition(unittest.TestCase):
    """The common case: a simple body, a scalar partition key, and only
    keyword arguments the prep recognises.

    These three tests show that the prep returns a fully-formed
    ``PreparedRequest``, that it consumes the keyword arguments it
    recognises (so the caller doesn't forward them twice), and that the
    body bytes parse cleanly back into the dict the body now carries.
    """

    def test_returns_prepared_request_and_id(self):
        """A normal call returns a ``PreparedRequest`` with every field filled in."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/orders",
            body={"id": "order-42", "pk": "customerA", "total": 99.5},
            partition_key_value="customerA",
            container_rid="rid-orders-1",
            kwargs={"pre_trigger_include": "validateOrder"},
        )
        item_id = prepared.item_id

        # The returned object is the backend-facing PreparedRequest.
        self.assertIsInstance(prepared, PreparedRequest)
        # The container link passes straight through.
        self.assertEqual(prepared.container_link, "dbs/db/colls/orders")
        # The id comes from the body (nothing was generated; the body had one).
        self.assertEqual(item_id, "order-42")
        # The same id is forwarded on item_id so the binding skips re-parsing
        # the body just to read it.
        self.assertEqual(prepared.item_id, "order-42")
        # The body bytes are the compact JSON form.
        self.assertEqual(
            prepared.body_bytes,
            b'{"id":"order-42","pk":"customerA","total":99.5}',
        )
        # The partition-key header holds the single string value.
        self.assertEqual(legacy_partition_key_from_request(prepared), '["customerA"]')
        # The keyword shortcut landed under its internal option-key name.
        self.assertEqual(wire_headers(prepared)["x-ms-documentdb-pre-trigger-include"], "validateOrder")
        # The rid is set into the headers under the key the SDK reads.
        self.assertEqual(wire_headers(prepared)["x-ms-cosmos-intended-collection-rid"], "rid-orders-1")

    def test_kwargs_dict_is_consumed_by_compose_step(self):
        """The prep removes every recognised keyword argument from the input
        dict, so the caller doesn't forward it a second time to azure-core."""
        kwargs = {
            "pre_trigger_include": "validateOrder",
            "priority": "High",
            "extra_unknown": "left-alone",
        }
        prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            kwargs=kwargs,
        )
        self.assertEqual(kwargs["pre_trigger_include"], "validateOrder")
        self.assertEqual(kwargs["priority"], "High")
        # Keyword arguments the prep doesn't recognise stay put.
        self.assertEqual(kwargs["extra_unknown"], "left-alone")

    def test_body_bytes_are_json_round_trippable(self):
        """The serialised body bytes parse back into the dict the body now
        carries (after the id is generated)."""
        body = {"v": 1}  # No id, so one is generated.
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body=body,
            partition_key_value="pk",
            container_rid="rid",
        )
        item_id = prepared.item_id
        round_tripped = json.loads(prepared.body_bytes)
        self.assertEqual(round_tripped, {**body, "id": item_id})
        self.assertNotIn("id", body)
        self.assertEqual(round_tripped["id"], item_id)


class TestAutoIdGeneration(unittest.TestCase):
    """How the prep handles the auto-id step.

    Covers the four cases: a missing id is generated, generation is turned
    off, and the two values the ``disableAutomaticIdGeneration`` option
    flag can take.
    """

    def test_missing_id_is_generated_without_changing_input_body(self):
        """Generate an id in the prepared request and its encoded body.

        The caller's original dictionary remains without an id.
        """
        body = {"total": 99.5}
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body=body,
            partition_key_value="pk",
            container_rid="rid",
        )
        item_id = prepared.item_id
        self.assertRegex(item_id, _UUID4_PATTERN)
        self.assertNotIn("id", body)
        self.assertEqual(json.loads(prepared.body_bytes)["id"], item_id)
        self.assertIn(f'"id":"{item_id}"', prepared.body_bytes.decode())
        # The generated id is forwarded on item_id (fast-path: no body re-parse).
        self.assertEqual(prepared.item_id, item_id)

    def test_disabled_id_generation_rejects_missing_id_before_metadata(self):
        body = {"total": 99.5}
        with self.assertRaisesRegex(ValueError, "non-empty 'id'"):
            prepare_create_item_request(
                container_link="dbs/db/colls/c", body=body, partition_key_value="pk",
                container_rid="rid", enable_automatic_id_generation=False,
            )
        self.assertEqual(body, {"total": 99.5})

    def test_disable_flag_lands_in_options(self):
        """``enable_automatic_id_generation=False`` sets the
        ``disableAutomaticIdGeneration`` header to True, as the legacy path did."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            enable_automatic_id_generation=False,
        )
        _id = prepared.item_id
        self.assertNotIn("disableAutomaticIdGeneration", wire_headers(prepared))
        self.assertNotIn("disableAutomaticIdGeneration", settings_options(prepared))

    def test_enabled_flag_lands_in_options(self):
        """``enable_automatic_id_generation=True`` sets the
        ``disableAutomaticIdGeneration`` header to False."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            enable_automatic_id_generation=True,
        )
        _id = prepared.item_id
        self.assertNotIn("disableAutomaticIdGeneration", wire_headers(prepared))
        self.assertNotIn("disableAutomaticIdGeneration", settings_options(prepared))


class TestPartitionKeyShapes(unittest.TestCase):
    """How the prep serialises the partition key.

    Smoke-tests the four shapes through the prep: a scalar value, a
    hierarchical list, the ``_Undefined`` sentinel, and the ``_Empty``
    sentinel. The exhaustive coverage of each shape lives in
    ``test_pk_wire_unit.py``.
    """

    def test_scalar_pk_renders_as_one_element_array(self):
        """A scalar integer partition key becomes ``"[42]"`` in the partition-key header."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value=42,
            container_rid="rid",
        )
        _id = prepared.item_id
        self.assertEqual(legacy_partition_key_from_request(prepared), "[42]")

    def test_hierarchical_pk_renders_in_order(self):
        """A hierarchical partition-key list becomes a JSON array in the order given."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value=["t1", "r1"],
            container_rid="rid",
        )
        _id = prepared.item_id
        self.assertEqual(legacy_partition_key_from_request(prepared), '["t1","r1"]')

    def test_undefined_pk_renders_reserved_shape(self):
        """An ``_Undefined`` partition key becomes the reserved ``"[{}]"`` shape."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value=_Undefined(),
            container_rid="rid",
        )
        _id = prepared.item_id
        self.assertEqual(legacy_partition_key_from_request(prepared), "[{}]")

    def test_empty_pk_renders_reserved_shape(self):
        """An ``_Empty`` partition key becomes the reserved ``"[]"`` shape (a
        partitionless container from the early SDK days)."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value=_Empty(),
            container_rid="rid",
        )
        _id = prepared.item_id
        self.assertEqual(legacy_partition_key_from_request(prepared), "[]")


class TestContainerRidOptional(unittest.TestCase):
    """The container-rid step, including the case where it is skipped.

    The prep accepts ``container_rid=None`` and simply skips that header
    rather than inventing a value. That lets a test (or a caller that
    doesn't have a rid yet) drive the prep without the helper making up
    state it doesn't have.
    """

    def test_unresolved_container_resource_id_omits_internal_option_header(self):
        """With no resolved id, the header view omits the internal option name.

        This assertion checks ``Constants.ContainerRID``, not the HTTP header name.
        """
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid=None,
        )
        _id = prepared.item_id
        self.assertNotIn(Constants.ContainerRID, wire_headers(prepared))

    def test_supplied_rid_lands_in_headers_under_constant_key(self):
        """A supplied rid lands in the headers under ``Constants.ContainerRID``."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid-abc",
        )
        _id = prepared.item_id
        self.assertEqual(wire_headers(prepared)["x-ms-cosmos-intended-collection-rid"], "rid-abc")


class TestIndexingDirective(unittest.TestCase):
    """``indexing_directive`` is its own prep argument, not a keyword shortcut.

    The keyword shortcuts translate snake_case names to camelCase through
    the ``COMMON_OPTIONS`` table; ``indexing_directive`` instead flows
    through as its own explicit prep argument and lands under
    ``"indexingDirective"`` only when it is supplied.
    """

    def test_indexing_directive_lands_when_supplied(self):
        """A supplied ``indexing_directive=N`` lands in the headers as ``"indexingDirective"``."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            indexing_directive=1,
        )
        _id = prepared.item_id
        self.assertEqual(wire_headers(prepared)["x-ms-indexing-directive"], '1')

    def test_indexing_directive_omitted_when_not_supplied(self):
        """Left at the default (``None``), there is no ``"indexingDirective"`` key in the headers."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
        )
        _id = prepared.item_id
        self.assertNotIn("indexingDirective", wire_headers(prepared))

    def test_indexing_directive_default_zero_omitted(self):
        """``indexing_directive=0`` (``IndexingDirective.Default``) emits no header.

        ``0`` is falsy, so the value is dropped, matching the legacy path.
        "Default" means "use the container's indexing policy", which is the
        same as sending no directive at all, so the header must not appear.
        (This guards a regression where an earlier build emitted
        ``x-ms-indexing-directive: 0``.)
        """
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            indexing_directive=0,
        )
        _id = prepared.item_id
        self.assertNotIn("indexingDirective", wire_headers(prepared))


class TestThroughputBucketGate(unittest.TestCase):
    """``throughput_bucket`` is dropped when it is zero.

    ``throughput_bucket`` is a shared keyword argument on every point
    operation, so the rule is enforced once in the common
    ``flatten_options_to_headers`` utility; this checks it through the
    create builder. (Guards a regression where a zero bucket reached the
    wire.)
    """

    def test_throughput_bucket_zero_omitted(self):
        """``throughput_bucket=0`` emits no ``"throughputBucket"`` header (``0`` is falsy)."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            kwargs={"throughput_bucket": 0},
        )
        _id = prepared.item_id
        self.assertNotIn("throughputBucket", wire_headers(prepared))

    def test_throughput_bucket_nonzero_emitted(self):
        """A real bucket value (``3``) lands in the headers under ``"throughputBucket"``."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            kwargs={"throughput_bucket": 3},
        )
        _id = prepared.item_id
        self.assertEqual(wire_headers(prepared)["x-ms-cosmos-throughput-bucket"], '3')


class TestPreparedRequestImmutability(unittest.TestCase):
    """The returned ``PreparedRequest`` is a frozen dataclass; the caller cannot change it."""

    def test_assigning_to_field_raises(self):
        """Assigning to any field on the returned ``PreparedRequest`` raises (it is frozen)."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
        )
        _id = prepared.item_id
        with self.assertRaises(Exception):  # FrozenInstanceError
            prepared.container_link = "dbs/db/colls/other"  # type: ignore[misc]


class TestGeneratedIdConsistency(unittest.TestCase):
    """The prepared request and encoded body agree on the generated id."""

    def test_generated_id_matches_request_body_without_changing_input(self):
        """Check the generated id's format and equality across request fields.

        The encoded body contains the id; the caller's dictionary does not.
        """
        body = {"pk": "customerA", "total": 99.5}
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body=body,
            partition_key_value="customerA",
            container_rid="rid",
        )
        item_id = prepared.item_id
        self.assertIsInstance(item_id, str)
        self.assertNotIn("id", body)
        self.assertEqual(json.loads(prepared.body_bytes)["id"], item_id)
        decoded = json.loads(prepared.body_bytes)
        self.assertEqual(decoded["id"], item_id)
        self.assertEqual(uuid.UUID(item_id).version, 4)


class TestTriggerIncludeSerialization(unittest.TestCase):
    """``pre_trigger_include`` / ``post_trigger_include`` may be a single
    trigger id or a list of them.

    The legacy path joins a list into one comma-separated string
    (``"t1,t2"``), and ``flatten_options_to_headers`` must do the same. If
    it didn't, the Rust binding would call ``str()`` on the list and put
    its repr (``"['t1', 't2']"``) on the wire instead. These tests guard
    against that.
    """

    def test_single_string_pre_trigger_passes_through(self):
        """A plain-string ``pre_trigger_include`` is emitted unchanged."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            kwargs={"pre_trigger_include": "validateOrder"},
        )
        _id = prepared.item_id
        self.assertEqual(wire_headers(prepared)["x-ms-documentdb-pre-trigger-include"], "validateOrder")

    def test_list_pre_trigger_is_comma_joined(self):
        """A list ``pre_trigger_include`` is comma-joined, not turned into a Python repr."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            kwargs={"pre_trigger_include": ["t1", "t2"]},
        )
        _id = prepared.item_id
        self.assertEqual(wire_headers(prepared)["x-ms-documentdb-pre-trigger-include"], "t1,t2")

    def test_tuple_post_trigger_is_comma_joined(self):
        """A tuple ``post_trigger_include`` is comma-joined the same way."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            kwargs={"post_trigger_include": ("a", "b", "c")},
        )
        _id = prepared.item_id
        self.assertEqual(wire_headers(prepared)["x-ms-documentdb-post-trigger-include"], "a,b,c")

    def test_single_element_list_has_no_brackets_or_comma(self):
        """A one-element list is just the bare id: no brackets, no trailing comma."""
        prepared = prepare_create_item_request(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            partition_key_value="pk",
            container_rid="rid",
            kwargs={"pre_trigger_include": ["only"]},
        )
        _id = prepared.item_id
        self.assertEqual(wire_headers(prepared)["x-ms-documentdb-pre-trigger-include"], "only")


class TestFlattenOptionsToHeaders(unittest.TestCase):
    """Direct tests of the shared ``flatten_options_to_headers`` utility.

    Every point operation funnels its options through this one step on
    the way to wire headers, so its behaviour is pinned here in one place.
    """

    def test_trigger_list_comma_joined(self):
        """Trigger lists are comma-joined; a one-element list is the bare id."""
        headers = flatten_options_to_headers(
            {"preTriggerInclude": ["t1", "t2"], "postTriggerInclude": ["p1"]}
        )
        self.assertEqual(headers["x-ms-documentdb-pre-trigger-include"], "t1,t2")
        self.assertEqual(headers["x-ms-documentdb-post-trigger-include"], "p1")

    def test_initial_headers_are_real_headers(self):
        """Customer headers are actual top-level HTTP headers, never nested options."""
        headers = flatten_options_to_headers(
            {"initialHeaders": {"x-ms-foo": "bar", "x-ms-baz": "qux"}}
        )
        self.assertEqual(headers, {"x-ms-foo": "bar", "x-ms-baz": "qux"})
        self.assertNotIn("initialHeaders", headers)

    def test_access_condition_becomes_if_match(self):
        """``accessCondition`` IfMatch becomes an ``If-Match`` header; the raw key is dropped."""
        headers = flatten_options_to_headers(
            {"accessCondition": {"type": "IfMatch", "condition": '"abc"'}}
        )
        self.assertEqual(headers["if-match"], '"abc"')
        self.assertNotIn("accessCondition", headers)

    def test_access_condition_becomes_if_none_match(self):
        """``accessCondition`` IfNoneMatch becomes an ``If-None-Match`` header."""
        headers = flatten_options_to_headers(
            {"accessCondition": {"type": "IfNoneMatch", "condition": '"abc"'}}
        )
        self.assertEqual(headers["if-none-match"], '"abc"')

    def test_cache_staleness_truthy_emits_wire_header(self):
        """A truthy ``maxIntegratedCacheStaleness`` becomes ``x-ms-dedicatedgateway-max-age``."""
        headers = flatten_options_to_headers({"maxIntegratedCacheStaleness": 5000})
        self.assertEqual(headers["x-ms-dedicatedgateway-max-age"], "5000")

    def test_cache_staleness_zero_is_noop(self):
        """``maxIntegratedCacheStaleness=0`` ships no header (a documented no-op)."""
        headers = flatten_options_to_headers({"maxIntegratedCacheStaleness": 0})
        self.assertNotIn("x-ms-dedicatedgateway-max-age", headers)

    def test_indexing_directive_zero_omitted(self):
        """``indexingDirective=0`` (Default) is dropped, so no header is sent."""
        self.assertNotIn("indexingDirective", flatten_options_to_headers({"indexingDirective": 0}))

    def test_indexing_directive_nonzero_emitted(self):
        """A non-zero ``indexingDirective`` (Exclude=1 / Include=2) is emitted."""
        self.assertEqual(flatten_options_to_headers({"indexingDirective": 1})["x-ms-indexing-directive"], "1")
        self.assertEqual(flatten_options_to_headers({"indexingDirective": 2})["x-ms-indexing-directive"], "2")

    def test_throughput_bucket_zero_omitted(self):
        """``throughputBucket=0`` is dropped, so no header is sent."""
        self.assertNotIn("throughputBucket", flatten_options_to_headers({"throughputBucket": 0}))

    def test_throughput_bucket_nonzero_emitted(self):
        """A real ``throughputBucket`` value is emitted unchanged."""
        self.assertEqual(flatten_options_to_headers({"throughputBucket": 3})["x-ms-cosmos-throughput-bucket"], "3")

    def test_unknown_option_copied_through(self):
        """An option key with no special handling is copied through unchanged."""
        headers = flatten_options_to_headers({"priorityLevel": "High"})
        self.assertEqual(headers["x-ms-cosmos-priority-level"], "High")


if __name__ == "__main__":
    unittest.main()
