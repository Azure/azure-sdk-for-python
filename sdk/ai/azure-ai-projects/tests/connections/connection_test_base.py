# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import logging
import functools
import pprint
from typing import cast, Optional
from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AIProjectClientAsync
from azure.ai.projects.models import ConnectionProperties, ConnectionType, AuthenticationType
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, is_live_and_not_recording

servicePreparerConnectionsTests = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_projects_connections_tests",
    azure_ai_projects_connections_tests_project_connection_string="region.api.azureml.ms;00000000-0000-0000-0000-000000000000;rg-name;project-name",
    azure_ai_projects_connections_tests_default_key_auth_aoai_connection_name="default-key-auth-aoai-connection-name",
    azure_ai_projects_connections_tests_default_key_auth_aiservices_connection_name="default-key-auth-aiservices-connection-name",
    azure_ai_projects_connections_tests_aoai_api_version="aoai-api-version",
    azure_ai_projects_connections_tests_entraid_auth_aoai_connection_name="entraid-auth-aoai-connection-name",
    azure_ai_projects_connections_tests_entraid_auth_aiservices_connection_name="entraid-auth-aiservices-connection-name",
    azure_ai_projects_connections_tests_aoai_model_deployment_name="aoai-model-deployment-name",
    azure_ai_projects_connections_tests_chat_completions_model_deployment_name="chat-completions-model-deployment-name",
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


class ConnectionsTestBase(AzureRecordedTestCase):

    EXPECTED_EXCEPTION_MESSAGE_FOR_EMPTY_CONNECTION_NAME = f"Connection name cannot be empty"

    NON_EXISTING_CONNECTION_NAME = "non-existing-connection-name"
    EXPECTED_EXCEPTION_MESSAGE_FOR_NON_EXISTING_CONNECTION_NAME = (
        f"Connection {NON_EXISTING_CONNECTION_NAME} can't be found in this workspace"
    )

    NON_EXISTING_CONNECTION_TYPE = "non-existing-connection-type"
    EXPECTED_EXCEPTION_MESSAGE_FOR_NON_EXISTING_CONNECTION_TYPE = (
        f"No connection of type {NON_EXISTING_CONNECTION_TYPE} found"
    )

    def get_sync_client(self, **kwargs) -> AIProjectClient:
        conn_str = kwargs.pop("azure_ai_projects_connections_tests_project_connection_string")
        project_client = AIProjectClient.from_connection_string(
            credential=self.get_credential(AIProjectClient, is_async=False),
            conn_str=conn_str,
            logging_enable=LOGGING_ENABLED,
        )
        return project_client

    def get_async_client(self, **kwargs) -> AIProjectClientAsync:
        conn_str = kwargs.pop("azure_ai_projects_connections_tests_project_connection_string")
        project_client = AIProjectClientAsync.from_connection_string(
            credential=self.get_credential(AIProjectClient, is_async=True),
            conn_str=conn_str,
            logging_enable=LOGGING_ENABLED,
        )
        return project_client

    @classmethod
    def validate_connection(
        cls,
        connection: ConnectionProperties,
        include_credentials: bool,
        *,
        expected_connection_type: ConnectionType = None,
        expected_connection_name: str = None,
        expected_authentication_type: AuthenticationType = None,
    ):
        assert connection.id is not None

        if expected_connection_name:
            assert connection.name == expected_connection_name
        else:
            assert connection.name is not None

        if expected_connection_type:
            assert connection.connection_type == expected_connection_type
        else:
            assert connection.connection_type is not None

        if expected_authentication_type:
            assert connection.authentication_type == expected_authentication_type
        else:
            assert connection.authentication_type is not None

        if include_credentials:
            assert (connection.key is not None) ^ (connection.token_credential is not None)
        else:
            assert connection.key == None
            assert connection.token_credential == None

    @classmethod
    def validate_inference(
        cls, connection: ConnectionProperties, model_deployment_name: str, *, aoai_api_version: Optional[str] = None
    ):
        if connection.connection_type == ConnectionType.AZURE_OPEN_AI:

            if not is_live_and_not_recording():
                print("Skipped chat completions call with AOAI client, because it cannot be recorded.")
                return

            from openai import AzureOpenAI

            if connection.authentication_type == AuthenticationType.API_KEY:
                print("====> Creating AzureOpenAI client using API key authentication")
                aoai_client = AzureOpenAI(
                    api_key=connection.key,
                    azure_endpoint=connection.endpoint_url,
                    api_version=aoai_api_version,  # See "Data plane - inference" row in table https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
                )
            elif connection.authentication_type == AuthenticationType.ENTRA_ID:
                print("====> Creating AzureOpenAI client using Entra ID authentication")
                from azure.core.credentials import TokenCredential
                from azure.identity import get_bearer_token_provider

                aoai_client = AzureOpenAI(
                    # See https://learn.microsoft.com/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider
                    azure_ad_token_provider=get_bearer_token_provider(
                        cast(TokenCredential, connection.token_credential),
                        "https://cognitiveservices.azure.com/.default",
                    ),
                    azure_endpoint=connection.endpoint_url,
                    api_version=aoai_api_version,  # See "Data plane - inference" row in table https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
                )
            else:
                raise ValueError(f"Authentication type {connection.authentication_type} not supported.")

            aoai_response = aoai_client.chat.completions.create(
                model=model_deployment_name,
                messages=[
                    {
                        "role": "user",
                        "content": "How many feet are in a mile?",
                    },
                ],
            )
            print("\nChatCompletionsClient response:")
            pprint.pprint(aoai_response)
            contains = ["5280", "5,280"]
            assert any(item in aoai_response.choices[0].message.content for item in contains)
            aoai_client.close()

        elif connection.connection_type == ConnectionType.AZURE_AI_SERVICES:

            from azure.ai.inference import ChatCompletionsClient
            from azure.ai.inference.models import UserMessage

            if connection.authentication_type == AuthenticationType.API_KEY:
                print("====> Creating ChatCompletionsClient using API key authentication")
                from azure.core.credentials import AzureKeyCredential

                inference_client = ChatCompletionsClient(
                    endpoint=f"{connection.endpoint_url}/models", credential=AzureKeyCredential(connection.key or "")
                )
            elif connection.authentication_type == AuthenticationType.ENTRA_ID:
                from azure.core.credentials import TokenCredential

                print("====> Creating ChatCompletionsClient using Entra ID authentication")
                inference_client = ChatCompletionsClient(
                    endpoint=f"{connection.endpoint_url}/models",
                    credential=cast(TokenCredential, connection.token_credential),
                    credential_scopes=["https://cognitiveservices.azure.com/.default"],
                )
            else:
                raise ValueError(f"Authentication type {connection.authentication_type} not supported.")

            inference_response = inference_client.complete(
                model=model_deployment_name, messages=[UserMessage(content="How many feet are in a mile?")]
            )
            print("\nChatCompletionsClient response:")
            pprint.pprint(inference_response)
            contains = ["5280", "5,280"]
            assert any(item in inference_response.choices[0].message.content for item in contains)
            inference_client.close()

    @classmethod
    async def validate_async_inference(
        cls, connection: ConnectionProperties, model_deployment_name: str, *, aoai_api_version: Optional[str] = None
    ):
        if connection.connection_type == ConnectionType.AZURE_OPEN_AI:

            if not is_live_and_not_recording():
                print("Skipped chat completions call with AOAI client, because it cannot be recorded.")
                return

            from openai import AsyncAzureOpenAI

            if connection.authentication_type == AuthenticationType.API_KEY:
                print("====> Creating AsyncAzureOpenAI client using API key authentication")
                aoai_client = AsyncAzureOpenAI(
                    api_key=connection.key,
                    azure_endpoint=connection.endpoint_url,
                    api_version=aoai_api_version,  # See "Data plane - inference" row in table https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
                )
            elif connection.authentication_type == AuthenticationType.ENTRA_ID:
                print("====> Creating AsyncAzureOpenAI client using Entra ID authentication")
                from azure.identity.aio import get_bearer_token_provider
                from azure.core.credentials_async import AsyncTokenCredential

                aoai_client = AsyncAzureOpenAI(
                    # See https://learn.microsoft.com/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider
                    azure_ad_token_provider=get_bearer_token_provider(
                        cast(AsyncTokenCredential, connection.token_credential),
                        "https://cognitiveservices.azure.com/.default",
                    ),
                    azure_endpoint=connection.endpoint_url,
                    api_version=aoai_api_version,  # See "Data plane - inference" row in table https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
                )
            else:
                raise ValueError(f"Authentication type {connection.authentication_type} not supported.")

            aoai_response = await aoai_client.chat.completions.create(
                model=model_deployment_name,
                messages=[
                    {
                        "role": "user",
                        "content": "How many feet are in a mile?",
                    },
                ],
            )
            print("\nChatCompletionsClient response:")
            pprint.pprint(aoai_response)
            contains = ["5280", "5,280"]
            assert any(item in aoai_response.choices[0].message.content for item in contains)
            await aoai_client.close()

        elif connection.connection_type == ConnectionType.AZURE_AI_SERVICES:

            from azure.ai.inference.aio import ChatCompletionsClient
            from azure.ai.inference.models import UserMessage

            if connection.authentication_type == AuthenticationType.API_KEY:
                print("====> Creating ChatCompletionsClient using API key authentication")
                from azure.core.credentials import AzureKeyCredential

                inference_client = ChatCompletionsClient(
                    endpoint=f"{connection.endpoint_url}/models", credential=AzureKeyCredential(connection.key or "")
                )
            elif connection.authentication_type == AuthenticationType.ENTRA_ID:
                from azure.core.credentials_async import AsyncTokenCredential

                print("====> Creating ChatCompletionsClient using Entra ID authentication")
                inference_client = ChatCompletionsClient(
                    endpoint=f"{connection.endpoint_url}/models",
                    credential=cast(AsyncTokenCredential, connection.token_credential),
                    credential_scopes=["https://cognitiveservices.azure.com/.default"],
                )
            else:
                raise ValueError(f"Authentication type {connection.authentication_type} not supported.")

            inference_response = await inference_client.complete(
                model=model_deployment_name, messages=[UserMessage(content="How many feet are in a mile?")]
            )
            print("\nChatCompletionsClient response:")
            pprint.pprint(inference_response)
            contains = ["5280", "5,280"]
            assert any(item in inference_response.choices[0].message.content for item in contains)
            await inference_client.close()
