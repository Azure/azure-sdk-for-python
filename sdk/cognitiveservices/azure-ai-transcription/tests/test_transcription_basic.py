# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from devtools_testutils import recorded_by_proxy
from preparer import TranscriptionClientTestBase, TranscriptionPreparer
from azure.ai.transcription.models import TranscriptionOptions


class TestTranscriptionBasic(TranscriptionClientTestBase):
    """Basic transcription functionality tests."""

    @TranscriptionPreparer()
    @recorded_by_proxy
    def test_transcribe_url_basic(self, transcription_endpoint, transcription_test_audio_url):
        """Test basic transcription from a URL."""
        client = self.create_client(endpoint=transcription_endpoint)
        
        audio_url = transcription_test_audio_url
        result = client.transcribe_from_url(audio_url)
        
        # Verify response structure
        assert result is not None
        assert result.combined_phrases is not None
        assert len(result.combined_phrases) > 0
        assert result.phrases is not None

    @TranscriptionPreparer()
    @recorded_by_proxy
    def test_transcribe_with_custom_locale(self, transcription_endpoint, transcription_test_audio_url):
        """Test transcription with a specific locale."""
        client = self.create_client(endpoint=transcription_endpoint)
        
        audio_url = transcription_test_audio_url
        options = TranscriptionOptions(
            audio_url=audio_url,
            locales=["en-US"]
        )
        
        result = client.transcribe_from_url(audio_url, options=options)
        
        assert result is not None
        assert result.combined_phrases is not None
        assert len(result.combined_phrases) > 0

    @TranscriptionPreparer()
    @recorded_by_proxy
    def test_transcribe_result_structure(self, transcription_endpoint, transcription_test_audio_url):
        """Test that the transcription result has the expected structure."""
        client = self.create_client(endpoint=transcription_endpoint)
        
        audio_url = transcription_test_audio_url
        result = client.transcribe_from_url(audio_url)
        
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
