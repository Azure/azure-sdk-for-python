# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import random
import re
import functools
from typing import Optional
from azure.ai.projects.models import (
    Connection,
    ConnectionType,
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
    AssetCredentialResponse,
)
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, is_live_and_not_recording


servicePreparer = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_projects_tests",
    azure_ai_projects_tests_project_endpoint="https://sanitized.services.ai.azure.com/api/projects/sanitized-project-name",
)


class TestBase(AzureRecordedTestCase):

    test_connections_params = {
        "connection_name": "connection1",
        "connection_type": ConnectionType.AZURE_OPEN_AI,
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

    test_inference_params = {
        "connection_name": "connection1",
        "model_deployment_name": "gpt-4o",
        "aoai_api_version": "2024-10-21",
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

    # Regular expression describing the pattern of an Application Insights connection string.
    REGEX_APPINSIGHTS_CONNECTION_STRING = re.compile(
        r"^InstrumentationKey=[0-9a-fA-F-]{36};IngestionEndpoint=https://.+.applicationinsights.azure.com/;LiveEndpoint=https://.+.monitor.azure.com/;ApplicationId=[0-9a-fA-F-]{36}$"
    )

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

        if include_credentials:
            if type(connection.credentials) == ApiKeyCredentials:
                assert connection.credentials.type == CredentialType.API_KEY
                assert connection.credentials.api_key is not None

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
    def validate_asset_credential(cls, asset_credential: AssetCredentialResponse):

        assert asset_credential.blob_reference is not None
        assert asset_credential.blob_reference.blob_uri
        assert asset_credential.blob_reference.storage_account_arm_id

        assert asset_credential.blob_reference.credential is not None
        assert (
            asset_credential.blob_reference.credential.type == "SAS"
        )  # Why is this not of type CredentialType.SAS as defined for Connections?
        assert asset_credential.blob_reference.credential.sas_uri
