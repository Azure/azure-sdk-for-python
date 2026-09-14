# pylint: disable=line-too-long,useless-suppression
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
TEST FILE: test_sample_detect_signatures_async.py

DESCRIPTION:
    These tests validate the sample_detect_signatures_async.py sample code.

USAGE:
    pytest test_sample_detect_signatures_async.py
"""

import os

import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer_async import (
    ContentUnderstandingPreparer,
    ContentUnderstandingClientTestBaseAsync,
)
from azure.ai.contentunderstanding.models import DocumentContent


pytestmark = pytest.mark.preview
SAMPLES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "samples"
)


class TestSampleDetectSignaturesAsync(ContentUnderstandingClientTestBaseAsync):
    """Tests for sample_detect_signatures.py (async version)"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_detect_signatures_async(self, **kwargs) -> None:
        contentunderstanding_endpoint = kwargs.pop("contentunderstanding_endpoint")
        client = self.create_preview_async_client(
            endpoint=contentunderstanding_endpoint
        )

        file_path = os.path.join(SAMPLES_DIR, "sample_files", "sample_signature.png")
        with open(file_path, "rb") as f:
            image_bytes = f.read()

        poller = await client.begin_analyze_binary(
            analyzer_id="prebuilt-layout", binary_input=image_bytes
        )
        result = await poller.result()
        document = next(
            content
            for content in result.contents
            if isinstance(content, DocumentContent)
        )

        assert poller.done()
        assert len(document.signatures) >= 2
        assert all(
            signature.id and signature.id.strip() for signature in document.signatures
        )
        assert all(
            signature.source and signature.source.strip()
            for signature in document.signatures
        )
        await client.close()
