# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os

import pytest
from devtools_testutils.aio import recorded_by_proxy_async

from testpreparer import PlaywrightPreparer
from testpreparer_async import PlaywrightClientTestBaseAsync


class TestPlaywrightBrowserSessionsOperationsAsync(PlaywrightClientTestBaseAsync):
    @PlaywrightPreparer()
    @recorded_by_proxy_async
    async def test_browser_sessions_list(self, playwright_endpoint, playwright_workspace_id):
        client = self.create_async_client(endpoint=playwright_endpoint)
        response = client.browser_sessions.list(
            workspace_id=playwright_workspace_id,
        )
        result = [r async for r in response]
        assert isinstance(result, list)

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_browser_sessions_get(self, **kwargs):
        """Test getting a browser session by ID.

        This test uses a pre-existing browser session from a separate workspace
        because there is no publicly available API to create a browser session.
        The session endpoint, workspace ID, and session ID are configured via
        PLAYWRIGHT_SESSION_ENDPOINT, PLAYWRIGHT_SESSION_WORKSPACE_ID, and
        PLAYWRIGHT_SESSION_ID environment variables.
        """
        endpoint = os.environ.get("PLAYWRIGHT_SESSION_ENDPOINT", "https://fake.api.playwright.microsoft.com")
        workspace_id = os.environ.get("PLAYWRIGHT_SESSION_WORKSPACE_ID", "00000000-0000-0000-0000-000000000000")
        session_id = os.environ.get("PLAYWRIGHT_SESSION_ID", "00000000-0000-0000-0000-000000000000")

        client = self.create_async_client(endpoint=endpoint)
        response = await client.browser_sessions.get(
            workspace_id=workspace_id,
            session_id=session_id,
        )

        assert response is not None
        assert "id" in response
        assert "status" in response
