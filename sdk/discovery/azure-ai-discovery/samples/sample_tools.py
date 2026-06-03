# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to run tools using the WorkspaceClient.
    Tools allow you to execute compute jobs on supercomputer node pools,
    check run status, and monitor compute usage.

USAGE:
    python sample_tools.py

    Set these environment variables before running the sample:
    1) AZURE_DISCOVERY_WORKSPACE_ENDPOINT - Your workspace endpoint URL, e.g.
        https://<workspaceName>.workspace.discovery.azure.com
    2) AZURE_DISCOVERY_PROJECT_NAME - The name of your project.
    3) AZURE_DISCOVERY_TOOL_ID - The ARM resource ID of the tool to run.
    4) AZURE_DISCOVERY_NODE_POOL_ID - The ARM resource ID of the node pool.
"""


def sample_tools():
    import os
    from azure.identity import DefaultAzureCredential
    from azure.ai.discovery import WorkspaceClient

    endpoint = os.environ["AZURE_DISCOVERY_WORKSPACE_ENDPOINT"]
    project_name = os.environ["AZURE_DISCOVERY_PROJECT_NAME"]
    tool_id = os.environ["AZURE_DISCOVERY_TOOL_ID"]
    node_pool_id = os.environ["AZURE_DISCOVERY_NODE_POOL_ID"]

    client = WorkspaceClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    # Start a tool run (long-running operation)
    poller = client.tools.begin_run(
        project_name=project_name,
        tool_id=tool_id,
        node_pool_ids=[node_pool_id],
        command='echo "Hello from Discovery"',
    )
    print("Tool run started. Waiting for completion...")
    result = poller.result()
    print(f"Run completed: {result.status}")

    # Get compute usage for the project
    usage = client.tools.get_compute_usage(project_name=project_name)
    print("\nCompute usage:")
    for sc_name, sc_usage in usage.supercomputers.items():
        print(f"  Supercomputer: {sc_name} (active jobs: {sc_usage.active_jobs})")
        for pool_name, pool_usage in sc_usage.nodepools.items():
            print(f"    Pool {pool_name}: GPUs reserved={pool_usage.reserved_gp_us}")

    # List recent operations
    operations = client.tools.get_operations(project_name=project_name)
    print("\nRecent operations:")
    for op in operations.value:
        print(f"  - {op.id}: {op.status}")


if __name__ == "__main__":
    sample_tools()
