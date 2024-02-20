# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import WorkflowPowerShellPreparer
from testcase_async import WorkflowAsyncTest
from devtools_testutils.aio import recorded_by_proxy_async


class TestWorkflowSmokeAsync(WorkflowAsyncTest):

    @WorkflowPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_smoke_async(self, workflow_endpoint):
        client = self.create_async_client(endpoint=workflow_endpoint)
        response = client.list_workflows()
        result = [item async for item in response]
        assert len(result) >= 1
