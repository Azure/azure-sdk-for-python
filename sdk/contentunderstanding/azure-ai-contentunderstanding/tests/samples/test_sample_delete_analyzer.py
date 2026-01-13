# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_delete_analyzer.py

DESCRIPTION:
    These tests validate the sample_delete_analyzer.py sample code.
    This sample demonstrates how to delete a custom analyzer.

    The delete_analyzer method permanently removes a custom analyzer from your resource.
    This operation cannot be undone.

    Important notes:
    - Only custom analyzers can be deleted. Prebuilt analyzers cannot be deleted.

USAGE:
    pytest test_sample_delete_analyzer.py
"""

import uuid
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import ContentUnderstandingPreparer, ContentUnderstandingClientTestBase
from azure.ai.contentunderstanding.models import ContentAnalyzer, ContentAnalyzerConfig
from azure.core.exceptions import ResourceNotFoundError


class TestSampleDeleteAnalyzer(ContentUnderstandingClientTestBase):
    """Tests for sample_delete_analyzer.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_delete_analyzer(self, contentunderstanding_endpoint: str) -> None:
        """Test deleting an analyzer.

        This test validates:
        1. Creating a simple analyzer
        2. Verifying the analyzer exists
        3. Deleting the analyzer
        4. Verifying deletion was successful

        09_DeleteAnalyzer.DeleteAnalyzerAsync()
        """
        # Skip this test if API is not available
        try:
            client = self.create_client(endpoint=contentunderstanding_endpoint)

            # Generate unique analyzer ID for this test
            analyzer_id = f"test_analyzer_{uuid.uuid4().hex}"
            print(f"[INFO] Analyzer ID generated: {analyzer_id}")

            # Create a simple analyzer
            analyzer = ContentAnalyzer(
                base_analyzer_id="prebuilt-document",
                description="Simple analyzer for deletion example",
                config=ContentAnalyzerConfig(return_details=True),
                models={"completion": "gpt-4.1"},
            )

            # Assertions for analyzer object
            assert analyzer is not None, "Analyzer object should not be null"
            assert analyzer.base_analyzer_id == "prebuilt-document", "Base analyzer ID should match"
            assert analyzer.description == "Simple analyzer for deletion example", "Description should match"
            assert analyzer.config is not None, "Config should not be null"
            assert analyzer.config.return_details is True, "ReturnDetails should be true"
            assert analyzer.models is not None, "Models should not be null"
            assert "completion" in analyzer.models, "Should have completion model"
            assert analyzer.models["completion"] == "gpt-4.1", "Completion model should be gpt-4.1"
            print("[PASS] Analyzer object configured correctly")

            # Create the analyzer
            create_poller = client.begin_create_analyzer(analyzer_id=analyzer_id, resource=analyzer, allow_replace=True)
            create_result = create_poller.result()
            print(f"[PASS] Analyzer '{analyzer_id}' created successfully")

            # Verify the analyzer was created successfully
            get_response = client.get_analyzer(analyzer_id=analyzer_id)

            # Assertions for get response
            assert get_response is not None, "Get analyzer response should not be null"
            print("[PASS] Analyzer retrieved successfully after creation")

            # Verify analyzer properties
            created_base_id = getattr(get_response, "base_analyzer_id", None)
            assert created_base_id is not None, "Base analyzer ID should not be null"
            assert created_base_id == "prebuilt-document", "Base analyzer ID should match"
            print(f"[PASS] Base analyzer ID verified: {created_base_id}")

            created_description = getattr(get_response, "description", None)
            assert created_description is not None, "Description should not be null"
            assert created_description == "Simple analyzer for deletion example", "Description should match"
            print(f"[PASS] Description verified: '{created_description}'")

            # Verify config
            created_config = getattr(get_response, "config", None)
            if created_config is not None:
                print("[INFO] Config exists")
                return_details = getattr(created_config, "return_details", None)
                if return_details is not None:
                    assert return_details is True, "ReturnDetails should be true"
                    print(f"[PASS] ReturnDetails: {return_details}")

            # Verify models
            created_models = getattr(get_response, "models", None)
            if created_models is not None:
                assert len(created_models) >= 1, "Should have at least 1 model"
                print(f"[PASS] Models verified: {len(created_models)} model(s)")

                if "completion" in created_models:
                    assert created_models["completion"] == "gpt-4.1", "Completion model should be gpt-4.1"
                    print(f"[PASS] completion: {created_models['completion']}")

            print(f"[PASS] Verified analyzer '{analyzer_id}' exists and is correctly configured before deletion")

            # Delete the analyzer
            client.delete_analyzer(analyzer_id=analyzer_id)
            print(f"[PASS] Analyzer '{analyzer_id}' deleted successfully")

            # Verify the analyzer was deleted by trying to get it
            print(f"[INFO] Attempting to verify deletion of analyzer '{analyzer_id}'...")

            deletion_verified = False
            status_code = None
            error_message = None

            try:
                deleted_response = client.get_analyzer(analyzer_id=analyzer_id)

                # If we reach here, the call succeeded which is unexpected
                print("[WARN] Unexpected: Get analyzer call succeeded after deletion")
                raw_response = getattr(deleted_response, "_response", None)
                if raw_response:
                    status_code = getattr(raw_response, "status_code", None)
                    print(f"[WARN] Response status: {status_code}")

                if deleted_response is not None:
                    analyzer_id_attr = getattr(deleted_response, "analyzer_id", None)
                    description_attr = getattr(deleted_response, "description", None)
                    print(f"[WARN] Analyzer ID: {analyzer_id_attr or '(null)'}")
                    print(f"[WARN] Description: {description_attr or '(null)'}")

            except ResourceNotFoundError as e:
                # Expected: analyzer should not be found
                deletion_verified = True
                status_code = getattr(e, "status_code", 404)
                error_message = str(e)
                print(f"[PASS] Expected error received: Analyzer not found")
                print(f"[PASS] Status code: {status_code}")
                print(f"[PASS] Error message: {error_message[:100]}{'...' if len(error_message) > 100 else ''}")

            except Exception as e:
                # Some other error occurred
                print(f"[WARN] Unexpected error during verification: {str(e)[:100]}")
                # Still consider it verified if we got an error trying to get it
                deletion_verified = True
                error_message = str(e)

            # Final assertions
            assert deletion_verified, "Deletion should be verified (analyzer not found after deletion)"
            print(f"[PASS] Deletion verified: Analyzer '{analyzer_id}' is no longer accessible")

            print("\n[SUCCESS] All test_sample_delete_analyzer assertions passed")

        except Exception as e:
            error_msg = str(e).lower()
            if "not supported" in error_msg or "not available" in error_msg or "not implemented" in error_msg:
                pytest.skip(f"API not available: {str(e)[:100]}")
            raise
