# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from azure.ai.projects import AIProjectClient
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, is_live


class TestTelemetry(TestBase):

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\telemetry\test_telemetry.py::TestTelemetry::test_telemetry -s
    #@pytest.mark.skip(reason="Temporary skip test until we have an AppInsights resource connected")
    @servicePreparer()
    @recorded_by_proxy
    def test_telemetry(self, **kwargs):

        with self.create_client(**kwargs) as project_client:

            print("\n[test_telemetry] Get the Application Insights connection string:")
            connection_string = project_client.telemetry.get_application_insights_connection_string()
            assert connection_string
            if is_live():
                assert bool(self.REGEX_APPINSIGHTS_CONNECTION_STRING.match(connection_string))
            else:
                assert connection_string == "sanitized-api-key"
            assert (
                connection_string == project_client.telemetry.get_application_insights_connection_string()
            )  # Test cached value
            print("Application Insights connection string = " + connection_string)
