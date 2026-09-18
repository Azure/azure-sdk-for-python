# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Tests for SDK retry policy improvements (BUGBASH umbrella #5269224).

Verifies:
1. POST retries capped at 2 (not 5) — surfaces root cause faster.
2. Retry-After header is honored over default backoff.
3. Network errors use escalating backoff between retries.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import pytest

# ---------------------------------------------------------------------------
# Async _post retry cap (#5261585)
# ---------------------------------------------------------------------------


class TestAsyncPostRetryCap:
    """The async _post function should retry at most 2 times (3 total attempts)."""

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client._heartbeat_tasks = {}
        client._post_semaphore = asyncio.Semaphore(64)
        client._sampling_session_seq = {}
        return client

    @pytest.mark.asyncio
    async def test_max_retries_is_2(self, mock_client):
        """After 2 consecutive same-status failures, the error surfaces immediately."""
        from azure.ai.finetuningsessions.aio._patch import _post
        from azure.ai.finetuningsessions._exceptions import NoCapacityError

        # Mock response: always return 503 with capacity message
        mock_resp = MagicMock()
        mock_resp.status_code = 503
        mock_resp.headers = {"Retry-After": "0.01"}
        mock_resp.json.return_value = {
            "reason": "engine_busy",
            "message": "No capacity available",
            "retry_after_sec": 0.01,
        }
        mock_client.send_request = AsyncMock(return_value=mock_resp)

        with pytest.raises(NoCapacityError):
            await _post(mock_client, "/fine_tuning_sessions/session_deadbeef/forward_backward", {})

        # 2 consecutive same-status → classified as persistent, raised immediately
        assert mock_client.send_request.call_count == 2

    @pytest.mark.asyncio
    async def test_honors_retry_after_header(self, mock_client):
        """When Retry-After header is present, SDK uses that wait time."""
        from azure.ai.finetuningsessions.aio._patch import _post

        # First call: 503 with Retry-After; second call: 200
        resp_503 = MagicMock()
        resp_503.status_code = 503
        resp_503.headers = {"Retry-After": "0.01"}
        resp_503.json.return_value = {
            "reason": "engine_busy",
            "message": "No capacity",
            "retry_after_sec": 0.01,
        }
        resp_200 = MagicMock()
        resp_200.status_code = 200
        resp_200.json.return_value = {"request_id": "req_123", "session_id": "s1"}
        resp_200.headers = {}

        mock_client.send_request = AsyncMock(side_effect=[resp_503, resp_200])

        with patch("azure.ai.finetuningsessions.aio._patch.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            request_id, op_type = await _post(
                mock_client, "/fine_tuning_sessions/session_deadbeef/forward_backward", {}
            )

        assert request_id == "req_123"
        # sleep should have been called with a value derived from Retry-After (0.01 * jitter)
        assert mock_sleep.called
        sleep_val = mock_sleep.call_args[0][0]
        # With jitter (1 - 0.25*random), value should be between 0.0075 and 0.01
        assert 0.005 <= sleep_val <= 0.011

    @pytest.mark.asyncio
    async def test_consecutive_same_status_raises_typed(self, mock_client):
        """After 2 consecutive same-status failures, a typed exception is raised."""
        from azure.ai.finetuningsessions.aio._patch import _post
        from azure.ai.finetuningsessions._exceptions import NoCapacityError

        mock_resp = MagicMock()
        mock_resp.status_code = 503
        mock_resp.headers = {"Retry-After": "0.01"}
        mock_resp.json.return_value = {
            "reason": "engine_busy",
            "message": "No capacity available",
            "retry_after_sec": 0.01,
        }
        mock_client.send_request = AsyncMock(return_value=mock_resp)

        with pytest.raises(NoCapacityError) as exc_info:
            await _post(mock_client, "/fine_tuning_sessions/session_deadbeef/forward_backward", {})

        # NoCapacityError should carry the reason
        assert exc_info.value.reason == "engine_busy"

    @pytest.mark.asyncio
    async def test_non_retryable_raises_immediately(self, mock_client):
        """400/413/422 are not retried — immediate typed exception."""
        from azure.ai.finetuningsessions.aio._patch import _post
        from azure.ai.finetuningsessions._exceptions import BatchTooLargeError

        mock_resp = MagicMock()
        mock_resp.status_code = 413
        mock_resp.headers = {}
        mock_resp.json.return_value = {
            "message": "Batch size (20) exceeds the maximum allowed (10)",
            "field": "forward_backward_input.data",
        }
        mock_client.send_request = AsyncMock(return_value=mock_resp)

        with pytest.raises(BatchTooLargeError):
            await _post(mock_client, "/fine_tuning_sessions/session_deadbeef/forward_backward", {})

        # Only one attempt — no retries for 413
        assert mock_client.send_request.call_count == 1

    @pytest.mark.asyncio
    async def test_timeout_escalates_on_network_error(self, mock_client):
        """connection_timeout increases on each retry attempt."""
        from azure.ai.finetuningsessions.aio._patch import _post
        from azure.core.exceptions import ServiceResponseError

        # All attempts raise network error to exercise the retry path fully.
        mock_client.send_request = AsyncMock(side_effect=ServiceResponseError("read timeout"))

        with patch("azure.ai.finetuningsessions.aio._patch.asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(ServiceResponseError):
                await _post(mock_client, "/fine_tuning_sessions/session_deadbeef/forward_backward", {})

        # 3 total attempts (initial + 2 retries)
        assert mock_client.send_request.call_count == 3

        # Verify escalating connection_timeout was passed on each call.
        calls = mock_client.send_request.call_args_list
        timeouts = [c.kwargs.get("connection_timeout") for c in calls]
        # Each subsequent timeout should be larger than the previous.
        assert timeouts[0] is not None
        assert timeouts[1] > timeouts[0]
        assert timeouts[2] > timeouts[1]
        # Verify multiplier: 100, 150, 225
        assert timeouts[0] == 100
        assert timeouts[1] == 150
        assert timeouts[2] == 225


# ---------------------------------------------------------------------------
# Terminal engine-dead 409 is non-retryable (bug 5547547)
# ---------------------------------------------------------------------------


class TestAsyncEngineDead409NonRetryable:
    """A structured ``engine_dead`` 409 is terminal: it must classify to a typed
    ``TrainingEngineError`` and hit the backend exactly ONCE, on both the
    ``_post`` (forward / forward_backward / optim / save) and ``_post_sample``
    paths. Before the fix a 409 fell into the generic 408/409/429/5xx retry
    tracking, so ``_post`` sent twice and ``_post_sample`` up to three times.
    """

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client._heartbeat_tasks = {}
        client._post_semaphore = asyncio.Semaphore(64)
        client._sampling_session_seq = {}
        return client

    @staticmethod
    def _engine_dead_409():
        resp = MagicMock()
        resp.status_code = 409
        resp.headers = {}
        resp.json.return_value = {
            "reason": "engine_dead",
            "message": "Model 'model_fffe9b40' failed because its engine died. " "LoRA weights are lost.",
            "error_code": "engine_dead",
        }
        return resp

    @pytest.mark.asyncio
    async def test_post_engine_dead_409_single_call(self, mock_client):
        """_post: terminal 409 raises TrainingEngineError after exactly one send."""
        from azure.ai.finetuningsessions.aio._patch import _post
        from azure.ai.finetuningsessions._exceptions import TrainingEngineError

        mock_client.send_request = AsyncMock(return_value=self._engine_dead_409())

        with patch(
            "azure.ai.finetuningsessions.aio._patch.asyncio.sleep",
            new_callable=AsyncMock,
        ) as mock_sleep:
            with pytest.raises(TrainingEngineError) as exc_info:
                await _post(
                    mock_client,
                    "/fine_tuning_sessions/session_deadbeef/forward_backward",
                    {},
                )

        assert mock_client.send_request.call_count == 1
        assert not mock_sleep.called
        assert exc_info.value.error_code == "engine_dead"

    @pytest.mark.asyncio
    async def test_post_sample_engine_dead_409_single_call(self, mock_client):
        """_post_sample: terminal 409 raises after exactly one send (no fault retry)."""
        from azure.ai.finetuningsessions.aio._patch import _post_sample
        from azure.ai.finetuningsessions._exceptions import TrainingEngineError

        mock_client.send_request = AsyncMock(return_value=self._engine_dead_409())

        with patch(
            "azure.ai.finetuningsessions.aio._patch.asyncio.sleep",
            new_callable=AsyncMock,
        ) as mock_sleep:
            with pytest.raises(TrainingEngineError) as exc_info:
                await _post_sample(
                    mock_client,
                    "/fine_tuning_sessions/session_deadbeef/sample",
                    {},
                )

        assert mock_client.send_request.call_count == 1
        assert not mock_sleep.called
        assert exc_info.value.error_code == "engine_dead"

    @pytest.mark.asyncio
    async def test_post_unclassified_409_still_retries(self, mock_client):
        """An unclassified 409 keeps its existing retry behavior (not made terminal)."""
        from azure.ai.finetuningsessions.aio._patch import _post

        resp = MagicMock()
        resp.status_code = 409
        resp.headers = {"Retry-After": "0.01"}
        # No engine-dead markers → _classify_http_error returns None.
        resp.json.return_value = {"reason": "lease_conflict", "message": "try again"}
        mock_client.send_request = AsyncMock(return_value=resp)

        with patch(
            "azure.ai.finetuningsessions.aio._patch.asyncio.sleep",
            new_callable=AsyncMock,
        ):
            with pytest.raises(Exception):
                await _post(
                    mock_client,
                    "/fine_tuning_sessions/session_deadbeef/forward_backward",
                    {},
                )

        # Unclassified 409 never becomes terminal, so it keeps exhausting the
        # full retry budget (initial + 2 retries = 3 sends) as before the fix.
        assert mock_client.send_request.call_count == 3
