# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from preparer import TranscriptionClientTestBase, TranscriptionPreparer


class TestTranscriptionUrlAsync(TranscriptionClientTestBase):
    """Tests for async URL-based transcription scenarios."""

    @TranscriptionPreparer()
    @recorded_by_proxy_async
    async def test_transcribe_from_public_url_async(self, transcription_endpoint, transcription_test_audio_url):
        """Test async transcription from a public URL."""
        client = self.create_async_client(endpoint=transcription_endpoint)
        
        async with client:
            audio_url = transcription_test_audio_url
            
            result = await client.transcribe_from_url(audio_url)
            
            assert result is not None
            assert result.combined_phrases is not None
            assert len(result.combined_phrases) > 0
            assert result.combined_phrases[0].text is not None
