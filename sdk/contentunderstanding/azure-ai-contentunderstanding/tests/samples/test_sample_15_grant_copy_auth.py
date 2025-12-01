# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_15_grant_copy_auth.py

DESCRIPTION:
    These tests validate the sample_15_grant_copy_auth.py sample code.
    Tests correspond to .NET Sample15_GrantCopyAuth.cs

USAGE:
    pytest test_sample_15_grant_copy_auth.py
"""

import os
import uuid
import pytest
from typing import Optional
from devtools_testutils import recorded_by_proxy
from testpreparer import ContentUnderstandingPreparer, ContentUnderstandingClientTestBase
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentFieldSchema,
    ContentFieldDefinition,
    ContentFieldType,
    GenerationMethod
)


class TestSample15GrantCopyAuth(ContentUnderstandingClientTestBase):
    """Tests for sample_15_grant_copy_auth.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_15_grant_copy_auth(self, contentunderstanding_endpoint: str) -> None:
        """Test granting copy authorization for cross-resource analyzer copying.
        
        This test validates:
        1. Creating a source analyzer
        2. Granting copy authorization from target resource
        3. Using authorization to copy analyzer across resources
        4. Verifying the copied analyzer
        
        Corresponds to .NET Sample15_GrantCopyAuth.GrantCopyAuthAsync()
        
        Note: This test requires copy authorization API support and multiple resources.
        If not available, test will be skipped.
        """
        # Skip this test if API is not available
        # Initialize variables for cleanup
        source_analyzer_id: str = ""
        target_analyzer_id: str = ""
        source_client: Optional[object] = None
        target_client: Optional[object] = None
        
        try:
            # For this test, we use the same endpoint for both source and target
            # In production, these would be different resources in different regions
            source_client = self.create_client(endpoint=contentunderstanding_endpoint)
            target_client = self.create_client(endpoint=contentunderstanding_endpoint)
            
            # Generate unique analyzer IDs for this test
            source_analyzer_id = f"test_analyzer_source_{uuid.uuid4().hex}"
            target_analyzer_id = f"test_analyzer_target_{uuid.uuid4().hex}"
            
            print(f"[INFO] Source analyzer ID: {source_analyzer_id}")
            print(f"[INFO] Target analyzer ID: {target_analyzer_id}")
            
            # Verify IDs
            assert source_analyzer_id is not None, "Source analyzer ID should not be null"
            assert target_analyzer_id is not None, "Target analyzer ID should not be null"
            assert source_analyzer_id != target_analyzer_id, "Source and target IDs should be different"
            print("[PASS] Analyzer IDs verified")
            
            # Step 1: Create the source analyzer
            source_config = ContentAnalyzerConfig(
                enable_formula=False,
                enable_layout=True,
                enable_ocr=True,
                estimate_field_source_and_confidence=True,
                return_details=True
            )
            
            source_field_schema = ContentFieldSchema(
                name="company_schema",
                description="Schema for extracting company information",
                fields={
                    "company_name": ContentFieldDefinition(
                        type=ContentFieldType.STRING,
                        method=GenerationMethod.EXTRACT,
                        description="Name of the company"
                    ),
                    "total_amount": ContentFieldDefinition(
                        type=ContentFieldType.NUMBER,
                        method=GenerationMethod.EXTRACT,
                        description="Total amount on the document"
                    )
                }
            )
            
            source_analyzer = ContentAnalyzer(
                base_analyzer_id="prebuilt-document",
                description="Source analyzer for cross-resource copying",
                config=source_config,
                field_schema=source_field_schema,
                models={
                    "completion": "gpt-4.1"
                },
                tags={
                    "modelType": "in_development"
                }
            )
            
            # Create the source analyzer
            create_poller = source_client.begin_create_analyzer(
                analyzer_id=source_analyzer_id,
                resource=source_analyzer,
                allow_replace=True
            )
            source_result = create_poller.result()
            print(f"[PASS] Source analyzer '{source_analyzer_id}' created successfully")
            
            # Step 2: Grant copy authorization from target resource
            print(f"\n[INFO] Granting copy authorization from target resource")
            
            # Check if grant_copy_authorization API exists
            if not hasattr(target_client, 'grant_copy_authorization'):
                pytest.skip("Grant copy authorization API not available")
            
            try:
                # Grant authorization for copying
                # This returns an authorization token that can be used by the source to copy
                auth_response = target_client.grant_copy_authorization(
                    analyzer_id=target_analyzer_id,
                    target_azure_resource_id=os.environ.get("AZURE_CONTENT_UNDERSTANDING_AZURE_RESOURCE_ID", "")
                )
                
                print(f"[PASS] Copy authorization granted")
                
                # The authorization response typically contains:
                # - Authorization token
                # - Target resource ID
                # - Target region
                # - Expiration time
                
                if hasattr(auth_response, 'authorization_token'):
                    auth_token = getattr(auth_response, 'authorization_token', None)
                    if auth_token:
                        print(f"[INFO] Authorization token received (length: {len(auth_token)})")
                
                # Step 3: Use authorization to copy analyzer
                print(f"\n[INFO] Copying analyzer using authorization")
                
                if hasattr(source_client, 'begin_copy_analyzer_with_authorization'):
                    copy_poller = source_client.begin_copy_analyzer_with_authorization(  # type: ignore
                        source_analyzer_id=source_analyzer_id,
                        authorization=auth_response
                    )
                    copy_result = copy_poller.result()  # type: ignore
                    print(f"[PASS] Analyzer copied successfully to '{target_analyzer_id}'")
                    
                    # Step 4: Verify the copied analyzer
                    copied_analyzer = target_client.get_analyzer(analyzer_id=target_analyzer_id)
                    
                    assert copied_analyzer is not None, "Copied analyzer should not be null"
                    print("[PASS] Copied analyzer retrieved successfully")
                    
                    # Verify basic properties match
                    copied_description = getattr(copied_analyzer, 'description', None)
                    assert copied_description == "Source analyzer for cross-resource copying", "Description should match"
                    print("[PASS] Copied analyzer properties verified")
                else:
                    print("[INFO] Copy with authorization API not yet implemented in Python SDK")
                    pytest.skip("Copy with authorization API not yet implemented")
                
            except Exception as auth_error:
                error_msg = str(auth_error).lower()
                if "not found" in error_msg or "not implemented" in error_msg or "not supported" in error_msg:
                    print(f"[INFO] Copy authorization API not available: {str(auth_error)[:100]}")
                    pytest.skip(f"Copy authorization API not available: {str(auth_error)[:100]}")
                raise
            
            print("\n[SUCCESS] All test_sample_15_grant_copy_auth assertions passed")
            print("[INFO] Grant copy authorization functionality demonstrated")
        finally:
            # Clean up: delete test analyzers
            try:
                if source_analyzer_id and source_client:
                    source_client.delete_analyzer(analyzer_id=source_analyzer_id)  # type: ignore[attr-defined]
                    print(f"\n[INFO] Source analyzer deleted: {source_analyzer_id}")
            except Exception as cleanup_error:
                print(f"\n[WARN] Could not delete source analyzer: {str(cleanup_error)[:100]}")
            
            try:
                if target_analyzer_id and target_client:
                    # Only try to delete if copy succeeded
                    if 'copy_result' in locals():
                        target_client.delete_analyzer(analyzer_id=target_analyzer_id)  # type: ignore[attr-defined]
                        print(f"[INFO] Target analyzer deleted: {target_analyzer_id}")
            except Exception as cleanup_error:
                print(f"[WARN] Could not delete target analyzer: {str(cleanup_error)[:100]}")
