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


class TestPlaywrightWorkspacesOperationsAsync(PlaywrightClientTestBaseAsync):
    @PlaywrightPreparer()
    @recorded_by_proxy_async
    async def test_workspaces_get(self, playwright_endpoint, playwright_workspace_id):
        client = self.create_async_client(endpoint=playwright_endpoint)
        response = await client.workspaces.get(
            workspace_id=playwright_workspace_id,
        )
        assert response is not None
        assert "id" in response

    @pytest.mark.live_test_only
    @pytest.mark.asyncio
    async def test_workspaces_get_browsers(self):
        endpoint = os.environ["PLAYWRIGHT_ENDPOINT"]
        workspace_id = os.environ["PLAYWRIGHT_WORKSPACE_ID"]
        client = self.create_async_client(endpoint=endpoint)
        response = await client.workspaces.get_browsers(
            workspace_id=workspace_id,
            os="Linux",
        )
        assert response is None
