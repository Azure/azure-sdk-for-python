# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Mock-transport unit tests for the Confidential Ledger client polling behavior.

These tests do NOT require a live Confidential Ledger; they exercise the polling logic added in
``_patch.py`` (sync and async) by stubbing out the generated parent operations.
"""
import asyncio
from unittest import mock

import pytest

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.rest import HttpResponse

from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger.aio import ConfidentialLedgerClient as AsyncConfidentialLedgerClient
from azure.confidentialledger._operations._operations import (
    _ConfidentialLedgerClientOperationsMixin as SyncGeneratedMixin,
)
from azure.confidentialledger._operations._patch import (
    DEFAULT_LOADING_POLLING_INTERVAL_S,
    MAX_LOADING_RETRIES,
    MAX_NOT_FOUND_RETRIES,
    StatePollingMethod,
    _is_loading_response,
)
from azure.confidentialledger.aio._operations._operations import (
    _ConfidentialLedgerClientOperationsMixin as AsyncGeneratedMixin,
)
from azure.confidentialledger.aio._operations._patch import AsyncStatePollingMethod


READY_RESPONSE = {
    "state": "Ready",
    "entry": {
        "contents": "hello",
        "transactionId": "2.10",
        "collectionId": "subledger:0",
    },
}
LOADING_RESPONSE = {"state": "Loading"}


def _make_client():
    """Create a ConfidentialLedgerClient instance without invoking __init__ (which would require a
    TLS cert). The polling methods we exercise only call ``super().get_ledger_entry`` and don't
    touch the underlying pipeline, so a bare instance is sufficient.
    """
    return ConfidentialLedgerClient.__new__(ConfidentialLedgerClient)


def _make_async_client():
    return AsyncConfidentialLedgerClient.__new__(AsyncConfidentialLedgerClient)


def _http_error(status_code):
    response = mock.MagicMock(spec=HttpResponse)
    response.status_code = status_code
    return HttpResponseError(response=response)


# ---------------------------------------------------------------------------
# get_ledger_entry — sync
# ---------------------------------------------------------------------------


class TestGetLedgerEntryPolling:
    def test_returns_immediately_when_ready(self):
        client = _make_client()
        with mock.patch.object(SyncGeneratedMixin, "get_ledger_entry", return_value=READY_RESPONSE) as mocked:
            result = client.get_ledger_entry("2.10", polling_interval=0)
        assert result == READY_RESPONSE
        assert mocked.call_count == 1

    def test_polls_until_ready(self):
        client = _make_client()
        responses = [LOADING_RESPONSE, LOADING_RESPONSE, LOADING_RESPONSE, READY_RESPONSE]
        with mock.patch.object(SyncGeneratedMixin, "get_ledger_entry", side_effect=responses) as mocked:
            result = client.get_ledger_entry("2.10", polling_interval=0)
        assert result == READY_RESPONSE
        assert mocked.call_count == 4

    def test_returns_last_loading_after_max_retries(self):
        client = _make_client()
        # MAX_LOADING_RETRIES additional calls + the initial one => MAX_LOADING_RETRIES + 1 total.
        responses = [LOADING_RESPONSE] * (MAX_LOADING_RETRIES + 5)
        with mock.patch.object(SyncGeneratedMixin, "get_ledger_entry", side_effect=responses) as mocked:
            result = client.get_ledger_entry("2.10", polling_interval=0)
        assert result == LOADING_RESPONSE
        assert mocked.call_count == MAX_LOADING_RETRIES + 1

    def test_non_200_response_is_not_retried(self):
        client = _make_client()
        with mock.patch.object(
            SyncGeneratedMixin, "get_ledger_entry", side_effect=ResourceNotFoundError(message="missing")
        ) as mocked:
            with pytest.raises(ResourceNotFoundError):
                client.get_ledger_entry("2.10", polling_interval=0)
        assert mocked.call_count == 1

    @pytest.mark.parametrize("bad_id", [None, ""])
    def test_invalid_transaction_id_raises(self, bad_id):
        client = _make_client()
        with pytest.raises(ValueError):
            client.get_ledger_entry(bad_id, polling_interval=0)

    def test_default_polling_interval_constant(self):
        # Sanity check that the documented default isn't accidentally regressed.
        assert DEFAULT_LOADING_POLLING_INTERVAL_S == 0.5
        assert MAX_LOADING_RETRIES == 10
        assert MAX_NOT_FOUND_RETRIES == 3


# ---------------------------------------------------------------------------
# get_ledger_entry — async
# ---------------------------------------------------------------------------


class TestGetLedgerEntryPollingAsync:
    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_returns_immediately_when_ready(self):
        client = _make_async_client()

        async def fake_get(*args, **kwargs):
            return READY_RESPONSE

        with mock.patch.object(AsyncGeneratedMixin, "get_ledger_entry", side_effect=fake_get) as mocked:
            result = self._run(client.get_ledger_entry("2.10", polling_interval=0))
        assert result == READY_RESPONSE
        assert mocked.call_count == 1

    def test_polls_until_ready(self):
        client = _make_async_client()
        sequence = [LOADING_RESPONSE, LOADING_RESPONSE, READY_RESPONSE]
        index = {"i": 0}

        async def fake_get(*args, **kwargs):
            value = sequence[index["i"]]
            index["i"] += 1
            return value

        with mock.patch.object(AsyncGeneratedMixin, "get_ledger_entry", side_effect=fake_get) as mocked:
            result = self._run(client.get_ledger_entry("2.10", polling_interval=0))
        assert result == READY_RESPONSE
        assert mocked.call_count == 3

    def test_returns_last_loading_after_max_retries(self):
        client = _make_async_client()

        async def fake_get(*args, **kwargs):
            return LOADING_RESPONSE

        with mock.patch.object(AsyncGeneratedMixin, "get_ledger_entry", side_effect=fake_get) as mocked:
            result = self._run(client.get_ledger_entry("2.10", polling_interval=0))
        assert result == LOADING_RESPONSE
        assert mocked.call_count == MAX_LOADING_RETRIES + 1

    def test_non_200_response_is_not_retried(self):
        client = _make_async_client()

        async def fake_get(*args, **kwargs):
            raise ResourceNotFoundError(message="missing")

        with mock.patch.object(AsyncGeneratedMixin, "get_ledger_entry", side_effect=fake_get) as mocked:
            with pytest.raises(ResourceNotFoundError):
                self._run(client.get_ledger_entry("2.10", polling_interval=0))
        assert mocked.call_count == 1

    @pytest.mark.parametrize("bad_id", [None, ""])
    def test_invalid_transaction_id_raises(self, bad_id):
        client = _make_async_client()
        with pytest.raises(ValueError):
            self._run(client.get_ledger_entry(bad_id, polling_interval=0))


# ---------------------------------------------------------------------------
# StatePollingMethod — 406 / 404 LRO behavior
# ---------------------------------------------------------------------------


class TestStatePollingMethod406And404:
    def _build(self, operation):
        method = StatePollingMethod(operation, desired_state="Committed", polling_interval_s=0, retry_not_found=True)
        # ``initialize`` evaluates the initial response; pass an empty dict so polling continues.
        method.initialize(client=None, initial_response={}, deserialization_callback=lambda x: x)
        return method

    def test_406_keeps_polling_indefinitely_no_retry_cap(self):
        # Five consecutive 406s (well above MAX_NOT_FOUND_RETRIES) followed by a Committed result.
        outputs = [
            _http_error(406),
            _http_error(406),
            _http_error(406),
            _http_error(406),
            _http_error(406),
            {"state": "Committed"},
        ]

        def operation():
            value = outputs.pop(0)
            if isinstance(value, Exception):
                raise value
            return value

        method = self._build(operation)
        method.run()
        assert method.status() == "finished"
        assert method.resource() == {"state": "Committed"}

    def test_404_followed_by_200_succeeds_and_resets_counter(self):
        # 404 once, then a successful Committed response. Counter must reset so a future 404 does
        # not immediately fail.
        outputs = [
            ResourceNotFoundError(message="not yet replicated"),
            {"state": "Committed"},
        ]

        def operation():
            value = outputs.pop(0)
            if isinstance(value, Exception):
                raise value
            return value

        method = self._build(operation)
        method.run()
        assert method.status() == "finished"
        assert method.resource() == {"state": "Committed"}

    def test_four_consecutive_404s_surfaces_failure(self):
        outputs = [ResourceNotFoundError(message="missing")] * (MAX_NOT_FOUND_RETRIES + 1)

        def operation():
            raise outputs.pop(0)

        method = self._build(operation)
        with pytest.raises(ResourceNotFoundError):
            method.run()
        assert method.status() == "failed"

    def test_200_resets_404_counter(self):
        # Three 404s, then a Pending 200, then three more 404s, then a Committed. Should succeed
        # because the 200 reset the counter so the second batch of 404s never exceeds the cap.
        outputs = [
            ResourceNotFoundError(message="m"),
            ResourceNotFoundError(message="m"),
            ResourceNotFoundError(message="m"),
            {"state": "Pending"},
            ResourceNotFoundError(message="m"),
            ResourceNotFoundError(message="m"),
            ResourceNotFoundError(message="m"),
            {"state": "Committed"},
        ]

        def operation():
            value = outputs.pop(0)
            if isinstance(value, Exception):
                raise value
            return value

        method = self._build(operation)
        method.run()
        assert method.status() == "finished"
        assert method.resource() == {"state": "Committed"}

    def test_406_resets_404_counter(self):
        # Mix 404s and 406s — the 406 between batches must reset the 404 counter so this succeeds.
        outputs = [
            ResourceNotFoundError(message="m"),
            ResourceNotFoundError(message="m"),
            ResourceNotFoundError(message="m"),
            _http_error(406),
            ResourceNotFoundError(message="m"),
            ResourceNotFoundError(message="m"),
            ResourceNotFoundError(message="m"),
            {"state": "Committed"},
        ]

        def operation():
            value = outputs.pop(0)
            if isinstance(value, Exception):
                raise value
            return value

        method = self._build(operation)
        method.run()
        assert method.status() == "finished"


class TestAsyncStatePollingMethod406And404:
    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def _build(self, operation):
        method = AsyncStatePollingMethod(
            operation, desired_state="Committed", polling_interval_s=0, retry_not_found=True
        )
        method.initialize(client=None, initial_response={}, deserialization_callback=lambda x: x)
        return method

    def test_406_keeps_polling_indefinitely_no_retry_cap(self):
        outputs = [
            _http_error(406),
            _http_error(406),
            _http_error(406),
            _http_error(406),
            _http_error(406),
            {"state": "Committed"},
        ]

        async def operation():
            value = outputs.pop(0)
            if isinstance(value, Exception):
                raise value
            return value

        method = self._build(operation)
        self._run(method.run())
        assert method.status() == "finished"

    def test_four_consecutive_404s_surfaces_failure(self):
        outputs = [ResourceNotFoundError(message="missing")] * (MAX_NOT_FOUND_RETRIES + 1)

        async def operation():
            raise outputs.pop(0)

        method = self._build(operation)
        with pytest.raises(ResourceNotFoundError):
            self._run(method.run())
        assert method.status() == "failed"


# ---------------------------------------------------------------------------
# _is_loading_response helper
# ---------------------------------------------------------------------------


class TestIsLoadingResponse:
    def test_loading_body(self):
        assert _is_loading_response({"state": "Loading"}) is True

    def test_ready_body(self):
        assert _is_loading_response(READY_RESPONSE) is False

    def test_non_mapping_body(self):
        assert _is_loading_response("not-a-dict") is False
        assert _is_loading_response(None) is False
