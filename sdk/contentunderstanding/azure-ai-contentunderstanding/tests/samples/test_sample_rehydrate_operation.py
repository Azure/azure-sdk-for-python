# pylint: disable=line-too-long,useless-suppression
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
TEST FILE: test_sample_rehydrate_operation.py

DESCRIPTION:
    These live-only tests validate the sample_rehydrate_operation.py sample code.
    Keep this test in sync with samples/sample_rehydrate_operation.py.

USAGE:
    pytest test_sample_rehydrate_operation.py
"""

import tempfile
from pathlib import Path
from typing import Optional

import pytest
from devtools_testutils import is_live
from testpreparer import (
    ContentUnderstandingPreparer,
    ContentUnderstandingClientTestBase,
)
from azure.ai.contentunderstanding.models import AnalysisInput, AnalysisResult


class TestSampleRehydrateOperation(ContentUnderstandingClientTestBase):
    """Tests for sample_rehydrate_operation.py"""

    @ContentUnderstandingPreparer()
    def test_sample_rehydrate_operation(self, **kwargs) -> None:
        """Validate LRO continuation-token rehydration (sample_rehydrate_operation.py)."""
        if not is_live():
            pytest.skip("Live-only test: exercises LRO continuation token rehydration.")
        contentunderstanding_endpoint = kwargs.pop("contentunderstanding_endpoint")
        client = self.create_client(endpoint=contentunderstanding_endpoint)
        token_file_path: Optional[Path] = None

        try:
            # Keep in sync with samples/sample_rehydrate_operation.py
            # [START rehydrate_start_and_save_token]
            document_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/invoice.pdf"
            poller = client.begin_analyze(
                analyzer_id="prebuilt-read",
                inputs=[AnalysisInput(url=document_url)],
            )

            operation_id = poller.operation_id
            continuation_token = poller.continuation_token()
            assert operation_id
            assert continuation_token
            assert isinstance(continuation_token, str)

            token_file_path = Path(tempfile.gettempdir()) / f"cu-operation-{operation_id}.token"
            token_file_path.write_text(continuation_token, encoding="utf-8")
            # [END rehydrate_start_and_save_token]

            # [START rehydrate_resume_polling]
            saved_token = token_file_path.read_text(encoding="utf-8")
            assert saved_token == continuation_token

            rehydrated_poller = client.begin_analyze(
                analyzer_id="prebuilt-read",
                continuation_token=saved_token,
            )
            result: AnalysisResult = rehydrated_poller.result()
            # [END rehydrate_resume_polling]

            assert rehydrated_poller.done()
            assert result.contents
            assert result.contents[0].markdown
            print(f"[PASS] Rehydrated operation {operation_id} completed successfully")
        finally:
            if token_file_path is not None and token_file_path.exists():
                token_file_path.unlink()
