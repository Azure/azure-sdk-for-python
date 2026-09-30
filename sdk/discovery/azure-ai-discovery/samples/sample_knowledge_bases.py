# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to manage knowledge bases using the
    BookshelfClient. Knowledge bases store indexed data that can be queried
    via the long-running ``search`` operation.

    As of API version ``2026-06-01`` (GA), the previously separate
    ``KnowledgeBaseVersions`` operation group has been folded into the
    unified ``KnowledgeBases`` surface. Lifecycle, indexing, and search are
    all expressed as long-running operations on the knowledge base itself.

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
    from azure.ai.discovery.models import KnowledgeBase, SearchRequest, StorageAssetReference

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

    # List all knowledge bases. Unlike the Workspace list operations, this one
    # returns an ItemPaged[KnowledgeBase] and supports transparent paging.
    print("Listing knowledge bases:")
    for kb in client.knowledge_bases.list():
        print(f"  - {kb.name}")

    # Create or update a knowledge base (long-running). The final result is the
    # KnowledgeBase resource (name, description, status, etc.).
    create_poller = client.knowledge_bases.begin_create_or_update(
        knowledge_base_name=knowledge_base_name,
        resource=KnowledgeBase(
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
    final = create_poller.result()
    print(f"\nCreated or updated knowledge base: {final.name}")
    print(f"  Description: {final.description}")
    print(f"  Provisioning state: {final.provisioning_state}")

    # Get a specific knowledge base by name
    fetched = client.knowledge_bases.get(knowledge_base_name=knowledge_base_name)
    print(f"\nFetched knowledge base: {fetched.name}")
    print(f"  Indexing status: {fetched.status}")

    # Start indexing (long-running). The poller resolves to None on completion;
    # post-indexing state can be re-read via ``get`` or the
    # ``get_operation_status`` operation.
    indexing_poller = client.knowledge_bases.begin_start_indexing(
        knowledge_base_name=knowledge_base_name,
        node_pool_id=node_pool_id,
        project_id=project_arm_id,
    )
    print("\nIndexing started; waiting for completion...")
    indexing_poller.result()
    print("Indexing complete.")

    # Search the knowledge base (long-running). The poller currently resolves
    # to None; the textual results are surfaced via the operation-status
    # endpoint (KnowledgeBaseSearchOperationResponse). Real workflows would
    # poll get_operation_status with the operation id from the LRO headers.
    client.knowledge_bases.begin_search(
        knowledge_base_name=knowledge_base_name,
        body=SearchRequest(query="What are common drug interactions?"),
    ).result()
    print("\nSearch submitted.")

    # Delete the knowledge base (long-running). Returns None on completion.
    client.knowledge_bases.begin_delete(knowledge_base_name=knowledge_base_name).result()
    print(f"\nDeleted knowledge base: {knowledge_base_name}")


if __name__ == "__main__":
    sample_knowledge_bases()
