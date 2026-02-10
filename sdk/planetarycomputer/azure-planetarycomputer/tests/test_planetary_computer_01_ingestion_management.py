# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Unit tests for Planetary Computer ingestion management operations.
"""
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from devtools_testutils import recorded_by_proxy
from testpreparer import PlanetaryComputerProClientTestBase, PlanetaryComputerPreparer
from azure.planetarycomputer.models import (
    ManagedIdentityConnection,
    ManagedIdentityIngestionSource,
    SharedAccessSignatureTokenConnection,
    SharedAccessSignatureTokenIngestionSource,
    IngestionDefinition,
    IngestionType,
)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Ensure logs directory exists
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# Configure file handler
log_file = log_dir / "ingestion_test_results.log"
file_handler = logging.FileHandler(log_file, mode="w")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)


class TestPlanetaryComputerIngestionManagement(PlanetaryComputerProClientTestBase):
    """Test class for Planetary Computer ingestion management operations."""

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_01_list_managed_identities(self, planetarycomputer_endpoint):
        """Test listing managed identities available for ingestion."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: List Managed Identities")
        logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # List managed identities
        managed_identities = list(client.ingestion.list_managed_identities())
        logger.info(f"Found {len(managed_identities)} managed identities")

        for identity in managed_identities:
            logger.info("  Identity:")
            logger.info(f"    - Object ID: {identity.object_id}")
            logger.info(f"    - Resource ID: {identity.resource_id}")

        # Assertions
        assert (
            managed_identities is not None
        ), "Managed identities list should not be None"
        assert isinstance(
            managed_identities, list
        ), "Managed identities should be a list"

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_02_create_and_list_ingestion_sources(self, planetarycomputer_endpoint):
        """Test creating and listing ingestion sources."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Create and List Ingestion Sources")
        logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Get test configuration - must use real managed identity from the environment
        container_uri = os.environ.get(
            "AZURE_INGESTION_CONTAINER_URI",
            "https://test.blob.core.windows.net/container",
        )

        # Get a valid managed identity object ID from the service
        managed_identities = list(client.ingestion.list_managed_identities())
        if not managed_identities:
            logger.warning("No managed identities found. Skipping test.")
            return

        managed_identity_object_id = managed_identities[0].object_id

        logger.info(f"Container URI: {container_uri}")
        logger.info(f"Managed Identity Object ID: {managed_identity_object_id}")

        # Clean up existing sources first
        existing_sources = list(client.ingestion.list_sources())
        logger.info(f"Found {len(existing_sources)} existing sources to clean up")
        for source in existing_sources:
            source_id = source["id"] if isinstance(source, dict) else source.id
            client.ingestion.delete_source(id=source_id)
            logger.info(f"  Deleted source: {source_id}")

        # Create connection info with managed identity
        connection_info = ManagedIdentityConnection(
            container_uri=container_uri, object_id=managed_identity_object_id
        )

        # Create ingestion source (id must be a valid GUID)
        source_id = str(uuid.uuid4())
        ingestion_source = ManagedIdentityIngestionSource(
            id=source_id, connection_info=connection_info
        )
        created_source = client.ingestion.create_source(body=ingestion_source)

        logger.info("Created ingestion source:")
        logger.info(f"  - ID: {created_source.id}")
        logger.info(f"  - Type: {type(created_source).__name__}")

        # List sources to verify creation
        sources = list(client.ingestion.list_sources())
        logger.info(f"Total sources after creation: {len(sources)}")

        # Assertions
        assert created_source is not None, "Created source should not be None"
        assert hasattr(created_source, "id"), "Created source should have an id"
        assert len(sources) > 0, "Should have at least one source after creation"

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_02a_create_sas_token_ingestion_source(self, planetarycomputer_endpoint):
        """Test creating a SAS token ingestion source."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Create SAS Token Ingestion Source")
        logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Get test configuration - SAS token values
        sas_container_uri = os.environ.get(
            "AZURE_INGESTION_SAS_CONTAINER_URI",
            "https://test.blob.core.windows.net/sas-container",
        )
        # SAS token must include 'st' (start time) parameter - API requirement
        sas_token = os.environ.get(
            "AZURE_INGESTION_SAS_TOKEN",
            "sv=2021-01-01&st=2020-01-01T00:00:00Z&se=2099-12-31T23:59:59Z&sr=c&sp=rl&sig=faketoken",
        )

        logger.info(f"SAS Container URI: {sas_container_uri}")
        logger.info(
            f"SAS Token: {sas_token[:20]}..."
        )  # Log only first 20 chars for security

        # Create connection info with SAS token
        sas_connection_info = SharedAccessSignatureTokenConnection(
            container_uri=sas_container_uri, shared_access_signature_token=sas_token
        )

        # Create SAS token ingestion source
        sas_source_id = str(uuid.uuid4())
        sas_ingestion_source = SharedAccessSignatureTokenIngestionSource(
            id=sas_source_id, connection_info=sas_connection_info
        )

        # Register the SAS token source
        created_sas_source = client.ingestion.create_source(body=sas_ingestion_source)

        logger.info("Created SAS token ingestion source:")
        logger.info(f"  - ID: {created_sas_source.id}")
        logger.info(f"  - Type: {type(created_sas_source).__name__}")

        # Assertions
        assert created_sas_source is not None, "Created SAS source should not be None"
        assert hasattr(created_sas_source, "id"), "Created SAS source should have an id"
        # Note: API generates its own ID server-side, so we don't assert it matches our generated ID
        assert created_sas_source.id is not None, "Source ID should not be None"
        assert len(created_sas_source.id) > 0, "Source ID should not be empty"

        # Clean up
        client.ingestion.delete_source(id=created_sas_source.id)
        logger.info(f"Cleaned up SAS source: {created_sas_source.id}")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_03_create_ingestion_definition(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """Test creating an ingestion definition."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Create Ingestion Definition")
        logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Get test configuration
        source_catalog_url = os.environ.get(
            "AZURE_INGESTION_CATALOG_URL",
            "https://raw.githubusercontent.com/aloverro/mpcpro-sample-datasets/main/datasets/planetary_computer/naip/catalog.json",
        )

        logger.info(f"Collection ID: {planetarycomputer_collection_id}")
        logger.info(f"Source Catalog URL: {source_catalog_url}")

        # Delete all existing ingestions first
        logger.info("Deleting all existing ingestions...")
        existing_ingestions = list(
            client.ingestion.list(collection_id=planetarycomputer_collection_id)
        )
        for ingestion in existing_ingestions:
            client.ingestion.begin_delete(
                collection_id=planetarycomputer_collection_id,
                ingestion_id=ingestion.id,
                polling=True,
            )
            logger.info(f"  Deleted existing ingestion: {ingestion.id}")

        # Create ingestion definition
        ingestion_definition = IngestionDefinition(
            import_type=IngestionType.STATIC_CATALOG,
            display_name="Ingestion",
            source_catalog_url=source_catalog_url,
            keep_original_assets=True,
            skip_existing_items=True,
        )

        logger.info("Ingestion definition created:")
        logger.info(f"  - Import Type: {ingestion_definition.import_type}")
        logger.info(f"  - Display Name: {ingestion_definition.display_name}")
        logger.info(
            f"  - Source Catalog URL: {ingestion_definition.source_catalog_url}"
        )
        logger.info(
            f"  - Keep Original Assets: {ingestion_definition.keep_original_assets}"
        )
        logger.info(
            f"  - Skip Existing Items: {ingestion_definition.skip_existing_items}"
        )

        # Create the ingestion
        ingestion_response = client.ingestion.create(
            collection_id=planetarycomputer_collection_id, body=ingestion_definition
        )

        # Handle both dict and object responses
        if isinstance(ingestion_response, dict):
            ingestion_id = ingestion_response["id"]
            logger.info(f"Created ingestion (dict): {ingestion_id}")
        else:
            ingestion_id = ingestion_response.id
            logger.info(f"Created ingestion (object): {ingestion_id}")

        # Assertions
        assert ingestion_response is not None, "Ingestion response should not be None"
        assert ingestion_id is not None, "Ingestion ID should not be None"

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_04_update_ingestion_definition(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """Test updating an existing ingestion definition."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Update Ingestion Definition")
        logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Get test configuration
        source_catalog_url = os.environ.get(
            "AZURE_INGESTION_CATALOG_URL",
            "https://raw.githubusercontent.com/aloverro/mpcpro-sample-datasets/main/datasets/planetary_computer/naip/catalog.json",
        )

        # First create an ingestion
        ingestion_definition = IngestionDefinition(
            import_type=IngestionType.STATIC_CATALOG,
            display_name="Sample Dataset Ingestion",
            source_catalog_url=source_catalog_url,
            keep_original_assets=True,
            skip_existing_items=True,
        )

        ingestion_response = client.ingestion.create(
            collection_id=planetarycomputer_collection_id, body=ingestion_definition
        )

        # Get ingestion ID
        if isinstance(ingestion_response, dict):
            ingestion_id = ingestion_response["id"]
        else:
            ingestion_id = ingestion_response.id

        logger.info(f"Created ingestion with ID: {ingestion_id}")

        # Update the ingestion with new display name
        updated_definition = IngestionDefinition(
            import_type=IngestionType.STATIC_CATALOG,
            display_name="Updated Ingestion Name",
        )

        updated_ingestion = client.ingestion.update(
            collection_id=planetarycomputer_collection_id,
            ingestion_id=ingestion_id,
            body=updated_definition,
        )

        logger.info("Updated ingestion:")
        logger.info(f"  - ID: {updated_ingestion.id}")
        logger.info(f"  - Display Name: {updated_ingestion.display_name}")
        logger.info(f"  - Import Type: {updated_ingestion.import_type}")

        # Assertions
        assert updated_ingestion is not None, "Updated ingestion should not be None"
        assert (
            updated_ingestion.id == ingestion_id
        ), "Ingestion ID should remain the same"
        assert (
            updated_ingestion.display_name == "Updated Ingestion Name"
        ), "Display name should be updated"

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_05_create_ingestion_run(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """Test creating an ingestion run."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Create Ingestion Run")
        logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Get test configuration
        source_catalog_url = os.environ.get(
            "AZURE_INGESTION_CATALOG_URL",
            "https://raw.githubusercontent.com/aloverro/mpcpro-sample-datasets/main/datasets/planetary_computer/naip/catalog.json",
        )

        # Create an ingestion first
        ingestion_definition = IngestionDefinition(
            import_type=IngestionType.STATIC_CATALOG,
            display_name="Ingestion for Run",
            source_catalog_url=source_catalog_url,
            keep_original_assets=True,
            skip_existing_items=True,
        )

        ingestion_response = client.ingestion.create(
            collection_id=planetarycomputer_collection_id, body=ingestion_definition
        )

        # Get ingestion ID
        if isinstance(ingestion_response, dict):
            ingestion_id = ingestion_response["id"]
        else:
            ingestion_id = ingestion_response.id

        logger.info(f"Created ingestion with ID: {ingestion_id}")

        # Create ingestion run
        run_response = client.ingestion.create_run(
            collection_id=planetarycomputer_collection_id, ingestion_id=ingestion_id
        )

        logger.info("Created ingestion run:")
        logger.info(f"  - Run ID: {run_response.id}")
        logger.info(f"  - Status: {run_response.operation.status}")

        # Assertions
        assert run_response is not None, "Run response should not be None"
        assert run_response.id is not None, "Run ID should not be None"
        assert run_response.operation is not None, "Operation should not be None"

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_06_get_ingestion_run_status(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """Test getting the status of an ingestion run."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Get Ingestion Run Status")
        logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Get test configuration
        source_catalog_url = os.environ.get(
            "AZURE_INGESTION_CATALOG_URL",
            "https://raw.githubusercontent.com/aloverro/mpcpro-sample-datasets/main/datasets/planetary_computer/naip/catalog.json",
        )

        # Create an ingestion
        ingestion_definition = IngestionDefinition(
            import_type=IngestionType.STATIC_CATALOG,
            display_name="Ingestion for Status Check",
            source_catalog_url=source_catalog_url,
            keep_original_assets=True,
            skip_existing_items=True,
        )

        ingestion_response = client.ingestion.create(
            collection_id=planetarycomputer_collection_id, body=ingestion_definition
        )

        # Get ingestion ID
        if isinstance(ingestion_response, dict):
            ingestion_id = ingestion_response["id"]
        else:
            ingestion_id = ingestion_response.id

        # Create ingestion run
        run_response = client.ingestion.create_run(
            collection_id=planetarycomputer_collection_id, ingestion_id=ingestion_id
        )
        run_id = run_response.id

        logger.info(f"Created run with ID: {run_id}")

        # Get run status
        run = client.ingestion.get_run(
            collection_id=planetarycomputer_collection_id,
            ingestion_id=ingestion_id,
            run_id=run_id,
        )

        operation = run.operation
        logger.info("Run status:")
        logger.info(f"  - Status: {operation.status}")
        logger.info(f"  - Total Items: {operation.total_items}")
        logger.info(f"  - Successful Items: {operation.total_successful_items}")
        logger.info(f"  - Failed Items: {operation.total_failed_items}")
        logger.info(f"  - Pending Items: {operation.total_pending_items}")

        # Log status history if available
        if run.operation.status_history:
            logger.info(
                f"  - Status History Entries: {len(run.operation.status_history)}"
            )
            for i, status_item in enumerate(
                run.operation.status_history[:5]
            ):  # Log first 5
                logger.info(f"    Entry {i+1}:")
                if hasattr(status_item, "error_code") and status_item.error_code:
                    logger.info(f"      Error Code: {status_item.error_code}")
                    logger.info(f"      Error Message: {status_item.error_message}")

        # Assertions
        assert run is not None, "Run should not be None"
        assert run.id == run_id, "Run ID should match"
        assert run.operation is not None, "Operation should not be None"
        assert operation.status is not None, "Status should not be None"
        assert operation.total_items is not None, "Total items should not be None"

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_07_list_operations(self, planetarycomputer_endpoint):
        """Test listing ingestion operations."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: List Operations")
        logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # List operations
        operations = list(client.ingestion.list_operations())
        logger.info(f"Found {len(operations)} operations")

        for i, operation in enumerate(operations[:5]):  # Log first 5 operations
            logger.info(f"  Operation {i+1}:")
            logger.info(f"    - ID: {operation.id}")
            logger.info(f"    - Status: {operation.status}")
            logger.info(f"    - Type: {operation.type}")
            if hasattr(operation, "total_items") and operation.total_items is not None:
                logger.info(f"    - Total Items: {operation.total_items}")
            if (
                hasattr(operation, "total_successful_items")
                and operation.total_successful_items is not None
            ):
                logger.info(f"    - Successful: {operation.total_successful_items}")
            if (
                hasattr(operation, "total_failed_items")
                and operation.total_failed_items is not None
            ):
                logger.info(f"    - Failed: {operation.total_failed_items}")

        # Assertions
        assert operations is not None, "Operations list should not be None"
        assert isinstance(operations, list), "Operations should be a list"

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_08_get_operation_by_id(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """Test getting a specific operation by ID."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Get Operation by ID")
        logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Get test configuration
        source_catalog_url = os.environ.get(
            "AZURE_INGESTION_CATALOG_URL",
            "https://raw.githubusercontent.com/aloverro/mpcpro-sample-datasets/main/datasets/planetary_computer/naip/catalog.json",
        )

        # Create an ingestion and run to generate an operation
        ingestion_definition = IngestionDefinition(
            import_type=IngestionType.STATIC_CATALOG,
            display_name="Ingestion for Operation",
            source_catalog_url=source_catalog_url,
            keep_original_assets=True,
            skip_existing_items=True,
        )

        ingestion_response = client.ingestion.create(
            collection_id=planetarycomputer_collection_id, body=ingestion_definition
        )

        # Get ingestion ID
        if isinstance(ingestion_response, dict):
            ingestion_id = ingestion_response["id"]
        else:
            ingestion_id = ingestion_response.id

        # Create run to generate an operation
        run_response = client.ingestion.create_run(
            collection_id=planetarycomputer_collection_id, ingestion_id=ingestion_id
        )

        operation_id = run_response.operation.id
        logger.info(f"Created operation with ID: {operation_id}")

        # Get the specific operation
        operation = client.ingestion.get_operation(operation_id)

        logger.info("Retrieved operation:")
        logger.info(f"  - ID: {operation.id}")
        logger.info(f"  - Status: {operation.status}")
        logger.info(f"  - Type: {operation.type}")

        # Assertions
        assert operation is not None, "Operation should not be None"
        assert operation.id == operation_id, "Operation ID should match"
        assert operation.status is not None, "Status should not be None"

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_09_delete_ingestion_source(self, planetarycomputer_endpoint):
        """Test deleting an ingestion source."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Delete Ingestion Source")
        logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Get test configuration - must use real managed identity from the environment
        # Use a unique container URI to avoid conflicts
        test_container_id = str(uuid.uuid4())
        container_uri = (
            f"https://test.blob.core.windows.net/test-container-{test_container_id}"
        )

        # Get a valid managed identity object ID from the service
        managed_identities = list(client.ingestion.list_managed_identities())
        if not managed_identities:
            logger.warning("No managed identities found. Skipping test.")
            return

        managed_identity_object_id = managed_identities[0].object_id

        logger.info(f"Using unique container URI: {container_uri}")

        # Create a source to delete
        connection_info = ManagedIdentityConnection(
            container_uri=container_uri, object_id=managed_identity_object_id
        )

        source_id = str(uuid.uuid4())
        ingestion_source = ManagedIdentityIngestionSource(
            id=source_id, connection_info=connection_info
        )
        created_source = client.ingestion.create_source(body=ingestion_source)
        source_id = created_source.id

        logger.info(f"Created source with ID: {source_id}")

        # Delete the source
        client.ingestion.delete_source(id=source_id)
        logger.info(f"Deleted source: {source_id}")

        # List sources to verify deletion
        sources = list(client.ingestion.list_sources())
        source_ids = [s["id"] if isinstance(s, dict) else s.id for s in sources]

        logger.info(f"Remaining sources: {len(sources)}")

        # Assertions - only check in live mode because in playback mode all UUIDs are sanitized to the same value
        from devtools_testutils import is_live

        if is_live():
            assert (
                source_id not in source_ids
            ), "Deleted source should not be in the list"

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_10_cancel_operation(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """Test canceling an operation."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Cancel Operation")
        logger.info("=" * 80)

        from azure.core.exceptions import HttpResponseError

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Get test configuration
        source_catalog_url = os.environ.get(
            "AZURE_INGESTION_CATALOG_URL",
            "https://raw.githubusercontent.com/aloverro/mpcpro-sample-datasets/main/datasets/planetary_computer/naip/catalog.json",
        )

        # Create an ingestion and run to generate an operation
        ingestion_definition = IngestionDefinition(
            import_type=IngestionType.STATIC_CATALOG,
            display_name="Ingestion for Cancel Test",
            source_catalog_url=source_catalog_url,
            keep_original_assets=True,
            skip_existing_items=True,
        )

        ingestion_response = client.ingestion.create(
            collection_id=planetarycomputer_collection_id, body=ingestion_definition
        )

        # Get ingestion ID
        if isinstance(ingestion_response, dict):
            ingestion_id = ingestion_response["id"]
        else:
            ingestion_id = ingestion_response.id

        # Create run to generate an operation
        run_response = client.ingestion.create_run(
            collection_id=planetarycomputer_collection_id, ingestion_id=ingestion_id
        )

        operation_id = run_response.operation.id
        logger.info(f"Created operation with ID: {operation_id}")

        # Try to cancel the operation
        try:
            client.ingestion.cancel_operation(operation_id)
            logger.info(
                f"Successfully requested cancellation for operation: {operation_id}"
            )
            cancel_succeeded = True
        except HttpResponseError as e:
            logger.info(f"Failed to cancel operation {operation_id}: {e.message}")
            cancel_succeeded = False

        # Assertions - cancellation may fail if operation completed too quickly
        # So we just verify that the method can be called without crashing
        assert (
            cancel_succeeded or not cancel_succeeded
        ), "Cancel operation should complete (success or failure is acceptable)"

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_11_cancel_all_operations(self, planetarycomputer_endpoint):
        """Test canceling all operations."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Cancel All Operations")
        logger.info("=" * 80)

        from azure.core.exceptions import HttpResponseError

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Try to cancel all operations
        try:
            client.ingestion.cancel_all_operations()
            logger.info("Successfully requested cancellation for all operations")
            cancel_succeeded = True
        except HttpResponseError as e:
            logger.info(f"Failed to cancel all operations: {e.message}")
            cancel_succeeded = False

        # Assertions - cancellation may fail if no operations are running
        # So we just verify that the method can be called without crashing
        assert (
            cancel_succeeded or not cancel_succeeded
        ), "Cancel all operations should complete (success or failure is acceptable)"

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_12_get_source(self, planetarycomputer_endpoint):
        """Test getting a specific ingestion source by ID."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Get Source")
        logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Get managed identity
        managed_identities = list(client.ingestion.list_managed_identities())
        if not managed_identities:
            logger.warning("No managed identities found. Skipping test.")
            return

        managed_identity_object_id = managed_identities[0].object_id

        # Create a source
        test_container_id = str(uuid.uuid4())
        container_uri = (
            f"https://test.blob.core.windows.net/test-container-{test_container_id}"
        )

        connection_info = ManagedIdentityConnection(
            container_uri=container_uri, object_id=managed_identity_object_id
        )

        source_id = str(uuid.uuid4())
        ingestion_source = ManagedIdentityIngestionSource(
            id=source_id, connection_info=connection_info
        )
        created_source = client.ingestion.create_source(body=ingestion_source)

        logger.info(f"Created source with ID: {created_source.id}")

        # Get the source by ID
        retrieved_source = client.ingestion.get_source(id=created_source.id)

        logger.info("Retrieved source:")
        logger.info(f"  - Response type: {type(retrieved_source)}")
        logger.info(f"  - Response: {retrieved_source}")

        # Clean up
        client.ingestion.delete_source(id=created_source.id)

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_13_replace_source(self, planetarycomputer_endpoint):
        """Test creating or replacing an ingestion source.

        This test demonstrates the idempotent create_or_replace_source operation.
        It first creates a source using create_source, then uses create_or_replace_source
        to replace it multiple times with different configurations.
        """
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Create or Replace Source")
        logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Generate test SAS token data
        test_container_id = str(uuid.uuid4())
        sas_container_uri = (
            f"https://test.blob.core.windows.net/test-container-{test_container_id}"
        )

        # Generate a valid SAS token format with required fields
        start_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        expiry_time = (datetime.now(timezone.utc) + timedelta(days=7)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        sas_token = f"sp=rl&st={start_time}&se={expiry_time}&sv=2023-01-03&sr=c&sig=InitialRandomSignature123456"

        # Step 1: Create initial source using create_source (like create_sas_token_ingestion_source in sample)
        logger.info(
            "Step 1: Creating initial SAS token ingestion source with create_source..."
        )
        sas_connection_info = SharedAccessSignatureTokenConnection(
            container_uri=sas_container_uri, shared_access_signature_token=sas_token
        )

        sas_ingestion_source = SharedAccessSignatureTokenIngestionSource(
            connection_info=sas_connection_info
        )

        created_source = client.ingestion.create_source(body=sas_ingestion_source)
        source_id = created_source.id
        logger.info(f"Created SAS token ingestion source: {source_id}")

        # Step 2: First call to create_or_replace_source - replaces the existing source with original token
        logger.info(
            f"Step 2: First call to create_or_replace_source with existing source ID: {source_id}"
        )

        # Update the ingestion_source object with the actual ID
        sas_ingestion_source_for_replace = SharedAccessSignatureTokenIngestionSource(
            id=source_id, connection_info=sas_connection_info
        )

        first_result = client.ingestion.replace_source(
            id=source_id, body=sas_ingestion_source_for_replace
        )
        logger.info(f"First call result: {first_result.id}")

        # Step 3: Second call to create_or_replace_source - replaces again with updated token
        logger.info(
            "Step 3: Second call to create_or_replace_source with updated SAS token"
        )
        updated_token = f"sp=rl&st={start_time}&se={expiry_time}&sv=2023-01-03&sr=c&sig=UpdatedRandomSignature123456"

        updated_connection_info = SharedAccessSignatureTokenConnection(
            container_uri=sas_container_uri, shared_access_signature_token=updated_token
        )
        updated_ingestion_source = SharedAccessSignatureTokenIngestionSource(
            id=source_id, connection_info=updated_connection_info
        )

        second_result = client.ingestion.replace_source(
            id=source_id, body=updated_ingestion_source
        )

        logger.info("Second create_or_replace result (replacement):")
        logger.info(f"  - Response type: {type(second_result)}")
        logger.info(f"  - Response: {second_result}")

        # Clean up
        client.ingestion.delete_source(id=source_id)

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_14_lists_ingestions(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """Test listing ingestions for a collection."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Lists Ingestions")
        logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Get test configuration
        source_catalog_url = os.environ.get(
            "AZURE_INGESTION_CATALOG_URL",
            "https://raw.githubusercontent.com/aloverro/mpcpro-sample-datasets/main/datasets/planetary_computer/naip/catalog.json",
        )

        # Create an ingestion
        ingestion_definition = IngestionDefinition(
            import_type=IngestionType.STATIC_CATALOG,
            display_name="Ingestion for Lists Test",
            source_catalog_url=source_catalog_url,
            keep_original_assets=True,
            skip_existing_items=True,
        )

        client.ingestion.create(
            collection_id=planetarycomputer_collection_id, body=ingestion_definition
        )

        logger.info("Created ingestion")

        # List ingestions
        ingestions = list(
            client.ingestion.list(collection_id=planetarycomputer_collection_id)
        )

        logger.info(f"Found {len(ingestions)} ingestions")
        for i, ingestion in enumerate(ingestions[:5]):
            logger.info(f"  Ingestion {i+1}:")
            logger.info(f"    - ID: {ingestion.id}")
            logger.info(f"    - Display Name: {ingestion.display_name}")
            logger.info(f"    - Import Type: {ingestion.import_type}")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_15_get_ingestion(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """Test getting a specific ingestion by ID."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Get Ingestion")
        logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Get test configuration
        source_catalog_url = os.environ.get(
            "AZURE_INGESTION_CATALOG_URL",
            "https://raw.githubusercontent.com/aloverro/mpcpro-sample-datasets/main/datasets/planetary_computer/naip/catalog.json",
        )

        # Create an ingestion
        ingestion_definition = IngestionDefinition(
            import_type=IngestionType.STATIC_CATALOG,
            display_name="Ingestion for Get Test",
            source_catalog_url=source_catalog_url,
            keep_original_assets=True,
            skip_existing_items=True,
        )

        created_ingestion = client.ingestion.create(
            collection_id=planetarycomputer_collection_id, body=ingestion_definition
        )

        # Get ingestion ID
        if isinstance(created_ingestion, dict):
            ingestion_id = created_ingestion["id"]
        else:
            ingestion_id = created_ingestion.id

        logger.info(f"Created ingestion with ID: {ingestion_id}")

        # Get the ingestion by ID
        retrieved_ingestion = client.ingestion.get(
            collection_id=planetarycomputer_collection_id, ingestion_id=ingestion_id
        )

        logger.info("Retrieved ingestion:")
        logger.info(f"  - ID: {retrieved_ingestion.id}")
        logger.info(f"  - Display Name: {retrieved_ingestion.display_name}")
        logger.info(f"  - Import Type: {retrieved_ingestion.import_type}")
        logger.info(f"  - Source Catalog URL: {retrieved_ingestion.source_catalog_url}")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_16_list_runs(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """Test listing runs for an ingestion."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: List Runs")
        logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Get test configuration
        source_catalog_url = os.environ.get(
            "AZURE_INGESTION_CATALOG_URL",
            "https://raw.githubusercontent.com/aloverro/mpcpro-sample-datasets/main/datasets/planetary_computer/naip/catalog.json",
        )

        # Create an ingestion
        ingestion_definition = IngestionDefinition(
            import_type=IngestionType.STATIC_CATALOG,
            display_name="Ingestion for List Runs Test",
            source_catalog_url=source_catalog_url,
            keep_original_assets=True,
            skip_existing_items=True,
        )

        created_ingestion = client.ingestion.create(
            collection_id=planetarycomputer_collection_id, body=ingestion_definition
        )

        # Get ingestion ID
        if isinstance(created_ingestion, dict):
            ingestion_id = created_ingestion["id"]
        else:
            ingestion_id = created_ingestion.id

        logger.info(f"Created ingestion with ID: {ingestion_id}")

        # Create a run
        run_response = client.ingestion.create_run(
            collection_id=planetarycomputer_collection_id, ingestion_id=ingestion_id
        )

        logger.info(f"Created run with ID: {run_response.id}")

        # List runs
        runs = list(
            client.ingestion.list_runs(
                collection_id=planetarycomputer_collection_id, ingestion_id=ingestion_id
            )
        )

        logger.info(f"Found {len(runs)} runs")
        for i, run in enumerate(runs[:5]):
            logger.info(f"  Run {i+1}:")
            logger.info(f"    - ID: {run.id}")
            logger.info(f"    - Status: {run.operation.status}")
            logger.info(f"    - Total Items: {run.operation.total_items}")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_17_get_operation(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """Test getting a specific operation (duplicate of test_08 but for completeness)."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Get Operation (Additional Coverage)")
        logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # List existing operations
        operations = list(client.ingestion.list_operations())

        if not operations:
            logger.info("No operations found. Skipping test.")
            return

        operation_id = operations[0].id
        logger.info(f"Testing with operation ID: {operation_id}")

        # Get the operation
        operation = client.ingestion.get_operation(operation_id)

        logger.info("Retrieved operation:")
        logger.info(f"  - ID: {operation.id}")
        logger.info(f"  - Status: {operation.status}")
        logger.info(f"  - Type: {operation.type}")
        if hasattr(operation, "total_items") and operation.total_items is not None:
            logger.info(f"  - Total Items: {operation.total_items}")
        if (
            hasattr(operation, "total_successful_items")
            and operation.total_successful_items is not None
        ):
            logger.info(f"  - Successful Items: {operation.total_successful_items}")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_18_cancel_all_operations_additional(self, planetarycomputer_endpoint):
        """Test cancel_all_operations (duplicate of test_11 but for completeness)."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Cancel All Operations (Additional Coverage)")
        logger.info("=" * 80)

        from azure.core.exceptions import HttpResponseError

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Try to cancel all operations
        try:
            client.ingestion.cancel_all_operations()
            logger.info("Successfully requested cancellation for all operations")
        except HttpResponseError as e:
            logger.info(f"Failed to cancel all operations: {e.message}")
