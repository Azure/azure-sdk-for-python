# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: planetarycomputer_ingestion.py

DESCRIPTION:
    This sample demonstrates comprehensive ingestion management operations including:
    - Creating and managing ingestion sources (managed identity-based) - DEMONSTRATION ONLY
    - Creating or replacing sources with create_or_replace_source (idempotent)
    - Retrieving specific sources with get_source
    - Creating and updating ingestion definitions
    - Retrieving specific ingestions with get
    - Running ingestion jobs from public catalogs
    - Listing ingestion runs with list_runs
    - Monitoring ingestion status
    - Managing ingestion operations

USAGE:
    python planetarycomputer_ingestion.py

    Set the environment variable PLANETARYCOMPUTER_ENDPOINT with your endpoint URL.
    Set the environment variable PLANETARYCOMPUTER_COLLECTION_ID with your collection ID.

    Optional (for managed identity examples):
    Set the environment variable PLANETARYCOMPUTER_INGESTION_CONTAINER_URI with your container URI.
    Set the environment variable PLANETARYCOMPUTER_INGESTION_CATALOG_URL with your source catalog URL.
    Set the environment variable PLANETARYCOMPUTER_MANAGED_IDENTITY_OBJECT_ID with your managed identity object ID.

    Optional (for SAS token examples):
    Set the environment variable AZURE_INGESTION_SAS_CONTAINER_URI with your SAS container URI.
    Set the environment variable AZURE_INGESTION_SAS_TOKEN with your SAS token.
"""

import os
import asyncio
from azure.planetarycomputer.aio import PlanetaryComputerProClient
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.planetarycomputer.models import (
    ManagedIdentityConnection,
    ManagedIdentityIngestionSource,
    SharedAccessSignatureTokenConnection,
    SharedAccessSignatureTokenIngestionSource,
    IngestionDefinition,
    IngestionType,
)
import uuid

import logging

# Enable HTTP request/response logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
    logging.ERROR
)
logging.basicConfig(level=logging.INFO)


async def create_managed_identity_ingestion_sources(
    client: PlanetaryComputerProClient,
    container_uri: str,
    managed_identity_object_id: str,
):
    """Create managed identity-based ingestion source and return the source_id."""

    # Validate required parameters
    if not container_uri:
        raise ValueError(
            "PLANETARYCOMPUTER_INGESTION_CONTAINER_URI environment variable must be set. "
            "Example: https://yourstorageaccount.blob.core.windows.net/yourcontainer"
        )
    if not managed_identity_object_id:
        raise ValueError(
            "PLANETARYCOMPUTER_MANAGED_IDENTITY_OBJECT_ID environment variable must be set. "
            "This is the object ID of the managed identity with access to the storage account."
        )

    # Clean up existing sources
    async for source in client.ingestion.list_sources():
        await client.ingestion.delete_source(id=source.id)
        logging.info(f"Deleted existing source: {source.id}")

    # Create connection info with managed identity
    connection_info = ManagedIdentityConnection(
        container_uri=container_uri, object_id=managed_identity_object_id
    )

    # Create ingestion source with unique ID
    source_id = str(uuid.uuid4())
    ingestion_source = ManagedIdentityIngestionSource(
        id=source_id, connection_info=connection_info
    )
    created_source = await client.ingestion.create_source(body=ingestion_source)
    logging.info(f"Created managed identity ingestion source: {created_source.id}")

    # List managed identities
    logging.info("Listing available managed identities:")
    async for identity in client.ingestion.list_managed_identities():
        logging.info(f"  - Object ID: {identity.object_id}")
        logging.info(f"    Resource ID: {identity.resource_id}")

    return source_id


async def create_or_replace_source(
    client: PlanetaryComputerProClient,
    sas_container_uri: str,
    sas_token: str,
    source_id: str,
):
    """Demonstrate create_or_replace_source idempotent operation.

    This assumes the source already exists (created by create_sas_token_ingestion_source).
    It demonstrates that create_or_replace_source can be called multiple times with the same source_id
    to update/replace the source (in this case, updating the SAS token).
    """
    # Validate required parameters
    if not sas_container_uri:
        raise ValueError(
            "AZURE_INGESTION_SAS_CONTAINER_URI environment variable must be set for create_or_replace_source"
        )
    if not sas_token:
        raise ValueError(
            "AZURE_INGESTION_SAS_TOKEN environment variable must be set for create_or_replace_source"
        )

    # Create connection info with SAS token
    connection_info = SharedAccessSignatureTokenConnection(
        container_uri=sas_container_uri, shared_access_signature_token=sas_token
    )

    # Create ingestion source
    ingestion_source = SharedAccessSignatureTokenIngestionSource(
        id=source_id, connection_info=connection_info
    )

    # First call - replaces the existing source with original token
    logging.info(
        f"First call to create_or_replace_source with existing source ID: {source_id}"
    )
    first_result = await client.ingestion.replace_source(
        id=source_id, body=ingestion_source
    )
    logging.info(f"First call result: {first_result.id}")

    # Second call - replaces again with modified token (demonstrates update capability)
    updated_token = "sp=rl&st=2024-01-01T00:00:00Z&se=2024-12-31T23:59:59Z&sv=2023-01-03&sr=c&sig=UpdatedRandomSignature123456"

    updated_connection_info = SharedAccessSignatureTokenConnection(
        container_uri=sas_container_uri, shared_access_signature_token=updated_token
    )
    updated_ingestion_source = SharedAccessSignatureTokenIngestionSource(
        id=source_id, connection_info=updated_connection_info
    )

    logging.info("Second call to create_or_replace_source with updated SAS token")
    second_result = await client.ingestion.replace_source(
        id=source_id, body=updated_ingestion_source
    )
    logging.info(f"Second call result: {second_result.id}")

    return second_result.id


async def get_source_by_id(client: PlanetaryComputerProClient, source_id: str):
    """Retrieve a specific ingestion source by ID.

    This demonstrates using get_source to fetch a specific source directly
    instead of listing all sources.
    """
    logging.info(f"Retrieving ingestion source: {source_id}")

    try:
        source = await client.ingestion.get_source(id=source_id)
        logging.info(f"Successfully retrieved source: {source.id}")
        return source
    except Exception as e:
        logging.error(f"Failed to retrieve source {source_id}: {str(e)}")
        return None


async def create_github_public_ingestion(
    client: PlanetaryComputerProClient, collection_id: str, source_catalog_url: str
):
    """Create, update, and run ingestion from sample public catalog on GitHub."""

    # Delete all existing ingestions
    logging.info("Deleting all existing ingestions...")
    async for ingestion in client.ingestion.list(collection_id=collection_id):
        await client.ingestion.begin_delete(
            collection_id=collection_id, ingestion_id=ingestion.id, polling=True
        )
        logging.info(f"Deleted existing ingestion: {ingestion.id}")

    # Create ingestion definition
    ingestion_definition = IngestionDefinition(
        import_type=IngestionType.STATIC_CATALOG,
        display_name="Sample Ingestion",
        source_catalog_url=source_catalog_url,
        keep_original_assets=True,
        skip_existing_items=True,  # Skip items that already exist
    )

    # Create the ingestion
    logging.info("Creating ingestion for sample catalog...")
    ingestion_response = await client.ingestion.create(
        collection_id=collection_id, body=ingestion_definition
    )
    ingestion_id = ingestion_response.id
    logging.info(f"Created ingestion: {ingestion_id}")

    # Update the ingestion display name
    updated_definition = IngestionDefinition(
        import_type=IngestionType.STATIC_CATALOG,
        display_name="Sample Dataset Ingestion",
    )

    ingestion = await client.ingestion.update(
        collection_id=collection_id, ingestion_id=ingestion_id, body=updated_definition
    )
    logging.info(
        f"Updated ingestion display name to: {updated_definition.display_name}"
    )

    return ingestion_id


async def get_ingestion_by_id(
    client: PlanetaryComputerProClient, collection_id: str, ingestion_id: str
):
    """Retrieve a specific ingestion by ID.

    This demonstrates using get to fetch a specific ingestion directly
    instead of listing all ingestions.
    """
    logging.info(
        f"Retrieving ingestion: {ingestion_id} from collection: {collection_id}"
    )

    try:
        ingestion = await client.ingestion.get(
            collection_id=collection_id, ingestion_id=ingestion_id
        )

        logging.info(f"Successfully retrieved ingestion: {ingestion.id}")
        logging.info(f"  Display name: {ingestion.display_name}")
        logging.info(f"  Import type: {ingestion.import_type}")
        if ingestion.source_catalog_url:
            logging.info(f"  Source catalog: {ingestion.source_catalog_url}")

        return ingestion
    except Exception as e:
        logging.error(f"Failed to retrieve ingestion {ingestion_id}: {str(e)}")
        return None


async def list_ingestion_runs(
    client: PlanetaryComputerProClient, collection_id: str, ingestion_id: str
):
    """List all runs for a specific ingestion.

    This demonstrates using list_runs to get all execution runs for an ingestion,
    which is useful for monitoring ingestion history and troubleshooting.
    """
    logging.info(f"Listing runs for ingestion: {ingestion_id}")

    try:
        async for run in client.ingestion.list_runs(
            collection_id=collection_id, ingestion_id=ingestion_id
        ):
            operation = run.operation
            logging.info(f"  Run ID: {run.id}")
            logging.info(f"    Status: {operation.status}")
            logging.info(
                f"    Items - Total: {operation.total_items}, "
                f"Successful: {operation.total_successful_items}, "
                f"Failed: {operation.total_failed_items}, "
                f"Pending: {operation.total_pending_items}"
            )

            if operation.status_history:
                for status_item in operation.status_history:
                    if status_item.error_code:
                        logging.info(
                            f"    Error: {status_item.error_code} - {status_item.error_message}"
                        )
    except Exception as e:
        logging.error(f"Failed to list runs for ingestion {ingestion_id}: {str(e)}")


async def create_sas_token_ingestion_source(
    client: PlanetaryComputerProClient, sas_container_uri: str, sas_token: str
):
    """Create a SAS token ingestion source with example values."""

    # Validate required parameters
    if not sas_container_uri:
        raise ValueError(
            "AZURE_INGESTION_SAS_CONTAINER_URI environment variable must be set. "
            "Example: https://yourstorageaccount.blob.core.windows.net/yourcontainer"
        )
    if not sas_token:
        raise ValueError(
            "AZURE_INGESTION_SAS_TOKEN environment variable must be set. "
            "This is the SAS token for accessing the storage account."
        )

    logging.info("Creating SAS token ingestion source...")

    # Create connection info with SAS token (using fake/example values)
    sas_connection_info = SharedAccessSignatureTokenConnection(
        container_uri=sas_container_uri, shared_access_signature_token=sas_token
    )

    # Create SAS token ingestion source
    sas_source_id = str(uuid.uuid4())
    sas_ingestion_source = SharedAccessSignatureTokenIngestionSource(
        id=sas_source_id, connection_info=sas_connection_info
    )

    # Register the SAS token source
    created_sas_source = await client.ingestion.create_source(body=sas_ingestion_source)
    logging.info(f"Created SAS token ingestion source: {created_sas_source.id}")
    return created_sas_source.id


async def create_ingestion_run(
    client: PlanetaryComputerProClient, collection_id: str, ingestion_id: str
):
    """Create an ingestion run."""

    # Create ingestion run
    run_response = await client.ingestion.create_run(
        collection_id=collection_id, ingestion_id=ingestion_id
    )
    logging.info(f"Created ingestion run: {run_response.id}")
    return run_response.id


async def manage_operations(client: "PlanetaryComputerProClient"):
    """List, get, and cancel ingestion operations."""

    # List operations and get the first one if available
    operation_id = None
    async for operation in client.ingestion.list_operations():
        operation_id = operation.id
        break

    if operation_id:
        # Get a specific operation
        operation = await client.ingestion.get_operation(operation_id)

        # Try to cancel the operation
        try:
            await client.ingestion.cancel_operation(operation.id)
        except HttpResponseError as e:
            logging.info(f"Failed to cancel operation {operation.id}: {e.message}")
            pass

    # Cancel all operations
    try:
        await client.ingestion.cancel_all_operations()
    except HttpResponseError as e:
        raise RuntimeError("Failed to cancel all operations") from e


async def main():
    # Get configuration from environment
    endpoint = os.environ.get("PLANETARYCOMPUTER_ENDPOINT")
    collection_id = os.environ.get("PLANETARYCOMPUTER_COLLECTION_ID")

    # Get optional ingestion-specific configuration (for examples)
    container_uri = os.environ.get("PLANETARYCOMPUTER_INGESTION_CONTAINER_URI")
    source_catalog_url = os.environ.get("PLANETARYCOMPUTER_INGESTION_CATALOG_URL")
    managed_identity_object_id = os.environ.get(
        "PLANETARYCOMPUTER_MANAGED_IDENTITY_OBJECT_ID"
    )
    sas_container_uri = os.environ.get("AZURE_INGESTION_SAS_CONTAINER_URI")
    sas_token = os.environ.get("AZURE_INGESTION_SAS_TOKEN")

    assert endpoint is not None
    assert collection_id is not None
    assert container_uri is not None
    assert source_catalog_url is not None
    assert managed_identity_object_id is not None
    assert sas_container_uri is not None
    assert sas_token is not None

    if not endpoint:
        raise ValueError("PLANETARYCOMPUTER_ENDPOINT environment variable must be set")

    logging.info(f"Connected to: {endpoint}")
    logging.info(f"Collection ID: {collection_id}\n")

    # Create client
    credential = DefaultAzureCredential()
    client = PlanetaryComputerProClient(
        endpoint=endpoint,
        credential=credential,
        logging_enable=False,  # Set to True for detailed HTTP logging
    )

    # Execute ingestion management workflow
    # 1. Create managed identity and SAS token ingestion sources
    await create_managed_identity_ingestion_sources(
        client, container_uri, managed_identity_object_id
    )
    sas_source_id = await create_sas_token_ingestion_source(
        client, sas_container_uri, sas_token
    )

    # 2. Demonstrate advanced source operations (idempotent)
    updated_source_id = await create_or_replace_source(
        client, sas_container_uri, sas_token, sas_source_id
    )
    await get_source_by_id(client, updated_source_id)

    # 3. Run actual ingestion hosted on GitHub
    public_ingestion_id = await create_github_public_ingestion(
        client, collection_id, source_catalog_url
    )

    # 4. Demonstrate advanced ingestion operations
    await get_ingestion_by_id(client, collection_id, public_ingestion_id)

    # 5. Create an ingestion run
    await create_ingestion_run(client, collection_id, public_ingestion_id)

    # 6. List all runs for the ingestion
    await list_ingestion_runs(client, collection_id, public_ingestion_id)

    # 7. Manage operations
    await manage_operations(client)

    await client.close()
    await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
