# pylint: disable=line-too-long,useless-suppression
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
TEST FILE: test_sample_classify_in_page_segments.py

DESCRIPTION:
    These tests validate the sample_classify_in_page_segments.py sample code.

USAGE:
    pytest test_sample_classify_in_page_segments.py
"""

import os
from typing import Dict
import uuid

import pytest
from devtools_testutils import is_live, recorded_by_proxy
from testpreparer import (
    ContentUnderstandingPreparer,
    ContentUnderstandingClientTestBase,
)
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentCategoryDefinition,
    DocumentContent,
)


pytestmark = pytest.mark.preview
SAMPLES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "samples"
)


class TestSampleClassifyInPageSegments(ContentUnderstandingClientTestBase):
    """Tests for sample_classify_in_page_segments.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_classify_in_page_segments(self, **kwargs) -> Dict[str, str]:
        contentunderstanding_endpoint = kwargs.pop("contentunderstanding_endpoint")
        variables = kwargs.pop("variables", {})
        client = self.create_preview_client(endpoint=contentunderstanding_endpoint)
        profile = self.get_model_profile(api_version="2026-06-01-preview")
        analyzer_id = variables.setdefault(
            "inPageClassifierId", f"test_in_page_classifier_{uuid.uuid4().hex[:16]}"
        )

        config = ContentAnalyzerConfig(
            return_details=True,
            enable_segment=True,
            allow_in_page_segments=True,
            estimate_field_source_and_confidence=True,
            content_categories={
                "Invoice": ContentCategoryDefinition(
                    description="An invoice requesting payment for goods or services, with line items, totals, and payment terms."
                ),
                "BankStatement": ContentCategoryDefinition(
                    description="A bank account statement listing balances, deposits, withdrawals, fees, and transactions."
                ),
            },
        )
        classifier = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Classify financial documents that may share a page.",
            config=config,
            models={"completion": profile.completion_model},
        )

        create_poller = client.begin_create_analyzer(
            analyzer_id=analyzer_id, resource=classifier
        )
        create_poller.result()
        try:
            file_path = os.path.join(
                SAMPLES_DIR, "sample_files", "mixed_financial_docs_in_page.pdf"
            )
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            analyze_poller = client.begin_analyze_binary(
                analyzer_id=analyzer_id, binary_input=file_bytes
            )
            result = analyze_poller.result()
            document = next(
                content
                for content in result.contents
                if isinstance(content, DocumentContent)
            )

            assert analyze_poller.done()
            assert document.start_page_number == 1
            assert document.end_page_number == 1
            assert len(document.segments) == 2
            assert {segment.category for segment in document.segments} == {
                "Invoice",
                "BankStatement",
            }
            assert all(
                segment.start_page_number == 1 and segment.end_page_number == 1
                for segment in document.segments
            )
            assert all(
                segment.source and segment.source.strip()
                for segment in document.segments
            )
            assert all(
                segment.span and segment.span.length > 0
                for segment in document.segments
            )
            if is_live():
                assert len({segment.source for segment in document.segments}) == 2

            invoice_segment = next(
                segment
                for segment in document.segments
                if segment.category == "Invoice"
            )
            bank_statement_segment = next(
                segment
                for segment in document.segments
                if segment.category == "BankStatement"
            )
            assert invoice_segment.span.offset == 0
            assert invoice_segment.span.length == 687
            assert bank_statement_segment.span.offset == 687
            assert bank_statement_segment.span.length == 964
            assert (
                invoice_segment.span.offset + invoice_segment.span.length
                == bank_statement_segment.span.offset
            )
            assert (
                bank_statement_segment.span.offset + bank_statement_segment.span.length
                == len(document.markdown)
            )
            assert (
                "INVOICE"
                in document.markdown[
                    invoice_segment.span.offset : invoice_segment.span.offset
                    + invoice_segment.span.length
                ]
            )
            assert (
                "CONTOSO BANK"
                in document.markdown[
                    bank_statement_segment.span.offset : bank_statement_segment.span.offset
                    + bank_statement_segment.span.length
                ]
            )
        finally:
            client.delete_analyzer(analyzer_id=analyzer_id)

        return variables
