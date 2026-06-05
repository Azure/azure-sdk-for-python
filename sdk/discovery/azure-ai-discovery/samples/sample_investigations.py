# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to manage investigations using the
    WorkspaceClient. It shows how to create, list, get, and delete
    investigations, as well as how to manage the Discovery Engine.

USAGE:
    python sample_investigations.py

    Set these environment variables before running the sample:
    1) AZURE_DISCOVERY_WORKSPACE_ENDPOINT - Your workspace endpoint URL, e.g.
        https://<workspaceName>.workspace.discovery.azure.com
    2) AZURE_DISCOVERY_PROJECT_NAME - The name of your project.
"""


def sample_investigations():
    import os
    from azure.identity import DefaultAzureCredential
    from azure.ai.discovery import WorkspaceClient
    from azure.ai.discovery.models import Investigation

    endpoint = os.environ["AZURE_DISCOVERY_WORKSPACE_ENDPOINT"]
    project_name = os.environ["AZURE_DISCOVERY_PROJECT_NAME"]

    client = WorkspaceClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    # Create a new investigation
    investigation = client.investigations.create_or_replace(
        project_name=project_name,
        investigation_name="sample-investigation",
        resource=Investigation(
            description="Investigating anomalies in dataset X",
            display_name="Sample Investigation",
        ),
    )
    print(f"Created investigation: {investigation.name}")
    print(f"  Status: {investigation.status}")
    print(f"  Created at: {investigation.created_at}")

    # List all investigations in the project
    investigations = list(client.investigations.list(project_name=project_name))
    print(f"\nFound {len(investigations)} investigation(s):")
    for inv in investigations:
        print(f"  - {inv.name} ({inv.status})")

    # Get a specific investigation
    fetched = client.investigations.get(
        project_name=project_name,
        investigation_name="sample-investigation",
    )
    print(f"\nFetched investigation: {fetched.display_name}")

    # Start the Discovery Engine for the investigation
    engine = client.investigations.start_discovery_engine(
        project_name=project_name,
        investigation_name="sample-investigation",
    )
    print(f"\nDiscovery Engine status: {engine.discovery_engine_status}")

    # Get Discovery Engine status
    engine = client.investigations.get_discovery_engine(
        project_name=project_name,
        investigation_name="sample-investigation",
    )
    print(f"Discovery Engine status: {engine.discovery_engine_status}")

    # Stop the Discovery Engine
    engine = client.investigations.stop_discovery_engine(
        project_name=project_name,
        investigation_name="sample-investigation",
    )
    print(f"Discovery Engine stopped: {engine.discovery_engine_status}")

    # Delete the investigation (long-running operation)
    poller = client.investigations.begin_delete(
        project_name=project_name,
        investigation_name="sample-investigation",
    )
    result = poller.result()
    print(f"\nDeleted investigation: {result.name}")


if __name__ == "__main__":
    sample_investigations()
