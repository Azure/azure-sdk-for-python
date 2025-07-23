# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# cspell:ignore toint
from datetime import datetime, timezone

from azure.monitor.querylogs import LogsQueryClient

from base_testcase import AzureMonitorQueryLogsTestCase


class TestLogsResponse(AzureMonitorQueryLogsTestCase):

    def test_query_response_data(self, recorded_test, monitor_info):
        # Sample log entry that is populated in table before test.
        # {
        #    "Time": "2022-11-07T01:03:07.584426Z",
        #    "Computer": "Computer1",
        #    "AdditionalContext": '{"testContextKey": 1, "CounterName": "AppMetric1"}}'
        # }

        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = (
            f"{monitor_info['table_name']} | project TimeGenerated, Type, ExtendedColumn, AdditionalContext"
            f"| order by TimeGenerated desc | take 5"
        )

        # returns LogsQueryResult
        result = client.query_workspace(monitor_info["workspace_id"], query, timespan=None)
        assert isinstance(result.tables[0].rows[0][0], datetime)

        assert isinstance(result.tables[0].rows[0][1], str)
        assert result.tables[0].rows[0][1] == monitor_info["table_name"]

        assert isinstance(result.tables[0].rows[0][2], str)
        # Check if DCR transformation correctly populated the ExtendedColumn field.
        assert "AppMetric" in result.tables[0].rows[0][2]

        assert isinstance(result.tables[0].rows[0][3], str)
        assert "testContextKey" in result.tables[0].rows[0][3]

    def test_query_response_types(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = """print "hello", true, make_datetime("2000-01-02 03:04:05Z"), toint(100), long(101), 102.1
            | project
                stringcolumn=print_0,
                boolcolumn=print_1,
                datecolumn=print_2,
                intcolumn=print_3,
                longcolumn=print_4,
                realcolumn=print_5
        """

        result = client.query_workspace(monitor_info["workspace_id"], query, timespan=None)

        table = result.tables[0]
        columns = table.columns
        row = table.rows[0]

        assert columns[0] == "stringcolumn"
        assert isinstance(row[0], str)
        assert row[0] == "hello"

        assert columns[1] == "boolcolumn"
        assert isinstance(row[1], bool)
        assert row[1] is True

        assert columns[2] == "datecolumn"
        assert isinstance(row[2], datetime)
        assert row[2] == datetime(2000, 1, 2, 3, 4, 5, tzinfo=timezone.utc)

        assert columns[3] == "intcolumn"
        assert isinstance(row[3], int)
        assert row[3] == 100

        assert columns[4] == "longcolumn"
        assert isinstance(row[4], int)
        assert row[4] == 101

        assert columns[5] == "realcolumn"
        assert isinstance(row[5], float)
        assert row[5] == 102.1
