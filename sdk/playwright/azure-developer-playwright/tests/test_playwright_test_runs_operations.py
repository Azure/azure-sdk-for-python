# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import uuid

import pytest
from devtools_testutils import recorded_by_proxy

from testpreparer import PlaywrightClientTestBase, PlaywrightPreparer


class TestPlaywrightTestRunsOperations(PlaywrightClientTestBase):
    @PlaywrightPreparer()
    @recorded_by_proxy
    def test_test_runs_create_or_update(self, playwright_endpoint, playwright_workspace_id, **kwargs):
        variables = kwargs.pop("variables", {})
        run_id = variables.setdefault("run_id", str(uuid.uuid4()))

        client = self.create_client(endpoint=playwright_endpoint)
        response = client.test_runs.create_or_update(
            workspace_id=playwright_workspace_id,
            run_id=run_id,
            resource={
                "displayName": "test-run",
            },
        )

        assert response is not None
        assert response["displayName"] == "test-run"
        assert "runId" in response
        assert "creatorId" in response
        return variables

    @PlaywrightPreparer()
    @recorded_by_proxy
    def test_test_runs_list(self, playwright_endpoint, playwright_workspace_id):
        client = self.create_client(endpoint=playwright_endpoint)
        response = client.test_runs.list(
            workspace_id=playwright_workspace_id,
        )
        result = [r for r in response]
        assert isinstance(result, list)
