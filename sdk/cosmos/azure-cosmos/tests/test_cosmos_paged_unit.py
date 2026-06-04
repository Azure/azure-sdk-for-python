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
        # Before any page is fetched, callers must still be able to safely
        # ask for response headers and get back an empty collection rather
        # than a missing or null value that would crash their code.
        pager = _new_paged()
        headers = pager.get_response_headers()
        self.assertIsInstance(headers, CaseInsensitiveDict)
        self.assertEqual(len(headers), 0)

    def test_default_constructor_creates_fresh_header_dict(self):
        # When the caller does not supply a place to store headers, the
        # pager must create one on its own so the response-headers feature
        # always works out of the box.
        pager = _new_paged()
        self.assertIsInstance(pager._response_headers, CaseInsensitiveDict)

    def test_explicit_none_response_headers_creates_fresh_dict(self):
        # Explicitly opting out of providing a headers container must be
        # treated the same as not providing one at all: the pager still
        # gives the caller a working, empty headers collection.
        pager = _new_paged(response_headers=None)
        self.assertIsInstance(pager._response_headers, CaseInsensitiveDict)
        self.assertEqual(len(pager._response_headers), 0)

    def test_response_headers_kwarg_is_the_same_instance_used_internally(self):
        # When the caller supplies their own headers container, the pager
        # must use that exact container (not a copy of it) so headers the
        # query pipeline records later are visible to the caller.
        shared = CaseInsensitiveDict()
        pager = _new_paged(response_headers=shared)
        self.assertIs(pager._response_headers, shared)

    def test_external_mutation_of_shared_dict_is_visible_via_getter(self):
        # After each page is fetched, the query pipeline records the latest
        # response headers. Reading headers back through the pager must
        # reflect those updates so callers always see the freshest values.
        shared = CaseInsensitiveDict()
        pager = _new_paged(response_headers=shared)

        shared["x-ms-request-charge"] = "12.34"
        shared["x-ms-activity-id"] = "abc-123"

        headers = pager.get_response_headers()
        self.assertEqual(headers["x-ms-request-charge"], "12.34")
        self.assertEqual(headers["x-ms-activity-id"], "abc-123")

    def test_get_response_headers_returns_a_copy_not_a_reference(self):
        # Each read of the response headers must give the caller an
        # independent snapshot they can freely modify without corrupting
        # later reads or the pager's own internal state.
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
        # Service response headers can arrive in any letter casing, so
        # callers must be able to look them up without having to guess or
        # normalize the casing themselves.
        shared = CaseInsensitiveDict()
        pager = _new_paged(response_headers=shared)
        shared["x-ms-request-charge"] = "5.0"

        headers = pager.get_response_headers()
        self.assertEqual(headers["X-MS-Request-Charge"], "5.0")
        self.assertEqual(headers["x-ms-request-charge"], "5.0")
        self.assertEqual(headers["X-Ms-Request-Charge"], "5.0")

    def test_overwriting_simulates_pagination_and_keeps_only_latest_page(self):
        # Reading response headers after many pages have been fetched must
        # reflect only the most recent page's headers, never silently
        # accumulate headers from every earlier page.
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
        # Only the most recent page's headers should remain.
        self.assertEqual(len(headers), 3)
        self.assertEqual(headers["x-ms-request-charge"], "99")
        self.assertEqual(headers["x-ms-activity-id"], "id-99")

    def test_return_type_is_caseinsensitivedict_not_list(self):
        # Reading response headers must return the headers for a single
        # page, not a collection of headers from many pages.
        pager = _new_paged()
        headers = pager.get_response_headers()
        self.assertIsInstance(headers, CaseInsensitiveDict)
        self.assertNotIsInstance(headers, list)

    def test_get_last_response_headers_attribute_does_not_exist(self):
        # The old, removed way of reading response headers must not
        # silently reappear on either pager type.
        pager = _new_paged()
        self.assertFalse(hasattr(pager, "get_last_response_headers"))
        self.assertFalse(hasattr(CosmosItemPaged, "get_last_response_headers"))
        self.assertFalse(hasattr(CosmosAsyncItemPaged, "get_last_response_headers"))

    def test_get_last_response_headers_raises_attribute_error_when_invoked(self):
        # Make sure the old method is truly gone — not just hidden — so a
        # caller who reaches for it gets a clear failure instead of a
        # silent surprise, whether they go through an instance or the class.
        pager = _new_paged()
        with self.assertRaises(AttributeError):
            getattr(pager, "get_last_response_headers")()
        with self.assertRaises(AttributeError):
            getattr(CosmosItemPaged, "get_last_response_headers")
        with self.assertRaises(AttributeError):
            getattr(CosmosAsyncItemPaged, "get_last_response_headers")

    def test_two_pagers_do_not_share_their_header_dicts(self):
        # Each pager must own its own response headers so two queries
        # running side by side never see each other's headers.
        p1 = _new_paged()
        p2 = _new_paged()
        self.assertIsNot(p1._response_headers, p2._response_headers)

        # Updating one pager's headers must not show up on the other.
        p1._response_headers["x-ms-request-charge"] = "9.0"
        self.assertNotIn("x-ms-request-charge", p2.get_response_headers())


@pytest.mark.cosmosEmulator
class TestCosmosDictAndListHeaders(unittest.TestCase):
    """Header API guards for CosmosDict and CosmosList."""

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

    def test_cosmos_dict_does_not_expose_get_last_response_headers(self):
        # The old, removed way of reading response headers must not
        # silently reappear on the single-item response wrapper, whether
        # accessed through the wrapper itself or its class.
        wrapper = CosmosDict({"id": "x"}, response_headers=CaseInsensitiveDict())
        self.assertFalse(hasattr(wrapper, "get_last_response_headers"))
        self.assertFalse(hasattr(CosmosDict, "get_last_response_headers"))
        with self.assertRaises(AttributeError):
            getattr(wrapper, "get_last_response_headers")()

    def test_cosmos_list_does_not_expose_get_last_response_headers(self):
        # The same removed method must also stay absent on the list
        # response wrapper.
        wrapper = CosmosList([{"id": "a"}], response_headers=CaseInsensitiveDict())
        self.assertFalse(hasattr(wrapper, "get_last_response_headers"))
        self.assertFalse(hasattr(CosmosList, "get_last_response_headers"))
        with self.assertRaises(AttributeError):
            getattr(wrapper, "get_last_response_headers")()


if __name__ == "__main__":
    unittest.main()



