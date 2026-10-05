# pylint: disable=line-too-long,useless-suppression
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
TEST FILE: test_sample_content_source.py

DESCRIPTION:
    These live-only tests validate the sample_content_source.py sample code.
    Keep this test in sync with samples/sample_content_source.py.

USAGE:
    pytest test_sample_content_source.py
"""

from typing import cast

import pytest
from devtools_testutils import is_live
from testpreparer import (
    ContentUnderstandingPreparer,
    ContentUnderstandingClientTestBase,
)
from azure.ai.contentunderstanding.models import AnalysisInput, DocumentContent


class TestSampleContentSource(ContentUnderstandingClientTestBase):
    """Tests for sample_content_source.py"""

    @ContentUnderstandingPreparer()
    def test_sample_content_source(self, **kwargs) -> None:
        """Validate field grounding sources as plain strings (sample_content_source.py)."""
        if not is_live():
            pytest.skip("Live-only test: exercises field grounding sources.")
        contentunderstanding_endpoint = kwargs.pop("contentunderstanding_endpoint")
        client = self.create_client(endpoint=contentunderstanding_endpoint)

        # Keep in sync with samples/sample_content_source.py
        # [START content_source_from_analysis]
        invoice_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/invoice.pdf"

        poller = client.begin_analyze(
            analyzer_id="prebuilt-invoice",
            inputs=[AnalysisInput(url=invoice_url)],
        )
        result = poller.result()
        document = cast(DocumentContent, result.contents[0])

        fields_with_source = 0
        for _field_name, field in (document.fields or {}).items():
            if field.source:
                fields_with_source += 1
                assert isinstance(field.source, str)
                assert field.source.strip()
                # Keep the wire-format string as-is. Split only if you need each region separately.
                regions = [region.strip() for region in field.source.split(";") if region.strip()]
                assert regions
                assert all(region in field.source for region in regions)
        # [END content_source_from_analysis]

        assert poller.done()
        assert document.fields
        assert fields_with_source > 0, "Expected at least one field with a grounding source string"
        print(f"[PASS] Found {fields_with_source} field(s) with grounding source strings")
