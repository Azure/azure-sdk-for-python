# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from preparer import TranscriptionClientTestBase, TranscriptionPreparer
from azure.ai.transcription.models import TranscriptionOptions


class TestTranscriptionBasicAsync(TranscriptionClientTestBase):
    """Tests for basic asynchronous transcription functionality."""

    @TranscriptionPreparer()
    @recorded_by_proxy_async
    async def test_transcribe_url_basic_async(self, transcription_endpoint, transcription_test_audio_url):
        """Test basic async transcription from a URL."""
        client = self.create_async_client(endpoint=transcription_endpoint)
        
        async with client:
            audio_url = transcription_test_audio_url
            
            result = await client.transcribe_from_url(audio_url)
            
            # Verify response structure
            assert result is not None
            assert result.combined_phrases is not None
            assert len(result.combined_phrases) > 0
            assert result.combined_phrases[0].text is not None

    @TranscriptionPreparer()
    @recorded_by_proxy_async
    async def test_transcribe_with_custom_locale_async(self, transcription_endpoint, transcription_test_audio_url):
        """Test async transcription from URL with custom locale."""
        client = self.create_async_client(endpoint=transcription_endpoint)
        
        async with client:
            audio_url = transcription_test_audio_url
            
            # Create transcription options
            options = TranscriptionOptions(
                audio_url=audio_url,
                locales=["en-US"]
            )
            
            result = await client.transcribe_from_url(audio_url, options=options)
            
            assert result is not None
            assert result.combined_phrases is not None
            assert len(result.combined_phrases) > 0
            assert result.combined_phrases[0].text is not None

    @TranscriptionPreparer()
    @recorded_by_proxy_async
    async def test_transcribe_result_structure_async(self, transcription_endpoint, transcription_test_audio_url):
        """Test that async transcription result has expected structure."""
        client = self.create_async_client(endpoint=transcription_endpoint)
        
        async with client:
            audio_url = transcription_test_audio_url
            
            result = await client.transcribe_from_url(audio_url)
            
            # Verify result structure
            assert result is not None
            assert hasattr(result, 'combined_phrases')
            assert hasattr(result, 'phrases')
            assert hasattr(result, 'duration_milliseconds')
            
            # Verify combined_phrases structure
            assert len(result.combined_phrases) > 0
            assert hasattr(result.combined_phrases[0], 'text')
            assert result.combined_phrases[0].text is not None
            
            # If phrases exist, verify their structure
            if result.phrases:
                phrase = result.phrases[0]
                assert hasattr(phrase, 'text')
