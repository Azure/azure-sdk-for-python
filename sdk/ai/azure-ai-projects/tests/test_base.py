# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
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
)
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader

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

    # Regular expression describing the pattern of an Application Insights connection string.
    REGEX_APPINSIGHTS_CONNECTION_STRING = re.compile(
        r"^InstrumentationKey=[0-9a-fA-F-]{36};IngestionEndpoint=https://.+.applicationinsights.azure.com/;LiveEndpoint=https://.+.monitor.azure.com/;ApplicationId=[0-9a-fA-F-]{36}$"
    )

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

        if expected_connection_name:
            assert connection.name == expected_connection_name
        else:
            assert connection.name is not None

        if expected_connection_type:
            assert connection.type == expected_connection_type
        else:
            assert connection.type is not None

        if expected_authentication_type:
            assert connection.credentials.type == expected_authentication_type
        else:
            assert connection.credentials.type is not None

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

        if expected_model_name:
            assert deployment.model_name == expected_model_name
        else:
            assert deployment.model_name is not None

        if expected_model_deployment_name:
            assert deployment.name == expected_model_deployment_name
        else:
            assert deployment.name is not None

        if expected_model_publisher:
            assert deployment.model_publisher == expected_model_publisher
        else:
            assert deployment.model_publisher is not None
