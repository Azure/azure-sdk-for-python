# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from devtools_testutils import recorded_by_proxy
from preparer import TranscriptionClientTestBase, TranscriptionPreparer


class TestTranscriptionUrl(TranscriptionClientTestBase):
    """Tests for URL-based transcription scenarios."""

    @TranscriptionPreparer()
    @recorded_by_proxy
    def test_transcribe_from_public_url(self, transcription_endpoint, transcription_test_audio_url):
        """Test transcription from a publicly accessible URL."""
        client = self.create_client(endpoint=transcription_endpoint)
        
        audio_url = transcription_test_audio_url
        result = client.transcribe_from_url(audio_url)
        
        assert result is not None
        assert result.combined_phrases is not None
        assert len(result.combined_phrases) > 0
        assert result.combined_phrases[0].text is not None
