# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os

import pytest
from devtools_testutils import recorded_by_proxy

from testpreparer import PlaywrightClientTestBase, PlaywrightPreparer


class TestPlaywrightBrowserSessionsOperations(PlaywrightClientTestBase):
    @PlaywrightPreparer()
    @recorded_by_proxy
    def test_browser_sessions_list(self, playwright_endpoint, playwright_workspace_id):
        client = self.create_client(endpoint=playwright_endpoint)
        response = client.browser_sessions.list(
            workspace_id=playwright_workspace_id,
        )
        result = [r for r in response]
        assert isinstance(result, list)

    @recorded_by_proxy
    def test_browser_sessions_get(self, **kwargs):
        """Test getting a browser session by ID.

        This test uses a pre-existing browser session from a separate workspace
        because there is no publicly available API to create a browser session.
        The session endpoint, workspace ID, and session ID are configured via
        PLAYWRIGHT_SESSION_ENDPOINT, PLAYWRIGHT_SESSION_WORKSPACE_ID, and
        PLAYWRIGHT_SESSION_ID environment variables.
        """
        endpoint = os.environ["PLAYWRIGHT_SESSION_ENDPOINT"]
        workspace_id = os.environ["PLAYWRIGHT_SESSION_WORKSPACE_ID"]
        session_id = os.environ["PLAYWRIGHT_SESSION_ID"]

        client = self.create_client(endpoint=endpoint)
        response = client.browser_sessions.get(
            workspace_id=workspace_id,
            session_id=session_id,
        )

        assert response is not None
        assert "id" in response
        assert "status" in response

