# pylint: disable=line-too-long,useless-suppression
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
TEST FILE: test_sample_extract_document_metadata.py

DESCRIPTION:
    These tests validate the sample_extract_document_metadata.py sample code.

USAGE:
    pytest test_sample_extract_document_metadata.py
"""

import os

import pytest
from devtools_testutils import is_live, recorded_by_proxy
from testpreparer import (
    ContentUnderstandingPreparer,
    ContentUnderstandingClientTestBase,
)
from azure.ai.contentunderstanding.models import DocumentContent


pytestmark = pytest.mark.preview
SAMPLES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "samples"
)


class TestSampleExtractDocumentMetadata(ContentUnderstandingClientTestBase):
    """Tests for sample_extract_document_metadata.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_extract_pdf_metadata(self, **kwargs) -> None:
        contentunderstanding_endpoint = kwargs.pop("contentunderstanding_endpoint")
        client = self.create_preview_client(endpoint=contentunderstanding_endpoint)

        file_path = os.path.join(SAMPLES_DIR, "sample_files", "sample_metadata.pdf")
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()

        poller = client.begin_analyze_binary(
            analyzer_id="prebuilt-layout", binary_input=pdf_bytes
        )
        result = poller.result()
        document = next(
            content
            for content in result.contents
            if isinstance(content, DocumentContent)
        )

        assert poller.done()
        assert document.metadata
        assert document.metadata["author"] == "Contoso Metadata Team"
        assert document.metadata["contentType"] == "application/pdf"
        assert document.metadata["language"] == "en-US"
        assert document.metadata["pageCount"] == "1"
        assert document.metadata["title"] == "Contoso Metadata Extraction Sample"

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_extract_docx_metadata(self, **kwargs) -> None:
        contentunderstanding_endpoint = kwargs.pop("contentunderstanding_endpoint")
        client = self.create_preview_client(endpoint=contentunderstanding_endpoint)

        file_path = os.path.join(SAMPLES_DIR, "sample_files", "sample_metadata.docx")
        with open(file_path, "rb") as f:
            docx_bytes = f.read()

        poller = client.begin_analyze_binary(
            analyzer_id="prebuilt-layout", binary_input=docx_bytes
        )
        result = poller.result()
        document = next(
            content
            for content in result.contents
            if isinstance(content, DocumentContent)
        )

        assert poller.done()
        assert document.metadata
        assert document.metadata["author"] == "Contoso Metadata Team"
        assert document.metadata["characterCount"] == "207"
        assert (
            document.metadata["contentType"]
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        assert document.metadata["createdAt"] == "2026-07-16T19:00:00Z"
        assert document.metadata["lastModifiedAt"] == "2026-07-16T20:30:00Z"
        assert document.metadata["lastModifiedBy"]
        if is_live():
            assert document.metadata["lastModifiedBy"] == "Megan Bowen"
        assert document.metadata["pageCount"] == "1"
        assert document.metadata["title"] == "Contoso Metadata Extraction Sample"
        assert document.metadata["wordCount"] == "29"
