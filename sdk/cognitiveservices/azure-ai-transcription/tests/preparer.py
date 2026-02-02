# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import functools
import os
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from azure.core.credentials import AzureKeyCredential
from azure.ai.transcription import TranscriptionClient
from azure.ai.transcription.aio import TranscriptionClient as AsyncTranscriptionClient


class TranscriptionClientTestBase(AzureRecordedTestCase):
    """Base class for transcription tests."""

    def create_client(self, endpoint, **kwargs):
        """Create a synchronous TranscriptionClient for testing."""
        # Try to get API key from environment or kwargs
        api_key = kwargs.pop('transcription_api_key', os.environ.get('TRANSCRIPTION_API_KEY'))
        
        if api_key:
            # Use API key authentication
            credential = AzureKeyCredential(api_key)
        else:
            # Fall back to default credential
            credential = self.get_credential(TranscriptionClient)
        
        return self.create_client_from_credential(
            TranscriptionClient,
            credential=credential,
            endpoint=endpoint,
            **kwargs
        )

    def create_async_client(self, endpoint, **kwargs):
        """Create an asynchronous TranscriptionClient for testing."""
        # Try to get API key from environment or kwargs
        api_key = kwargs.pop('transcription_api_key', os.environ.get('TRANSCRIPTION_API_KEY'))
        
        if api_key:
            # Use API key authentication
            credential = AzureKeyCredential(api_key)
        else:
            # Fall back to default credential
            credential = self.get_credential(AsyncTranscriptionClient, is_async=True)
        
        return self.create_client_from_credential(
            AsyncTranscriptionClient,
            credential=credential,
            endpoint=endpoint,
            **kwargs
        )


# Environment variable loader for transcription tests
TranscriptionPreparer = functools.partial(
    EnvironmentVariableLoader,
    "transcription",
    transcription_endpoint="https://fakeendpoint.cognitiveservices.azure.com",
    transcription_api_key="fake-api-key",
    transcription_test_audio_url="https://example.com/test-audio.wav"
)
