# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.ai.projects.aio import AIProjectClient
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import is_live


class TestTelemetryAsync(TestBase):

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_telemetry_async.py::TestTelemetryAsync::test_telemetry_async -s
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_telemetry_async(self, **kwargs):

        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        print("\n=====> Endpoint:", endpoint)

        async with AIProjectClient(
            endpoint=endpoint,
            credential=self.get_credential(AIProjectClient, is_async=True),
        ) as project_client:

            print("[test_telemetry_async] Get the Application Insights connection string:")
            connection_string = await project_client.telemetry.get_connection_string()
            assert connection_string
            if is_live():
                assert bool(self.REGEX_APPINSIGHTS_CONNECTION_STRING.match(connection_string))
            else:
                assert connection_string == "Sanitized-api-key"
            assert connection_string == await project_client.telemetry.get_connection_string()  # Test cached value
            print("Application Insights connection string = " + connection_string)
