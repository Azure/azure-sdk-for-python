import uuid
from typing import Any, cast
from urllib.parse import urlparse

from azure.core.credentials import TokenCredential
from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.mgmt.authorization import AuthorizationManagementClient, models as authorization_models
from azure.mgmt.resource import ResourceManagementClient

from azure.ai.projects.models import AgentVersionDetails

AZURE_AI_USER_ROLE_DEFINITION_GUID = "53ca6127-db72-4b80-b1b0-d745d6d5456d"


def _extract_resource_group_name(resource_id: str) -> str:
    parts = resource_id.strip("/").split("/")
    for index, part in enumerate(parts):
        if part.lower() == "resourcegroups" and index + 1 < len(parts):
            return parts[index + 1]
    return ""


def _resolve_ai_account_resource_id(
    credential: TokenCredential,
    account_name: str,
    project_name: str,
    subscription_id: str,
) -> str:
    resource_client = ResourceManagementClient(credential, subscription_id)
    project_resources = resource_client.resources.list(
        filter="resourceType eq 'Microsoft.CognitiveServices/accounts/projects'"
    )

    project_id_segment = f"/accounts/{account_name}/projects/{project_name}".lower()
    matching_projects = [
        resource for resource in project_resources if resource.id and project_id_segment in resource.id.lower()
    ]
    if not matching_projects:
        raise RuntimeError(f"Could not locate Foundry project '{project_name}' in subscription '{subscription_id}'.")

    if not matching_projects[0].id:
        raise RuntimeError("Foundry project resource ID is empty.")
    resource_group_name = _extract_resource_group_name(matching_projects[0].id)
    account_resources = resource_client.resources.list_by_resource_group(
        resource_group_name=resource_group_name,
        filter="resourceType eq 'Microsoft.CognitiveServices/accounts'",
    )

    account_matches = [resource.id for resource in account_resources if resource.name == account_name and resource.id]
    if not account_matches:
        raise RuntimeError(
            f"Could not locate Azure AI account '{account_name}' in resource group '{resource_group_name}'."
        )
    return account_matches[0]


def _ensure_agent_identity_rbac_with_role_id(
    credential: TokenCredential, principal_id: str, scope_resource_id: str, subscription_id: str, role_id: str
) -> tuple[bool, str]:
    authorization_client = AuthorizationManagementClient(credential, subscription_id)
    role_definition_id = f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/{role_id}"
    role_assignment_name = str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"{scope_resource_id}|{principal_id}|{role_definition_id}",
        )
    )

    try:
        authorization_client.role_assignments.get(scope_resource_id, role_assignment_name)
        print(f"Azure AI User role already assigned to principal {principal_id}.")
        return False, role_assignment_name
    except ResourceNotFoundError:
        pass

    create_parameters_kwargs = cast(
        dict[str, Any],
        {
            "role_definition_id": role_definition_id,
            "principal_id": principal_id,
            "principal_type": authorization_models.PrincipalType.SERVICE_PRINCIPAL,
        },
    )
    parameters = authorization_models.RoleAssignmentCreateParameters(**create_parameters_kwargs)

    authorization_client.role_assignments.create(scope_resource_id, role_assignment_name, parameters)
    print(f"Assigned Azure AI User role to principal {principal_id} at scope {scope_resource_id}.")
    return True, role_assignment_name


def ensure_agent_identity_rbac(
    agent: AgentVersionDetails,
    credential: TokenCredential,
    subscription_id: str,
    foundry_project_endpoint: str,
) -> None:
    """Ensure the hosted agent identity has Azure AI User role on the Azure AI account.

    This resolves the Azure AI account resource ID from the Foundry project endpoint,
    reads the hosted agent managed identity principal ID from ``agent``, and
    creates a deterministic role assignment for the Azure AI User role if one does not
    already exist.

    :param agent: Agent version details containing ``instance_identity``.
    :type agent: ~azure.ai.projects.models.AgentVersionDetails
    :param credential: Credential used for Azure Resource Manager authorization calls.
    :type credential: ~azure.core.credentials.TokenCredential
    :param subscription_id: Azure subscription ID containing the Foundry project/account.
    :type subscription_id: str
    :param foundry_project_endpoint: Foundry project endpoint in the format
        ``https://<account>.services.ai.azure.com/api/projects/<project-name>``.
    :type foundry_project_endpoint: str
    :raises RuntimeError: If the agent identity principal ID is unavailable, or if the
        account/project resources cannot be resolved.
    :raises ~azure.core.exceptions.HttpResponseError: If role assignment creation fails
        for reasons other than an existing assignment.
    """
    if not agent.instance_identity or not agent.instance_identity.principal_id:
        raise RuntimeError("Agent instance_identity or principal_id is not available.")
    principal_id = agent.instance_identity.principal_id

    account_name = urlparse(foundry_project_endpoint).hostname.split(".")[0]  # type: ignore[union-attr]
    project_name = foundry_project_endpoint.rstrip("/").split("/api/projects/")[1].split("/")[0]
    scope_resource_id = _resolve_ai_account_resource_id(credential, account_name, project_name, subscription_id)

    _ensure_agent_identity_rbac_with_role_id(
        credential=credential,
        principal_id=principal_id,
        scope_resource_id=scope_resource_id,
        subscription_id=subscription_id,
        role_id=AZURE_AI_USER_ROLE_DEFINITION_GUID,
    )
