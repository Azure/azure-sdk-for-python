# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: planetarycomputer_ingestion_management.py

DESCRIPTION:
    This sample demonstrates comprehensive ingestion management operations including:
    - Creating and managing ingestion sources (managed identity-based) - DEMONSTRATION ONLY
    - Creating or replacing sources with create_or_replace_source (idempotent)
    - Retrieving specific sources with get_source
    - Creating and updating ingestion definitions
    - Retrieving specific ingestions with get
    - Running ingestion jobs from public catalogs (NAIP)
    - Listing ingestion runs with list_runs
    - Monitoring ingestion status
    - Managing ingestion operations

USAGE:
    python planetarycomputer_ingestion_management.py

    Set the environment variable AZURE_PLANETARY_COMPUTER_ENDPOINT with your endpoint URL.
    Set the environment variable AZURE_COLLECTION_ID with your collection ID.
    
    Optional (for managed identity examples):
    Set the environment variable AZURE_INGESTION_CONTAINER_URI with your container URI.
    Set the environment variable AZURE_INGESTION_CATALOG_URL with your source catalog URL.
    Set the environment variable AZURE_MANAGED_IDENTITY_OBJECT_ID with your managed identity object ID.
    
    Optional (for SAS token examples):
    Set the environment variable AZURE_INGESTION_SAS_CONTAINER_URI with your SAS container URI.
    Set the environment variable AZURE_INGESTION_SAS_TOKEN with your SAS token.
"""

import os
import time
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.planetarycomputer.models import (
    ManagedIdentityConnection,
    ManagedIdentityIngestionSource,
    SharedAccessSignatureTokenConnection,
    SharedAccessSignatureTokenIngestionSource,
    Ingestion,
    IngestionType,
    OperationStatus,
)
import uuid

import logging

# Enable HTTP request/response logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)


def create_managed_identity_ingestion_sources(client: PlanetaryComputerClient, container_uri: str, managed_identity_object_id: str):
    """Create managed identity-based ingestion source."""

    # Clean up existing sources
    existing_sources = list(client.ingestion_management.list_sources())
    for source in existing_sources:
        client.ingestion_management.delete_source(id=source.id)
        logging.info(f"Deleted existing source: {source.id}")

    # Create connection info with managed identity
    connection_info = ManagedIdentityConnection(container_uri=container_uri, object_id=managed_identity_object_id)

    # Create ingestion source with unique ID
    source_id = str(uuid.uuid4())
    ingestion_source = ManagedIdentityIngestionSource(id=source_id, connection_info=connection_info)
    created_source = client.ingestion_management.create_source(ingestion_source=ingestion_source)
    logging.info(f"Created managed identity ingestion source: {created_source.id}")

    # List managed identities
    logging.info("Listing available managed identities:")
    managed_identities = client.ingestion_management.list_managed_identities()
    for identity in managed_identities:
        logging.info(f"  - Object ID: {identity.object_id}")
        logging.info(f"    Resource ID: {identity.resource_id}")


def create_or_replace_source(client: PlanetaryComputerClient, container_uri: str, managed_identity_object_id: str):
    """Create or replace an ingestion source (idempotent operation).
    
    This demonstrates using create_or_replace_source which is idempotent:
    - If the source doesn't exist, it creates it
    - If the source exists, it replaces it completely
    - Multiple calls with the same data produce the same result
    """
    source_id = "sample-managed-identity-source"
    
    # Create connection info with managed identity
    connection_info = ManagedIdentityConnection(
        container_uri=container_uri,
        object_id=managed_identity_object_id
    )
    
    # Create ingestion source
    ingestion_source = ManagedIdentityIngestionSource(
        id=source_id,
        connection_info=connection_info
    )
    
    logging.info(f"Creating or replacing ingestion source: {source_id}")
    
    # Create or replace the source (idempotent operation)
    created_source = client.ingestion_management.create_or_replace_source(
        id=source_id,
        ingestion_source=ingestion_source
    )
    
    logging.info(f"Source created/replaced successfully: {created_source.id}")
    
    # Demonstrate idempotency - calling again with same data
    time.sleep(1)
    
    logging.info("Calling create_or_replace_source again (demonstrating idempotency)...")
    replaced_source = client.ingestion_management.create_or_replace_source(
        id=source_id,
        ingestion_source=ingestion_source
    )
    
    logging.info("Source operation completed (idempotent)")
    
    return replaced_source.id


def get_source_by_id(client: PlanetaryComputerClient, source_id: str):
    """Retrieve a specific ingestion source by ID.
    
    This demonstrates using get_source to fetch a specific source directly
    instead of listing all sources.
    """
    logging.info(f"Retrieving ingestion source: {source_id}")
    
    try:
        source = client.ingestion_management.get_source(id=source_id)
        logging.info(f"Successfully retrieved source: {source.id}")
        return source
    except Exception as e:
        logging.error(f"Failed to retrieve source {source_id}: {str(e)}")
        return None


def create_github_naip_ingestion(client: PlanetaryComputerClient, collection_id: str, source_catalog_url: str):
    """Create, update, and run ingestion from NAIP public catalog on GitHub."""
    
    # Delete all existing ingestions
    logging.info("Deleting all existing ingestions...")
    existing_ingestions = list(client.ingestion_management.lists(collection_id=collection_id))
    for ingestion in existing_ingestions:
        client.ingestion_management.begin_delete(collection_id=collection_id, ingestion_id=ingestion.id, polling=True)
        logging.info(f"Deleted existing ingestion: {ingestion.id}")
    
    # Create ingestion definition
    ingestion_definition = Ingestion(
        import_type=IngestionType.STATIC_CATALOG,
        display_name="NAIP Ingestion",
        source_catalog_url=source_catalog_url,
        keep_original_assets=True,
        skip_existing_items=True,  # Skip items that already exist
    )

    # Create the ingestion
    logging.info("Creating ingestion for NAIP catalog...")
    ingestion_response = client.ingestion_management.create(
        collection_id=collection_id, definition=ingestion_definition
    )
    ingestion_id = ingestion_response.id
    logging.info(f"Created ingestion: {ingestion_id}")

    # Update the ingestion display name
    updated_definition = Ingestion(
        import_type=IngestionType.STATIC_CATALOG,
        display_name="NAIP Sample Dataset Ingestion",
    )

    ingestion = client.ingestion_management.update(
        collection_id=collection_id, ingestion_id=ingestion_id, definition=updated_definition
    )
    logging.info(f"Updated ingestion display name to: {updated_definition.display_name}")

    return ingestion_id


def get_ingestion_by_id(client: PlanetaryComputerClient, collection_id: str, ingestion_id: str):
    """Retrieve a specific ingestion by ID.
    
    This demonstrates using get to fetch a specific ingestion directly
    instead of listing all ingestions.
    """
    logging.info(f"Retrieving ingestion: {ingestion_id} from collection: {collection_id}")
    
    try:
        ingestion = client.ingestion_management.get(
            collection_id=collection_id,
            ingestion_id=ingestion_id
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


def list_ingestion_runs(client: PlanetaryComputerClient, collection_id: str, ingestion_id: str):
    """List all runs for a specific ingestion.
    
    This demonstrates using list_runs to get all execution runs for an ingestion,
    which is useful for monitoring ingestion history and troubleshooting.
    """
    logging.info(f"Listing runs for ingestion: {ingestion_id}")
    
    try:
        runs = list(client.ingestion_management.list_runs(
            collection_id=collection_id,
            ingestion_id=ingestion_id
        ))
        
        logging.info(f"Found {len(runs)} run(s) for ingestion {ingestion_id}")
        
        for run in runs:
            operation = run.operation
            logging.info(f"  Run ID: {run.id}")
            logging.info(f"    Status: {operation.status}")
            logging.info(f"    Items - Total: {operation.total_items}, "
                        f"Successful: {operation.total_successful_items}, "
                        f"Failed: {operation.total_failed_items}, "
                        f"Pending: {operation.total_pending_items}")
            
            if operation.status_history:
                for status_item in operation.status_history:
                    if status_item.error_code:
                        logging.info(f"    Error: {status_item.error_code} - {status_item.error_message}")
        
        return runs
    except Exception as e:
        logging.error(f"Failed to list runs for ingestion {ingestion_id}: {str(e)}")
        return []


def create_sas_token_ingestion_source(client: PlanetaryComputerClient, sas_container_uri: str, sas_token: str):
    """Create a SAS token ingestion source with example values."""
    logging.info("Creating SAS token ingestion source...")
    
    # Create connection info with SAS token (using fake/example values)
    sas_connection_info = SharedAccessSignatureTokenConnection(
        container_uri=sas_container_uri,
        shared_access_signature_token=sas_token
    )
    
    # Create SAS token ingestion source
    sas_source_id = str(uuid.uuid4())
    sas_ingestion_source = SharedAccessSignatureTokenIngestionSource(
        id=sas_source_id,
        connection_info=sas_connection_info
    )
    
    # Register the SAS token source
    created_sas_source = client.ingestion_management.create_source(
        ingestion_source=sas_ingestion_source
    )
    logging.info(f"Created SAS token ingestion source: {created_sas_source.id}")
    return created_sas_source.id


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
    collection_id = os.environ.get("PLANETARYCOMPUTER_COLLECTION_ID", "naip-sample-datasets")

    # Get optional ingestion-specific configuration (for examples)
    container_uri = os.environ.get("PLANETARYCOMPUTER_INGESTION_CONTAINER_URI", "")
    source_catalog_url = os.environ.get("PLANETARYCOMPUTER_INGESTION_CATALOG_URL", "https://raw.githubusercontent.com/aloverro/mpcpro-sample-datasets/main/datasets/planetary_computer/naip/catalog.json")
    managed_identity_object_id = os.environ.get("AZURE_MANAGED_IDENTITY_OBJECT_ID", "")
    sas_container_uri = os.environ.get("PLANETARYCOMPUTER_INGESTION_SAS_CONTAINER_URI", "")
    sas_token = os.environ.get("PLANETARYCOMPUTER_INGESTION_SAS_TOKEN", "")

    if not endpoint:
        raise ValueError("AZURE_PLANETARY_COMPUTER_ENDPOINT environment variable must be set")

    logging.info(f"Connected to: {endpoint}")
    logging.info(f"Collection ID: {collection_id}\n")

    # Create client
    credential = DefaultAzureCredential()
    client = PlanetaryComputerClient(
        endpoint=endpoint,
        credential=credential,
        logging_enable=False,  # Set to True for detailed HTTP logging
    )

    # Execute ingestion management workflow
    # 1. Create managed identity and SAS token ingestion sources
    create_managed_identity_ingestion_sources(client, container_uri, managed_identity_object_id)
    create_sas_token_ingestion_source(client, sas_container_uri, sas_token)
    
    # 2. Demonstrate advanced source operations (idempotent)
    source_id = create_or_replace_source(client, container_uri, managed_identity_object_id)
    get_source_by_id(client, source_id)

    # 3. Run actual NAIP ingestion hosted on GitHub
    naip_ingestion_id = create_github_naip_ingestion(client, collection_id, source_catalog_url)
    
    # 4. Demonstrate advanced ingestion operations
    get_ingestion_by_id(client, collection_id, naip_ingestion_id)
    
    # 5. Monitor the NAIP ingestion
    run_and_monitor_ingestion(client, collection_id, naip_ingestion_id)
    
    # 6. List all runs for the ingestion
    list_ingestion_runs(client, collection_id, naip_ingestion_id)
    
    # 7. Manage operations
    manage_operations(client)


if __name__ == "__main__":
    main()
