# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tests sequential _Request() decode isolation across multiple responses.

These tests call _Request() repeatedly with different response bodies to ensure
decode behavior from one call does not poison later calls when malformed UTF-8
appears. This does not exercise CosmosItemPaged/continuation-token state."""
import asyncio
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from azure.core.exceptions import DecodeError

from azure.cosmos import _synchronized_request
from azure.cosmos.aio import _asynchronous_request
from azure.cosmos.http_constants import ResourceType


_MALFORMED_INPUT_ENV_VAR = "AZURE_COSMOS_CHARSET_DECODER_ERROR_ACTION_ON_MALFORMED_INPUT"
pytestmark = pytest.mark.cosmosEmulator

# Page 1 is valid JSON but a string value contains an invalid UTF-8
# byte sequence. Page 2 is fully well-formed.
_PAGE_WITH_BAD_UTF8_IN_STRING_VALUE = (
    b'{"_rid":"rid","Documents":[{"id":"doc1","x":"caf\xc3\x28 dining"}],"_count":1}'
)
_PAGE_VALID_UTF8 = (
    b'{"_rid":"rid","Documents":[{"id":"doc2","x":"hello"}],"_count":1}'
)

_FAKE_ENDPOINT = "https://example.documents.azure.com:443/"


def _build_request_args():
    """Builds the minimum set of mocks needed for one request call."""
    request_params = MagicMock()
    request_params.healthy_tentative_location = False
    request_params.resource_type = ResourceType.DatabaseAccount
    request_params.read_timeout_override = None
    request_params.endpoint_override = _FAKE_ENDPOINT
    request_params.should_cancel_request.return_value = False
    request_params.operation_type = "ReadFeed"
    request_params.availability_strategy = None

    connection_policy = MagicMock()
    connection_policy.RequestTimeout = 30
    connection_policy.ReadTimeout = 30
    connection_policy.RecoveryReadTimeout = 5
    connection_policy.DBAReadTimeout = 5
    connection_policy.DBAConnectionTimeout = 5
    connection_policy.SSLConfiguration = None
    connection_policy.DisableSSLVerification = False

    global_endpoint_manager = MagicMock()
    pipeline_client = MagicMock()

    request = MagicMock()
    request.url = _FAKE_ENDPOINT + "dbs/db/colls/c/docs"
    request.headers = {}

    return global_endpoint_manager, request_params, connection_policy, pipeline_client, request


def _mock_response(body: bytes, status_code: int = 200):
    """Builds a fake HTTP response with the given body and status."""
    mock_response = MagicMock()
    mock_response.http_response.status_code = status_code
    mock_response.http_response.headers = {}
    mock_response.http_response.body.return_value = body
    return mock_response


class _DecoderEnvIsolatedTestCase(unittest.TestCase):
    """Saves and restores the env var so tests don't leak settings."""

    def setUp(self):
        self._saved = os.environ.get(_MALFORMED_INPUT_ENV_VAR)
        os.environ.pop(_MALFORMED_INPUT_ENV_VAR, None)

    def tearDown(self):
        if self._saved is not None:
            os.environ[_MALFORMED_INPUT_ENV_VAR] = self._saved
        else:
            os.environ.pop(_MALFORMED_INPUT_ENV_VAR, None)


class TestSyncPagedIterationWithReplace(_DecoderEnvIsolatedTestCase):
    """Calls the sync request function repeatedly with different bodies."""

    def _drive_sequential_requests(self, page_bodies):
        """Call _Request once per body and return each decoded result.

        A fresh args tuple is built each time because _Request mutates
        request objects in place.
        """
        results = []
        for body in page_bodies:
            args = _build_request_args()
            with patch(
                "azure.cosmos._synchronized_request._PipelineRunFunction",
                return_value=_mock_response(body, status_code=200),
            ):
                results.append(_synchronized_request._Request(*args))
        return results

    def test_strict_mode_iteration_aborts_on_corrupt_page(self):
        """With the env var unset, the bad page should fail right
        away. This is the default behavior."""
        with self.assertRaises(DecodeError):
            self._drive_sequential_requests([_PAGE_WITH_BAD_UTF8_IN_STRING_VALUE, _PAGE_VALID_UTF8])

    def test_replace_mode_iteration_completes_past_corrupt_page(self):
        """With REPLACE set, both pages should decode and parse. The
        bad byte on page 1 becomes a replacement character."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"

        results = self._drive_sequential_requests([_PAGE_WITH_BAD_UTF8_IN_STRING_VALUE, _PAGE_VALID_UTF8])

        self.assertEqual(len(results), 2)

        page1_body, _ = results[0]
        page2_body, _ = results[1]

        # Page 1 came through with a replacement character in place of
        # the bad byte. Surrounding text is preserved.
        self.assertIn("Documents", page1_body)
        self.assertEqual(page1_body["Documents"][0]["id"], "doc1")
        self.assertIn("\ufffd", page1_body["Documents"][0]["x"])
        self.assertIn("caf", page1_body["Documents"][0]["x"])
        self.assertIn("dining", page1_body["Documents"][0]["x"])

        # Page 2 is normal text. The setting only kicks in when the
        # bytes are actually invalid.
        self.assertEqual(page2_body["Documents"][0]["id"], "doc2")
        self.assertEqual(page2_body["Documents"][0]["x"], "hello")

    def test_ignore_mode_iteration_completes_past_corrupt_page(self):
        """With IGNORE set, both pages decode. The bad byte is dropped
        instead of being replaced."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "IGNORE"

        results = self._drive_sequential_requests([_PAGE_WITH_BAD_UTF8_IN_STRING_VALUE, _PAGE_VALID_UTF8])

        self.assertEqual(len(results), 2)
        page1_body, _ = results[0]
        page2_body, _ = results[1]

        # No replacement character; the surrounding text stays intact.
        self.assertNotIn("\ufffd", page1_body["Documents"][0]["x"])
        self.assertIn("caf", page1_body["Documents"][0]["x"])
        self.assertEqual(page2_body["Documents"][0]["x"], "hello")

    def test_replace_mode_corrupt_page_does_not_poison_next_request_headers(self):
        """Three pages in a row (bad, good, bad) should each decode
        based on their own bytes, so any state accidentally shared
        between calls would show up here."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"

        results = self._drive_sequential_requests([
            _PAGE_WITH_BAD_UTF8_IN_STRING_VALUE,
            _PAGE_VALID_UTF8,
            _PAGE_WITH_BAD_UTF8_IN_STRING_VALUE,
        ])

        self.assertEqual(len(results), 3)
        page1_body, _ = results[0]
        page2_body, _ = results[1]
        page3_body, _ = results[2]

        self.assertIn("\ufffd", page1_body["Documents"][0]["x"])
        self.assertNotIn("\ufffd", page2_body["Documents"][0]["x"])
        self.assertIn("\ufffd", page3_body["Documents"][0]["x"])


class TestAsyncPagedIterationWithReplace(_DecoderEnvIsolatedTestCase):
    """Async version of the sequential _Request decode-isolation checks."""

    def _drive_sequential_requests(self, page_bodies):
        async def _run():
            results = []
            for body in page_bodies:
                args = _build_request_args()
                with patch(
                    "azure.cosmos.aio._asynchronous_request._PipelineRunFunction",
                    new=AsyncMock(return_value=_mock_response(body, status_code=200)),
                ):
                    results.append(await _asynchronous_request._Request(*args))
            return results
        return asyncio.run(_run())

    def test_strict_mode_iteration_aborts_on_corrupt_page(self):
        with self.assertRaises(DecodeError):
            self._drive_sequential_requests([_PAGE_WITH_BAD_UTF8_IN_STRING_VALUE, _PAGE_VALID_UTF8])

    def test_replace_mode_iteration_completes_past_corrupt_page(self):
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"

        results = self._drive_sequential_requests([_PAGE_WITH_BAD_UTF8_IN_STRING_VALUE, _PAGE_VALID_UTF8])

        self.assertEqual(len(results), 2)
        page1_body, _ = results[0]
        page2_body, _ = results[1]
        self.assertIn("\ufffd", page1_body["Documents"][0]["x"])
        self.assertEqual(page2_body["Documents"][0]["x"], "hello")

    def test_ignore_mode_iteration_completes_past_corrupt_page(self):
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "IGNORE"

        results = self._drive_sequential_requests([_PAGE_WITH_BAD_UTF8_IN_STRING_VALUE, _PAGE_VALID_UTF8])

        self.assertEqual(len(results), 2)
        page1_body, _ = results[0]
        page2_body, _ = results[1]
        self.assertNotIn("\ufffd", page1_body["Documents"][0]["x"])
        self.assertIn("caf", page1_body["Documents"][0]["x"])
        self.assertEqual(page2_body["Documents"][0]["x"], "hello")

    def test_replace_mode_corrupt_page_does_not_poison_next_request_headers(self):
        """Three async pages in a row (bad, good, bad) must each decode based on
        their own bytes; no decoder state may leak across async requests."""
        # patch.dict scopes the env var to this test and restores the prior
        # value when the block exits, even if an assertion below raises.
        with patch.dict(os.environ, {_MALFORMED_INPUT_ENV_VAR: "REPLACE"}):
            results = self._drive_sequential_requests([
                _PAGE_WITH_BAD_UTF8_IN_STRING_VALUE,
                _PAGE_VALID_UTF8,
                _PAGE_WITH_BAD_UTF8_IN_STRING_VALUE,
            ])

        self.assertEqual(len(results), 3)
        page1_body, _ = results[0]
        page2_body, _ = results[1]
        page3_body, _ = results[2]

        self.assertIn("\ufffd", page1_body["Documents"][0]["x"])
        self.assertNotIn("\ufffd", page2_body["Documents"][0]["x"])
        self.assertIn("\ufffd", page3_body["Documents"][0]["x"])


if __name__ == "__main__":
    unittest.main()
