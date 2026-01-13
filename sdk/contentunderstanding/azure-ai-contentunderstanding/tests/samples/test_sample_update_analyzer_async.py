# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_update_analyzer_async.py

DESCRIPTION:
    These tests validate the sample_update_analyzer.py sample code (async version).
    This sample demonstrates how to update an existing custom analyzer, including updating
    its description and tags.

    The update_analyzer method allows you to modify certain properties of an existing analyzer.
    The following properties can be updated:
    - Description: Update the analyzer's description
    - Tags: Add or update tags

USAGE:
    pytest test_sample_update_analyzer_async.py
"""

import uuid
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer_async import ContentUnderstandingPreparer, ContentUnderstandingClientTestBaseAsync
from azure.ai.contentunderstanding.models import ContentAnalyzer, ContentAnalyzerConfig


class TestSampleUpdateAnalyzerAsync(ContentUnderstandingClientTestBaseAsync):
    """Tests for sample_update_analyzer.py (async version)"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_update_analyzer_async(self, contentunderstanding_endpoint: str) -> None:
        """Test updating an analyzer's properties (async version).

        This test validates:
        1. Creating an initial analyzer
        2. Getting current analyzer state
        3. Updating analyzer description and tags
        4. Verifying updates were applied correctly

        08_UpdateAnalyzer.UpdateAnalyzerAsync()
        """
        # Skip this test if API is not available
        try:
            client = self.create_async_client(endpoint=contentunderstanding_endpoint)

            # Generate unique analyzer ID for this test
            analyzer_id = f"test_analyzer_{uuid.uuid4().hex}"
            print(f"[INFO] Creating test analyzer: {analyzer_id}")

            # Create initial analyzer
            initial_analyzer = ContentAnalyzer(
                base_analyzer_id="prebuilt-document",
                description="Initial description",
                config=ContentAnalyzerConfig(return_details=True),
                models={"completion": "gpt-4.1"},
                tags={"tag1": "tag1_initial_value"},
            )

            # Create the analyzer
            create_poller = await client.begin_create_analyzer(
                analyzer_id=analyzer_id, resource=initial_analyzer, allow_replace=True
            )
            create_result = await create_poller.result()
            assert create_result is not None, "Created analyzer should not be null"
            print("[PASS] Initial analyzer created successfully")

            # Get the current analyzer to preserve base analyzer ID
            current_analyzer = await client.get_analyzer(analyzer_id=analyzer_id)

            # Assertions for initial retrieval
            assert current_analyzer is not None, "Current analyzer response should not be null"
            print("[PASS] Current analyzer retrieved successfully")

            # Display current analyzer information
            print("\n[INFO] Current analyzer information:")
            current_description = getattr(current_analyzer, "description", None)
            current_tags = getattr(current_analyzer, "tags", {})
            print(f"  Description: {current_description}")
            print(f"  Tags: {', '.join(f'{k}={v}' for k, v in current_tags.items())}")

            # Verify initial state
            assert current_description == "Initial description", "Initial description should match"
            assert "tag1" in current_tags, "tag1 should exist"
            assert current_tags.get("tag1") == "tag1_initial_value", "tag1 value should match"
            print("[PASS] Initial analyzer state verified")

            # Create an updated analyzer with new description and tags
            base_id = getattr(current_analyzer, "base_analyzer_id", "prebuilt-document")
            updated_analyzer = ContentAnalyzer(
                base_analyzer_id=base_id,
                description="Updated description",
                tags={
                    "tag1": "tag1_updated_value",  # Update existing tag
                    "tag3": "tag3_value",  # Add new tag
                },
            )

            # Update the analyzer
            await client.update_analyzer(analyzer_id=analyzer_id, resource=updated_analyzer)
            print("[PASS] Analyzer updated successfully")

            # Verify the update
            updated = await client.get_analyzer(analyzer_id=analyzer_id)

            # Assertions for updated analyzer
            assert updated is not None, "Updated analyzer response should not be null"
            print("[PASS] Updated analyzer retrieved successfully")

            # Display updated analyzer information
            print("\n[INFO] Updated analyzer information:")
            updated_description = getattr(updated, "description", None)
            updated_tags = getattr(updated, "tags", {})
            print(f"  Description: {updated_description}")
            print(f"  Tags: {', '.join(f'{k}={v}' for k, v in updated_tags.items())}")

            # Verify description was updated
            assert updated_description == "Updated description", "Description should be updated"
            print("[PASS] Description updated correctly")

            # Verify tags were updated
            assert "tag1" in updated_tags, "tag1 should still exist"
            assert updated_tags.get("tag1") == "tag1_updated_value", "tag1 value should be updated"
            print("[PASS] tag1 updated correctly")

            # Verify tag3 was added
            assert "tag3" in updated_tags, "tag3 should be added"
            assert updated_tags.get("tag3") == "tag3_value", "tag3 value should match"
            print("[PASS] tag3 added correctly")

            print("\n[SUCCESS] All test_sample_update_analyzer_async assertions passed")

        except Exception as e:
            error_msg = str(e).lower()
            if "not supported" in error_msg or "not available" in error_msg or "not implemented" in error_msg:
                pytest.skip(f"API not available: {str(e)[:100]}")
            raise
        finally:
            # Clean up: delete the test analyzer
            try:
                if "analyzer_id" in locals() and "client" in locals():
                    await client.delete_analyzer(analyzer_id=analyzer_id)  # type: ignore
                    print(f"\n[INFO] Test analyzer deleted: {analyzer_id}")  # type: ignore
            except Exception as cleanup_error:
                print(f"\n[WARN] Could not delete test analyzer: {str(cleanup_error)[:100]}")

            try:
                if "client" in locals():
                    await client.close()
            except Exception:
                pass
