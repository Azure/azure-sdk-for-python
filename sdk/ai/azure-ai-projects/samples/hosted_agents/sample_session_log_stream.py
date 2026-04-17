# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
        This sample demonstrates how to stream hosted agent session logs
        using `project_client.beta.agents.get_session_log_stream` with the
        synchronous AIProjectClient.

        Sessions only work with Hosted Agents.

        Session and log stream operations are currently preview features.
        In the Python SDK, you access these operations via
        `project_client.beta.agents`.

USAGE:
        python sample_session_log_stream.py

        Before running the sample:

    pip install "azure-ai-projects>=2.1.0" python-dotenv azure-mgmt-authorization azure-mgmt-resource

    This sample verifies/assigns `Azure AI User` role for the hosted agent identity
    using Azure management SDK clients.

        Set these environment variables with your own values:
        1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
           page of your Microsoft Foundry portal.
    2) FOUNDRY_AGENT_CONTAINER_IMAGE - The Hosted Agent container image in the format
       '<registry>/<repository>[:<tag>|@<digest>]'
    3) FOUNDRY_PROJECTS_AZURE_SUBSCRIPTION_ID - Azure subscription ID where the
       Azure AI account and project are deployed.

        NOTE: This sample assumes the Foundry project and Azure AI account are in the
        same resource group.

        You can build and push an example image from
        `samples/hosted_agents/assets/responses-echo-agent` and use that image value
        for `FOUNDRY_AGENT_CONTAINER_IMAGE`.
"""

import os
import uuid
from urllib.parse import urlparse

from dotenv import load_dotenv

from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentCreateParameters
from azure.mgmt.resource import ResourceManagementClient

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentEndpoint,
    AgentEndpointProtocol,
    FixedRatioVersionSelectionRule,
    VersionSelector,
)
from hosted_agents_util import create_agent_and_session

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
image = os.environ["FOUNDRY_AGENT_CONTAINER_IMAGE"]
subscription_id = os.environ["FOUNDRY_PROJECTS_AZURE_SUBSCRIPTION_ID"]
agent_name = "MySessionHostedAgent32"
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



def _ensure_azure_ai_user_role(
    credential: TokenCredential, principal_id: str, scope_resource_id: str, subscription_id: str, role_id: str
) -> None:
    authorization_client = AuthorizationManagementClient(credential, subscription_id)
    role_definition_id = (
        f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/{role_id}"
    )
    role_assignment_name = str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"{scope_resource_id}|{principal_id}|{role_definition_id}",
        )
    )

    try:
        authorization_client.role_assignments.get(scope_resource_id, role_assignment_name)
        print(f"Azure AI User role already assigned to principal {principal_id}.")
        return
    except ResourceNotFoundError:
        pass

    parameters = RoleAssignmentCreateParameters(
        role_definition_id=role_definition_id,
        principal_id=principal_id,
        principal_type="ServicePrincipal",
    )
    try:
        authorization_client.role_assignments.create(scope_resource_id, role_assignment_name, parameters)
        print(f"Assigned Azure AI User role to principal {principal_id} at scope {scope_resource_id}.")
    except (ResourceExistsError, HttpResponseError) as e:
        if isinstance(e, HttpResponseError) and "RoleAssignmentExists" not in str(e):
            raise
        print(f"Azure AI User role already assigned to principal {principal_id} (existing assignment detected).")


def _ensure_agent_identity_rbac(
    project_client: AIProjectClient,
    credential: TokenCredential,
    subscription_id: str,
    foundry_project_endpoint: str,
    current_agent_name: str,
) -> None:
    agent_details = project_client.agents.get(agent_name=current_agent_name)
    if not agent_details.instance_identity or not agent_details.instance_identity.principal_id:
        raise RuntimeError("Agent instance_identity or principal_id is not available.")
    principal_id = agent_details.instance_identity.principal_id

    account_name = urlparse(foundry_project_endpoint).hostname.split(".")[0]  # type: ignore[union-attr]
    project_name = foundry_project_endpoint.rstrip("/").split("/api/projects/")[1].split("/")[0]
    scope_resource_id = _resolve_ai_account_resource_id(credential, account_name, project_name, subscription_id)

    _ensure_azure_ai_user_role(
        credential=credential,
        principal_id=principal_id,
        scope_resource_id=scope_resource_id,
        subscription_id=subscription_id,
        role_id=AZURE_AI_USER_ROLE_DEFINITION_GUID,
    )


def _iter_sse_frames(stream, max_log_events: int):
    event_count = 0
    buffer = ""

    for chunk in stream:
        buffer += chunk.decode("utf-8", errors="replace")

        while "\n\n" in buffer:
            frame, buffer = buffer.split("\n\n", 1)
            event_name = None
            data_lines = []

            for line in frame.splitlines():
                if line.startswith("event: "):
                    event_name = line[7:]
                elif line.startswith("data: "):
                    data_lines.append(line[6:])

            if data_lines or event_name:
                event_count += 1
                yield {
                    "event": event_name,
                    "data": "\n".join(data_lines),
                }

                if event_count >= max_log_events:
                    return


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=endpoint,
        credential=credential,
        allow_preview=True,
    ) as project_client,
    create_agent_and_session(project_client, agent_name, image) as (agent, session),
):
    endpoint_config = AgentEndpoint(
        version_selector=VersionSelector(
            version_selection_rules=[
                FixedRatioVersionSelectionRule(agent_version=agent.version, traffic_percentage=100),
            ]
        ),
        protocols=[AgentEndpointProtocol.RESPONSES],
    )

    project_client.beta.agents.patch_agent_details(
        agent_name=agent_name,
        agent_endpoint=endpoint_config,
    )

    _ensure_agent_identity_rbac(
        project_client=project_client,
        credential=credential,
        subscription_id=subscription_id,
        foundry_project_endpoint=endpoint,
        current_agent_name=agent_name,
    )

    print(f"Agent endpoint configured for agent: {agent_name}")
    input_text = "Say hello in one short sentence."

    with project_client.get_openai_client(agent_name=agent_name) as openai_client:
        response = openai_client.responses.create(
            input=input_text,
            extra_body={
                "agent_session_id": session.agent_session_id,
            },
        )
        print(f"Response output: {response.output_text}")

    print("Streaming session logs...")
    raw_stream = project_client.beta.agents.get_session_log_stream(
        agent_name=agent_name,
        agent_version=agent.version,
        session_id=session.agent_session_id,
    )
    for frame in _iter_sse_frames(raw_stream, max_log_events=30):
        print(f"SSE event: {frame.get('event')}")
        print(f"SSE data: {frame.get('data')}\n")
