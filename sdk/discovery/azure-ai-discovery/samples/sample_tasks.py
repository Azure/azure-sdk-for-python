# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to manage tasks using the WorkspaceClient.
    Tasks represent units of work within an investigation, such as research
    steps, analysis activities, or follow-up actions.

USAGE:
    python sample_tasks.py

    Set these environment variables before running the sample:
    1) AZURE_DISCOVERY_WORKSPACE_ENDPOINT - Your workspace endpoint URL, e.g.
        https://<workspaceName>.workspace.discovery.azure.com
    2) AZURE_DISCOVERY_PROJECT_NAME - The name of your project.
    3) AZURE_DISCOVERY_INVESTIGATION_NAME - The name of an existing investigation.
"""


def sample_tasks():
    import os
    from azure.identity import DefaultAzureCredential
    from azure.ai.discovery import WorkspaceClient
    from azure.ai.discovery.models import Task, TaskAssignee, TaskComment

    endpoint = os.environ["AZURE_DISCOVERY_WORKSPACE_ENDPOINT"]
    project_name = os.environ["AZURE_DISCOVERY_PROJECT_NAME"]
    investigation_name = os.environ["AZURE_DISCOVERY_INVESTIGATION_NAME"]
    investigation_path = f"/projects/{project_name}/investigations/{investigation_name}"

    client = WorkspaceClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    # Create a task
    task = client.tasks.create(
        project_name=project_name,
        investigation_name=investigation_name,
        body=Task(
            title="Analyze compound interactions",
            priority="High",
            description="Review the interaction data for compounds A and B",
            assigned_to=TaskAssignee(id="researcher-agent", type="Application"),
            investigation_id=investigation_path,
        ),
    )
    print(f"Created task: {task.name}")
    print(f"  Title: {task.title}")
    print(f"  Status: {task.status}")
    print(f"  Priority: {task.priority}")

    task_name = task.name

    # List all tasks in the investigation
    tasks = list(
        client.tasks.list(
            project_name=project_name,
            investigation_name=investigation_name,
        )
    )
    print(f"\nFound {len(tasks)} task(s):")
    for t in tasks:
        print(f"  - {t.title} ({t.status})")

    # List tasks with a filter
    new_tasks = list(
        client.tasks.list(
            project_name=project_name,
            investigation_name=investigation_name,
            filter="status eq 'New'",
        )
    )
    print(f"\nNew tasks: {len(new_tasks)}")

    # Get a specific task
    fetched = client.tasks.get(
        project_name=project_name,
        investigation_name=investigation_name,
        task_name=task_name,
    )
    print(f"\nFetched task: {fetched.title}")

    # Add a comment to the task
    updated = client.tasks.add_comment(
        project_name=project_name,
        investigation_name=investigation_name,
        task_name=task_name,
        body=TaskComment(
            created_by="sample-user",
            created_by_type="User",
            text="Initial analysis shows promising results.",
        ),
    )
    print(f"\nAdded comment to task: {updated.title}")

    # Start the task
    started = client.tasks.start(
        project_name=project_name,
        investigation_name=investigation_name,
        task_name=task_name,
    )
    print(f"Task started: {started.status}")

    # Delete the task
    client.tasks.delete(
        project_name=project_name,
        investigation_name=investigation_name,
        task_name=task_name,
    )
    print(f"\nDeleted task: {task_name}")


if __name__ == "__main__":
    sample_tasks()
