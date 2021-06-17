# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

import os
import sys

from devtools_testutils import AzureTestCase

from azure.core.exceptions import HttpResponseError
from azure.monitor.query import LogsQueryClient, LogsQueryRequest
from tests.preparers import logs_decorator


class LogsSingleQueryTest(AzureTestCase):
    @pytest.mark.live_test_only
    @logs_decorator
    def test_logs_send_single_query(self, workspace_id, secondary_workspace_id, credential, workspace_key, secondary_workspace_key):
        client = LogsQueryClient(credential)
        query = """AppRequests | 
        where TimeGenerated > ago(12h) | 
        summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

        # returns LogsQueryResults 
        response = client.query(workspace_id, query)

        assert response is not None
        assert response.tables is not None
