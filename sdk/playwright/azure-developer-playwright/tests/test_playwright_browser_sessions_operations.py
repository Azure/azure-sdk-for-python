# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
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
