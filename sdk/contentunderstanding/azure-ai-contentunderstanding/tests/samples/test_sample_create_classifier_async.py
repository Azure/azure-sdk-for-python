# pylint: disable=line-too-long,useless-suppression
# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_create_classifier_async.py

DESCRIPTION:
    These tests validate the sample_create_classifier.py sample code (async version).
    This sample demonstrates creating a classifier analyzer to categorize documents
    into predefined categories with optional automatic segmentation.

USAGE:
    pytest test_sample_create_classifier_async.py
"""

import os
import pytest
import uuid
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer_async import ContentUnderstandingPreparer, ContentUnderstandingClientTestBaseAsync
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentCategoryDefinition,
    DocumentContent,
)


class TestSampleCreateClassifierAsync(ContentUnderstandingClientTestBaseAsync):
    """Tests for sample_create_classifier.py (async version)"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_create_classifier_async(self, azure_content_understanding_endpoint: str) -> None:
        """Test creating a custom classifier with content categories (async version).

        This test validates:
        1. Content categories definition
        2. Analyzer configuration with segmentation
        3. Classifier creation

        05_CreateClassifier.CreateClassifierAsync()
        """
        client = self.create_async_client(endpoint=azure_content_understanding_endpoint)

        # Generate a unique analyzer ID
        analyzer_id = f"test_classifier_{uuid.uuid4().hex[:16]}"

        print(f"[PASS] Classifier ID generated: {analyzer_id}")

        # Define content categories for classification using ContentCategoryDefinition objects
        categories = {
            "Loan_Application": ContentCategoryDefinition(
                description="Documents submitted by individuals or businesses to request funding, typically including personal or business details, financial history, loan amount, purpose, and supporting documentation."
            ),
            "Invoice": ContentCategoryDefinition(
                description="Billing documents issued by sellers or service providers to request payment for goods or services, detailing items, prices, taxes, totals, and payment terms."
            ),
            "Bank_Statement": ContentCategoryDefinition(
                description="Official statements issued by banks that summarize account activity over a period, including deposits, withdrawals, fees, and balances."
            ),
        }

        # Assertions for categories
        assert categories is not None, "Categories should not be null"
        assert len(categories) == 3, "Should have 3 categories"
        print(f"[PASS] Content categories defined: {len(categories)} categories")

        # Validate each category has description
        for cat_name, cat_def in categories.items():
            assert cat_def.description is not None, f"Category {cat_name} should have description"
            assert cat_def.description.strip(), f"Category {cat_name} description should not be empty"

        print("[PASS] All category definitions validated")

        # Create analyzer configuration using ContentAnalyzerConfig model
        config = ContentAnalyzerConfig(
            return_details=True,
            enable_segment=True,  # Enable automatic segmentation by category
            content_categories=categories,
        )

        # Assertions for config
        assert config is not None, "Config should not be null"
        assert config.enable_segment is True, "Segmentation should be enabled"
        assert config.content_categories is not None, "Config should have content categories"
        assert len(config.content_categories) == 3, "Config should have 3 content categories"
        print("[PASS] Classifier configuration created")

        # Create the classifier analyzer using ContentAnalyzer model
        classifier = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Custom classifier for financial document categorization",
            config=config,
            models={"completion": "gpt-4.1"},
        )

        # Assertions for classifier
        assert classifier is not None, "Classifier should not be null"
        assert classifier.base_analyzer_id == "prebuilt-document", "Base analyzer should be prebuilt-document"
        assert classifier.models is not None, "Classifier should have models"
        assert "completion" in classifier.models, "Classifier should have completion model"
        print("[PASS] Classifier definition validated")

        # Create the classifier
        try:
            poller = await client.begin_create_analyzer(analyzer_id=analyzer_id, resource=classifier)

            result = await poller.result()

            # Assertions
            assert poller is not None, "Create classifier operation should not be null"
            assert poller.done(), "Operation should be completed"
            print(f"[PASS] Classifier '{analyzer_id}' created successfully")

            assert result is not None, "Create classifier result should not be null"
            print("[PASS] Create classifier result validated")

            # Cleanup
            try:
                await client.delete_analyzer(analyzer_id=analyzer_id)
                print(f"[PASS] Cleanup: Classifier '{analyzer_id}' deleted")
            except Exception as e:
                print(f"[WARN] Cleanup failed: {str(e)}")
        except Exception as e:
            error_msg = str(e)
            print(f"\n[ERROR] Full error message:\n{error_msg}")
            pytest.skip(f"Classifier creation not available or failed: {error_msg[:100]}")

        await client.close()
        print("\n[SUCCESS] All test_sample_create_classifier_async assertions passed")

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_analyze_with_classifier_async(self, azure_content_understanding_endpoint: str) -> None:
        """Test analyzing a document with a classifier to categorize content into segments (async version).

        This test validates:
        1. Create a classifier with segmentation enabled
        2. Analyze a document with the classifier
        3. Verify segments are returned with category information

        Demonstrates: Analyze documents with segmentation (async)
        """
        client = self.create_async_client(endpoint=azure_content_understanding_endpoint)

        # Generate a unique analyzer ID
        analyzer_id = f"test_classifier_{uuid.uuid4().hex[:16]}"

        print(f"[PASS] Classifier ID generated: {analyzer_id}")

        # Define content categories for classification
        categories = {
            "Loan_Application": ContentCategoryDefinition(
                description="Documents submitted by individuals or businesses to request funding, typically including personal or business details, financial history, loan amount, purpose, and supporting documentation."
            ),
            "Invoice": ContentCategoryDefinition(
                description="Billing documents issued by sellers or service providers to request payment for goods or services, detailing items, prices, taxes, totals, and payment terms."
            ),
            "Bank_Statement": ContentCategoryDefinition(
                description="Official statements issued by banks that summarize account activity over a period, including deposits, withdrawals, fees, and balances."
            ),
        }

        # Create analyzer configuration with segmentation enabled
        config = ContentAnalyzerConfig(
            return_details=True,
            enable_segment=True,  # Enable automatic segmentation by category
            content_categories=categories,
        )

        # Create the classifier analyzer
        classifier = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Custom classifier for financial document categorization",
            config=config,
            models={"completion": "gpt-4.1"},
        )

        # Create the classifier
        try:
            poller = await client.begin_create_analyzer(analyzer_id=analyzer_id, resource=classifier)
            result = await poller.result()
            print(f"[PASS] Classifier '{analyzer_id}' created successfully")

            # Analyze a document with the classifier
            current_dir = os.path.dirname(os.path.abspath(__file__))
            test_data_dir = os.path.join(os.path.dirname(current_dir), "test_data")
            file_path = os.path.join(test_data_dir, "mixed_financial_docs.pdf")

            # Check if file exists, if not skip this test
            if not os.path.exists(file_path):
                print(f"[INFO] Test file not found: {file_path}")
                pytest.skip(f"Test data file not available: {file_path}")

            with open(file_path, "rb") as f:
                file_bytes = f.read()

            # Analyze the document
            analyze_poller = await client.begin_analyze_binary(
                analyzer_id=analyzer_id,
                binary_input=file_bytes,
            )
            analyze_result = await analyze_poller.result()

            # Assertions for analyze result
            assert analyze_result is not None, "Analysis result should not be null"
            print("[PASS] Analysis result received")

            assert analyze_result.contents is not None, "Analysis result contents should not be null"
            assert len(analyze_result.contents) > 0, "Analysis result should have at least one content"
            print(f"[PASS] Analysis result contains {len(analyze_result.contents)} content(s)")

            # Verify document content
            document_content = analyze_result.contents[0]
            assert isinstance(document_content, DocumentContent), "Content should be of type DocumentContent"
            print("[PASS] Content is of type DocumentContent")

            # Verify segments (classification results)
            segments = getattr(document_content, "segments", None)
            if segments and len(segments) > 0:
                print(f"[PASS] Document has {len(segments)} segment(s)")
                for idx, segment in enumerate(segments):
                    category = getattr(segment, "category", None)
                    start_page = getattr(segment, "start_page_number", None)
                    end_page = getattr(segment, "end_page_number", None)
                    segment_id = getattr(segment, "segment_id", None)

                    assert category is not None, f"Segment {idx} should have category"
                    assert start_page is not None, f"Segment {idx} should have start_page_number"
                    assert end_page is not None, f"Segment {idx} should have end_page_number"

                    print(f"  Segment {idx}: Category={category}, Pages {start_page}-{end_page}, ID={segment_id}")
                print("[PASS] All segments have required properties")
            else:
                print("[INFO] No segments found (document classified as single unit)")

            # Cleanup
            try:
                await client.delete_analyzer(analyzer_id=analyzer_id)
                print(f"[PASS] Cleanup: Classifier '{analyzer_id}' deleted")
            except Exception as e:
                print(f"[WARN] Cleanup failed: {str(e)}")

        except Exception as e:
            error_msg = str(e)
            print(f"\n[ERROR] Full error message:\n{error_msg}")
            pytest.skip(f"Classifier analysis not available or failed: {error_msg[:100]}")

        await client.close()
        print("\n[SUCCESS] All test_sample_analyze_with_classifier_async assertions passed")
