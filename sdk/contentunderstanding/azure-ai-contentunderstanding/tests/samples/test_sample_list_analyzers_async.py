# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_list_analyzers_async.py

DESCRIPTION:
    These tests validate the sample_list_analyzers.py sample code (async version).
    This sample demonstrates how to list all available analyzers in your Microsoft Foundry
    resource, including both prebuilt and custom analyzers.

    The list_analyzers method returns all analyzers in your resource, including:
    - Prebuilt analyzers: System-provided analyzers like prebuilt-documentSearch, prebuilt-invoice, etc.
    - Custom analyzers: Analyzers you've created

    This is useful for:
    - Discovery: See what analyzers are available in your resource
    - Management: Get an overview of all your custom analyzers
    - Debugging: Verify that analyzers were created successfully

USAGE:
    pytest test_sample_list_analyzers_async.py
"""

import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer_async import ContentUnderstandingPreparer, ContentUnderstandingClientTestBaseAsync


class TestSampleListAnalyzersAsync(ContentUnderstandingClientTestBaseAsync):
    """Tests for sample_list_analyzers.py (async version)"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_list_analyzers_async(self, contentunderstanding_endpoint: str) -> None:
        """Test listing all available analyzers (async version).

        This test validates:
        1. Listing all analyzers using list_analyzers
        2. Counting prebuilt vs custom analyzers
        3. Displaying analyzer details
        """
        client = self.create_async_client(endpoint=contentunderstanding_endpoint)

        # List all analyzers
        analyzers = [analyzer async for analyzer in client.list_analyzers()]

        # Assertions
        assert analyzers is not None, "Analyzers list should not be null"
        assert len(analyzers) > 0, "Should have at least one analyzer"
        print(f"[PASS] Found {len(analyzers)} analyzer(s)")

        # Count prebuilt vs custom analyzers
        prebuilt_count = sum(
            1 for a in analyzers if hasattr(a, "analyzer_id") and getattr(a, "analyzer_id", "").startswith("prebuilt-")
        )
        custom_count = len(analyzers) - prebuilt_count

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

        # Display details for each analyzer
        print("\n[INFO] Analyzer details:")
        for analyzer in analyzers:
            analyzer_id = getattr(analyzer, "analyzer_id", "unknown")
            description = getattr(analyzer, "description", "(none)")
            status = getattr(analyzer, "status", "unknown")

            print(f"  ID: {analyzer_id}")
            if description and description != "(none)":
                print(f"  Description: {description[:80]}{'...' if len(description) > 80 else ''}")
            else:
                print(f"  Description: (none)")
            print(f"  Status: {status}")

            if analyzer_id.startswith("prebuilt-"):
                print("  Type: Prebuilt analyzer")
            else:
                print("  Type: Custom analyzer")

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

        await client.close()
        print("\n[SUCCESS] All test_sample_list_analyzers_async assertions passed")
