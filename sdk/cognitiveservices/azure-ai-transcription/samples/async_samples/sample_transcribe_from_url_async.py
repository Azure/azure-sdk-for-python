# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_transcribe_from_url_async.py

DESCRIPTION:
    This sample demonstrates how to asynchronously transcribe audio from a publicly
    accessible URL using the Azure AI Transcription client.

USAGE:
    python sample_transcribe_from_url_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SPEECH_ENDPOINT - the endpoint to your Speech resource.
    2) AZURE_SPEECH_API_KEY - your Speech API key.
"""

import asyncio
import os


async def sample_transcribe_from_url_async():
    # [START transcribe_from_url_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.transcription.aio import TranscriptionClient
    from azure.ai.transcription.models import TranscriptionOptions

    # Get configuration from environment variables
    endpoint = os.environ["AZURE_SPEECH_ENDPOINT"]
    api_key = os.environ["AZURE_SPEECH_API_KEY"]

    # Create the transcription client
    async with TranscriptionClient(endpoint=endpoint, credential=AzureKeyCredential(api_key)) as client:
        # URL to your audio file (must be publicly accessible)
        audio_url = "https://example.com/path/to/audio.wav"

        # Configure transcription options
        options = TranscriptionOptions(locales=["en-US"])

        # Transcribe the audio from URL
        # The service will access and transcribe the audio directly from the URL
        result = await client.transcribe_from_url(audio_url, options=options)

        # Print the transcription result
        print(f"Transcription: {result.combined_phrases[0].text}")

        # Print duration information
        if result.duration_milliseconds:
            print(f"Audio duration: {result.duration_milliseconds / 1000:.2f} seconds")
    # [END transcribe_from_url_async]


if __name__ == "__main__":
    asyncio.run(sample_transcribe_from_url_async())
