# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os
import pytest
from devtools_testutils import recorded_by_proxy
from preparer import TranscriptionClientTestBase, TranscriptionPreparer
from azure.ai.transcription.models import TranscriptionOptions, TranscriptionContent


class TestTranscriptionFile(TranscriptionClientTestBase):
    """Tests for file-based transcription and audio format handling."""

    @TranscriptionPreparer()
    @recorded_by_proxy
    def test_transcribe_wav_file(self, transcription_endpoint):
        """Test transcription from a local WAV file."""
        client = self.create_client(endpoint=transcription_endpoint)
        
        # Path to test audio file
        test_audio_path = os.path.join(os.path.dirname(__file__), "assets", "audio.wav")
        
        # Skip test if audio file doesn't exist
        if not os.path.exists(test_audio_path):
            pytest.skip(f"Test audio file not found: {test_audio_path}")
        
        with open(test_audio_path, "rb") as audio_file:
            # Create transcription content with audio file and options
            content = TranscriptionContent(
                definition=TranscriptionOptions(locales=["en-US"]),
                audio=audio_file
            )
            
            result = client.transcribe(body=content)
        
        assert result is not None
        assert result.combined_phrases is not None
        assert len(result.combined_phrases) > 0
        assert result.combined_phrases[0].text is not None
        assert len(result.combined_phrases[0].text) > 0
