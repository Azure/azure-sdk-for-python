# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import logging
import functools
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader


servicePreparerEvaluationsTests = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_projects_evaluations_tests",
    azure_ai_projects_evaluations_tests_project_connection_string="region.api.azureml.ms;00000000-0000-0000-0000-000000000000;rg-name;project-name",
    azure_ai_projects_evaluations_tests_default_aoai_connection_name="connection_name",
    azure_ai_projects_evaluations_tests_deployment_name="deployment_name",
    azure_ai_projects_evaluations_tests_api_version="2024-09-01-preview",
    azure_ai_projects_evaluations_tests_dataset_id="test_dataset_id",
)

# Set to True to enable SDK logging
LOGGING_ENABLED = False

if LOGGING_ENABLED:
    # Create a logger for the 'azure' SDK
    # See https://docs.python.org/3/library/logging.html
    logger = logging.getLogger("azure")
    logger.setLevel(logging.DEBUG)  # INFO or DEBUG

    # Configure a console output
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)


class EvaluationsTestBase(AzureRecordedTestCase):

    def get_sync_client(self, **kwargs) -> AIProjectClient:
        conn_str = kwargs.pop("azure_ai_projects_evaluations_tests_project_connection_string")
        project_client = AIProjectClient.from_connection_string(
            credential=self.get_credential(AIProjectClient, is_async=False),
            conn_str=conn_str,
            logging_enable=LOGGING_ENABLED,
        )
        return project_client
