# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_create_analyzer_with_labels.py

DESCRIPTION:
    These tests validate the sample_create_analyzer_with_labels.py sample code.
    This sample demonstrates the API pattern for creating a custom analyzer with labeled training
    data from Azure Blob Storage.

USAGE:
    pytest test_sample_create_analyzer_with_labels.py
"""

import os
import pytest
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from dotenv import load_dotenv
from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import recorded_by_proxy, is_live
from conftest import SANITIZED_CONTAINER_SAS_URL
from testpreparer import ContentUnderstandingPreparer, ContentUnderstandingClientTestBase
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentFieldDefinition,
    ContentFieldSchema,
    LabeledDataKnowledgeSource,
)

load_dotenv()


def _get_training_data_sas_url() -> str:
    """Get a SAS URL pointing to a blob container with labeled training data.

    The test only needs the URL — the CU service reads blobs server-side.
    Training data is assumed to already exist in the container (upload via
    the sample or manually beforehand). In playback mode the sanitized URL
    placeholder is sufficient since the test proxy replays recorded responses.

    Must be called at module load time (before the test proxy patches transports),
    otherwise Azure Storage SDK calls get routed through the proxy and hang.
    """
    # Option A: Pre-configured SAS URL
    sas_url = os.getenv("CONTENTUNDERSTANDING_TRAINING_DATA_SAS_URL")
    if sas_url:
        return sas_url

    # Option B: Generate User Delegation SAS from storage account + container
    storage_account = os.getenv("CONTENTUNDERSTANDING_TRAINING_DATA_STORAGE_ACCOUNT")
    container = os.getenv("CONTENTUNDERSTANDING_TRAINING_DATA_CONTAINER")
    if storage_account and container:
        from azure.identity import DefaultAzureCredential
        from azure.storage.blob import BlobServiceClient, ContainerSasPermissions, generate_container_sas

        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(
            account_url=f"https://{storage_account}.blob.core.windows.net",
            credential=credential,
        )
        user_delegation_key = blob_service_client.get_user_delegation_key(
            key_start_time=datetime.now(timezone.utc),
            key_expiry_time=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        sas_token = generate_container_sas(
            account_name=storage_account,
            container_name=container,
            user_delegation_key=user_delegation_key,
            permission=ContainerSasPermissions(read=True, list=True),
            expiry=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        return f"https://{storage_account}.blob.core.windows.net/{container}?{sas_token}"

    # Fallback for playback mode - use sanitized URL matching conftest.py sanitizer output
    return SANITIZED_CONTAINER_SAS_URL


# Resolve the SAS URL eagerly at module load time, before the test proxy patches transports.
# If resolved inside the test method, Azure Storage SDK calls would be routed through the
# test proxy and hang during record/playback.
_TRAINING_DATA_SAS_URL = _get_training_data_sas_url()


class TestSampleCreateAnalyzerWithLabels(ContentUnderstandingClientTestBase):
    """Tests for sample_create_analyzer_with_labels.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_create_analyzer_with_labels(self, contentunderstanding_endpoint: str, **kwargs) -> Dict[str, str]:
        """Test creating a custom analyzer with labeled training data.

        This test validates:
        1. Receipt field schema definition (MerchantName, Items, TotalPrice)
        2. LabeledDataKnowledgeSource creation
        3. Analyzer creation with knowledge sources
        4. Analyzer cleanup

        16_CreateAnalyzerWithLabels.CreateAnalyzerWithLabels()
        """
        # Get variables from test proxy (recorded values in playback, empty dict in recording)
        variables = kwargs.pop("variables", {})

        client = self.create_client(endpoint=contentunderstanding_endpoint)

        # Generate a unique analyzer ID
        default_analyzer_id = f"test_receipt_analyzer_{uuid.uuid4().hex[:16]}"
        analyzer_id = variables.setdefault("createAnalyzerWithLabelsId", default_analyzer_id)
        assert analyzer_id and analyzer_id.strip(), "Analyzer ID should not be empty"
        print(f"[PASS] Analyzer ID generated: {analyzer_id}")

        # Step 1: Build the receipt field schema
        item_definition = ContentFieldDefinition(
            type="object",
            method="extract",
            description="Individual item details",
            properties={
                "Quantity": ContentFieldDefinition(
                    type="string",
                    method="extract",
                    description="Quantity of the item",
                ),
                "Name": ContentFieldDefinition(
                    type="string",
                    method="extract",
                    description="Name of the item",
                ),
                "Price": ContentFieldDefinition(
                    type="string",
                    method="extract",
                    description="Price of the item",
                ),
            },
        )

        field_schema = ContentFieldSchema(
            name="receipt_schema",
            description="Schema for receipt extraction with items",
            fields={
                "MerchantName": ContentFieldDefinition(
                    type="string",
                    method="extract",
                    description="Name of the merchant",
                ),
                "Items": ContentFieldDefinition(
                    type="array",
                    method="generate",
                    description="List of items purchased",
                    item_definition=item_definition,
                ),
                "TotalPrice": ContentFieldDefinition(
                    type="string",
                    method="extract",
                    description="Total amount",
                ),
            },
        )

        # Validate field schema
        assert field_schema and field_schema.fields, "Field schema should have fields"
        assert len(field_schema.fields) == 3, "Field schema should have 3 fields"
        assert field_schema.name == "receipt_schema", "Field schema name should match"
        print(f"[PASS] Field schema defined with {len(field_schema.fields)} fields")

        # Validate Items field has item_definition with properties
        items_field = field_schema.fields["Items"]
        assert items_field.type == "array", "Items field should be array type"
        assert items_field.item_definition is not None, "Items field should have item_definition"
        assert items_field.item_definition.properties is not None, "Item definition should have properties"
        assert len(items_field.item_definition.properties) == 3, "Item definition should have 3 properties"
        print("[PASS] Items field definition validated with nested properties")

        # Step 3: Create knowledge source from labeled data
        # Use the module-level cached SAS URL (resolved before proxy patched transports)
        container_sas_url = _TRAINING_DATA_SAS_URL
        training_data_prefix = os.getenv("CONTENTUNDERSTANDING_TRAINING_DATA_PREFIX", "")

        labeled_source = LabeledDataKnowledgeSource(
            container_url=container_sas_url,
            file_list_path="",
        )
        if training_data_prefix:
            labeled_source.prefix = training_data_prefix
        assert labeled_source.container_url, "Knowledge source should have container_url"
        print(f"[PASS] LabeledDataKnowledgeSource created (prefix={training_data_prefix or 'none'})")

        # Step 4: Create the analyzer
        custom_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Receipt analyzer with labeled training data",
            config=ContentAnalyzerConfig(enable_layout=True, enable_ocr=True),
            field_schema=field_schema,
            models={
                "completion": "gpt-4.1",
                "embedding": "text-embedding-3-large",
            },
            knowledge_sources=[labeled_source],
        )

        assert custom_analyzer.base_analyzer_id == "prebuilt-document", "Base analyzer should be prebuilt-document"
        assert custom_analyzer.models and len(custom_analyzer.models) >= 2, "Should have at least 2 model mappings"
        assert (
            custom_analyzer.knowledge_sources and len(custom_analyzer.knowledge_sources) == 1
        ), "Should have 1 knowledge source"
        print("[PASS] Custom analyzer definition validated")

        # Create the analyzer
        try:
            poller = client.begin_create_analyzer(analyzer_id=analyzer_id, resource=custom_analyzer, allow_replace=True)
            result = poller.result()

            # Verify operation completed
            assert poller.done(), "Operation should be completed"
            print(f"[PASS] Analyzer '{analyzer_id}' created successfully")

            # Verify result properties if available
            if result:
                result_id = getattr(result, "analyzer_id", None) or getattr(result, "id", None)
                if result_id:
                    assert result_id == analyzer_id, "Result analyzer ID should match"
                    print(f"[PASS] Result analyzer ID verified: {result_id}")

                if result.description:
                    assert result.description == "Receipt analyzer with labeled training data"
                    print(f"[PASS] Description verified: {result.description}")

                if result.field_schema and result.field_schema.fields:
                    assert len(result.field_schema.fields) == 3, "Result should have 3 fields"
                    print(f"[PASS] Fields verified: {len(result.field_schema.fields)}")

                if result.knowledge_sources:
                    print(f"[PASS] Knowledge sources: {len(result.knowledge_sources)}")

        except ResourceNotFoundError as proxy_error:
            # Check if this is a test proxy playback error (missing recording)
            error_msg = str(proxy_error)
            if "Unable to find a record for the request" in error_msg:
                raise
            raise
        except Exception as e:
            error_msg = str(e)
            print(f"\n[ERROR] Analyzer creation failed: {error_msg}")
            raise
        finally:
            # Cleanup: Delete the analyzer
            try:
                client.delete_analyzer(analyzer_id=analyzer_id)
                print(f"[PASS] Cleanup: Analyzer '{analyzer_id}' deleted")
            except Exception as e:
                print(f"[WARN] Cleanup failed: {str(e)}")

        print("\n[SUCCESS] All test_sample_create_analyzer_with_labels assertions passed")

        # Return variables to be recorded for playback mode
        return variables
