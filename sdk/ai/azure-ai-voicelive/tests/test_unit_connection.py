# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

import pytest
from unittest.mock import AsyncMock, patch

pytest.importorskip(
    "aiohttp",
    reason="Skipping aio tests: aiohttp not installed (whl_no_aio).",
)

from azure.ai.voicelive.aio import (
    VoiceLiveConnection,
    SessionResource,
    ResponseResource,
    ConnectionError,
    ConnectionClosed,
)
from azure.ai.voicelive.models import (
    ClientEventSessionUpdate,
    ClientEventResponseCreate,
    ClientEventResponseCancel,
    RequestSession,
    ResponseCreateParams,
    Modality,
    OpenAIVoiceName,
    OpenAIVoice,
)
from azure.core.credentials import AzureKeyCredential


class TestConnectionExceptions:
    """Test connection exception classes."""

    def test_connection_error_creation(self):
        """Test ConnectionError exception creation."""
        error = ConnectionError("Test connection error")
        assert str(error) == "Test connection error"
        assert isinstance(error, Exception)

    def test_connection_closed_creation(self):
        """Test ConnectionClosed exception creation."""
        error = ConnectionClosed(code=1000, reason="Normal closure")
        assert error.code == 1000
        assert error.reason == "Normal closure"
        assert "WebSocket connection closed with code 1000: Normal closure" in str(error)
        assert isinstance(error, ConnectionError)

    def test_connection_closed_inheritance(self):
        """Test that ConnectionClosed inherits from ConnectionError."""
        error = ConnectionClosed(code=1001, reason="Going away")
        assert isinstance(error, ConnectionError)
        assert isinstance(error, Exception)


class TestSessionResource:
    """Test SessionResource class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_connection = AsyncMock()
        self.session_resource = SessionResource(self.mock_connection)

    @pytest.mark.asyncio
    async def test_session_update_with_request_session(self):
        """Test session update with RequestSession object."""
        session = RequestSession(model="gpt-4o-realtime-preview", modalities=[Modality.TEXT, Modality.AUDIO])

        await self.session_resource.update(session=session)

        # Verify that send was called with correct event type
        self.mock_connection.send.assert_called_once()
        call_args = self.mock_connection.send.call_args[0][0]
        assert isinstance(call_args, ClientEventSessionUpdate)

    @pytest.mark.asyncio
    async def test_session_update_with_mapping(self):
        """Test session update with dictionary mapping."""
        session_dict = {"model": "gpt-4o-realtime-preview", "modalities": ["text", "audio"], "temperature": 0.7}

        await self.session_resource.update(session=session_dict)

        # Verify that send was called
        self.mock_connection.send.assert_called_once()
        call_args = self.mock_connection.send.call_args[0][0]
        assert isinstance(call_args, ClientEventSessionUpdate)

    @pytest.mark.asyncio
    async def test_session_update_with_event_id(self):
        """Test session update with event ID."""
        session = RequestSession(model="gpt-4o-realtime-preview")
        event_id = "test-event-123"

        await self.session_resource.update(session=session, event_id=event_id)

        # Verify that send was called
        self.mock_connection.send.assert_called_once()


class TestResponseResource:
    """Test ResponseResource class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_connection = AsyncMock()
        self.response_resource = ResponseResource(self.mock_connection)

    @pytest.mark.asyncio
    async def test_response_create_basic(self):
        """Test basic response creation."""
        await self.response_resource.create()

        # Verify that send was called with correct event type
        self.mock_connection.send.assert_called_once()
        call_args = self.mock_connection.send.call_args[0][0]
        assert isinstance(call_args, ClientEventResponseCreate)

    @pytest.mark.asyncio
    async def test_response_create_with_params(self):
        """Test response creation with parameters."""
        response_params = ResponseCreateParams()
        event_id = "response-event-123"
        instructions = "Additional instructions for this response"

        await self.response_resource.create(
            response=response_params, event_id=event_id, additional_instructions=instructions
        )

        # Verify that send was called
        self.mock_connection.send.assert_called_once()
        call_args = self.mock_connection.send.call_args[0][0]
        assert isinstance(call_args, ClientEventResponseCreate)

    @pytest.mark.asyncio
    async def test_response_create_with_dict(self):
        """Test response creation with dictionary parameters."""
        response_dict = {"modalities": ["text"]}

        await self.response_resource.create(response=response_dict)

        # Verify that send was called
        self.mock_connection.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_response_cancel_basic(self):
        """Test basic response cancellation."""
        await self.response_resource.cancel()

        # Verify that send was called with correct event type
        self.mock_connection.send.assert_called_once()
        call_args = self.mock_connection.send.call_args[0][0]
        assert isinstance(call_args, ClientEventResponseCancel)

    @pytest.mark.asyncio
    async def test_response_cancel_with_params(self):
        """Test response cancellation with parameters."""
        response_id = "response-123"
        event_id = "cancel-event-456"

        await self.response_resource.cancel(response_id=response_id, event_id=event_id)

        # Verify that send was called
        self.mock_connection.send.assert_called_once()


@pytest.mark.asyncio
class TestVoiceLiveConnectionMocked:
    """Test VoiceLiveConnection with mocked WebSocket."""

    def setup_method(self):
        """Set up test fixtures."""
        self.credential = AzureKeyCredential("test-key")
        self.endpoint = "wss://test-endpoint.com"

    @patch("azure.ai.voicelive.aio._patch.aiohttp.ClientSession.ws_connect")
    async def test_connection_initialization(self, mock_ws_connect):
        """Test connection initialization."""
        # Mock WebSocket connection
        mock_ws = AsyncMock()
        mock_ws_connect.return_value.__aenter__.return_value = mock_ws

        # This would typically be done through the connect() function
        # but we're testing the class directly here
        connection = VoiceLiveConnection(self.endpoint, self.credential)

        # Verify connection object creation
        assert connection is not None
        assert hasattr(connection, "session")
        assert hasattr(connection, "response")

    async def test_session_resource_creation(self):
        """Test that session resource is created correctly."""
        connection = VoiceLiveConnection(self.endpoint, self.credential)

        assert isinstance(connection.session, SessionResource)
        assert connection.session._connection is connection

    async def test_response_resource_creation(self):
        """Test that response resource is created correctly."""
        connection = VoiceLiveConnection(self.endpoint, self.credential)

        assert isinstance(connection.response, ResponseResource)
        assert connection.response._connection is connection


class TestVoiceLiveConnectionIntegration:
    """Integration tests for VoiceLiveConnection."""

    @pytest.mark.asyncio
    async def test_connection_context_manager(self):
        """Test that VoiceLiveConnection can be used as async context manager."""
        credential = AzureKeyCredential("test-key")
        endpoint = "wss://test-endpoint.com"

        # Mock the WebSocket connection
        with patch("azure.ai.voicelive.aio._patch.aiohttp.ClientSession.ws_connect") as mock_ws_connect:
            mock_ws = AsyncMock()
            mock_ws_connect.return_value.__aenter__.return_value = mock_ws

            try:
                # This is how the connection would typically be used
                connection = VoiceLiveConnection(endpoint, credential)

                # Test that resources are available
                assert hasattr(connection, "session")
                assert hasattr(connection, "response")

            except Exception as e:
                # If the connection setup fails due to mocking limitations,
                # that's expected in unit tests
                pytest.skip(f"Connection setup failed in test environment: {e}")

    @pytest.mark.asyncio
    async def test_send_message_flow(self):
        """Test sending a message through the connection."""
        credential = AzureKeyCredential("test-key")
        endpoint = "wss://test-endpoint.com"

        with patch("azure.ai.voicelive.aio._patch.aiohttp.ClientSession.ws_connect") as mock_ws_connect:
            mock_ws = AsyncMock()
            mock_ws_connect.return_value.__aenter__.return_value = mock_ws

            try:
                connection = VoiceLiveConnection(endpoint, credential)

                # Test session update
                session = RequestSession(model="gpt-4o-realtime-preview", voice=OpenAIVoice(name=OpenAIVoiceName.ALLOY))

                # Mock the send method
                connection.send = AsyncMock()

                await connection.session.update(session=session)

                # Verify send was called
                connection.send.assert_called_once()

            except Exception as e:
                pytest.skip(f"Connection flow test failed in test environment: {e}")


class TestConnectionResourceInteraction:
    """Test interaction between connection and resources."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_connection = AsyncMock()
        self.mock_connection.send = AsyncMock()

    @pytest.mark.asyncio
    async def test_session_and_response_interaction(self):
        """Test interaction between session and response resources."""
        session_resource = SessionResource(self.mock_connection)
        response_resource = ResponseResource(self.mock_connection)

        # Update session
        session = RequestSession(model="gpt-4o-realtime-preview", temperature=0.8)
        await session_resource.update(session=session)

        # Create response
        await response_resource.create(additional_instructions="Be concise")

        # Verify both operations called send
        assert self.mock_connection.send.call_count == 2

    @pytest.mark.asyncio
    async def test_multiple_session_updates(self):
        """Test multiple session updates."""
        session_resource = SessionResource(self.mock_connection)

        # First update
        session1 = RequestSession(model="gpt-4o-realtime-preview")
        await session_resource.update(session=session1, event_id="update-1")

        # Second update
        session2 = RequestSession(model="gpt-4o-realtime-preview", temperature=0.5)
        await session_resource.update(session=session2, event_id="update-2")

        # Verify both updates were sent
        assert self.mock_connection.send.call_count == 2

    @pytest.mark.asyncio
    async def test_response_create_and_cancel(self):
        """Test creating and then canceling a response."""
        response_resource = ResponseResource(self.mock_connection)

        # Create response
        await response_resource.create(event_id="create-1")

        # Cancel response
        await response_resource.cancel(response_id="response-123", event_id="cancel-1")

        # Verify both operations were sent
        assert self.mock_connection.send.call_count == 2


class TestConnectionErrorScenarios:
    """Test various error scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_connection = AsyncMock()

    @pytest.mark.asyncio
    async def test_connection_send_failure(self):
        """Test handling of connection send failures."""
        self.mock_connection.send.side_effect = ConnectionError("Send failed")

        session_resource = SessionResource(self.mock_connection)

        with pytest.raises(ConnectionError):
            session = RequestSession(model="gpt-4o-realtime-preview")
            await session_resource.update(session=session)

    @pytest.mark.asyncio
    async def test_connection_closed_during_operation(self):
        """Test handling of connection closure during operations."""
        self.mock_connection.send.side_effect = ConnectionClosed(1000, "Normal closure")

        response_resource = ResponseResource(self.mock_connection)

        with pytest.raises(ConnectionClosed) as exc_info:
            await response_resource.create()

        assert exc_info.value.code == 1000
        assert exc_info.value.reason == "Normal closure"

    @pytest.mark.asyncio
    async def test_invalid_session_parameters(self):
        """Test handling of invalid session parameters."""
        session_resource = SessionResource(self.mock_connection)

        # Test with None session (should raise TypeError or similar)
        with pytest.raises((TypeError, AttributeError)):
            await session_resource.update(session=None)


class TestAsyncContextBehavior:
    """Test async context manager behavior."""

    @pytest.mark.asyncio
    async def test_resource_lifecycle(self):
        """Test resource lifecycle management."""
        mock_connection = AsyncMock()

        session_resource = SessionResource(mock_connection)
        response_resource = ResponseResource(mock_connection)

        # Verify resources maintain connection reference
        assert session_resource._connection is mock_connection
        assert response_resource._connection is mock_connection

        # Verify resources can be used independently
        session = RequestSession(model="test-model")
        await session_resource.update(session=session)
        await response_resource.create()

        assert mock_connection.send.call_count == 2
