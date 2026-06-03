# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Unit tests for the async paged response wrapper in azure.cosmos.

These tests exercise get_response_headers() on CosmosAsyncItemPaged directly,
without requiring a live emulator or any network round-trip.
"""

import unittest

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._cosmos_responses import (
    CosmosAsyncItemPaged,
    CosmosItemPaged,
)


async def _async_get_next(_continuation):
    return {"value": [], "nextLink": None}


async def _async_extract(_response):
    return None, []


def _new_async_paged(**kwargs):
    """Build a CosmosAsyncItemPaged without invoking the real query pipeline."""
    return CosmosAsyncItemPaged(
        get_next=_async_get_next,
        extract_data=_async_extract,
        **kwargs,
    )


@pytest.mark.cosmosEmulator
class TestCosmosAsyncItemPagedUnit(unittest.TestCase):
    """Pure unit tests for CosmosAsyncItemPaged.get_response_headers().

    The getter just reads a dict, so the tests do not need an event loop.
    """

    def test_get_response_headers_is_empty_before_any_page_fetch(self):
        # No page has been fetched, so headers must be an empty dict, not None.
        pager = _new_async_paged()
        headers = pager.get_response_headers()
        self.assertIsInstance(headers, CaseInsensitiveDict)
        self.assertEqual(len(headers), 0)

    def test_default_constructor_creates_fresh_header_dict(self):
        # No response_headers kwarg supplied: the pager allocates its own dict.
        pager = _new_async_paged()
        self.assertIsInstance(pager._response_headers, CaseInsensitiveDict)

    def test_explicit_none_response_headers_creates_fresh_dict(self):
        # Passing response_headers=None must behave the same as omitting it.
        pager = _new_async_paged(response_headers=None)
        self.assertIsInstance(pager._response_headers, CaseInsensitiveDict)
        self.assertEqual(len(pager._response_headers), 0)

    def test_response_headers_kwarg_is_the_same_instance_used_internally(self):
        # The pager must hold the exact dict the caller passed in, so external
        # writes into that dict are visible through the pager.
        shared = CaseInsensitiveDict()
        pager = _new_async_paged(response_headers=shared)
        self.assertIs(pager._response_headers, shared)

    def test_external_mutation_of_shared_dict_is_visible_via_getter(self):
        # The async query code writes into the shared dict after each page
        # fetch. The next call to the getter must reflect those writes.
        shared = CaseInsensitiveDict()
        pager = _new_async_paged(response_headers=shared)

        shared["x-ms-request-charge"] = "12.34"
        shared["x-ms-activity-id"] = "abc-123"

        headers = pager.get_response_headers()
        self.assertEqual(headers["x-ms-request-charge"], "12.34")
        self.assertEqual(headers["x-ms-activity-id"], "abc-123")

    def test_get_response_headers_returns_a_copy_not_a_reference(self):
        # Two calls must return distinct dicts, and mutating one must not
        # affect the other or the underlying shared dict.
        shared = CaseInsensitiveDict({"x-ms-request-charge": "1"})
        pager = _new_async_paged(response_headers=shared)

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
        pager = _new_async_paged(response_headers=shared)
        shared["x-ms-request-charge"] = "5.0"

        headers = pager.get_response_headers()
        self.assertEqual(headers["X-MS-Request-Charge"], "5.0")
        self.assertEqual(headers["x-ms-request-charge"], "5.0")

    def test_overwriting_simulates_pagination_and_keeps_only_latest_page(self):
        # Simulate many page fetches that overwrite the shared dict. The
        # getter must reflect only the most recent page, not accumulate pages.
        shared = CaseInsensitiveDict()
        pager = _new_async_paged(response_headers=shared)

        for i in range(100):
            shared.clear()
            shared.update({
                "x-ms-request-charge": str(i),
                "x-ms-activity-id": f"id-{i}",
                "x-ms-item-count": str(i),
            })

        headers = pager.get_response_headers()
        self.assertEqual(len(headers), 3)
        self.assertEqual(headers["x-ms-request-charge"], "99")
        self.assertEqual(headers["x-ms-activity-id"], "id-99")

    def test_return_type_is_caseinsensitivedict_not_list(self):
        # Regression guard: the getter must return a single dict, not a list.
        pager = _new_async_paged()
        headers = pager.get_response_headers()
        self.assertIsInstance(headers, CaseInsensitiveDict)
        self.assertNotIsInstance(headers, list)

    def test_get_last_response_headers_attribute_does_not_exist(self):
        # Regression guard: the removed method must not come back accidentally.
        pager = _new_async_paged()
        self.assertFalse(hasattr(pager, "get_last_response_headers"))
        self.assertFalse(hasattr(CosmosAsyncItemPaged, "get_last_response_headers"))
        self.assertFalse(hasattr(CosmosItemPaged, "get_last_response_headers"))

    def test_two_pagers_do_not_share_their_header_dicts(self):
        # Each pager must own its own header dict so concurrent async queries
        # do not leak header state into each other.
        p1 = _new_async_paged()
        p2 = _new_async_paged()
        self.assertIsNot(p1._response_headers, p2._response_headers)

        p1._response_headers["x-ms-request-charge"] = "9.0"
        self.assertNotIn("x-ms-request-charge", p2.get_response_headers())


if __name__ == "__main__":
    unittest.main()



