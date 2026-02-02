# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from preparer import TranscriptionClientTestBase, TranscriptionPreparer


class TestTranscriptionClientManagementAsync(TranscriptionClientTestBase):
    """Tests for async client lifecycle and management."""

    @TranscriptionPreparer()
    @recorded_by_proxy_async
    async def test_client_context_manager_async(self, transcription_endpoint, transcription_test_audio_url):
        """Test that async client works properly with context manager."""
        # Test creating and using client with context manager
        async with self.create_async_client(endpoint=transcription_endpoint) as client:
            audio_url = transcription_test_audio_url
            
            result = await client.transcribe_from_url(audio_url)
            
            assert result is not None
            assert result.combined_phrases is not None
