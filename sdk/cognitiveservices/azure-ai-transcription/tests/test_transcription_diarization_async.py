# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from preparer import TranscriptionClientTestBase, TranscriptionPreparer
from azure.ai.transcription.models import TranscriptionOptions, TranscriptionDiarizationOptions


class TestTranscriptionDiarizationAsync(TranscriptionClientTestBase):
    """Tests for async speaker diarization features."""

    @TranscriptionPreparer()
    @recorded_by_proxy_async
    async def test_transcribe_with_diarization_enabled_async(self, transcription_endpoint, transcription_test_audio_url):
        """Test async transcription with speaker diarization enabled."""
        client = self.create_async_client(endpoint=transcription_endpoint)
        
        async with client:
            # For diarization, ideally use multi-speaker audio, but single-speaker works for testing
            audio_url = transcription_test_audio_url
            
            # Enable diarization
            options = TranscriptionOptions(
                audio_url=audio_url,
                locales=["en-US"],
                diarization_options=TranscriptionDiarizationOptions(max_speakers=2)
            )
            
            result = await client.transcribe_from_url(audio_url, options=options)
            
            assert result is not None
            assert result.combined_phrases is not None
            assert result.phrases is not None
