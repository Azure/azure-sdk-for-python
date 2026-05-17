# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``_helpers/_auto_id.py`` — no network, no Cosmos emulator.

When a customer calls ``container.create_item(body)`` without putting
an ``"id"`` field on the body, the SDK has to invent one (a random
UUID4) and stamp it onto the document before sending it. That tiny
piece of logic lives in ``ensure_item_id`` and these tests cover its
behavior, branch by branch.

Why this matters: if the SDK ever minted one id but routed the
request using a *different* id (e.g. for a retry), the same logical
write could land in storage twice under two different ids. There is
no loud error for that — it just shows up later as duplicated
documents. So every branch of ``ensure_item_id`` (id present, id
missing, id falsy, generation disabled) gets its own test here.

These tests are pure-Python and run in milliseconds; they do not
need the emulator, credentials, or the rust binding.
"""
import re
import unittest
import uuid

from azure.cosmos._helpers._auto_id import ensure_item_id

# Standard UUID4 string shape: 8-4-4-4-12 hex with the version nibble
# fixed to 4 and the variant nibble in [8,9,a,b].
_UUID4_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


class TestEnsureItemIdWhenIdAlreadyPresent(unittest.TestCase):
    """Caller-supplied id wins.

    When the body already has a truthy ``"id"``, the helper must
    return that id verbatim and leave the body untouched — no
    minting, no overwriting, no surprise mutation.
    """

    def test_existing_string_id_is_returned(self):
        """A normal string id is returned as-is and the body is not mutated."""
        body = {"id": "order-42", "total": 99.5}
        returned = ensure_item_id(body)
        self.assertEqual(returned, "order-42")
        self.assertEqual(body, {"id": "order-42", "total": 99.5})

    def test_existing_id_is_returned_even_when_generate_is_false(self):
        """``generate=False`` does not strip an id that the caller already supplied."""
        body = {"id": "order-42"}
        returned = ensure_item_id(body, generate=False)
        self.assertEqual(returned, "order-42")
        self.assertEqual(body, {"id": "order-42"})

    def test_existing_non_string_truthy_id_passed_through_unchanged(self):
        """A non-string truthy id (e.g. ``int``) is passed through, matching legacy behavior.

        Cosmos rejects non-string ids server-side with HTTP 400. The
        legacy code path forwarded them anyway; we deliberately match
        that so existing customer fixtures keep producing the same
        request payload (and the same server-side error).
        """
        body = {"id": 123}
        returned = ensure_item_id(body)
        self.assertEqual(returned, 123)
        self.assertEqual(body, {"id": 123})


class TestEnsureItemIdWhenIdMissing(unittest.TestCase):
    """Missing or falsy id triggers minting (or returns ``None`` if disabled).

    "Falsy" mirrors the legacy ``not document.get("id")`` check:
    missing key, ``None``, empty string, ``0`` and ``False`` all count
    as "no id" and cause a UUID4 to be minted when ``generate=True``.
    With ``generate=False``, those same inputs produce ``None`` and
    leave the body alone.
    """

    def test_missing_id_mints_uuid_and_mutates_body(self):
        """No ``id`` key at all: a UUID4 is minted, written into the body, and returned."""
        body = {"total": 99.5}
        returned = ensure_item_id(body)
        self.assertIsNotNone(returned)
        # Returned value is exactly what got written into the body.
        self.assertEqual(body["id"], returned)
        # Other fields are preserved untouched.
        self.assertEqual(body["total"], 99.5)
        # Minted id is a UUID4 string in canonical form.
        self.assertIsInstance(returned, str)
        self.assertRegex(returned, _UUID4_PATTERN)
        self.assertEqual(uuid.UUID(returned).version, 4)

    def test_empty_string_id_treated_as_missing_and_minted(self):
        """``id=""`` is falsy, so it is replaced with a freshly minted UUID4."""
        body = {"id": "", "v": 1}
        returned = ensure_item_id(body)
        self.assertNotEqual(returned, "")
        self.assertEqual(body["id"], returned)
        self.assertRegex(returned, _UUID4_PATTERN)

    def test_none_id_treated_as_missing_and_minted(self):
        """``id=None`` is falsy, so it is replaced with a freshly minted UUID4."""
        body = {"id": None, "v": 1}
        returned = ensure_item_id(body)
        self.assertIsNotNone(returned)
        self.assertEqual(body["id"], returned)
        self.assertRegex(returned, _UUID4_PATTERN)

    def test_zero_id_treated_as_missing_and_minted(self):
        """``id=0`` is falsy in Python and is therefore replaced with a UUID4 (legacy parity)."""
        body = {"id": 0}
        returned = ensure_item_id(body)
        self.assertIsNotNone(returned)
        self.assertEqual(body["id"], returned)

    def test_false_id_treated_as_missing_and_minted(self):
        """``id=False`` is falsy and is therefore replaced with a UUID4 (legacy parity)."""
        body = {"id": False}
        returned = ensure_item_id(body)
        self.assertIsNotNone(returned)
        self.assertEqual(body["id"], returned)

    def test_missing_id_with_generate_false_returns_none_and_no_mutation(self):
        """``generate=False`` + missing id: returns ``None`` and adds no ``id`` key.

        This is the "I'll supply the id myself, don't mint for me" path.
        """
        body = {"total": 99.5}
        returned = ensure_item_id(body, generate=False)
        self.assertIsNone(returned)
        self.assertEqual(body, {"total": 99.5})

    def test_falsy_id_with_generate_false_returns_none_and_no_mutation(self):
        """``generate=False`` + falsy id: returns ``None`` and leaves the falsy id in place."""
        body = {"id": "", "v": 1}
        returned = ensure_item_id(body, generate=False)
        self.assertIsNone(returned)
        # The falsy id is left as-is — not overwritten, not removed.
        self.assertEqual(body, {"id": "", "v": 1})


class TestEnsureItemIdProperties(unittest.TestCase):
    """Properties of the *minted* id that callers and other tests rely on.

    The format of the id is part of the public contract: it must be a
    standard lowercase UUID4 string and each call must produce a
    fresh value. These tests catch regressions like an accidental
    shared default, a global counter, or a switch to ``uuid1``/``uuid5``.
    """

    def test_each_call_mints_a_distinct_uuid(self):
        """Two empty bodies must end up with two different minted ids."""
        first = ensure_item_id({})
        second = ensure_item_id({})
        self.assertNotEqual(first, second)

    def test_minted_id_round_trips_through_uuid_parser(self):
        """The minted id parses back as a UUID with version == 4."""
        minted = ensure_item_id({})
        self.assertEqual(uuid.UUID(minted).version, 4)


class TestParityWithLegacyGenerator(unittest.TestCase):
    """Cross-check ``ensure_item_id`` against the legacy mint branch.

    The legacy code (still in ``_base.GenerateGuidId`` + the inline
    check on the create_item path) does this::

        if not document.get("id") and not options.get("disableAutomaticIdGeneration"):
            document["id"] = base.GenerateGuidId()

    The new helper must be a drop-in replacement for that block: same
    falsy-trigger rule, same key (``"id"``), same shape of value
    (lowercase UUID4 string). This class re-implements the legacy
    branch inline and asserts both paths agree on a representative
    set of inputs.
    """

    @staticmethod
    def _legacy_mint_if_needed(document, generate):
        """Inline reproduction of the legacy mint branch, kept byte-for-byte."""
        if not document.get("id") and generate:
            from azure.cosmos._base import GenerateGuidId
            document["id"] = GenerateGuidId()
            return document["id"]
        return document.get("id") if document.get("id") else None

    def test_helper_and_legacy_produce_same_shape_for_each_input(self):
        """For preset / empty / None / missing ids, helper and legacy agree on shape."""
        inputs = [
            {"id": "preset"},
            {"id": "", "v": 1},
            {"id": None},
            {"v": 1},
        ]
        for body in inputs:
            with self.subTest(body=body):
                helper_body = dict(body)
                legacy_body = dict(body)
                helper_id = ensure_item_id(helper_body)
                legacy_id = self._legacy_mint_if_needed(legacy_body, generate=True)
                # Both paths agree on whether an id is now present.
                self.assertEqual(
                    "id" in helper_body and bool(helper_body["id"]),
                    "id" in legacy_body and bool(legacy_body["id"]),
                )
                # Both produce a non-None id (preset or minted).
                self.assertIsNotNone(helper_id)
                self.assertIsNotNone(legacy_id)
                # When the input had no truthy id, both ids must be UUID4.
                if not body.get("id"):
                    self.assertEqual(uuid.UUID(helper_id).version, 4)
                    self.assertEqual(uuid.UUID(legacy_id).version, 4)


if __name__ == "__main__":
    unittest.main()
