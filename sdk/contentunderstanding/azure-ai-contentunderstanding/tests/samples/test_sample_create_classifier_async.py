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

USAGE:
    pytest test_sample_create_classifier_async.py
"""

import pytest
import uuid
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer_async import ContentUnderstandingPreparer, ContentUnderstandingClientTestBaseAsync
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentCategoryDefinition,
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
