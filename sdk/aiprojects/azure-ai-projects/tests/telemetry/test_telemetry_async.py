# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from azure.ai.projects.aio import AIProjectClient
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import is_live


class TestTelemetryAsync(TestBase):

    # To run this test, use the following command in the \sdk\aiprojects\azure-ai-projects folder:
    # cls & pytest tests\telemetry\test_telemetry_async.py::TestTelemetryAsync::test_telemetry_async -s
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_telemetry_async(self, **kwargs):

        async with self.create_async_client(**kwargs) as project_client:

            print("\n[test_telemetry_async] Get the Application Insights connection string:")
            connection_string = await project_client.telemetry.get_application_insights_connection_string()
            assert connection_string
            if is_live():
                assert bool(self.REGEX_APPINSIGHTS_CONNECTION_STRING.match(connection_string))
            else:
                assert connection_string == "sanitized-api-key"
            assert (
                connection_string == await project_client.telemetry.get_application_insights_connection_string()
            )  # Test cached value
            print("Application Insights connection string = " + connection_string)
