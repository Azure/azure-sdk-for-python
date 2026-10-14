# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Temporary Foundry project Application Insights provisioning helpers."""

import hashlib
import re
import time
import uuid
from typing import Any, Mapping, Optional

from azure.core.exceptions import AzureError, HttpResponseError
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.loganalytics import LogAnalyticsManagementClient

_API_KEY_AUTH = "api_key"
_PROJECT_MANAGED_IDENTITY_AUTH = "project_managed_identity"
_MONITORING_METRICS_PUBLISHER_ROLE_ID = "3913510d-42f4-4e42-8a64-420c390055eb"
_PUBLIC_MONITOR_AUDIENCE = "https://monitor.azure.com/.default"


class FoundryAppInsightsProvisioningError(RuntimeError):
    """Reports a failed stage without exposing the Application Insights credential."""

    def __init__(self, stage: str, resource_ids: Mapping[str, str], error: Exception) -> None:
        resource_summary = ", ".join(f"{name}={value}" for name, value in resource_ids.items() if value)
        suffix = f" Created resources: {resource_summary}." if resource_summary else ""
        status_code = getattr(getattr(error, "response", None), "status_code", None)
        error_code = _error_code(error) if isinstance(error, HttpResponseError) else ""
        error_details = [type(error).__name__]
        if status_code is not None:
            error_details.append(f"HTTP {status_code}")
        if error_code:
            error_details.append(f"code {error_code}")
        super().__init__(
            f"Default Application Insights provisioning failed during '{stage}'."
            f" Underlying error: {', '.join(error_details)}."
            f"{suffix} Retry the same create_with_default_app_insights call to reconcile the setup."
        )
        self.stage = stage
        self.resource_ids = dict(resource_ids)
        self.error_type = type(error).__name__
        self.status_code = status_code
        self.error_code = error_code


class FoundryAppInsightsProvisioner:
    """Composes ARM management clients for the temporary Python SDK preview."""

    def __init__(
        self,
        *,
        credential: Any,
        subscription_id: str,
        project_connections: Any,
        base_url: Optional[str] = None,
        cloud_setting: Any = None,
        credential_scopes: Optional[list[str]] = None,
        polling_interval: int = 30,
    ) -> None:
        client_options: dict[str, Any] = {
            "cloud_setting": cloud_setting,
            "polling_interval": polling_interval,
        }
        if base_url:
            client_options["base_url"] = base_url
        if credential_scopes:
            client_options["credential_scopes"] = credential_scopes

        self._subscription_id = subscription_id
        self._project_connections = project_connections
        self._log_analytics_client = LogAnalyticsManagementClient(
            credential=credential,
            subscription_id=subscription_id,
            **client_options,
        )
        self._app_insights_client = ApplicationInsightsManagementClient(
            credential=credential,
            subscription_id=subscription_id,
            **client_options,
        )
        self._authorization_client = AuthorizationManagementClient(
            credential=credential,
            subscription_id=subscription_id,
            **client_options,
        )

    def close(self) -> None:
        """Close auxiliary management clients."""
        self._log_analytics_client.close()
        self._app_insights_client.close()
        self._authorization_client.close()

    def provision(
        self,
        *,
        project: Any,
        resource_group_name: str,
        account_name: str,
        project_name: str,
        auth_mode: str,
        location: str,
        app_insights_resource_group_name: Optional[str] = None,
        log_analytics_workspace_name: Optional[str] = None,
        app_insights_name: Optional[str] = None,
        connection_name: str = "appinsights",
        monitor_audience: str = _PUBLIC_MONITOR_AUDIENCE,
    ) -> None:
        """Create or reconcile the account-scoped observability resources and project connection."""
        normalized_auth_mode = validate_app_insights_auth(auth_mode)
        resource_group = app_insights_resource_group_name or resource_group_name
        mode_suffix = "apikey" if normalized_auth_mode == _API_KEY_AUTH else "pmi"
        workspace_name = log_analytics_workspace_name or _resource_name(account_name, mode_suffix, "law")
        component_name = app_insights_name or _resource_name(account_name, mode_suffix, "ai")
        resource_ids: dict[str, str] = {
            "project": _resource_id(project),
        }
        principal_id = None
        if normalized_auth_mode == _PROJECT_MANAGED_IDENTITY_AUTH:
            try:
                principal_id = _project_principal_id(project)
            except ValueError as error:
                raise FoundryAppInsightsProvisioningError("project_identity", resource_ids, error) from None

        try:
            workspace = self._log_analytics_client.workspaces.begin_create_or_update(
                resource_group_name=resource_group,
                workspace_name=workspace_name,
                parameters={
                    "location": location,
                    "properties": {
                        "retentionInDays": 30,
                        "sku": {"name": "PerGB2018"},
                    },
                },
            ).result()
            resource_ids["log_analytics"] = _required_resource_id(workspace, "Log Analytics workspace")
        except (AzureError, ValueError, TypeError) as error:
            raise FoundryAppInsightsProvisioningError("log_analytics_workspace", resource_ids, error) from None

        try:
            component = self._app_insights_client.components.create_or_update(
                resource_group_name=resource_group,
                resource_name=component_name,
                insight_properties={
                    "kind": "web",
                    "location": location,
                    "properties": {
                        "Application_Type": "web",
                        "Flow_Type": "Bluefield",
                        "Request_Source": "rest",
                        "WorkspaceResourceId": resource_ids["log_analytics"],
                        "DisableLocalAuth": normalized_auth_mode == _PROJECT_MANAGED_IDENTITY_AUTH,
                    },
                },
            )
            resource_ids["app_insights"] = _required_resource_id(component, "Application Insights component")
            connection_string = _connection_string(component)
            ingestion_endpoint = _connection_string_value(connection_string, "IngestionEndpoint")
        except (AzureError, ValueError, TypeError) as error:
            raise FoundryAppInsightsProvisioningError("application_insights", resource_ids, error) from None

        if normalized_auth_mode == _PROJECT_MANAGED_IDENTITY_AUTH:
            try:
                self._assign_monitoring_metrics_publisher(
                    principal_id=principal_id or "",
                    app_insights_resource_id=resource_ids["app_insights"],
                )
            except (AzureError, ValueError, TypeError) as error:
                raise FoundryAppInsightsProvisioningError(
                    "monitoring_metrics_publisher_role", resource_ids, error
                ) from None
            connection_properties = {
                "authType": "ProjectManagedIdentity",
                "category": "AppInsights",
                "target": ingestion_endpoint,
                "audience": monitor_audience,
                "metadata": {
                    "ApplicationInsightsConnectionString": connection_string,
                    "ResourceId": resource_ids["app_insights"],
                },
            }
        else:
            connection_properties = {
                "authType": "ApiKey",
                "category": "AppInsights",
                "target": ingestion_endpoint,
                "credentials": {"key": connection_string},
                "metadata": {
                    "ResourceId": resource_ids["app_insights"],
                },
            }

        try:
            self._project_connections.create(
                resource_group_name=resource_group_name,
                account_name=account_name,
                project_name=project_name,
                connection_name=connection_name,
                connection={"properties": connection_properties},
            )
        except (AzureError, ValueError, TypeError) as error:
            raise FoundryAppInsightsProvisioningError("project_connection", resource_ids, error) from None

    def _assign_monitoring_metrics_publisher(
        self,
        *,
        principal_id: str,
        app_insights_resource_id: str,
    ) -> None:
        role_definition_id = (
            f"/subscriptions/{self._subscription_id}/providers/Microsoft.Authorization/"
            f"roleDefinitions/{_MONITORING_METRICS_PUBLISHER_ROLE_ID}"
        )
        assignment_name = str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"{app_insights_resource_id.lower()}:{principal_id.lower()}:{role_definition_id.lower()}",
            )
        )
        delays = (0, 2, 5, 10, 20)
        for attempt, delay in enumerate(delays):
            if delay:
                time.sleep(delay)
            try:
                self._authorization_client.role_assignments.create(
                    scope=app_insights_resource_id,
                    role_assignment_name=assignment_name,
                    parameters={
                        "properties": {
                            "principalId": principal_id,
                            "principalType": "ServicePrincipal",
                            "roleDefinitionId": role_definition_id,
                        }
                    },
                )
                return
            except HttpResponseError as error:
                if _is_role_assignment_present(error):
                    return
                if not _is_principal_not_found(error) or attempt == len(delays) - 1:
                    raise


def validate_app_insights_auth(auth_mode: str) -> str:
    """Validate and normalize the preview authentication mode."""
    normalized = auth_mode.strip().lower()
    if normalized not in {_API_KEY_AUTH, _PROJECT_MANAGED_IDENTITY_AUTH}:
        raise ValueError(
            "app_insights_auth must be 'api_key' or 'project_managed_identity'."
        )
    return normalized


def _resource_name(account_name: str, mode_suffix: str, resource_suffix: str) -> str:
    normalized = re.sub(r"[^a-z0-9-]", "-", account_name.lower()).strip("-")
    normalized = re.sub(r"-+", "-", normalized) or "foundry"
    suffix = f"-{mode_suffix}-{resource_suffix}"
    if len(normalized) + len(suffix) <= 63:
        return normalized + suffix
    digest = hashlib.sha256(account_name.encode("utf-8")).hexdigest()[:8]
    available = 63 - len(suffix) - len(digest) - 1
    return f"{normalized[:available].rstrip('-')}-{digest}{suffix}"


def _project_principal_id(project: Any) -> str:
    identity = getattr(project, "identity", None)
    principal_id = getattr(identity, "principal_id", None)
    if principal_id is None and isinstance(identity, Mapping):
        principal_id = identity.get("principalId") or identity.get("principal_id")
    if not principal_id:
        raise ValueError(
            "Project Managed Identity mode requires a project with a system-assigned identity."
        )
    return str(principal_id)


def _resource_id(resource: Any) -> str:
    resource_id = getattr(resource, "id", None)
    if resource_id is None and isinstance(resource, Mapping):
        resource_id = resource.get("id")
    return str(resource_id or "")


def _required_resource_id(resource: Any, resource_kind: str) -> str:
    resource_id = _resource_id(resource)
    if not resource_id:
        raise ValueError(f"{resource_kind} did not return a resource ID.")
    return resource_id


def _connection_string(component: Any) -> str:
    value = getattr(component, "connection_string", None)
    properties = getattr(component, "properties", None)
    if value is None and properties is not None:
        value = getattr(properties, "connection_string", None)
    if value is None and isinstance(component, Mapping):
        properties_mapping = component.get("properties") or {}
        value = properties_mapping.get("ConnectionString") or properties_mapping.get("connectionString")
    if not value:
        raise ValueError("Application Insights did not return a connection string.")
    return str(value)


def _connection_string_value(connection_string: str, key: str) -> str:
    for part in connection_string.split(";"):
        name, separator, value = part.partition("=")
        if separator and name.strip().lower() == key.lower():
            return value.strip()
    raise ValueError(f"Application Insights connection string is missing '{key}'.")


def _error_code(error: HttpResponseError) -> str:
    model = getattr(error, "model", None) or getattr(error, "error", None)
    code = getattr(model, "code", None)
    if code is None:
        nested = getattr(model, "error", None)
        code = getattr(nested, "code", None)
    return str(code or "")


def _is_principal_not_found(error: HttpResponseError) -> bool:
    return _error_code(error).lower() == "principalnotfound" or "PrincipalNotFound" in str(error)


def _is_role_assignment_present(error: Exception) -> bool:
    if not isinstance(error, HttpResponseError):
        return False
    return _error_code(error).lower() == "roleassignmentexists"
