# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Tests for the custom StatePollingMethod and AsyncStatePollingMethod classes,
covering transient 404 and 406 handling during transaction-status polling.
"""

import pytest

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError, ODataV4Format

from azure.confidentialledger._operations._patch import StatePollingMethod
from azure.confidentialledger.aio._operations._patch import AsyncStatePollingMethod


def _make_resource_not_found(error_code=None):
    """Create a ResourceNotFoundError (HTTP 404) with an optional error code."""
    error = ResourceNotFoundError(message="Not found")
    error.status_code = 404
    if error_code:
        error.error = ODataV4Format({"error": {"code": error_code, "message": ""}})
    return error


def _make_http_response_error(status_code, message="Error"):
    """Create an HttpResponseError with the given status code."""
    error = HttpResponseError(message=message)
    error.status_code = status_code
    return error


# ---------------------------------------------------------------------------
# Sync StatePollingMethod tests
# ---------------------------------------------------------------------------


class TestStatePollingMethodTransient404:
    """Verify that 404 responses during polling are treated as transient when
    retry_not_found is True, up to 3 retries.
    """

    def test_404_retried_then_committed(self):
        """404 should be retried (up to 3 times) and eventually succeed."""
        call_count = 0

        def operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise _make_resource_not_found()
            return {"state": "Committed"}

        poller = StatePollingMethod(operation, "Committed", 0, retry_not_found=True)
        poller._status = "polling"
        poller.run()

        assert poller.status() == "finished"
        assert call_count == 3

    def test_404_raises_when_retry_not_found_false(self):
        """404 should raise immediately when retry_not_found is False."""

        def operation():
            raise _make_resource_not_found()

        poller = StatePollingMethod(operation, "Ready", 0, retry_not_found=False)
        poller._status = "polling"

        with pytest.raises(ResourceNotFoundError):
            poller.run()

        assert poller.status() == "failed"

    def test_404_with_invalid_transaction_id_raises(self):
        """404 with InvalidTransactionId error code should raise even when
        retry_not_found is True (permanent error, not transient).
        """

        def operation():
            raise _make_resource_not_found(error_code="InvalidTransactionId")

        poller = StatePollingMethod(operation, "Committed", 0, retry_not_found=True)
        poller._status = "polling"

        with pytest.raises(ResourceNotFoundError):
            poller.run()

        assert poller.status() == "failed"

    def test_404_raises_after_3_retries(self):
        """After 3 consecutive 404s the poller should give up and raise."""

        def operation():
            raise _make_resource_not_found()

        poller = StatePollingMethod(operation, "Committed", 0, retry_not_found=True)
        poller._status = "polling"

        with pytest.raises(ResourceNotFoundError):
            poller.run()

        assert poller.status() == "failed"


class TestStatePollingMethodTransient406:
    """Verify that 406 responses during polling are treated as transient when
    retry_not_found is True.
    """

    def test_406_retried_then_committed(self):
        """406 should be retried and eventually succeed when the transaction commits."""
        call_count = 0

        def operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise _make_http_response_error(406, "Not Acceptable")
            return {"state": "Committed"}

        poller = StatePollingMethod(operation, "Committed", 0, retry_not_found=True)
        poller._status = "polling"
        poller.run()

        assert poller.status() == "finished"
        assert call_count == 4

    def test_406_raises_when_retry_not_found_false(self):
        """406 should raise immediately when retry_not_found is False."""

        def operation():
            raise _make_http_response_error(406, "Not Acceptable")

        poller = StatePollingMethod(operation, "Ready", 0, retry_not_found=False)
        poller._status = "polling"

        with pytest.raises(HttpResponseError):
            poller.run()

        assert poller.status() == "failed"

    def test_many_406s_retried_without_limit(self):
        """More than 3 consecutive 406s should still be retried (no hard limit)."""
        call_count = 0

        def operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 10:
                raise _make_http_response_error(406, "Not Acceptable")
            return {"state": "Committed"}

        poller = StatePollingMethod(operation, "Committed", 0, retry_not_found=True)
        poller._status = "polling"
        poller.run()

        assert poller.status() == "finished"
        assert call_count == 11


class TestStatePollingMethodMixed:
    """Verify mixed 404/406 sequences and non-transient errors."""

    def test_mixed_404_and_406_retried(self):
        """Alternating 404 and 406 should both be retried."""
        call_count = 0

        def operation():
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 1 and call_count <= 4:
                raise _make_resource_not_found()
            if call_count % 2 == 0 and call_count <= 4:
                raise _make_http_response_error(406, "Not Acceptable")
            return {"state": "Committed"}

        poller = StatePollingMethod(operation, "Committed", 0, retry_not_found=True)
        poller._status = "polling"
        poller.run()

        assert poller.status() == "finished"
        assert call_count == 5

    def test_other_http_errors_raise_immediately(self):
        """Non-404/406 HTTP errors should raise immediately even when
        retry_not_found is True.
        """

        def operation():
            raise _make_http_response_error(500, "Internal Server Error")

        poller = StatePollingMethod(operation, "Committed", 0, retry_not_found=True)
        poller._status = "polling"

        with pytest.raises(HttpResponseError):
            poller.run()

        assert poller.status() == "failed"

    def test_pending_state_keeps_polling(self):
        """Responses with 'state': 'Pending' should keep polling (baseline behavior)."""
        call_count = 0

        def operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return {"state": "Pending"}
            return {"state": "Committed"}

        poller = StatePollingMethod(operation, "Committed", 0, retry_not_found=True)
        poller._status = "polling"
        poller.run()

        assert poller.status() == "finished"
        assert call_count == 3


# ---------------------------------------------------------------------------
# Async AsyncStatePollingMethod tests
# ---------------------------------------------------------------------------


class TestAsyncStatePollingMethodTransient404:
    """Verify that 404 responses during async polling are treated as transient."""

    @pytest.mark.asyncio
    async def test_404_retried_then_committed(self):
        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise _make_resource_not_found()
            return {"state": "Committed"}

        poller = AsyncStatePollingMethod(operation, "Committed", 0, retry_not_found=True)
        poller._status = "polling"
        await poller.run()

        assert poller.status() == "finished"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_404_raises_when_retry_not_found_false(self):
        async def operation():
            raise _make_resource_not_found()

        poller = AsyncStatePollingMethod(operation, "Ready", 0, retry_not_found=False)
        poller._status = "polling"

        with pytest.raises(ResourceNotFoundError):
            await poller.run()

        assert poller.status() == "failed"

    @pytest.mark.asyncio
    async def test_404_with_invalid_transaction_id_raises(self):
        async def operation():
            raise _make_resource_not_found(error_code="InvalidTransactionId")

        poller = AsyncStatePollingMethod(operation, "Committed", 0, retry_not_found=True)
        poller._status = "polling"

        with pytest.raises(ResourceNotFoundError):
            await poller.run()

        assert poller.status() == "failed"

    @pytest.mark.asyncio
    async def test_404_raises_after_3_retries(self):
        """After 3 consecutive 404s the async poller should give up and raise."""

        async def operation():
            raise _make_resource_not_found()

        poller = AsyncStatePollingMethod(operation, "Committed", 0, retry_not_found=True)
        poller._status = "polling"

        with pytest.raises(ResourceNotFoundError):
            await poller.run()

        assert poller.status() == "failed"


class TestAsyncStatePollingMethodTransient406:
    """Verify that 406 responses during async polling are treated as transient."""

    @pytest.mark.asyncio
    async def test_406_retried_then_committed(self):
        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise _make_http_response_error(406, "Not Acceptable")
            return {"state": "Committed"}

        poller = AsyncStatePollingMethod(operation, "Committed", 0, retry_not_found=True)
        poller._status = "polling"
        await poller.run()

        assert poller.status() == "finished"
        assert call_count == 4

    @pytest.mark.asyncio
    async def test_406_raises_when_retry_not_found_false(self):
        async def operation():
            raise _make_http_response_error(406, "Not Acceptable")

        poller = AsyncStatePollingMethod(operation, "Ready", 0, retry_not_found=False)
        poller._status = "polling"

        with pytest.raises(HttpResponseError):
            await poller.run()

        assert poller.status() == "failed"

    @pytest.mark.asyncio
    async def test_many_406s_retried_without_limit(self):
        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 10:
                raise _make_http_response_error(406, "Not Acceptable")
            return {"state": "Committed"}

        poller = AsyncStatePollingMethod(operation, "Committed", 0, retry_not_found=True)
        poller._status = "polling"
        await poller.run()

        assert poller.status() == "finished"
        assert call_count == 11


class TestAsyncStatePollingMethodMixed:
    """Verify mixed 404/406 sequences and non-transient errors in async polling."""

    @pytest.mark.asyncio
    async def test_mixed_404_and_406_retried(self):
        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 1 and call_count <= 4:
                raise _make_resource_not_found()
            if call_count % 2 == 0 and call_count <= 4:
                raise _make_http_response_error(406, "Not Acceptable")
            return {"state": "Committed"}

        poller = AsyncStatePollingMethod(operation, "Committed", 0, retry_not_found=True)
        poller._status = "polling"
        await poller.run()

        assert poller.status() == "finished"
        assert call_count == 5

    @pytest.mark.asyncio
    async def test_other_http_errors_raise_immediately(self):
        async def operation():
            raise _make_http_response_error(500, "Internal Server Error")

        poller = AsyncStatePollingMethod(operation, "Committed", 0, retry_not_found=True)
        poller._status = "polling"

        with pytest.raises(HttpResponseError):
            await poller.run()

        assert poller.status() == "failed"
