# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import random
import re
import functools
import json
import os
import tempfile
from typing import Optional, Any, Dict, Final, IO, Union, overload, Literal, TextIO, BinaryIO
from azure.ai.projects.models import (
    Connection,
    ConnectionType,
    CustomCredential,
    CredentialType,
    ApiKeyCredentials,
    Deployment,
    DeploymentType,
    ModelDeployment,
    Index,
    IndexType,
    AzureAISearchIndex,
    DatasetVersion,
    DatasetType,
    DatasetCredential,
    ItemResource,
    ItemType,
    ResponsesMessageRole,
    ItemContentType,
)
from azure.ai.projects.models._models import AgentDetails, AgentVersionDetails
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from azure.ai.projects import AIProjectClient as AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient

# Store reference to built-in open before any mocking occurs
_BUILTIN_OPEN = open


# Load secrets from environment variables
servicePreparer = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_projects_tests",
    azure_ai_projects_tests_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
    azure_ai_projects_tests_agents_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
    azure_ai_projects_tests_tracing_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
    azure_ai_projects_tests_container_app_resource_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/00000/providers/Microsoft.App/containerApps/00000",
    azure_ai_projects_tests_container_ingress_subdomain_suffix="00000",
    azure_ai_projects_tests_bing_project_connection_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sanitized-resource-group/providers/Microsoft.CognitiveServices/accounts/sanitized-account/projects/sanitized-project/connections/sanitized-bing-connection",
    azure_ai_projects_tests_ai_search_project_connection_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sanitized-resource-group/providers/Microsoft.CognitiveServices/accounts/sanitized-account/projects/sanitized-project/connections/sanitized-ai-search-connection",
    azure_ai_projects_tests_ai_search_index_name="sanitized-index-name",
    azure_ai_projects_tests_mcp_project_connection_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sanitized-resource-group/providers/Microsoft.CognitiveServices/accounts/sanitized-account/projects/sanitized-project/connections/sanitized-mcp-connection",
    azure_ai_projects_tests_sharepoint_project_connection_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sanitized-resource-group/providers/Microsoft.CognitiveServices/accounts/sanitized-account/projects/sanitized-project/connections/sanitized-sharepoint-connection",
    azure_ai_projects_tests_ai_search_user_input="What is Azure AI Projects?",
    azure_ai_projects_tests_sharepoint_user_input="What is SharePoint?",
)

# Fine-tuning job type constants
SFT_JOB_TYPE: Final[str] = "sft"
DPO_JOB_TYPE: Final[str] = "dpo"
RFT_JOB_TYPE: Final[str] = "rft"

# Training type constants
STANDARD_TRAINING_TYPE: Final[str] = "Standard"
GLOBAL_STANDARD_TRAINING_TYPE: Final[str] = "GlobalStandard"
DEVELOPER_TIER_TRAINING_TYPE: Final[str] = "developerTier"


def patched_open_crlf_to_lf(*args, **kwargs):
    """
    Patched open function that converts CRLF to LF for text files.

    This function should be used with mock.patch("builtins.open", side_effect=TestBase.patched_open_crlf_to_lf)
    to ensure consistent line endings in test files during recording and playback.
    """
    # Extract file path - first positional arg or 'file' keyword arg
    if args:
        file_path = args[0]
    elif "file" in kwargs:
        file_path = kwargs["file"]
    else:
        # No file path provided, just pass through
        return _BUILTIN_OPEN(*args, **kwargs)

    # Extract mode - second positional arg or 'mode' keyword arg
    if len(args) > 1:
        mode = args[1]
    else:
        mode = kwargs.get("mode", "r")

    # Check if this is binary read mode for text-like files
    if "r" in mode and "b" in mode and file_path and isinstance(file_path, str):
        # Check file extension to determine if it's a text file
        text_extensions = {".txt", ".json", ".jsonl", ".csv", ".md", ".yaml", ".yml", ".xml"}
        ext = os.path.splitext(file_path)[1].lower()
        if ext in text_extensions:
            # Read the original file
            with _BUILTIN_OPEN(file_path, "rb") as f:
                content = f.read()

            # Convert CRLF to LF
            converted_content = content.replace(b"\r\n", b"\n")

            # Only create temp file if conversion was needed
            if converted_content != content:
                # Create a sub temp folder and save file with same filename
                temp_dir = tempfile.mkdtemp()
                original_filename = os.path.basename(file_path)
                temp_path = os.path.join(temp_dir, original_filename)

                # Write the converted content to the temp file
                with _BUILTIN_OPEN(temp_path, "wb") as temp_file:
                    temp_file.write(converted_content)

                # Replace file path with temp path
                if args:
                    # File path was passed as positional arg
                    return _BUILTIN_OPEN(temp_path, *args[1:], **kwargs)
                else:
                    # File path was passed as keyword arg
                    kwargs = kwargs.copy()
                    kwargs["file"] = temp_path
                    return _BUILTIN_OPEN(**kwargs)

    return _BUILTIN_OPEN(*args, **kwargs)


class TestBase(AzureRecordedTestCase):

    test_redteams_params = {
        # cSpell:disable-next-line
        "connection_name": "naposaniwestus3",
        "connection_type": ConnectionType.AZURE_OPEN_AI,
        "model_deployment_name": "gpt-4o-mini",
    }

    test_connections_params = {
        "connection_name": "custom_keys_connection",
        "connection_type": ConnectionType.CUSTOM,
    }

    test_deployments_params = {
        "model_publisher": "Cohere",
        "model_name": "gpt-4o",
        "model_deployment_name": "DeepSeek-V3",
    }

    test_agents_params = {
        "model_deployment_name": "gpt-4o",
        "agent_name": "agent-for-python-projects-sdk-testing",
    }

    test_agents_tools_params = {
        "image_generation_model_deployment_name": "gpt-image-1-mini",
    }

    test_inference_params = {
        "connection_name_api_key_auth": "connection1",
        "connection_name_entra_id_auth": "connection2",
        "model_deployment_name": "gpt-4o",
        "aoai_api_version": "2025-04-01-preview",
    }

    test_indexes_params = {
        "index_name": f"test-index-name",
        "index_version": "1",
        "ai_search_connection_name": "my-ai-search-connection",
        "ai_search_index_name": "my-ai-search-index",
    }

    test_datasets_params = {
        "dataset_name_1": f"test-dataset-name-{random.randint(0, 99999):05d}",
        "dataset_name_2": f"test-dataset-name-{random.randint(0, 99999):05d}",
        "dataset_name_3": f"test-dataset-name-{random.randint(0, 99999):05d}",
        "dataset_name_4": f"test-dataset-name-{random.randint(0, 99999):05d}",
        "dataset_version": 1,
        "connection_name": "balapvbyostoragecanary",
    }

    test_files_params = {
        "test_file_name": "test_file.jsonl",
        "file_purpose": "fine-tune",
    }

    test_finetuning_params = {
        "sft": {
            "openai": {
                "model_name": "gpt-4.1",
            },
            "oss": {"model_name": "Ministral-3B"},
            "training_file_name": "sft_training_set.jsonl",
            "validation_file_name": "sft_validation_set.jsonl",
        },
        "dpo": {
            "openai": {"model_name": "gpt-4o-mini"},
            "training_file_name": "dpo_training_set.jsonl",
            "validation_file_name": "dpo_validation_set.jsonl",
        },
        "rft": {
            "openai": {"model_name": "o4-mini"},
            "training_file_name": "rft_training_set.jsonl",
            "validation_file_name": "rft_validation_set.jsonl",
        },
        "n_epochs": 1,
        "batch_size": 1,
        "learning_rate_multiplier": 1.0,
    }

    # Regular expression describing the pattern of an Application Insights connection string.
    REGEX_APPINSIGHTS_CONNECTION_STRING = re.compile(
        r"^InstrumentationKey=[0-9a-fA-F-]{36};IngestionEndpoint=https://.+.applicationinsights.azure.com/;LiveEndpoint=https://.+.monitor.azure.com/;ApplicationId=[0-9a-fA-F-]{36}$"
    )

    @overload
    def open_with_lf(
        self,
        file: Union[str, bytes, os.PathLike, int],
        mode: Literal["r", "w", "a", "x", "r+", "w+", "a+", "x+"] = "r",
        buffering: int = -1,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
        closefd: bool = True,
        opener: Optional[Any] = None,
    ) -> TextIO: ...

    @overload
    def open_with_lf(
        self,
        file: Union[str, bytes, os.PathLike, int],
        mode: Literal["rb", "wb", "ab", "xb", "r+b", "w+b", "a+b", "x+b"],
        buffering: int = -1,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
        closefd: bool = True,
        opener: Optional[Any] = None,
    ) -> BinaryIO: ...

    @overload
    def open_with_lf(
        self,
        file: Union[str, bytes, os.PathLike, int],
        mode: str,
        buffering: int = -1,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
        closefd: bool = True,
        opener: Optional[Any] = None,
    ) -> IO[Any]: ...

    def open_with_lf(
        self,
        file: Union[str, bytes, os.PathLike, int],
        mode: str = "r",
        buffering: int = -1,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
        closefd: bool = True,
        opener: Optional[Any] = None,
    ) -> IO[Any]:
        """
        Open function that converts CRLF to LF for text files.

        This function has the same signature as built-in open and converts line endings
        to ensure consistent behavior during test recording and playback.
        """
        return patched_open_crlf_to_lf(file, mode, buffering, encoding, errors, newline, closefd, opener)

    # helper function: create projects client using environment variables
    def create_client(self, *, operation_group: Optional[str] = None, **kwargs) -> AIProjectClient:
        # fetch environment variables
        project_endpoint_env_variable = (
            f"azure_ai_projects_tests_{operation_group}_project_endpoint"
            if operation_group
            else "azure_ai_projects_tests_project_endpoint"
        )
        endpoint = kwargs.pop(project_endpoint_env_variable)
        credential = self.get_credential(AIProjectClient, is_async=False)

        # create and return client
        client = AIProjectClient(
            endpoint=endpoint,
            credential=credential,
        )

        return client

    # helper function: create async projects client using environment variables
    def create_async_client(self, *, operation_group: Optional[str] = None, **kwargs) -> AsyncAIProjectClient:
        # fetch environment variables
        project_endpoint_env_variable = (
            f"azure_ai_projects_tests_{operation_group}_project_endpoint"
            if operation_group
            else "azure_ai_projects_tests_project_endpoint"
        )
        endpoint = kwargs.pop(project_endpoint_env_variable)
        credential = self.get_credential(AsyncAIProjectClient, is_async=True)

        # create and return async client
        client = AsyncAIProjectClient(
            endpoint=endpoint,
            credential=credential,
        )

        return client

    @staticmethod
    def assert_equal_or_not_none(actual, expected=None):
        assert actual is not None
        if expected is not None:
            assert actual == expected

    # Checks that a given dictionary has at least one non-empty (non-whitespace) string key-value pair.
    @classmethod
    def is_valid_dict(cls, d: dict[str, str]) -> bool:
        return bool(d) and all(
            isinstance(k, str) and isinstance(v, str) and k.strip() and v.strip() for k, v in d.items()
        )

    @classmethod
    def validate_connection(
        cls,
        connection: Connection,
        include_credentials: bool,
        *,
        expected_connection_type: Optional[ConnectionType] = None,
        expected_connection_name: Optional[str] = None,
        expected_authentication_type: Optional[CredentialType] = None,
        expected_is_default: Optional[bool] = None,
    ):
        assert connection.id is not None

        TestBase.assert_equal_or_not_none(connection.name, expected_connection_name)
        TestBase.assert_equal_or_not_none(connection.type, expected_connection_type)
        TestBase.assert_equal_or_not_none(connection.credentials.type, expected_authentication_type)

        if expected_is_default is not None:
            assert connection.is_default == expected_is_default

        if isinstance(connection.credentials, ApiKeyCredentials):
            assert connection.credentials.type == CredentialType.API_KEY
            if include_credentials:
                assert connection.credentials.api_key is not None
        elif isinstance(connection.credentials, CustomCredential):
            assert connection.credentials.type == CredentialType.CUSTOM
            if include_credentials:
                assert TestBase.is_valid_dict(connection.credentials.credential_keys)

    @classmethod
    def validate_red_team_response(
        cls, response, expected_attack_strategies: int = -1, expected_risk_categories: int = -1
    ):
        """Assert basic red team scan response properties."""
        assert response is not None
        assert hasattr(response, "name")
        assert hasattr(response, "display_name")
        assert hasattr(response, "status")
        assert hasattr(response, "attack_strategies")
        assert hasattr(response, "risk_categories")
        assert hasattr(response, "target")
        assert hasattr(response, "properties")

        # Validate attack strategies and risk categories
        if expected_attack_strategies != -1:
            assert len(response.attack_strategies) == expected_attack_strategies
        if expected_risk_categories != -1:
            assert len(response.risk_categories) == expected_risk_categories
        assert response.status is not None
        cls._assert_azure_ml_properties(response)

    @classmethod
    def _assert_azure_ml_properties(cls, response):
        """Assert Azure ML specific properties are present and valid."""
        properties = response.properties
        assert properties is not None, "Red team scan properties should not be None"

        required_properties = [
            "runType",
            "redteaming",
            "_azureml.evaluation_run",
            "_azureml.evaluate_artifacts",
            "AiStudioEvaluationUri",
        ]

        for prop in required_properties:
            assert prop in properties, f"Missing required property: {prop}"

        # Validate specific property values
        assert properties["runType"] == "eval_run"
        assert properties["_azureml.evaluation_run"] == "evaluation.service"
        assert "instance_results.json" in properties["_azureml.evaluate_artifacts"]
        assert properties["redteaming"] == "asr"

        # Validate AI Studio URI format
        ai_studio_uri = properties["AiStudioEvaluationUri"]
        assert ai_studio_uri.startswith("https://ai.azure.com/resource/build/redteaming/")
        assert "wsid=" in ai_studio_uri
        assert "tid=" in ai_studio_uri

    @classmethod
    def validate_deployment(
        cls,
        deployment: Deployment,
        *,
        expected_model_name: Optional[str] = None,
        expected_model_deployment_name: Optional[str] = None,
        expected_model_publisher: Optional[str] = None,
    ):
        assert type(deployment) == ModelDeployment
        assert deployment.type == DeploymentType.MODEL_DEPLOYMENT
        assert deployment.model_version is not None
        # Comment out the below, since I see that `Cohere-embed-v3-english` has an empty capabilities dict.
        # assert TestBase.is_valid_dict(deployment.capabilities)
        assert bool(deployment.sku)  # Check none-empty

        TestBase.assert_equal_or_not_none(deployment.model_name, expected_model_name)
        TestBase.assert_equal_or_not_none(deployment.name, expected_model_deployment_name)
        TestBase.assert_equal_or_not_none(deployment.model_publisher, expected_model_publisher)

    @classmethod
    def validate_index(
        cls,
        index: Index,
        *,
        expected_index_type: Optional[IndexType] = None,
        expected_index_name: Optional[str] = None,
        expected_index_version: Optional[str] = None,
        expected_ai_search_connection_name: Optional[str] = None,
        expected_ai_search_index_name: Optional[str] = None,
    ):

        TestBase.assert_equal_or_not_none(index.name, expected_index_name)
        TestBase.assert_equal_or_not_none(index.version, expected_index_version)

        if expected_index_type == IndexType.AZURE_SEARCH:
            assert type(index) == AzureAISearchIndex
            assert index.type == IndexType.AZURE_SEARCH
            TestBase.assert_equal_or_not_none(index.connection_name, expected_ai_search_connection_name)
            TestBase.assert_equal_or_not_none(index.index_name, expected_ai_search_index_name)

    @classmethod
    def validate_dataset(
        cls,
        dataset: DatasetVersion,
        *,
        expected_dataset_type: Optional[DatasetType] = None,
        expected_dataset_name: Optional[str] = None,
        expected_dataset_version: Optional[str] = None,
        expected_connection_name: Optional[str] = None,
    ):
        assert dataset.data_uri is not None

        if expected_dataset_type:
            assert dataset.type == expected_dataset_type
        else:
            assert dataset.type == DatasetType.URI_FILE or dataset.type == DatasetType.URI_FOLDER

        TestBase.assert_equal_or_not_none(dataset.name, expected_dataset_name)
        TestBase.assert_equal_or_not_none(dataset.version, expected_dataset_version)
        if expected_connection_name:
            assert dataset.connection_name == expected_connection_name

    @classmethod
    def validate_dataset_credential(cls, dataset_credential: DatasetCredential):

        assert dataset_credential.blob_reference is not None
        assert dataset_credential.blob_reference.blob_uri
        assert dataset_credential.blob_reference.storage_account_arm_id

        assert dataset_credential.blob_reference.credential is not None
        assert (
            dataset_credential.blob_reference.credential.type == "SAS"
        )  # Why is this not of type CredentialType.SAS as defined for Connections?
        assert dataset_credential.blob_reference.credential.sas_uri

    @staticmethod
    def _validate_conversation(
        conversation: Any, *, expected_id: Optional[str] = None, expected_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        assert conversation.id
        assert conversation.created_at
        if expected_id is not None:
            assert conversation.id == expected_id
        if expected_metadata is not None:
            assert conversation.metadata == expected_metadata
        print(f"Conversation validated (id: {conversation.id})")

    def _validate_agent_version(
        self, agent: AgentVersionDetails, expected_name: Optional[str] = None, expected_version: Optional[str] = None
    ) -> None:
        assert agent is not None
        assert isinstance(agent, AgentVersionDetails)
        assert agent.id
        if expected_name:
            assert agent.name == expected_name
        else:
            assert agent.name
        if expected_version:
            assert agent.version == expected_version
        else:
            assert agent.version
        print(f"Agent version validated (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    def _validate_agent(
        self, agent: AgentDetails, expected_name: Optional[str] = None, expected_latest_version: Optional[str] = None
    ) -> None:
        assert agent is not None
        assert isinstance(agent, AgentDetails)
        assert agent.id
        if expected_name:
            assert agent.name == expected_name
        else:
            assert agent.name
        if expected_latest_version:
            assert agent.versions.latest.version == expected_latest_version
        else:
            assert agent.versions.latest.version
        print(f"Agent validated (id: {agent.id}, name: {agent.name}, latest version: {agent.versions.latest.version})")

    def _validate_conversation_item(
        self,
        item: ItemResource,
        *,
        expected_type: Optional[ItemType] = None,
        expected_id: Optional[str] = None,
        expected_role: Optional[ResponsesMessageRole] = None,
        expected_content_type: Optional[ItemContentType] = None,
        expected_content_text: Optional[str] = None,
    ) -> None:
        assert item

        # From ItemResource:
        if expected_type:
            assert item.type == expected_type
        else:
            assert item.type
        if expected_id:
            assert item.id == expected_id
        else:
            assert item.id

        # From ResponsesMessageItemResource:
        if expected_type == ItemType.MESSAGE:
            assert item.status == "completed"
            if expected_role:
                assert item.role == expected_role
            else:
                assert item.role

            # From ResponsesAssistantMessageItemResource, ResponsesDeveloperMessageItemResource, ResponsesSystemMessageItemResource, ResponsesUserMessageItemResource:
            assert len(item.content) == 1

            # From ItemContent:
            if expected_content_type:
                assert item.content[0].type == expected_content_type
            if expected_content_text:
                assert item.content[0].text == expected_content_text
        print(
            f"Conversation item validated (id: {item.id}, type: {item.type}, role: {item.role if item.type == ItemType.MESSAGE else 'N/A'})"
        )

    @classmethod
    def validate_file(
        cls,
        file_obj,
        *,
        expected_file_id: Optional[str] = None,
        expected_filename: Optional[str] = None,
        expected_purpose: Optional[str] = None,
    ):
        assert file_obj is not None
        assert file_obj.id is not None
        assert file_obj.bytes is not None
        assert file_obj.created_at is not None
        assert file_obj.filename is not None
        assert file_obj.purpose is not None

        TestBase.assert_equal_or_not_none(file_obj.id, expected_file_id)
        TestBase.assert_equal_or_not_none(file_obj.filename, expected_filename)
        TestBase.assert_equal_or_not_none(file_obj.purpose, expected_purpose)

    @classmethod
    def validate_fine_tuning_job(
        cls,
        job_obj,
        *,
        expected_job_id: Optional[str] = None,
        expected_model: Optional[str] = None,
        expected_status: Optional[str] = None,
    ):
        assert job_obj is not None
        assert job_obj.id is not None
        assert job_obj.model is not None
        assert job_obj.created_at is not None
        assert job_obj.status is not None
        assert job_obj.training_file is not None

        TestBase.assert_equal_or_not_none(job_obj.id, expected_job_id)
        TestBase.assert_equal_or_not_none(job_obj.model, expected_model)
        TestBase.assert_equal_or_not_none(job_obj.status, expected_status)

    def _request_callback(self, pipeline_request) -> None:
        self.pipeline_request = pipeline_request

    @staticmethod
    def _are_json_equal(json_str1: str, json_str2: str) -> bool:
        try:
            obj1 = json.loads(json_str1)
            obj2 = json.loads(json_str2)
            return obj1 == obj2
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            return False
