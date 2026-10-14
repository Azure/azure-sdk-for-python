# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to manage conversations using the
    WorkspaceClient. Conversations are used to interact with the
    Discovery Engine within an investigation.

USAGE:
    python sample_conversations.py

    Set these environment variables before running the sample:
    1) AZURE_DISCOVERY_WORKSPACE_ENDPOINT - Your workspace endpoint URL, e.g.
        https://<workspaceName>.workspace.discovery.azure.com
    2) AZURE_DISCOVERY_PROJECT_NAME - The name of your project.
    3) AZURE_DISCOVERY_INVESTIGATION_NAME - The name of an existing investigation.
"""


def sample_conversations():
    import os
    from azure.identity import DefaultAzureCredential
    from azure.ai.discovery import WorkspaceClient

    endpoint = os.environ["AZURE_DISCOVERY_WORKSPACE_ENDPOINT"]
    project_name = os.environ["AZURE_DISCOVERY_PROJECT_NAME"]
    investigation_name = os.environ["AZURE_DISCOVERY_INVESTIGATION_NAME"]
    investigation_path = f"/projects/{project_name}/investigations/{investigation_name}"

    client = WorkspaceClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    # Create a new conversation
    conversation = client.conversations.create(
        project_name=project_name,
        investigation_name=investigation_path,
        display_name="My research conversation",
    )
    print(f"Created conversation: {conversation.name}")
    print(f"  Display name: {conversation.display_name}")
    print(f"  Created at: {conversation.created_at}")

    conversation_name = conversation.name

    # List conversations in the project. The list operation returns a
    # ``PagedConversation`` envelope with a ``value`` list of items and an
    # optional ``next_link`` for the next page. Iterating the model directly
    # would iterate its field names, so always access ``.value``.
    page = client.conversations.list(project_name=project_name)
    print(f"\nFound {len(page.value)} conversation(s) on the first page:")
    for conv in page.value:
        print(f"  - {conv.name}: {conv.display_name}")
    if page.next_link:
        print(f"  (additional pages available via next_link={page.next_link})")

    # Get a specific conversation
    fetched = client.conversations.get(conversation_name=conversation_name)
    print(f"\nFetched conversation: {fetched.display_name}")

    # Delete the conversation
    client.conversations.delete(conversation_name=conversation_name)
    print(f"\nDeleted conversation: {conversation_name}")


if __name__ == "__main__":
    sample_conversations()
