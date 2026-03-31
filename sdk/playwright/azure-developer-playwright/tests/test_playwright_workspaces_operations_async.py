# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from devtools_testutils.aio import recorded_by_proxy_async

from testpreparer import PlaywrightPreparer
from testpreparer_async import PlaywrightClientTestBaseAsync


class TestPlaywrightWorkspacesOperationsAsync(PlaywrightClientTestBaseAsync):
    @pytest.mark.live_test_only
    @PlaywrightPreparer()
    @recorded_by_proxy_async
    async def test_workspaces_get_browsers(self, playwright_endpoint, playwright_workspace_id):
        client = self.create_async_client(endpoint=playwright_endpoint)
        response = await client.workspaces.get_browsers(
            workspace_id=playwright_workspace_id,
            os="Linux",
        )
        assert response is None
