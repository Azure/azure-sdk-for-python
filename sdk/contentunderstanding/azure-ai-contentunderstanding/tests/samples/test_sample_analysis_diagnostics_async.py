# pylint: disable=line-too-long,useless-suppression
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
TEST FILE: test_sample_analysis_diagnostics_async.py

DESCRIPTION:
    These tests validate the sample_analysis_diagnostics_async.py sample code.

USAGE:
    pytest test_sample_analysis_diagnostics_async.py
"""

import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer_async import (
    ContentUnderstandingPreparer,
    ContentUnderstandingClientTestBaseAsync,
)
from azure.ai.contentunderstanding.models import AnalysisInput


pytestmark = pytest.mark.preview


class TestSampleAnalysisDiagnosticsAsync(ContentUnderstandingClientTestBaseAsync):
    """Tests for sample_analysis_diagnostics.py (async version)"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_analysis_diagnostics_async(self, **kwargs) -> None:
        contentunderstanding_endpoint = kwargs.pop("contentunderstanding_endpoint")
        client = self.create_preview_async_client(
            endpoint=contentunderstanding_endpoint
        )

        invoice_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-dotnet/main/ContentUnderstanding.Common/data/invoice.pdf"
        poller = await client.begin_analyze(
            analyzer_id="prebuilt-invoice",
            inputs=[AnalysisInput(url=invoice_url)],
        )
        result = await poller.result()

        assert poller.done()
        assert result.contents
        assert result.infos
        assert any(info.code == "LLMStats" for info in result.infos)
        assert all(
            info.message and info.message.strip()
            for info in result.infos
            if info.code == "LLMStats"
        )
        await client.close()
