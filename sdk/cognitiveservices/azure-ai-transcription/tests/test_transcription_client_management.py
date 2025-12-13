# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from devtools_testutils import recorded_by_proxy
from preparer import TranscriptionClientTestBase, TranscriptionPreparer


class TestTranscriptionClientManagement(TranscriptionClientTestBase):
    """Tests for client lifecycle and management."""

    @TranscriptionPreparer()
    @recorded_by_proxy
    def test_client_context_manager(self, transcription_endpoint, transcription_test_audio_url):
        """Test using client as a context manager."""
        with self.create_client(endpoint=transcription_endpoint) as client:
            audio_url = transcription_test_audio_url
            result = client.transcribe_from_url(audio_url)
            
            assert result is not None
            assert result.combined_phrases is not None
            assert len(result.combined_phrases) > 0

    @TranscriptionPreparer()
    @recorded_by_proxy
    def test_client_close(self, transcription_endpoint, transcription_test_audio_url):
        """Test explicit client close."""
        client = self.create_client(endpoint=transcription_endpoint)
        
        audio_url = transcription_test_audio_url
        result = client.transcribe_from_url(audio_url)
        
        assert result is not None
        
        # Explicitly close the client
        client.close()
