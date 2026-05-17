# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to manage knowledge bases and their
    versions using the BookshelfClient. Knowledge bases store indexed
    data that can be queried by the Discovery Engine.

USAGE:
    python sample_knowledge_bases.py

    Set these environment variables before running the sample:
    1) AZURE_DISCOVERY_BOOKSHELF_ENDPOINT - Your bookshelf endpoint URL, e.g.
        https://<bookshelfName>.bookshelf.discovery.azure.com
    2) AZURE_DISCOVERY_KNOWLEDGE_BASE_NAME - The name of a knowledge base.
    3) AZURE_DISCOVERY_STORAGE_ASSET_ID - ARM resource ID of the storage asset.
    4) AZURE_DISCOVERY_USER_ASSIGNED_IDENTITY - ARM resource ID of the managed identity.
    5) AZURE_DISCOVERY_NODE_POOL_ID - ARM resource ID of the node pool for indexing.
    6) AZURE_DISCOVERY_PROJECT_ARM_ID - ARM resource ID of the project.
"""


def sample_knowledge_bases():
    import os
    from azure.identity import DefaultAzureCredential
    from azure.ai.discovery import BookshelfClient
    from azure.ai.discovery.models import KnowledgeBaseVersion, StorageAssetReference

    endpoint = os.environ["AZURE_DISCOVERY_BOOKSHELF_ENDPOINT"]
    knowledge_base_name = os.environ["AZURE_DISCOVERY_KNOWLEDGE_BASE_NAME"]
    storage_asset_id = os.environ["AZURE_DISCOVERY_STORAGE_ASSET_ID"]
    user_assigned_identity = os.environ["AZURE_DISCOVERY_USER_ASSIGNED_IDENTITY"]
    node_pool_id = os.environ["AZURE_DISCOVERY_NODE_POOL_ID"]
    project_arm_id = os.environ["AZURE_DISCOVERY_PROJECT_ARM_ID"]

    client = BookshelfClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    # List all knowledge bases
    knowledge_bases = list(client.knowledge_bases.list())
    print(f"Found {len(knowledge_bases)} knowledge base(s):")
    for kb in knowledge_bases:
        print(f"  - {kb.name}")

    # Create or update a knowledge base version
    version = client.knowledge_base_versions.create_or_update(
        knowledge_base_name=knowledge_base_name,
        version_name="v1",
        resource=KnowledgeBaseVersion(
            description="Research data for compound analysis",
            copilot_instruction="Use this to query information about compound interactions.",
            storage_asset_references=[
                StorageAssetReference(
                    id=storage_asset_id,
                    user_assigned_identity=user_assigned_identity,
                ),
            ],
        ),
    )
    print(f"\nCreated version: {version.name}")
    print(f"  Description: {version.description}")

    # List versions for a knowledge base
    versions = list(
        client.knowledge_base_versions.list(knowledge_base_name=knowledge_base_name)
    )
    print(f"\nVersions for '{knowledge_base_name}':")
    for v in versions:
        print(f"  - {v.name}")

    # Get the latest version
    latest = client.knowledge_base_versions.get_latest_version(
        knowledge_base_name=knowledge_base_name,
    )
    print(f"\nLatest version: {latest.name}")

    # Start indexing the knowledge base version
    poller = client.knowledge_base_versions.begin_start_indexing(
        knowledge_base_name=knowledge_base_name,
        version_name="v1",
        node_pool_id=node_pool_id,
        project_id=project_arm_id,
    )
    print("\nIndexing started. Waiting for completion...")
    result = poller.result()
    print(f"Indexing complete: {result.name}")

    # Get a specific version
    fetched = client.knowledge_base_versions.get(
        knowledge_base_name=knowledge_base_name,
        version_name="v1",
    )
    print(f"\nFetched version: {fetched.name}")
    print(f"  Indexing status: {fetched.status}")


if __name__ == "__main__":
    sample_knowledge_bases()
