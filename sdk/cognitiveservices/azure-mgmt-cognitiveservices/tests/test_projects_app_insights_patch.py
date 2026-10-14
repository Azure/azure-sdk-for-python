# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Unit tests for the temporary Foundry project Application Insights preview."""

import time
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices._app_insights_provisioning import (
    FoundryAppInsightsProvisioner,
    FoundryAppInsightsProvisioningError,
)
from azure.mgmt.cognitiveservices.operations._operations import ProjectsOperations as GeneratedProjectsOperations
from azure.mgmt.cognitiveservices.operations._patch import ProjectsOperations

_SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
_PROJECT_ID = (
    f"/subscriptions/{_SUBSCRIPTION_ID}/resourceGroups/rg/providers/"
    "Microsoft.CognitiveServices/accounts/account/projects/project"
)
_WORKSPACE_ID = (
    f"/subscriptions/{_SUBSCRIPTION_ID}/resourceGroups/rg/providers/"
    "Microsoft.OperationalInsights/workspaces/account-apikey-law"
)
_APP_INSIGHTS_ID = (
    f"/subscriptions/{_SUBSCRIPTION_ID}/resourceGroups/rg/providers/"
    "Microsoft.Insights/components/account-apikey-ai"
)
_CONNECTION_STRING = (
    "InstrumentationKey=not-a-real-secret;"
    "IngestionEndpoint=https://eastus2-1.in.applicationinsights.azure.com/"
)


class _FakeCredential:
    def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        return AccessToken("fake-token", int(time.time()) + 3600)


@pytest.fixture
def auxiliary_clients():
    log_analytics_client = MagicMock()
    app_insights_client = MagicMock()
    authorization_client = MagicMock()
    project_connections = MagicMock()

    workspace = SimpleNamespace(id=_WORKSPACE_ID)
    log_analytics_client.workspaces.begin_create_or_update.return_value.result.return_value = workspace
    app_insights_client.components.create_or_update.return_value = SimpleNamespace(
        id=_APP_INSIGHTS_ID,
        connection_string=_CONNECTION_STRING,
    )

    with (
        patch(
            "azure.mgmt.cognitiveservices._app_insights_provisioning.LogAnalyticsManagementClient",
            return_value=log_analytics_client,
        ),
        patch(
            "azure.mgmt.cognitiveservices._app_insights_provisioning.ApplicationInsightsManagementClient",
            return_value=app_insights_client,
        ),
        patch(
            "azure.mgmt.cognitiveservices._app_insights_provisioning.AuthorizationManagementClient",
            return_value=authorization_client,
        ),
    ):
        provisioner = FoundryAppInsightsProvisioner(
            credential=_FakeCredential(),
            subscription_id=_SUBSCRIPTION_ID,
            project_connections=project_connections,
            polling_interval=0,
        )
        yield provisioner, log_analytics_client, app_insights_client, authorization_client, project_connections


def _project(*, principal_id="11111111-1111-1111-1111-111111111111"):
    identity = SimpleNamespace(principal_id=principal_id) if principal_id else None
    return SimpleNamespace(
        id=_PROJECT_ID,
        location="eastus2",
        identity=identity,
        properties=SimpleNamespace(provisioning_state="Succeeded"),
    )


def test_public_client_uses_patched_projects_operations():
    client = CognitiveServicesManagementClient(_FakeCredential(), _SUBSCRIPTION_ID)

    assert isinstance(client.projects, ProjectsOperations)
    assert hasattr(client.projects, "create_with_default_app_insights")


def test_preview_method_defaults_to_api_key_and_returns_project():
    client = CognitiveServicesManagementClient(_FakeCredential(), _SUBSCRIPTION_ID)
    created_project = _project()
    poller = MagicMock()
    poller.result.return_value = created_project

    with (
        patch.object(GeneratedProjectsOperations, "begin_create", return_value=poller) as begin_create,
        patch(
            "azure.mgmt.cognitiveservices.operations._patch.FoundryAppInsightsProvisioner"
        ) as provisioner_type,
    ):
        result = client.projects.create_with_default_app_insights(
            "rg",
            "account",
            "project",
            {"location": "eastus2", "identity": {"type": "SystemAssigned"}},
            polling_interval=0,
        )

    assert result is created_project
    begin_create.assert_called_once()
    provisioner_type.return_value.provision.assert_called_once()
    assert provisioner_type.return_value.provision.call_args.kwargs["auth_mode"] == "api_key"
    provisioner_type.return_value.close.assert_called_once()


def test_invalid_auth_mode_does_not_create_project():
    client = CognitiveServicesManagementClient(_FakeCredential(), _SUBSCRIPTION_ID)

    with patch.object(GeneratedProjectsOperations, "begin_create") as begin_create:
        with pytest.raises(ValueError, match="api_key"):
            client.projects.create_with_default_app_insights(
                "rg",
                "account",
                "project",
                {"location": "eastus2"},
                app_insights_auth="password",
            )

    begin_create.assert_not_called()


def test_preview_waits_for_backend_project_readiness():
    client = CognitiveServicesManagementClient(_FakeCredential(), _SUBSCRIPTION_ID)
    creating_project = _project()
    creating_project.properties.provisioning_state = "Creating"
    succeeded_project = _project()
    poller = MagicMock()
    poller.result.return_value = creating_project

    with (
        patch.object(GeneratedProjectsOperations, "begin_create", return_value=poller),
        patch.object(ProjectsOperations, "get", return_value=succeeded_project) as get_project,
        patch("azure.mgmt.cognitiveservices.operations._patch.time.sleep") as sleep,
        patch(
            "azure.mgmt.cognitiveservices.operations._patch.FoundryAppInsightsProvisioner"
        ),
    ):
        result = client.projects.create_with_default_app_insights(
            "rg",
            "account",
            "project",
            {"location": "eastus2", "identity": {"type": "SystemAssigned"}},
            polling_interval=2,
        )

    assert result is succeeded_project
    sleep.assert_called_once_with(2)
    get_project.assert_called_once_with("rg", "account", "project")


def test_preview_stops_when_backend_project_fails():
    client = CognitiveServicesManagementClient(_FakeCredential(), _SUBSCRIPTION_ID)
    failed_project = _project()
    failed_project.properties.provisioning_state = "Failed"
    poller = MagicMock()
    poller.result.return_value = failed_project

    with (
        patch.object(GeneratedProjectsOperations, "begin_create", return_value=poller),
        patch(
            "azure.mgmt.cognitiveservices.operations._patch.FoundryAppInsightsProvisioner"
        ) as provisioner_type,
    ):
        with pytest.raises(HttpResponseError, match="terminal state 'failed'"):
            client.projects.create_with_default_app_insights(
                "rg",
                "account",
                "project",
                {"location": "eastus2", "identity": {"type": "SystemAssigned"}},
                polling_interval=0,
            )

    provisioner_type.assert_not_called()


def test_api_key_mode_matches_create_project_ui_shape(auxiliary_clients):
    provisioner, log_client, app_client, authorization_client, project_connections = auxiliary_clients

    provisioner.provision(
        project=_project(),
        resource_group_name="rg",
        account_name="account",
        project_name="project",
        auth_mode="api_key",
        location="eastus2",
    )

    workspace_call = log_client.workspaces.begin_create_or_update.call_args.kwargs
    assert workspace_call["workspace_name"] == "account-apikey-law"
    assert workspace_call["parameters"]["properties"]["sku"]["name"] == "PerGB2018"
    component_call = app_client.components.create_or_update.call_args.kwargs
    assert component_call["resource_name"] == "account-apikey-ai"
    assert component_call["insight_properties"]["properties"]["WorkspaceResourceId"] == _WORKSPACE_ID
    assert component_call["insight_properties"]["properties"]["DisableLocalAuth"] is False
    authorization_client.role_assignments.create.assert_not_called()

    connection = project_connections.create.call_args.kwargs["connection"]["properties"]
    assert connection["authType"] == "ApiKey"
    assert connection["category"] == "AppInsights"
    assert connection["target"] == "https://eastus2-1.in.applicationinsights.azure.com/"
    assert connection["credentials"]["key"] == _CONNECTION_STRING
    assert connection["metadata"] == {"ResourceId": _APP_INSIGHTS_ID}


def test_project_managed_identity_mode_assigns_role_and_creates_connection(auxiliary_clients):
    provisioner, _, app_client, authorization_client, project_connections = auxiliary_clients

    provisioner.provision(
        project=_project(),
        resource_group_name="rg",
        account_name="account",
        project_name="project",
        auth_mode="project_managed_identity",
        location="eastus2",
    )

    component_call = app_client.components.create_or_update.call_args.kwargs
    assert component_call["resource_name"] == "account-pmi-ai"
    assert component_call["insight_properties"]["properties"]["DisableLocalAuth"] is True

    role_call = authorization_client.role_assignments.create.call_args.kwargs
    assert role_call["scope"] == _APP_INSIGHTS_ID
    assert role_call["parameters"]["properties"]["principalId"] == "11111111-1111-1111-1111-111111111111"
    assert role_call["parameters"]["properties"]["principalType"] == "ServicePrincipal"
    assert role_call["parameters"]["properties"]["roleDefinitionId"].endswith(
        "/roleDefinitions/3913510d-42f4-4e42-8a64-420c390055eb"
    )

    connection = project_connections.create.call_args.kwargs["connection"]["properties"]
    assert connection["authType"] == "ProjectManagedIdentity"
    assert connection["audience"] == "https://monitor.azure.com/.default"
    assert connection["metadata"] == {
        "ApplicationInsightsConnectionString": _CONNECTION_STRING,
        "ResourceId": _APP_INSIGHTS_ID,
    }


def test_role_assignment_name_is_deterministic(auxiliary_clients):
    provisioner, _, _, authorization_client, _ = auxiliary_clients

    provisioner.provision(
        project=_project(),
        resource_group_name="rg",
        account_name="account",
        project_name="project",
        auth_mode="project_managed_identity",
        location="eastus2",
    )
    first_assignment_name = authorization_client.role_assignments.create.call_args.kwargs["role_assignment_name"]
    provisioner.provision(
        project=_project(),
        resource_group_name="rg",
        account_name="account",
        project_name="project",
        auth_mode="project_managed_identity",
        location="eastus2",
    )
    second_assignment_name = authorization_client.role_assignments.create.call_args.kwargs["role_assignment_name"]

    assert first_assignment_name == second_assignment_name


def test_pmi_missing_identity_fails_before_creating_observability_resources(auxiliary_clients):
    provisioner, log_client, app_client, _, _ = auxiliary_clients

    with pytest.raises(FoundryAppInsightsProvisioningError) as exc_info:
        provisioner.provision(
            project=_project(principal_id=None),
            resource_group_name="rg",
            account_name="account",
            project_name="project",
            auth_mode="project_managed_identity",
            location="eastus2",
        )

    assert exc_info.value.stage == "project_identity"
    log_client.workspaces.begin_create_or_update.assert_not_called()
    app_client.components.create_or_update.assert_not_called()


def test_role_assignment_retries_principal_propagation(auxiliary_clients):
    provisioner, _, _, authorization_client, project_connections = auxiliary_clients
    principal_not_found = HttpResponseError(
        message="PrincipalNotFound",
        model=SimpleNamespace(code="PrincipalNotFound"),
    )
    authorization_client.role_assignments.create.side_effect = [principal_not_found, None]

    with patch("azure.mgmt.cognitiveservices._app_insights_provisioning.time.sleep") as sleep:
        provisioner.provision(
            project=_project(),
            resource_group_name="rg",
            account_name="account",
            project_name="project",
            auth_mode="project_managed_identity",
            location="eastus2",
        )

    assert authorization_client.role_assignments.create.call_count == 2
    sleep.assert_called_once_with(2)
    project_connections.create.assert_called_once()


def test_connection_failure_does_not_expose_connection_string(auxiliary_clients):
    provisioner, _, _, _, project_connections = auxiliary_clients
    project_connections.create.side_effect = ValueError(f"request body included {_CONNECTION_STRING}")

    with pytest.raises(FoundryAppInsightsProvisioningError) as exc_info:
        provisioner.provision(
            project=_project(),
            resource_group_name="rg",
            account_name="account",
            project_name="project",
            auth_mode="api_key",
            location="eastus2",
        )

    assert exc_info.value.stage == "project_connection"
    assert exc_info.value.error_type == "ValueError"
    assert _CONNECTION_STRING not in str(exc_info.value)
    assert exc_info.value.__cause__ is None
