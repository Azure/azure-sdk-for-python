# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.ai.projects import AIProjectClient
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, is_live


class TestTelemetry(TestBase):

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_telemetry.py::TestTelemetry::test_telemetry -s
    @servicePreparer()
    @recorded_by_proxy
    def test_telemetry(self, **kwargs):

        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        print("\n=====> Endpoint:", endpoint)

        with AIProjectClient(
            endpoint=endpoint,
            credential=self.get_credential(AIProjectClient, is_async=False),
        ) as project_client:

            print("[test_telemetry] Get the Application Insights connection string:")
            connection_string = project_client.telemetry.get_connection_string()
            assert connection_string
            if is_live():
                assert bool(self.REGEX_APPINSIGHTS_CONNECTION_STRING.match(connection_string))
            else:
                assert connection_string == "Sanitized-api-key"
            assert connection_string == project_client.telemetry.get_connection_string()  # Test cached value
            print("Application Insights connection string = " + connection_string)
