# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Unit tests for the sync paged response wrappers in azure.cosmos.

These tests exercise get_response_headers() and the wrapper types directly,
without requiring a live emulator or any network round-trip.
"""

import unittest

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._cosmos_responses import (
    CosmosAsyncItemPaged,
    CosmosDict,
    CosmosItemPaged,
    CosmosList,
)


def _new_paged(**kwargs):
    """Build a CosmosItemPaged without invoking the real query pipeline."""
    # No-op fetch callables are enough; these tests never iterate the pager.
    return CosmosItemPaged(
        get_next=lambda _continuation: {"value": [], "nextLink": None},
        extract_data=lambda _response: (None, []),
        **kwargs,
    )


@pytest.mark.cosmosEmulator
class TestCosmosItemPagedUnit(unittest.TestCase):
    """Pure unit tests for CosmosItemPaged.get_response_headers()."""

    def test_get_response_headers_is_empty_before_any_page_fetch(self):
        # No page has been fetched, so headers must be an empty dict, not None.
        pager = _new_paged()
        headers = pager.get_response_headers()
        self.assertIsInstance(headers, CaseInsensitiveDict)
        self.assertEqual(len(headers), 0)

    def test_default_constructor_creates_fresh_header_dict(self):
        # No response_headers kwarg supplied: the pager allocates its own dict.
        pager = _new_paged()
        self.assertIsInstance(pager._response_headers, CaseInsensitiveDict)

    def test_explicit_none_response_headers_creates_fresh_dict(self):
        # Passing response_headers=None must behave the same as omitting it.
        pager = _new_paged(response_headers=None)
        self.assertIsInstance(pager._response_headers, CaseInsensitiveDict)
        self.assertEqual(len(pager._response_headers), 0)

    def test_response_headers_kwarg_is_the_same_instance_used_internally(self):
        # The pager must hold the exact dict the caller passed in, so external
        # writes into that dict are visible through the pager.
        shared = CaseInsensitiveDict()
        pager = _new_paged(response_headers=shared)
        self.assertIs(pager._response_headers, shared)

    def test_external_mutation_of_shared_dict_is_visible_via_getter(self):
        # The query code writes into the shared dict after each page fetch.
        # The next call to the getter must reflect those writes.
        shared = CaseInsensitiveDict()
        pager = _new_paged(response_headers=shared)

        shared["x-ms-request-charge"] = "12.34"
        shared["x-ms-activity-id"] = "abc-123"

        headers = pager.get_response_headers()
        self.assertEqual(headers["x-ms-request-charge"], "12.34")
        self.assertEqual(headers["x-ms-activity-id"], "abc-123")

    def test_get_response_headers_returns_a_copy_not_a_reference(self):
        # Two calls must return distinct dicts, and mutating one must not
        # affect the other or the underlying shared dict.
        shared = CaseInsensitiveDict({"x-ms-request-charge": "1"})
        pager = _new_paged(response_headers=shared)

        first = pager.get_response_headers()
        second = pager.get_response_headers()

        self.assertIsNot(first, second)
        self.assertIsNot(first, shared)

        first["test-key"] = "test-value"
        self.assertNotIn("test-key", second)
        self.assertNotIn("test-key", shared)

    def test_returned_dict_is_case_insensitive(self):
        # Header lookups must work regardless of the case of the key.
        shared = CaseInsensitiveDict()
        pager = _new_paged(response_headers=shared)
        shared["x-ms-request-charge"] = "5.0"

        headers = pager.get_response_headers()
        self.assertEqual(headers["X-MS-Request-Charge"], "5.0")
        self.assertEqual(headers["x-ms-request-charge"], "5.0")
        self.assertEqual(headers["X-Ms-Request-Charge"], "5.0")

    def test_overwriting_simulates_pagination_and_keeps_only_latest_page(self):
        # Simulate many page fetches that overwrite the shared dict. The
        # getter must reflect only the most recent page, not accumulate pages.
        shared = CaseInsensitiveDict()
        pager = _new_paged(response_headers=shared)

        for i in range(100):
            shared.clear()
            shared.update({
                "x-ms-request-charge": str(i),
                "x-ms-activity-id": f"id-{i}",
                "x-ms-item-count": str(i),
            })

        headers = pager.get_response_headers()
        # Only the last page survives, so the dict has just the three keys.
        self.assertEqual(len(headers), 3)
        self.assertEqual(headers["x-ms-request-charge"], "99")
        self.assertEqual(headers["x-ms-activity-id"], "id-99")

    def test_return_type_is_caseinsensitivedict_not_list(self):
        # Regression guard: the getter must return a single dict, not a list.
        pager = _new_paged()
        headers = pager.get_response_headers()
        self.assertIsInstance(headers, CaseInsensitiveDict)
        self.assertNotIsInstance(headers, list)

    def test_get_last_response_headers_attribute_does_not_exist(self):
        # Regression guard: the removed method must not come back accidentally.
        pager = _new_paged()
        self.assertFalse(hasattr(pager, "get_last_response_headers"))
        self.assertFalse(hasattr(CosmosItemPaged, "get_last_response_headers"))
        self.assertFalse(hasattr(CosmosAsyncItemPaged, "get_last_response_headers"))

    def test_two_pagers_do_not_share_their_header_dicts(self):
        # Each pager must own its own header dict so concurrent queries do
        # not leak header state into each other.
        p1 = _new_paged()
        p2 = _new_paged()
        self.assertIsNot(p1._response_headers, p2._response_headers)

        # Writing to one pager's headers must not show up on the other.
        p1._response_headers["x-ms-request-charge"] = "9.0"
        self.assertNotIn("x-ms-request-charge", p2.get_response_headers())


@pytest.mark.cosmosEmulator
class TestCosmosDictAndListHeaders(unittest.TestCase):
    """Regression guard for the CosmosDict / CosmosList header API."""

    def test_cosmos_dict_returns_copy_of_response_headers(self):
        original = CaseInsensitiveDict({"x-ms-request-charge": "2.5"})
        wrapper = CosmosDict({"id": "x"}, response_headers=original)

        first = wrapper.get_response_headers()
        second = wrapper.get_response_headers()

        self.assertIsNot(first, original)
        self.assertIsNot(first, second)
        self.assertEqual(first["x-ms-request-charge"], "2.5")

        first["mutated"] = "yes"
        self.assertNotIn("mutated", second)
        self.assertNotIn("mutated", original)

    def test_cosmos_dict_with_none_payload_behaves_like_empty_dict(self):
        wrapper = CosmosDict(None, response_headers=CaseInsensitiveDict())
        self.assertEqual(len(wrapper), 0)
        self.assertEqual(len(wrapper.get_response_headers()), 0)

    def test_cosmos_dict_headers_are_case_insensitive(self):
        wrapper = CosmosDict(
            {"id": "x"},
            response_headers=CaseInsensitiveDict({"x-ms-request-charge": "7.0"}),
        )
        headers = wrapper.get_response_headers()
        self.assertEqual(headers["X-MS-REQUEST-CHARGE"], "7.0")

    def test_cosmos_list_returns_copy_of_response_headers(self):
        original = CaseInsensitiveDict({"x-ms-request-charge": "3.0"})
        wrapper = CosmosList([{"id": "a"}], response_headers=original)

        first = wrapper.get_response_headers()
        second = wrapper.get_response_headers()

        self.assertIsNot(first, original)
        self.assertIsNot(first, second)
        self.assertEqual(first["x-ms-request-charge"], "3.0")

        first["mutated"] = "yes"
        self.assertNotIn("mutated", second)
        self.assertNotIn("mutated", original)

    def test_cosmos_list_with_none_payload_behaves_like_empty_list(self):
        wrapper = CosmosList(None, response_headers=CaseInsensitiveDict())
        self.assertEqual(len(wrapper), 0)
        self.assertEqual(len(wrapper.get_response_headers()), 0)


if __name__ == "__main__":
    unittest.main()



