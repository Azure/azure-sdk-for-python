# pylint: disable=line-too-long,useless-suppression
# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_grant_copy_auth.py

DESCRIPTION:
    These tests validate the sample_grant_copy_auth.py sample code.
    This sample demonstrates how to grant copy authorization and copy an analyzer from a source
    Microsoft Foundry resource to a target Microsoft Foundry resource (cross-resource copying).

USAGE:
    pytest test_sample_grant_copy_auth.py
"""

import os
import uuid
import pytest
from datetime import datetime, timezone
from typing import Optional, cast, Dict
from devtools_testutils import recorded_by_proxy, is_live
from testpreparer import ContentUnderstandingPreparer, ContentUnderstandingClientTestBase
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentFieldSchema,
    ContentFieldDefinition,
    ContentFieldType,
    GenerationMethod,
)


class TestSampleGrantCopyAuth(ContentUnderstandingClientTestBase):
    """Tests for sample_grant_copy_auth.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_grant_copy_auth(self, contentunderstanding_endpoint: str, **kwargs) -> Dict[str, str]:
        """Test granting copy authorization for cross-resource analyzer copying.

        This test validates:
        1. Creating a source analyzer
        2. Granting copy authorization from source resource
        3. Using authorization to copy analyzer across resources
        4. Verifying the copied analyzer
        """
        # Initialize variables for cleanup
        source_analyzer_id: str = ""
        target_analyzer_id: str = ""
        source_client: Optional[ContentUnderstandingClient] = None
        target_client: Optional[ContentUnderstandingClient] = None

        # Get variables from test proxy (recorded values in playback, empty dict in recording)
        variables = kwargs.pop("variables", {})
        
        try:
            # Always use placeholder values in variables to avoid storing real resource IDs/regions
            # Real values are read from environment for API calls (they'll be sanitized in request bodies)
            # But variables should only contain placeholders for security
            target_endpoint = variables.setdefault("target_endpoint", contentunderstanding_endpoint)
            source_resource_id = variables.setdefault("source_resource_id", "placeholder-source-resource-id")
            source_region = variables.setdefault("source_region", "placeholder-source-region")
            target_resource_id = variables.setdefault("target_resource_id", "placeholder-target-resource-id")
            target_region = variables.setdefault("target_region", "placeholder-target-region")
            
            # For actual API calls, use real values from environment if available (in live mode)
            # These will be sanitized in request/response bodies by conftest sanitizers
            if is_live():
                env_target_endpoint = os.environ.get("CONTENTUNDERSTANDING_TARGET_ENDPOINT")
                if env_target_endpoint:
                    target_endpoint = env_target_endpoint
                env_source_resource_id = os.environ.get("CONTENTUNDERSTANDING_SOURCE_RESOURCE_ID")
                if env_source_resource_id:
                    source_resource_id = env_source_resource_id
                env_source_region = os.environ.get("CONTENTUNDERSTANDING_SOURCE_REGION")
                if env_source_region:
                    source_region = env_source_region
                env_target_resource_id = os.environ.get("CONTENTUNDERSTANDING_TARGET_RESOURCE_ID")
                if env_target_resource_id:
                    target_resource_id = env_target_resource_id
                env_target_region = os.environ.get("CONTENTUNDERSTANDING_TARGET_REGION")
                if env_target_region:
                    target_region = env_target_region
            
            target_key = os.environ.get("CONTENTUNDERSTANDING_TARGET_KEY")

            # Only require environment variables in live mode
            # In playback mode, the test proxy will replay recorded interactions
            if is_live():
                if source_resource_id == "placeholder-source-resource-id":
                    raise ValueError(
                        "CONTENTUNDERSTANDING_SOURCE_RESOURCE_ID is required for cross-resource copy test in live mode"
                    )
                if source_region == "placeholder-source-region":
                    raise ValueError(
                        "CONTENTUNDERSTANDING_SOURCE_REGION is required for cross-resource copy test in live mode"
                    )
                if target_resource_id == "placeholder-target-resource-id":
                    raise ValueError(
                        "CONTENTUNDERSTANDING_TARGET_RESOURCE_ID is required for cross-resource copy test in live mode"
                    )
                if target_region == "placeholder-target-region":
                    raise ValueError(
                        "CONTENTUNDERSTANDING_TARGET_REGION is required for cross-resource copy test in live mode"
                    )

            # Create clients
            source_client = self.create_client(endpoint=contentunderstanding_endpoint)

            # Create target client (may use different endpoint and credential)
            from azure.core.credentials import AzureKeyCredential
            from azure.identity import DefaultAzureCredential

            if target_endpoint != contentunderstanding_endpoint or target_key:
                # Create target client with different endpoint/credential
                if target_key:
                    target_credential = AzureKeyCredential(target_key)
                else:
                    target_credential = self.get_credential(ContentUnderstandingClient)
                target_client = cast(
                    ContentUnderstandingClient,
                    self.create_client_from_credential(
                        ContentUnderstandingClient,
                        credential=target_credential,
                        endpoint=target_endpoint,
                    ),
                )
            else:
                # Use same endpoint and credential as source
                target_client = self.create_client(endpoint=target_endpoint)

            # Generate unique analyzer IDs for this test
            # Use variables from recording if available (playback mode), otherwise generate new ones (record mode)
            default_source_id = f"test_analyzer_source_{uuid.uuid4().hex[:16]}"
            default_target_id = f"test_analyzer_target_{uuid.uuid4().hex[:16]}"
            source_analyzer_id = variables.setdefault("grantCopySourceAnalyzerId", default_source_id)
            target_analyzer_id = variables.setdefault("grantCopyTargetAnalyzerId", default_target_id)

            print(f"[INFO] Source analyzer ID: {source_analyzer_id}")
            print(f"[INFO] Target analyzer ID: {target_analyzer_id}")

            # Verify IDs
            assert source_analyzer_id is not None, "Source analyzer ID should not be null"
            assert source_analyzer_id.strip(), "Source analyzer ID should not be empty"
            assert target_analyzer_id is not None, "Target analyzer ID should not be null"
            assert target_analyzer_id.strip(), "Target analyzer ID should not be empty"
            assert source_analyzer_id != target_analyzer_id, "Source and target IDs should be different"
            print("[PASS] Analyzer IDs verified")

            # Verify resource information (only in live mode)
            # In playback mode, the test proxy will replay recorded interactions
            if is_live():
                assert source_resource_id is not None, "Source resource ID should not be null"
                assert source_resource_id.strip(), "Source resource ID should not be empty"
                assert source_region is not None, "Source region should not be null"
                assert source_region.strip(), "Source region should not be empty"
                assert target_resource_id is not None, "Target resource ID should not be null"
                assert target_resource_id.strip(), "Target resource ID should not be empty"
                assert target_region is not None, "Target region should not be null"
                assert target_region.strip(), "Target region should not be empty"

            assert target_endpoint is not None, "Target endpoint should not be null"
            assert target_endpoint.strip(), "Target endpoint should not be empty"

            if is_live():
                print(f"[INFO] Source resource: {source_resource_id}")
                print(f"[INFO] Source region: {source_region}")
                print(f"[INFO] Target resource: {target_resource_id}")
                print(f"[INFO] Target region: {target_region}")
            print(f"[INFO] Target endpoint: {target_endpoint}")

            # Verify clients
            assert source_client is not None, "Source client should not be null"
            assert target_client is not None, "Target client should not be null"
            print("[PASS] Source and target clients created")

            # Step 1: Create the source analyzer
            source_config = ContentAnalyzerConfig(
                enable_formula=False,
                enable_layout=True,
                enable_ocr=True,
                estimate_field_source_and_confidence=True,
                return_details=True,
            )

            # Verify source config
            assert source_config is not None, "Source config should not be null"
            assert source_config.enable_formula is False, "EnableFormula should be false"
            assert source_config.enable_layout is True, "EnableLayout should be true"
            assert source_config.enable_ocr is True, "EnableOcr should be true"
            assert (
                source_config.estimate_field_source_and_confidence is True
            ), "EstimateFieldSourceAndConfidence should be true"
            assert source_config.return_details is True, "ReturnDetails should be true"
            print("[PASS] Source config verified")

            source_field_schema = ContentFieldSchema(
                name="company_schema",
                description="Schema for extracting company information",
                fields={
                    "company_name": ContentFieldDefinition(
                        type=ContentFieldType.STRING, method=GenerationMethod.EXTRACT, description="Name of the company"
                    ),
                    "total_amount": ContentFieldDefinition(
                        type=ContentFieldType.NUMBER,
                        method=GenerationMethod.EXTRACT,
                        description="Total amount on the document",
                    ),
                },
            )

            # Verify source field schema
            assert source_field_schema is not None, "Source field schema should not be null"
            assert source_field_schema.name == "company_schema", "Field schema name should match"
            assert (
                source_field_schema.description == "Schema for extracting company information"
            ), "Field schema description should match"
            assert len(source_field_schema.fields) == 2, "Should have 2 fields"
            assert "company_name" in source_field_schema.fields, "Should contain company_name field"
            assert "total_amount" in source_field_schema.fields, "Should contain total_amount field"
            print(
                f"[PASS] Source field schema verified: {source_field_schema.name} ({len(source_field_schema.fields)} fields)"
            )

            source_analyzer = ContentAnalyzer(
                base_analyzer_id="prebuilt-document",
                description="Source analyzer for cross-resource copying",
                config=source_config,
                field_schema=source_field_schema,
                models={"completion": "gpt-4.1"},
            )

            # Verify source analyzer object
            assert source_analyzer is not None, "Source analyzer object should not be null"
            assert source_analyzer.base_analyzer_id == "prebuilt-document", "Base analyzer ID should match"
            assert (
                source_analyzer.description == "Source analyzer for cross-resource copying"
            ), "Description should match"
            assert source_analyzer.models is not None, "Models should not be null"
            assert "completion" in source_analyzer.models, "Should have completion model"
            assert source_analyzer.models["completion"] == "gpt-4.1", "Completion model should be gpt-4.1"
            print("[PASS] Source analyzer object verified")

            # Create the source analyzer
            create_poller = source_client.begin_create_analyzer(
                analyzer_id=source_analyzer_id, resource=source_analyzer, allow_replace=True
            )
            create_poller.result()  # Wait for creation to complete
            print(f"[PASS] Source analyzer '{source_analyzer_id}' created successfully")

            # Get the full analyzer details after creation (LRO result doesn't contain full details)
            source_result = source_client.get_analyzer(analyzer_id=source_analyzer_id)

            # Verify create operation
            assert source_result is not None, "Source analyzer result should not be null"
            assert source_result.base_analyzer_id == "prebuilt-document", "Base analyzer ID should match"
            assert source_result.description == "Source analyzer for cross-resource copying", "Description should match"
            assert source_result.config is not None, "Config should not be null"
            assert source_result.field_schema is not None, "Field schema should not be null"
            assert len(source_result.field_schema.fields) == 2, "Should have 2 fields"
            assert source_result.models is not None, "Models should not be null"
            assert "completion" in source_result.models, "Should have completion model"
            print(f"[PASS] Source analyzer created: '{source_analyzer_id}'")
            print(f"[INFO] Base: {source_result.base_analyzer_id}")
            print(f"[INFO] Fields: {len(source_result.field_schema.fields)}")
            print(f"[INFO] Models: {len(source_result.models)}")
            print("[INFO] Ready for cross-resource copy")

            # Step 2: Grant copy authorization from source resource
            # Grant authorization on the source client for copying to the target resource
            print(f"\n[INFO] Granting copy authorization from source resource")

            copy_auth = source_client.grant_copy_authorization(
                analyzer_id=source_analyzer_id,
                target_azure_resource_id=target_resource_id,
                target_region=target_region,
            )

            print("[PASS] Copy authorization granted successfully!")

            # Verify copy authorization response
            assert copy_auth is not None, "Copy authorization response should not be null"
            assert hasattr(
                copy_auth, "target_azure_resource_id"
            ), "Copy authorization should have target_azure_resource_id"
            assert copy_auth.target_azure_resource_id is not None, "Target Azure resource ID should not be null"
            assert copy_auth.target_azure_resource_id.strip(), "Target Azure resource ID should not be empty"
            # In playback mode, compare against the recorded response value
            # In live mode, compare against the environment variable
            if is_live():
                assert (
                    copy_auth.target_azure_resource_id == target_resource_id
                ), f"Target resource ID should match, but got '{copy_auth.target_azure_resource_id}' instead of '{target_resource_id}'"
                print(f"[PASS] Target Azure Resource ID verified: {copy_auth.target_azure_resource_id}")
                print(f"[INFO] Target region (tracked): {target_region}")
            else:
                # In playback mode, just verify the response has a value (from recording)
                print(f"[INFO] Target Azure Resource ID (from recording): {copy_auth.target_azure_resource_id}")
                print(f"[INFO] Target region (from recording): {target_region}")

            # Verify expiration time
            assert hasattr(copy_auth, "expires_at"), "Copy authorization should have expires_at"
            expires_at = copy_auth.expires_at
            # Only verify expiration time in live/record mode, not in playback mode
            # (recorded expiration times may be in the past during playback)
            if is_live():
                now = datetime.now(timezone.utc)

                assert (
                    expires_at > now
                ), f"Expiration time should be in the future, but expires at {expires_at} (now: {now})"

                # Calculate time until expiration
                time_until_expiration = expires_at - now
                assert time_until_expiration.total_seconds() > 0, "Should have positive time until expiration"

                print(f"[PASS] Expiration time verified: {expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")
                print(f"[INFO] Time until expiration: {time_until_expiration.total_seconds() / 60:.2f} minutes")

                if time_until_expiration.total_seconds() / 3600 < 24:
                    print("[WARN] Note: Authorization expires in less than 24 hours")
            else:
                print(
                    f"[INFO] Expiration time: {expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC (from recorded response)"
                )

            print(f"[INFO] Copy authorization granted successfully:")
            print(f"[INFO]   Source analyzer: {source_analyzer_id}")
            print(f"[INFO]   Target resource: {copy_auth.target_azure_resource_id}")
            print(f"[INFO]   Target region: {target_region}")
            print(f"[INFO]   Expires: {expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print("[INFO]   Authorization ready for cross-resource copy")

            # Step 3: Copy analyzer using authorization
            # Copy is performed on the target client, copying from source to target
            print(f"\n[INFO] Copying analyzer from source to target")

            copy_poller = target_client.begin_copy_analyzer(
                analyzer_id=target_analyzer_id,
                source_analyzer_id=source_analyzer_id,
                source_azure_resource_id=source_resource_id,
                source_region=source_region,
            )
            copy_result = copy_poller.result()
            print(f"[PASS] Target analyzer '{target_analyzer_id}' copied successfully to target resource!")

            # Verify copy result
            assert copy_result is not None, "Copy result should not be null"
            if hasattr(copy_result, "description"):
                print(f"[INFO] Target analyzer description: {copy_result.description}")

            # Step 4: Verify the copied analyzer
            copied_analyzer = target_client.get_analyzer(analyzer_id=target_analyzer_id)

            assert copied_analyzer is not None, "Copied analyzer should not be null"
            print("[PASS] Copied analyzer retrieved successfully")

            # Verify basic properties match
            if hasattr(copied_analyzer, "analyzer_id"):
                assert copied_analyzer.analyzer_id == target_analyzer_id, "Analyzer ID should match"
                print(f"[INFO] Target Analyzer ID: {copied_analyzer.analyzer_id}")

            copied_description = getattr(copied_analyzer, "description", None)
            assert copied_description == "Source analyzer for cross-resource copying", "Description should match"
            print(f"[INFO] Description: {copied_description}")

            if hasattr(copied_analyzer, "status"):
                print(f"[INFO] Status: {copied_analyzer.status}")

            print("[PASS] Copied analyzer properties verified")

            print("\n[SUCCESS] All test_sample_grant_copy_auth assertions passed")
            print("[INFO] Grant copy authorization functionality demonstrated")

            # Return variables to be recorded for playback mode
            return variables
        finally:
            # Clean up: delete test analyzers
            try:
                if source_analyzer_id and source_client:
                    source_client.delete_analyzer(analyzer_id=source_analyzer_id)  # type: ignore[attr-defined]
                    print(f"\n[INFO] Source analyzer '{source_analyzer_id}' deleted successfully.")
            except Exception as cleanup_error:
                print(f"\n[WARN] Could not delete source analyzer: {str(cleanup_error)[:100]}")

            try:
                if target_analyzer_id and target_client:
                    target_client.delete_analyzer(analyzer_id=target_analyzer_id)  # type: ignore[attr-defined]
                    print(f"[INFO] Target analyzer '{target_analyzer_id}' deleted successfully.")
            except Exception as cleanup_error:
                print(f"[WARN] Could not delete target analyzer: {str(cleanup_error)[:100]}")
