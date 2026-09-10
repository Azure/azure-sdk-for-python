# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_analyze_chunking.py

DESCRIPTION:
    Tests for sample_analyze_chunking.py.
"""

import pytest
import os
import uuid
from typing import Dict
from devtools_testutils import recorded_by_proxy
from testpreparer import (
    ContentUnderstandingPreparer,
    ContentUnderstandingClientTestBase,
)
from azure.ai.contentunderstanding.models import (
    AnalysisInput,
    ContentAnalyzer,
    ContentAnalyzerConfig,
    SemanticChunkingStrategy,
    ChunkingStrategyKind,
)


pytestmark = pytest.mark.preview


class TestSampleAnalyzeChunking(ContentUnderstandingClientTestBase):
    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_analyze_chunking(self, contentunderstanding_endpoint: str, **kwargs) -> Dict[str, str]:
        variables = kwargs.pop("variables", {})
        client = self.create_preview_client(endpoint=contentunderstanding_endpoint)
        profile = self.get_model_profile(api_version="2026-06-01-preview")
        analyzer_id = variables.setdefault("chunkingAnalyzerId", f"test_chunking_{uuid.uuid4().hex[:16]}")

        analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Analyzer with semantic chunking",
            config=ContentAnalyzerConfig(
                return_details=True,
                enable_layout=True,
                chunking_strategy=SemanticChunkingStrategy(max_tokens=300),
            ),
            models={"completion": profile.completion_model},
        )

        try:
            client.begin_create_analyzer(analyzer_id, analyzer, allow_replace=True).result()
            created = client.get_analyzer(analyzer_id)

            assert created.config is not None
            assert created.config.chunking_strategy is not None
            assert created.config.chunking_strategy.kind == ChunkingStrategyKind.SEMANTIC
            if isinstance(created.config.chunking_strategy, SemanticChunkingStrategy):
                assert created.config.chunking_strategy.max_tokens == 300

            tests_dir = os.path.dirname(os.path.dirname(__file__))
            file_path = os.path.join(tests_dir, "test_data", "sample_invoice.pdf")
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            result = client.begin_analyze(
                analyzer_id=analyzer_id,
                inputs=[AnalysisInput(data=file_bytes)],
            ).result()
            assert result.contents and len(result.contents) > 0

            doc = result.contents[0]
            assert hasattr(doc, "chunks")
            chunks = doc.chunks or []
            print(f"[INFO] chunk count: {len(chunks)}")
            for chunk in chunks:
                assert chunk.spans is not None
                assert len(chunk.spans) > 0
                for span in chunk.spans:
                    assert span.length > 0
        finally:
            client.delete_analyzer(analyzer_id)

        return variables
