# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from typing import Optional
from azure.ai.projects.models import Connection, ConnectionType, CredentialType, ApiKeyCredentials
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader

servicePreparerConnectionsTests = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_projects_connections_tests",
    azure_ai_projects_connections_tests_project_endpoint="https://sanitized.services.ai.azure.com/api/projects/sanitized-project-name",
    azure_ai_projects_connections_tests_connection_name="connection-name",
)


class TestBase(AzureRecordedTestCase):

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
