# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import logging
import functools
from os import path
from typing import Optional
from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AIProjectClientAsync
from azure.ai.inference.models import ImageEmbeddingInput
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader

servicePreparerInferenceTests = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_projects_inference_tests",
    azure_ai_projects_inference_tests_project_connection_string="region.api.azureml.ms;00000000-0000-0000-0000-000000000000;rg-name;project-name",
    azure_ai_projects_inference_tests_entraid_auth_aoai_connection_name="entraid-auth-aoai-connection-name",
    azure_ai_projects_inference_tests_entraid_auth_aiservices_connection_name="entraid-auth-aiservices-connection-name",
    azure_ai_projects_inference_tests_aoai_api_version="aoai-api-version",
    azure_ai_projects_inference_tests_aoai_model_deployment_name="aoai-model-deployment-name",
    azure_ai_projects_inference_tests_chat_completions_model_deployment_name="chat-completions-model-deployment-name",
    azure_ai_projects_inference_tests_embeddings_model_deployment_name="embeddings-model-deployment-name",
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

    NON_EXISTING_CONNECTION_NAME = "non-existing-connection-name"
    EXPECTED_EXCEPTION_MESSAGE_FOR_NON_EXISTING_CONNECTION_NAME = (
        f"Connection {NON_EXISTING_CONNECTION_NAME} can't be found in this workspace"
    )

    EXPECTED_EXCEPTION_MESSAGE_FOR_EMPTY_CONNECTION_NAME = f"Connection name cannot be empty"

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

    @staticmethod
    def get_image_embeddings_input(with_text: Optional[bool] = False) -> ImageEmbeddingInput:
        local_folder = path.dirname(path.abspath(__file__))
        image_file = path.join(local_folder, "test_image1.png")
        if with_text:
            return ImageEmbeddingInput.load(
                image_file=image_file,
                image_format="png",
                text="some text",
            )
        else:
            return ImageEmbeddingInput.load(
                image_file=image_file,
                image_format="png",
            )
