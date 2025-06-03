# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
import time
import pytest
import types
from unittest.mock import Mock, patch

from azure.core.pipeline.transport import (
    AioHttpTransport,
)


class MockClientSession:
    """Mock aiohttp.ClientSession with a close method that sleeps for 30 seconds."""

    def __init__(self):
        self._closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        pass

    async def close(self):
        """Simulate a slow closing session."""
        self._closed = True
        await asyncio.sleep(30)  # Simulate a very slow close operation

    def request(self, *args, **kwargs):
        return asyncio.Future()  # Just needs to be awaitable


@pytest.mark.asyncio
async def test_aiohttp_transport_close_timeout():
    """Test that AioHttpTransport.close() returns within 1 second even if session.close() takes 30 seconds."""

    # Create transport with our mock session
    mock_session = MockClientSession()
    transport = AioHttpTransport(session=mock_session, session_owner=True)

    # Open the transport to initialize the session
    await transport.open()

    # Time the close operation
    start_time = time.time()
    await transport.close()
    end_time = time.time()

    # Verify close returned in a reasonable time (should be around 0.0001 seconds due to timeout)
    assert end_time - start_time < 0.1, f"Transport close took {end_time - start_time} seconds, should be < 0.1 seconds"

    # Ensure transport's session was set to None
    assert transport.session is None
