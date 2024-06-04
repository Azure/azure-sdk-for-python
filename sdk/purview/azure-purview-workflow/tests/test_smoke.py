# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import WorkflowTest, WorkflowPowerShellPreparer
from devtools_testutils import recorded_by_proxy


class TestWorkflowSmoke(WorkflowTest):

    @WorkflowPowerShellPreparer()
    @recorded_by_proxy
    def test_smoke(self, workflow_endpoint):
        client = self.create_client(endpoint=workflow_endpoint)
        response = client.workflows.list()
        result = [item for item in response]
        assert len(result) >= 1
