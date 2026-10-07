# pylint: disable=line-too-long,useless-suppression
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
TEST FILE: test_service_version.py

DESCRIPTION:
    Service-version / back-compatibility coverage for ContentUnderstandingClient.

    The beta package defaults to the preview API version ``2026-06-01-preview`` but must
    remain back-compatible with the GA version ``2025-11-01``:

    - The client default API version is the latest preview.
    - The GA API version can still be selected and used (back-compat).
    - Preview-only operations (inline analysis returning ``ContentAnalyzerInlineResponse``)
      work against the preview API version.

    The default/override assertions run offline; the end-to-end analysis assertions are
    live-only (the preview surface is not recorded).

USAGE:
    pytest test_service_version.py
    AZURE_TEST_RUN_LIVE=true pytest test_service_version.py
"""

import os

import pytest
from devtools_testutils import is_live
from testpreparer import (
    ContentUnderstandingPreparer,
    ContentUnderstandingClientTestBase,
    GA_API_VERSION,
    PREVIEW_API_VERSION,
)
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentunderstanding.models import AnalysisInput, DocumentContent

TESTS_DIR = os.path.dirname(__file__)
_INLINE_INPUT_URL = (
    "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"
)


class TestServiceVersion(ContentUnderstandingClientTestBase):
    """Service-version selection and GA back-compatibility."""

    def test_default_client_uses_latest_preview_service_version(self) -> None:
        """The client default API version is the latest preview (offline check)."""
        client = ContentUnderstandingClient(
            endpoint="https://sanitized.services.ai.azure.com",
            credential=AzureKeyCredential("fake-key"),
        )
        assert client._config.api_version == PREVIEW_API_VERSION  # pylint: disable=protected-access

    def test_ga_service_version_can_be_selected(self) -> None:
        """The GA API version can still be explicitly selected (offline back-compat check)."""
        client = ContentUnderstandingClient(
            endpoint="https://sanitized.services.ai.azure.com",
            credential=AzureKeyCredential("fake-key"),
            api_version=GA_API_VERSION,
        )
        assert client._config.api_version == GA_API_VERSION  # pylint: disable=protected-access

    @pytest.mark.ga
    @ContentUnderstandingPreparer()
    def test_get_defaults_supports_configured_service_version(self, **kwargs) -> None:
        """get_defaults works for the matrix API version (GA and preview passes)."""
        if not is_live():
            pytest.skip("Live-only test: exercises the live service.")
        endpoint = kwargs.pop("contentunderstanding_endpoint")
        client = self.create_client(endpoint=endpoint)

        defaults = client.get_defaults()

        assert defaults is not None

    @pytest.mark.ga
    @ContentUnderstandingPreparer()
    def test_analyze_binary_supports_configured_service_version(self, **kwargs) -> None:
        """Binary analysis works for the matrix API version (GA and preview passes)."""
        if not is_live():
            pytest.skip("Live-only test: exercises the live service.")
        endpoint = kwargs.pop("contentunderstanding_endpoint")
        client = self.create_client(endpoint=endpoint)

        file_path = os.path.join(TESTS_DIR, "test_data", "sample_invoice.pdf")
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        poller = client.begin_analyze_binary(analyzer_id="prebuilt-documentSearch", binary_input=file_bytes)
        result = poller.result()

        assert poller.done()
        assert result is not None
        assert result.contents

    @pytest.mark.preview
    @ContentUnderstandingPreparer()
    def test_analyze_inline_supports_preview_service_version(self, **kwargs) -> None:
        """Preview-only inline analysis returns ContentAnalyzerInlineResponse."""
        if not is_live():
            pytest.skip("Live-only test: exercises preview features not recorded.")
        endpoint = kwargs.pop("contentunderstanding_endpoint")
        client = self.create_preview_client(endpoint=endpoint)

        response = client.analyze_inline(
            analyzer_id="prebuilt-layout",
            inputs=[AnalysisInput(url=_INLINE_INPUT_URL)],
        )

        assert response is not None
        assert response.result is not None
        assert response.result.contents
        assert any(isinstance(c, DocumentContent) for c in response.result.contents)
