# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``_helpers/_auto_id.py`` â—” no network, no Cosmos emulator.

These tests pin the auto-id contract by which the future item helper
mints ids on the body. The contract is small but every branch matters
because the failure mode (mismatched id between body and routing
reference) is silent and shows up only as duplicated documents under
different ids on a retried write.
"""
import re
import unittest
import uuid

from azure.cosmos._helpers._auto_id import ensure_item_id

_UUID4_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


class TestEnsureItemIdWhenIdAlreadyPresent(unittest.TestCase):
    """An existing truthy id is honoured; body is left alone."""

    def test_existing_string_id_is_returned(self):
        body = {"id": "order-42", "total": 99.5}
        returned = ensure_item_id(body)
        self.assertEqual(returned, "order-42")
        # Body must not be mutated when an id was already present.
        self.assertEqual(body, {"id": "order-42", "total": 99.5})

    def test_existing_id_is_returned_even_when_generate_is_false(self):
        body = {"id": "order-42"}
        returned = ensure_item_id(body, generate=False)
        self.assertEqual(returned, "order-42")
        self.assertEqual(body, {"id": "order-42"})

    def test_existing_non_string_truthy_id_passed_through_unchanged(self):
        # Cosmos rejects non-string ids server-side with a 400. The
        # legacy path passes them through; we match that for parity
        # so customer fixtures keep producing the same wire payload
        # (and the same server-side error).
        body = {"id": 123}
        returned = ensure_item_id(body)
        self.assertEqual(returned, 123)
        self.assertEqual(body, {"id": 123})


class TestEnsureItemIdWhenIdMissing(unittest.TestCase):
    """Missing / falsy id paths."""

    def test_missing_id_mints_uuid_and_mutates_body(self):
        body = {"total": 99.5}
        returned = ensure_item_id(body)
        self.assertIsNotNone(returned)
        # The returned id is the same value written into body.
        self.assertEqual(body["id"], returned)
        # All other fields are preserved.
        self.assertEqual(body["total"], 99.5)
        # The minted id is a UUID4 string.
        self.assertIsInstance(returned, str)
        self.assertRegex(returned, _UUID4_PATTERN)
        # And it parses back as a UUID4 (sanity check on the pattern).
        parsed = uuid.UUID(returned)
        self.assertEqual(parsed.version, 4)

    def test_empty_string_id_treated_as_missing_and_minted(self):
        # The legacy ``not document.get("id")`` check treats "" as
        # missing. Match that: empty string triggers minting.
        body = {"id": "", "v": 1}
        returned = ensure_item_id(body)
        self.assertNotEqual(returned, "")
        self.assertEqual(body["id"], returned)
        self.assertRegex(returned, _UUID4_PATTERN)

    def test_none_id_treated_as_missing_and_minted(self):
        body = {"id": None, "v": 1}
        returned = ensure_item_id(body)
        self.assertIsNotNone(returned)
        self.assertEqual(body["id"], returned)
        self.assertRegex(returned, _UUID4_PATTERN)

    def test_zero_id_treated_as_missing_and_minted(self):
        # 0 is falsy in Python; matches the legacy semantics.
        body = {"id": 0}
        returned = ensure_item_id(body)
        self.assertIsNotNone(returned)
        self.assertEqual(body["id"], returned)

    def test_false_id_treated_as_missing_and_minted(self):
        body = {"id": False}
        returned = ensure_item_id(body)
        self.assertIsNotNone(returned)
        self.assertEqual(body["id"], returned)

    def test_missing_id_with_generate_false_returns_none_and_no_mutation(self):
        # The "I'll supply the id, don't mint for me" path.
        body = {"total": 99.5}
        returned = ensure_item_id(body, generate=False)
        self.assertIsNone(returned)
        # Body is untouched â—” no "id" key was added.
        self.assertEqual(body, {"total": 99.5})

    def test_falsy_id_with_generate_false_returns_none_and_no_mutation(self):
        body = {"id": "", "v": 1}
        returned = ensure_item_id(body, generate=False)
        self.assertIsNone(returned)
        # The falsy id is left as-is; we did not overwrite or remove it.
        self.assertEqual(body, {"id": "", "v": 1})


class TestEnsureItemIdProperties(unittest.TestCase):
    """Properties of the minted id that callers and tests rely on."""

    def test_each_call_mints_a_distinct_uuid(self):
        # Two empty bodies must end up with two different ids. Catches
        # an accidental shared default or a global counter regression.
        first = ensure_item_id({})
        second = ensure_item_id({})
        self.assertNotEqual(first, second)

    def test_minted_id_round_trips_through_uuid_parser(self):
        # Defensive: if someone changes the helper to use uuid1 / uuid5
        # / a non-standard format, this test catches the version drift.
        body = {}
        minted = ensure_item_id(body)
        self.assertEqual(uuid.UUID(minted).version, 4)


class TestParityWithLegacyGenerator(unittest.TestCase):
    """Cross-check against ``_base.GenerateGuidId`` and the legacy mint check.

    The legacy code does:

        if not document.get("id") and not options.get("disableAutomaticIdGeneration"):
            document["id"] = base.GenerateGuidId()

    The helper produces the same shape of value (lowercase UUID4
    string), under the same falsy-trigger rule, and writes it into
    the same key. Reproducing that logic here as a small inline
    function lets us prove the helper is a drop-in replacement.
    """

    @staticmethod
    def _legacy_mint_if_needed(document, generate):
        """Mirrors the legacy mint branch byte-for-byte."""
        if not document.get("id") and generate:
            from azure.cosmos._base import GenerateGuidId  # local import keeps top tidy
            document["id"] = GenerateGuidId()
            return document["id"]
        return document.get("id") if document.get("id") else None

    def test_helper_and_legacy_produce_same_shape_for_each_input(self):
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
                # Both paths agree on whether an id is present.
                self.assertEqual(
                    "id" in helper_body and bool(helper_body["id"]),
                    "id" in legacy_body and bool(legacy_body["id"]),
                )
                # Both produce a non-None id (preset or minted).
                self.assertIsNotNone(helper_id)
                self.assertIsNotNone(legacy_id)
                # Both ids parse as UUID4 *if* they were minted (i.e.
                # the original body had no truthy id).
                if not body.get("id"):
                    self.assertEqual(uuid.UUID(helper_id).version, 4)
                    self.assertEqual(uuid.UUID(legacy_id).version, 4)


if __name__ == "__main__":
    unittest.main()
