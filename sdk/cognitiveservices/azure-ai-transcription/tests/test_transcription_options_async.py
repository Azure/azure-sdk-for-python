# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from preparer import TranscriptionClientTestBase, TranscriptionPreparer
from azure.ai.transcription.models import TranscriptionOptions, PhraseListProperties


class TestTranscriptionOptionsAsync(TranscriptionClientTestBase):
    """Tests for async transcription configuration options and parameters."""

    @TranscriptionPreparer()
    @recorded_by_proxy_async
    async def test_transcribe_profanity_filter_masked_async(self, transcription_endpoint, transcription_test_audio_url):
        """Test async transcription with masked profanity filter."""
        client = self.create_async_client(endpoint=transcription_endpoint)
        
        async with client:
            audio_url = transcription_test_audio_url
            
            options = TranscriptionOptions(
                audio_url=audio_url,
                locales=["en-US"],
                profanity_filter_mode="Masked"
            )
            
            result = await client.transcribe_from_url(audio_url, options=options)
            
            assert result is not None
            assert result.combined_phrases is not None
            assert len(result.combined_phrases) > 0

    @TranscriptionPreparer()
    @recorded_by_proxy_async
    async def test_transcribe_with_phrase_list_async(self, transcription_endpoint, transcription_test_audio_url):
        """Test async transcription with custom phrase list."""
        client = self.create_async_client(endpoint=transcription_endpoint)
        
        async with client:
            audio_url = transcription_test_audio_url
            
            # Add custom phrases for better recognition
            options = TranscriptionOptions(
                audio_url=audio_url,
                locales=["en-US"],
                phrase_list=PhraseListProperties(
                    phrases=["Azure", "Cognitive Services", "Speech SDK"],
                    biasing_weight=1.0
                )
            )
            
            result = await client.transcribe_from_url(audio_url, options=options)
            
            assert result is not None
            assert result.combined_phrases is not None
            assert len(result.combined_phrases) > 0
            assert result.combined_phrases[0].text is not None

    @TranscriptionPreparer()
    @recorded_by_proxy_async
    async def test_transcribe_multiple_locales_async(self, transcription_endpoint, transcription_test_audio_url):
        """Test async transcription with multiple language locales."""
        client = self.create_async_client(endpoint=transcription_endpoint)
        
        async with client:
            # For multi-locale, ideally use multilingual audio, but single language works for testing
            audio_url = transcription_test_audio_url
            
            # Specify multiple locales for auto-detection
            options = TranscriptionOptions(
                audio_url=audio_url,
                locales=["en-US", "es-ES", "fr-FR"]
            )
            
            result = await client.transcribe_from_url(audio_url, options=options)
            
            assert result is not None
            assert result.combined_phrases is not None
            assert len(result.combined_phrases) > 0
            assert result.combined_phrases[0].text is not None
