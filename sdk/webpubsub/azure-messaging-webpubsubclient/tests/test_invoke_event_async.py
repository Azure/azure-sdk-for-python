# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Client-level mocktests for invoke_event (async) exercising request/response
correlation, timeout, error mapping and disconnect rejection.
"""

import asyncio
import pytest
from unittest.mock import patch, AsyncMock

from azure.messaging.webpubsubclient.aio import WebPubSubClient as WebPubSubClientAsync
from azure.messaging.webpubsubclient.models import WebPubSubDataType
from azure.messaging.webpubsubclient.models._models import (
    InvokeResponseMessage,
    InvokeResponseError,
    InvocationError,
)


def _make_client() -> WebPubSubClientAsync:
    client = WebPubSubClientAsync(
        "wss://fake.webpubsub.azure.com",
        message_retry_total=0,
    )
    return client


@pytest.mark.asyncio
class TestInvokeEventAsync:
    """Client-level async invoke_event tests with mocked websocket."""

    async def test_request_response_correlation_text(self):
        """invoke_event returns the correct InvokeEventResult for a successful text response."""
        client = _make_client()

        async def fake_send(message, **kwargs):
            # Schedule the reply so it arrives after invoke_event starts waiting
            async def reply():
                client._invocation_map.resolve(
                    InvokeResponseMessage(
                        invocation_id=message.invocation_id,
                        success=True,
                        data_type=WebPubSubDataType.TEXT,
                        data="pong",
                    )
                )

            asyncio.get_event_loop().call_soon(lambda: asyncio.ensure_future(reply()))

        with patch.object(client, "_send_message", side_effect=fake_send):
            result = await client.invoke_event("echo", "ping", WebPubSubDataType.TEXT)

        assert result.data == "pong"
        assert result.data_type == WebPubSubDataType.TEXT
        assert result.invocation_id is not None

    async def test_request_response_correlation_json(self):
        """invoke_event returns the correct InvokeEventResult for a successful JSON response."""
        client = _make_client()

        async def fake_send(message, **kwargs):
            async def reply():
                client._invocation_map.resolve(
                    InvokeResponseMessage(
                        invocation_id=message.invocation_id,
                        success=True,
                        data_type=WebPubSubDataType.JSON,
                        data={"result": "ok"},
                    )
                )

            asyncio.get_event_loop().call_soon(lambda: asyncio.ensure_future(reply()))

        with patch.object(client, "_send_message", side_effect=fake_send):
            result = await client.invoke_event(
                "processOrder", {"orderId": 1}, WebPubSubDataType.JSON
            )

        assert result.data == {"result": "ok"}
        assert result.data_type == WebPubSubDataType.JSON

    async def test_custom_invocation_id(self):
        """When a custom invocation_id is provided it is used in the result."""
        client = _make_client()

        async def fake_send(message, **kwargs):
            assert message.invocation_id == "my-custom-id"

            async def reply():
                client._invocation_map.resolve(
                    InvokeResponseMessage(
                        invocation_id=message.invocation_id,
                        success=True,
                        data_type=WebPubSubDataType.TEXT,
                        data="ok",
                    )
                )

            asyncio.get_event_loop().call_soon(lambda: asyncio.ensure_future(reply()))

        with patch.object(client, "_send_message", side_effect=fake_send):
            result = await client.invoke_event(
                "echo", "hi", WebPubSubDataType.TEXT, invocation_id="my-custom-id"
            )

        assert result.invocation_id == "my-custom-id"

    async def test_timeout_raises_invocation_error(self):
        """invoke_event raises InvocationError when the response does not arrive within timeout."""
        client = _make_client()

        async def fake_send(message, **kwargs):
            pass  # No reply — simulates a timeout

        with patch.object(client, "_send_message", side_effect=fake_send):
            with pytest.raises(InvocationError) as exc_info:
                await client.invoke_event(
                    "slowEvent", "data", WebPubSubDataType.TEXT, timeout=0.1
                )

        assert "Timeout" in str(exc_info.value)

    async def test_timeout_sends_cancel_invocation(self):
        """invoke_event sends cancelInvocation when timeout occurs."""
        client = _make_client()
        cancel_ids = []

        original_send_cancel = client._send_cancel_invocation

        async def track_cancel(invocation_id):
            cancel_ids.append(invocation_id)
            await original_send_cancel(invocation_id)

        async def fake_send(message, **kwargs):
            pass  # No reply — simulates a timeout

        with patch.object(client, "_send_message", side_effect=fake_send):
            with patch.object(client, "_send_cancel_invocation", side_effect=track_cancel):
                with pytest.raises(InvocationError):
                    await client.invoke_event(
                        "slowEvent", "data", WebPubSubDataType.TEXT, timeout=0.1
                    )

        assert len(cancel_ids) == 1

    async def test_error_response_success_false(self):
        """invoke_event raises InvocationError with error_detail when success == False."""
        client = _make_client()

        async def fake_send(message, **kwargs):
            async def reply():
                client._invocation_map.resolve(
                    InvokeResponseMessage(
                        invocation_id=message.invocation_id,
                        success=False,
                        error=InvokeResponseError(
                            name="BadRequest", message="Invalid payload"
                        ),
                    )
                )

            asyncio.get_event_loop().call_soon(lambda: asyncio.ensure_future(reply()))

        with patch.object(client, "_send_message", side_effect=fake_send):
            with pytest.raises(InvocationError) as exc_info:
                await client.invoke_event("fail", "data", WebPubSubDataType.TEXT)

        err = exc_info.value
        assert err.error_detail is not None
        assert err.error_detail.name == "BadRequest"
        assert err.error_detail.message == "Invalid payload"

    async def test_error_response_success_false_no_error_detail(self):
        """invoke_event raises InvocationError with default message when success == False and no error detail."""
        client = _make_client()

        async def fake_send(message, **kwargs):
            async def reply():
                client._invocation_map.resolve(
                    InvokeResponseMessage(
                        invocation_id=message.invocation_id,
                        success=False,
                        error=None,
                    )
                )

            asyncio.get_event_loop().call_soon(lambda: asyncio.ensure_future(reply()))

        with patch.object(client, "_send_message", side_effect=fake_send):
            with pytest.raises(InvocationError) as exc_info:
                await client.invoke_event("fail", "data", WebPubSubDataType.TEXT)

        assert "Invocation failed" in str(exc_info.value)

    async def test_send_failure_raises_invocation_error(self):
        """invoke_event raises InvocationError when _send_message fails."""
        client = _make_client()

        async def fake_send(message, **kwargs):
            raise Exception("connection lost")

        with patch.object(client, "_send_message", side_effect=fake_send):
            with pytest.raises(InvocationError) as exc_info:
                await client.invoke_event("event", "data", WebPubSubDataType.TEXT)

        assert "connection lost" in str(exc_info.value)

    async def test_disconnect_rejects_pending_invocation(self):
        """Pending invocations are rejected when reject_all is called (simulating disconnect)."""
        client = _make_client()

        async def fake_send(message, **kwargs):
            # Simulate the connection dropping after the message is sent
            async def disconnect():
                client._invocation_map.reject_all(
                    lambda inv_id: InvocationError(
                        "Connection is disconnected",
                        invocation_id=inv_id,
                    )
                )

            asyncio.get_event_loop().call_soon(lambda: asyncio.ensure_future(disconnect()))

        with patch.object(client, "_send_message", side_effect=fake_send):
            with pytest.raises(InvocationError) as exc_info:
                await client.invoke_event("event", "data", WebPubSubDataType.TEXT)

        assert "disconnected" in str(exc_info.value).lower()

    async def test_invocation_entry_cleaned_up_after_success(self):
        """The invocation entry is discarded from the map after a successful call."""
        client = _make_client()

        async def fake_send(message, **kwargs):
            async def reply():
                client._invocation_map.resolve(
                    InvokeResponseMessage(
                        invocation_id=message.invocation_id,
                        success=True,
                        data_type=WebPubSubDataType.TEXT,
                        data="ok",
                    )
                )

            asyncio.get_event_loop().call_soon(lambda: asyncio.ensure_future(reply()))

        with patch.object(client, "_send_message", side_effect=fake_send):
            await client.invoke_event("echo", "hi", WebPubSubDataType.TEXT)

        assert len(client._invocation_map._entries) == 0

    async def test_invocation_entry_cleaned_up_after_error(self):
        """The invocation entry is discarded from the map after an error."""
        client = _make_client()

        async def fake_send(message, **kwargs):
            async def reply():
                client._invocation_map.resolve(
                    InvokeResponseMessage(
                        invocation_id=message.invocation_id,
                        success=False,
                        error=InvokeResponseError(
                            name="Error", message="fail"
                        ),
                    )
                )

            asyncio.get_event_loop().call_soon(lambda: asyncio.ensure_future(reply()))

        with patch.object(client, "_send_message", side_effect=fake_send):
            with pytest.raises(InvocationError):
                await client.invoke_event("fail", "data", WebPubSubDataType.TEXT)

        assert len(client._invocation_map._entries) == 0
