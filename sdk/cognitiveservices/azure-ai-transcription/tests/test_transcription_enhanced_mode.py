# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from devtools_testutils import recorded_by_proxy
from preparer import TranscriptionClientTestBase, TranscriptionPreparer
from azure.ai.transcription.models import TranscriptionOptions, EnhancedModeProperties


class TestTranscriptionEnhancedMode(TranscriptionClientTestBase):
    """Tests for enhanced mode and advanced transcription features."""

    @TranscriptionPreparer()
    @recorded_by_proxy
    def test_transcribe_enhanced_mode_with_prompt(self, transcription_endpoint, transcription_test_audio_url):
        """Test transcription with enhanced mode and prompt."""
        client = self.create_client(endpoint=transcription_endpoint)
        
        audio_url = transcription_test_audio_url
        
        # Use enhanced mode with prompts
        options = TranscriptionOptions(
            audio_url=audio_url,
            locales=["en-US"],
            enhanced_mode=EnhancedModeProperties(
                prompt=["This is a technical discussion about Azure services"],
                task="transcribe"
            )
        )
        
        result = client.transcribe_from_url(audio_url, options=options)
        
        assert result is not None
        assert result.combined_phrases is not None
        assert len(result.combined_phrases) > 0
        assert result.combined_phrases[0].text is not None
