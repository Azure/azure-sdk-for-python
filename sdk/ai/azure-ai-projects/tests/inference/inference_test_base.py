# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import os
import logging
import functools
from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AIProjectClientAsync
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader

servicePreparerInferenceTests = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_projects_inference_tests",
    azure_ai_projects_inference_tests_project_connection_string="region.api.azureml.ms;00000000-0000-0000-0000-000000000000;rg-name;project-name",
    azure_ai_projects_inference_tests_aoai_api_version="aoai-api-version",
    azure_ai_projects_inference_tests_aoai_model_deployment_name="aoai-model-deployment-name",
    azure_ai_projects_inference_tests_aiservices_model_deployment_name="aoai-model-deployment-name",
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


class InferenceTestBase(AzureRecordedTestCase):

    def get_sync_client(self, **kwargs) -> AIProjectClient:
        conn_str = kwargs.pop("azure_ai_projects_inference_tests_project_connection_string")
        project_client = AIProjectClient.from_connection_string(
            credential=self.get_credential(AIProjectClient, is_async=False),
            conn_str=conn_str,
            logging_enable=LOGGING_ENABLED,
        )
        return project_client

    def get_async_client(self, **kwargs) -> AIProjectClientAsync:
        conn_str = kwargs.pop("azure_ai_projects_inference_tests_project_connection_string")
        project_client = AIProjectClientAsync.from_connection_string(
            credential=self.get_credential(AIProjectClientAsync, is_async=True),
            conn_str=conn_str,
            logging_enable=LOGGING_ENABLED,
        )
        return project_client
