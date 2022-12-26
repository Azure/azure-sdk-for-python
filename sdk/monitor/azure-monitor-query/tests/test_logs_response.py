# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import datetime, timezone

from azure.monitor.query import LogsQueryClient
from devtools_testutils import AzureRecordedTestCase


class TestLogsResponse(AzureRecordedTestCase):

    def test_query_response_data(self, recorded_test, monitor_info):
        # Sample log entry that is populated in table before test.
        # {
        #    "Time": "2022-11-07T01:03:07.584426Z",
        #    "Computer": "Computer1",
        #    "AdditionalContext": '{"testContextKey": 1, "CounterName": "AppMetric1"}}'
        # }

        client = self.create_client_from_credential(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = (
            f"{monitor_info['table_name']} | project TimeGenerated, Type, ExtendedColumn, AdditionalContext"
            f"| order by TimeGenerated desc | take 5")

        # returns LogsQueryResult
        result = client.query_workspace(monitor_info['workspace_id'], query, timespan=None)
        assert isinstance(result.tables[0].rows[0][0], datetime)

        assert isinstance(result.tables[0].rows[0][1], str)
        assert result.tables[0].rows[0][1] == monitor_info['table_name']

        assert isinstance(result.tables[0].rows[0][2], str)
        # Check if DCR transformation correctly populated the ExtendedColumn field.
        assert "AppMetric" in result.tables[0].rows[0][2]

        assert isinstance(result.tables[0].rows[0][3], str)
        assert "testContextKey" in result.tables[0].rows[0][3]

    def test_query_response_types(self, recorded_test, monitor_info):
        client = self.create_client_from_credential(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = """print "hello", true, make_datetime("2000-01-02 03:04:05Z"), toint(100), long(101), 102.1
            | project
                stringcolumn=print_0,
                boolcolumn=print_1,
                datecolumn=print_2,
                intcolumn=print_3,
                longcolumn=print_4,
                realcolumn=print_5
            """
        result = client.query_workspace(monitor_info['workspace_id'], query, timespan=None)

        assert isinstance(result.tables[0].rows[0][0], str)
        assert result.tables[0].rows[0][0] == "hello"

        assert isinstance(result.tables[0].rows[0][1], bool)
        assert result.tables[0].rows[0][1] == True

        assert isinstance(result.tables[0].rows[0][2], datetime)
        assert result.tables[0].rows[0][2] == datetime(2000, 1, 2, 3, 4, 5, tzinfo=timezone.utc)

        assert isinstance(result.tables[0].rows[0][3], int)
        assert result.tables[0].rows[0][3] == 100

        assert isinstance(result.tables[0].rows[0][4], int)
        assert result.tables[0].rows[0][4] == 101

        assert isinstance(result.tables[0].rows[0][5], float)
        assert result.tables[0].rows[0][5] == 102.1
