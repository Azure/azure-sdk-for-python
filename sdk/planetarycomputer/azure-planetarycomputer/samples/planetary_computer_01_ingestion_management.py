# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: planetarycomputer_ingestion_management.py

DESCRIPTION:
    This sample demonstrates comprehensive ingestion management operations including:
    - Creating and managing ingestion sources (managed identity-based)
    - Creating and updating ingestion definitions
    - Running ingestion jobs and monitoring their status
    - Managing ingestion operations (cancel, list, etc.)

USAGE:
    python planetarycomputer_ingestion_management.py

    Set the environment variable AZURE_PLANETARY_COMPUTER_ENDPOINT with your endpoint URL.
    Set the environment variable AZURE_COLLECTION_ID with your collection ID.
    Set the environment variable AZURE_INGESTION_CONTAINER_URI_1 with your first container URI.
    Set the environment variable AZURE_INGESTION_CONTAINER_URI_2 with your second container URI (optional).
    Set the environment variable AZURE_INGESTION_CATALOG_URL with your source catalog URL.
    Set the environment variable AZURE_MANAGED_IDENTITY_OBJECT_ID with your managed identity object ID.
"""

import os
import time
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.planetarycomputer.models import (
    ManagedIdentityConnection,
    ManagedIdentityIngestionSource,
    Ingestion,
    IngestionType,
    OperationStatus,
)

import logging
from azure.core.pipeline.policies import HttpLoggingPolicy

# Enable HTTP request/response logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)


def create_ingestion_sources(client: PlanetaryComputerClient, container_uris: list, managed_identity_object_id: str):
    """Create managed identity-based ingestion sources."""

    # Clean up existing sources
    existing_sources = list(client.ingestion_management.list_sources())
    for source in existing_sources:
        client.ingestion_management.delete_source(id=source["id"])

    # Create new ingestion sources
    for container_uri in container_uris:
        # Create connection info with managed identity
        connection_info = ManagedIdentityConnection(container_uri=container_uri, object_id=managed_identity_object_id)

        # Create ingestion source
        ingestion_source = ManagedIdentityIngestionSource(connection_info=connection_info)
        ingestion_source = client.ingestion_management.create_source(ingestion_source=ingestion_source)
        logging.info(f"Created ingestion source: {ingestion_source.id}")

    # List managed identities
    managed_identities = client.ingestion_management.list_managed_identities()
    for identity in managed_identities:
        logging.info(f"  - {identity.object_id} | {identity.resource_id}")


def create_and_update_ingestion(client: PlanetaryComputerClient, collection_id: str, source_catalog_url: str):
    """Create and update an ingestion with various configurations."""

    # Create ingestion definition
    ingestion_definition = Ingestion(
        import_type=IngestionType.STATIC_CATALOG,
        display_name="Sentinel-2 Ingestion",
        source_catalog_url=source_catalog_url,
        keep_original_assets=False,
        skip_existing_items=False,
    )

    # Create the ingestion
    ingestion_response = client.ingestion_management.create(
        collection_id=collection_id, definition=ingestion_definition
    )
    ingestion_id = ingestion_response["id"]

    # Update the ingestion
    updated_definition = Ingestion(
        import_type=IngestionType.STATIC_CATALOG,
        display_name="Sentinel-2 Ingestion - Updated",
    )

    ingestion = client.ingestion_management.update(
        collection_id=collection_id, ingestion_id=ingestion_id, definition=updated_definition
    )

    logging.info(f"Updated ingestion: {ingestion.id}")

    return ingestion_id


def run_and_monitor_ingestion(client: PlanetaryComputerClient, collection_id: str, ingestion_id: str):
    """Create an ingestion run and monitor its progress."""

    # Create ingestion run
    run_response = client.ingestion_management.create_run(collection_id=collection_id, ingestion_id=ingestion_id)
    run_id = run_response.id

    # Monitor the run status
    status = None
    while True:
        run = client.ingestion_management.get_run(collection_id=collection_id, ingestion_id=ingestion_id, run_id=run_id)

        operation = run.operation
        status = operation.status

        logging.info(
            f"  Status: {status} | "
            f"Success: {operation.total_successful_items} | "
            f"Failed: {operation.total_failed_items} | "
            f"Pending: {operation.total_pending_items} | "
            f"Total: {operation.total_items}"
        )

        if status in [OperationStatus.SUCCEEDED, OperationStatus.FAILED, OperationStatus.CANCELED]:
            break

        time.sleep(2)

    # Check for errors in status history
    if run.operation.status_history:
        for status_item in run.operation.status_history:
            if status_item.error_code:
                logging.error(f"Ingestion error: {status_item.error_code} - {status_item.error_message}")



def manage_operations(client: PlanetaryComputerClient):
    """List, get, and cancel ingestion operations."""

    # List operations
    operations = list(client.ingestion_management.list_operations())

    if operations:
        # Get a specific operation
        operation_id = operations[0].id
        operation = client.ingestion_management.get_operation(operation_id)

        # Try to cancel the operation
        try:
            client.ingestion_management.cancel_operation(operation.id)
        except HttpResponseError as e:
            logging.info(f"Failed to cancel operation {operation.id}: {e.message}")
            pass

    # Cancel all operations
    try:
        client.ingestion_management.cancel_all_operations()
    except HttpResponseError as e:
        raise RuntimeError("Failed to cancel all operations") from e


def main():
    # Get configuration from environment
    endpoint = os.environ.get("AZURE_PLANETARY_COMPUTER_ENDPOINT")
    collection_id = os.environ.get("AZURE_COLLECTION_ID", "atl")

    # Get ingestion-specific configuration
    container_uri_1 = os.environ.get("AZURE_INGESTION_CONTAINER_URI_1")
    container_uri_2 = os.environ.get("AZURE_INGESTION_CONTAINER_URI_2")
    source_catalog_url = os.environ.get("AZURE_INGESTION_CATALOG_URL")
    managed_identity_object_id = os.environ.get("AZURE_MANAGED_IDENTITY_OBJECT_ID")

    if not endpoint:
        raise ValueError("AZURE_PLANETARY_COMPUTER_ENDPOINT environment variable must be set")

    if not container_uri_1:
        raise ValueError("AZURE_INGESTION_CONTAINER_URI_1 environment variable must be set")

    if not source_catalog_url:
        raise ValueError("AZURE_INGESTION_CATALOG_URL environment variable must be set")

    if not managed_identity_object_id:
        raise ValueError("AZURE_MANAGED_IDENTITY_OBJECT_ID environment variable must be set")

    # Build container URI list
    container_uris = [container_uri_1]
    if container_uri_2:
        container_uris.append(container_uri_2)

    # Create client
    credential = DefaultAzureCredential()
    client = PlanetaryComputerClient(
        endpoint=endpoint,
        credential=credential,
        logging_enable=False,  # Set to True for detailed HTTP logging
    )

    # Execute ingestion management workflow
    create_ingestion_sources(client, container_uris, managed_identity_object_id)
    ingestion_id = create_and_update_ingestion(client, collection_id, source_catalog_url)
    run_and_monitor_ingestion(client, collection_id, ingestion_id)
    manage_operations(client)


if __name__ == "__main__":
    main()
