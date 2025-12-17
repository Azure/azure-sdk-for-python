# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_list_analyzers.py

DESCRIPTION:
    These tests validate the sample_list_analyzers.py sample code.
    This sample demonstrates listing all available analyzers (prebuilt and custom).

USAGE:
    pytest test_sample_list_analyzers.py
"""

import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import ContentUnderstandingPreparer, ContentUnderstandingClientTestBase


class TestSampleListAnalyzers(ContentUnderstandingClientTestBase):
    """Tests for sample_list_analyzers.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_list_analyzers(self, azure_content_understanding_endpoint: str) -> None:
        """Test listing all available analyzers.

        This test validates:
        1. Listing all analyzers using list_analyzers
        2. Counting prebuilt vs custom analyzers
        3. Displaying analyzer details

        07_ListAnalyzers.ListAnalyzersAsync()
        """
        client = self.create_client(endpoint=azure_content_understanding_endpoint)

        # List all analyzers
        analyzers = []
        for analyzer in client.list_analyzers():
            analyzers.append(analyzer)

        # Assertions
        assert analyzers is not None, "Analyzers list should not be null"
        assert len(analyzers) > 0, "Should have at least one analyzer"
        print(f"[PASS] Found {len(analyzers)} analyzer(s)")

        # Count prebuilt vs custom analyzers
        prebuilt_count = sum(
            1 for a in analyzers if hasattr(a, "analyzer_id") and getattr(a, "analyzer_id", "").startswith("prebuilt-")
        )
        custom_count = sum(
            1
            for a in analyzers
            if hasattr(a, "analyzer_id") and not getattr(a, "analyzer_id", "").startswith("prebuilt-")
        )

        print(f"[INFO] Prebuilt analyzers: {prebuilt_count}")
        print(f"[INFO] Custom analyzers: {custom_count}")

        # Verify counts
        assert prebuilt_count >= 0, "Prebuilt count should be >= 0"
        assert custom_count >= 0, "Custom count should be >= 0"
        assert len(analyzers) == prebuilt_count + custom_count, "Total count should equal prebuilt + custom count"
        print(f"[PASS] Count breakdown: {prebuilt_count} prebuilt, {custom_count} custom")

        # Verify we have some prebuilt analyzers
        assert prebuilt_count > 0, "Should have at least one prebuilt analyzer"
        print(f"[PASS] Prebuilt analyzers found: {prebuilt_count}")

        # Display details for first 10 analyzers (for test output brevity)
        print("\n[INFO] Analyzer details (first 10):")
        for i, analyzer in enumerate(analyzers[:10]):
            analyzer_id = getattr(analyzer, "analyzer_id", "unknown")
            description = getattr(analyzer, "description", "(none)")
            status = getattr(analyzer, "status", "unknown")

            print(f"\n  [{i+1}] ID: {analyzer_id}")
            if description and description != "(none)":
                print(f"      Description: {description[:80]}{'...' if len(description) > 80 else ''}")
            else:
                print(f"      Description: (none)")
            print(f"      Status: {status}")

            if analyzer_id.startswith("prebuilt-"):
                print("      Type: Prebuilt analyzer")
            else:
                print("      Type: Custom analyzer")

        if len(analyzers) > 10:
            print(f"\n[INFO] ... and {len(analyzers) - 10} more analyzer(s)")

        # Verify each analyzer has required properties
        valid_analyzers = 0
        analyzers_with_description = 0

        for analyzer in analyzers:
            assert hasattr(analyzer, "analyzer_id"), "Analyzer should have analyzer_id property"
            analyzer_id = getattr(analyzer, "analyzer_id", None)
            assert analyzer_id is not None, "Analyzer ID should not be null"
            assert len(analyzer_id) > 0, "Analyzer ID should not be empty"

            # Verify analyzer ID format (should not contain spaces)
            assert " " not in analyzer_id, f"Analyzer ID should not contain spaces: {analyzer_id}"

            valid_analyzers += 1

            # Track optional properties
            description = getattr(analyzer, "description", None)
            if description and len(str(description).strip()) > 0:
                analyzers_with_description += 1

        assert len(analyzers) == valid_analyzers, "All analyzers should have valid IDs"
        print(f"\n[PASS] All {valid_analyzers} analyzers have valid IDs")
        print(f"[INFO] Analyzers with description: {analyzers_with_description}")
        print("\n[SUCCESS] All test_sample_list_analyzers assertions passed")
