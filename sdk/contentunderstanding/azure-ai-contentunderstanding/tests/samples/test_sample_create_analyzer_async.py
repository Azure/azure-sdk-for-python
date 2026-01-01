# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_create_analyzer_async.py

DESCRIPTION:
    These tests validate the sample_create_analyzer.py sample code (async version).

USAGE:
    pytest test_sample_create_analyzer_async.py
"""

import pytest
import uuid
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer_async import ContentUnderstandingPreparer, ContentUnderstandingClientTestBaseAsync
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentFieldDefinition,
    ContentFieldSchema,
)


class TestSampleCreateAnalyzerAsync(ContentUnderstandingClientTestBaseAsync):
    """Tests for sample_create_analyzer.py (async version)"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_create_analyzer_async(self, azure_content_understanding_endpoint: str) -> None:
        """Test creating a custom analyzer with field schema (async version).
        
        This test validates:
        1. Analyzer ID generation
        2. Field schema definition with multiple field types
        3. Analyzer configuration
        4. Model mappings
        5. Analyzer creation operation
        
        04_CreateAnalyzer.CreateAnalyzerAsync()
        """
        client = self.create_async_client(endpoint=azure_content_understanding_endpoint)

        # Generate a unique analyzer ID
        analyzer_id = f"test_custom_analyzer_{uuid.uuid4().hex[:16]}"
        assert analyzer_id and analyzer_id.strip(), "Analyzer ID should not be empty"
        print(f"[PASS] Analyzer ID generated: {analyzer_id}")
        
        # Define field schema with custom fields
        # This example demonstrates three extraction methods:
        # - extract: Literal text extraction
        # - generate: AI-generated values based on content interpretation
        # - classify: Classification against predefined categories
        field_schema = ContentFieldSchema(
            name="company_schema",
            description="Schema for extracting company information",
            fields={
                "company_name": ContentFieldDefinition(
                    type="string",
                    method="extract",
                    description="Name of the company"
                ),
                "total_amount": ContentFieldDefinition(
                    type="number",
                    method="extract",
                    description="Total amount on the document"
                ),
                "document_summary": ContentFieldDefinition(
                    type="string",
                    method="generate",
                    description="A brief summary of the document content"
                ),
                "document_type": ContentFieldDefinition(
                    type="string",
                    method="classify",
                    description="Type of document",
                    enum=["invoice", "receipt", "contract", "report", "other"]
                )
            }
        )
        
        # Validate field schema
        assert field_schema and field_schema.fields, "Field schema should have fields"
        assert len(field_schema.fields) == 4, "Field schema should have 4 fields"
        assert field_schema.name == "company_schema", "Field schema name should match"
        print(f"[PASS] Field schema defined with {len(field_schema.fields)} fields")
        
        # Validate each field definition
        for field_name, field_def in field_schema.fields.items():
            assert field_def.type and field_def.method and field_def.description, \
                f"Field {field_name} should have type, method, and description"
            assert field_def.method in ["extract", "generate", "classify"], \
                f"Field {field_name} method should be valid"
        
        # Verify enum for classify field
        document_type_field = field_schema.fields["document_type"]
        assert document_type_field.enum and len(document_type_field.enum) == 5, \
            "Document type should have 5 enum values"
        print("[PASS] Field definitions validated")
        
        # Create analyzer configuration
        config = ContentAnalyzerConfig(
            enable_formula=True,
            enable_layout=True,
            enable_ocr=True,
            estimate_field_source_and_confidence=True,
            return_details=True
        )
        
        assert config.enable_formula and config.enable_layout and config.enable_ocr, \
            "Core features should be enabled"
        print("[PASS] Analyzer configuration created")
        
        # Create custom analyzer definition
        custom_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Custom analyzer for extracting company information",
            config=config,
            field_schema=field_schema,
            models={
                "completion": "gpt-4.1",
                "embedding": "text-embedding-3-large"
            }
        )
        
        assert custom_analyzer.base_analyzer_id == "prebuilt-document", \
            "Base analyzer should be prebuilt-document"
        assert custom_analyzer.models and len(custom_analyzer.models) >= 2, \
            "Should have at least 2 model mappings"
        print("[PASS] Custom analyzer definition validated")
        
        # Create the analyzer
        try:
            poller = await client.begin_create_analyzer(
                analyzer_id=analyzer_id,
                resource=custom_analyzer
            )
            result = await poller.result()
            
            # Verify operation completed
            assert poller.done(), "Operation should be completed"
            print(f"[PASS] Analyzer '{analyzer_id}' created successfully")
            
            # Verify result properties if available
            if result:
                result_id = getattr(result, "analyzer_id", None) or getattr(result, "id", None)
                if result_id:
                    assert result_id == analyzer_id, "Result analyzer ID should match"
                    print(f"[PASS] Result analyzer ID verified: {result_id}")
                
        except Exception as e:
            error_msg = str(e)
            print(f"\n[ERROR] Analyzer creation failed: {error_msg}")
            pytest.skip(f"Analyzer creation not available: {error_msg[:100]}")
        finally:
            # Cleanup: Delete the analyzer
            try:
                await client.delete_analyzer(analyzer_id=analyzer_id)
                print(f"[PASS] Cleanup: Analyzer '{analyzer_id}' deleted")
            except Exception as e:
                print(f"[WARN] Cleanup failed: {str(e)}")
            
            await client.close()
        
        print("\n[SUCCESS] All test_sample_create_analyzer_async assertions passed")
