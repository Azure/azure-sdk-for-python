# pylint: disable=line-too-long,useless-suppression
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
TEST FILE: test_service_version_async.py

DESCRIPTION:
    Async service-version / back-compatibility coverage for the async
    ContentUnderstandingClient. See test_service_version.py for details.

USAGE:
    pytest test_service_version_async.py
    AZURE_TEST_RUN_LIVE=true pytest test_service_version_async.py
"""

import os

import pytest
from devtools_testutils import is_live
from testpreparer import GA_API_VERSION, PREVIEW_API_VERSION
from testpreparer_async import ContentUnderstandingClientTestBaseAsync
from testpreparer import ContentUnderstandingPreparer
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalysisInput, DocumentContent

TESTS_DIR = os.path.dirname(__file__)
_INLINE_INPUT_URL = (
    "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"
)


class TestServiceVersionAsync(ContentUnderstandingClientTestBaseAsync):
    """Async service-version selection and GA back-compatibility."""

    def test_default_client_uses_latest_preview_service_version(self) -> None:
        """The async client default API version is the latest preview (offline check)."""
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
    async def test_get_defaults_supports_configured_service_version(self, **kwargs) -> None:
        """get_defaults works for the matrix API version (GA and preview passes)."""
        if not is_live():
            pytest.skip("Live-only test: exercises the live service.")
        endpoint = kwargs.pop("contentunderstanding_endpoint")
        client = self.create_async_client(endpoint=endpoint)
        async with client:
            defaults = await client.get_defaults()
        assert defaults is not None

    @pytest.mark.ga
    @ContentUnderstandingPreparer()
    async def test_analyze_binary_supports_configured_service_version(self, **kwargs) -> None:
        """Binary analysis works for the matrix API version (GA and preview passes)."""
        if not is_live():
            pytest.skip("Live-only test: exercises the live service.")
        endpoint = kwargs.pop("contentunderstanding_endpoint")
        client = self.create_async_client(endpoint=endpoint)

        file_path = os.path.join(TESTS_DIR, "test_data", "sample_invoice.pdf")
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        async with client:
            poller = await client.begin_analyze_binary(analyzer_id="prebuilt-documentSearch", binary_input=file_bytes)
            result = await poller.result()

        assert poller.done()
        assert result is not None
        assert result.contents

    @pytest.mark.preview
    @ContentUnderstandingPreparer()
    async def test_analyze_inline_supports_preview_service_version(self, **kwargs) -> None:
        """Preview-only inline analysis returns ContentAnalyzerInlineResponse."""
        if not is_live():
            pytest.skip("Live-only test: exercises preview features not recorded.")
        endpoint = kwargs.pop("contentunderstanding_endpoint")
        client = self.create_preview_async_client(endpoint=endpoint)

        async with client:
            response = await client.analyze_inline(
                analyzer_id="prebuilt-layout",
                inputs=[AnalysisInput(url=_INLINE_INPUT_URL)],
            )

        assert response is not None
        assert response.result is not None
        assert response.result.contents
        assert any(isinstance(c, DocumentContent) for c in response.result.contents)
