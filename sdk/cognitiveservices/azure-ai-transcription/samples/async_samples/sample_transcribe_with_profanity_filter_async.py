# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_transcribe_with_profanity_filter_async.py

DESCRIPTION:
    This sample demonstrates how to asynchronously transcribe an audio file with
    profanity filtering using the Azure AI Transcription client. Profanity can
    be removed, masked, or tagged.

USAGE:
    python sample_transcribe_with_profanity_filter_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SPEECH_ENDPOINT - the endpoint to your Speech resource.
    2) AZURE_SPEECH_API_KEY - your Speech API key.
"""

import asyncio
import os


async def sample_transcribe_with_profanity_filter_async():
    # [START transcribe_with_profanity_filter_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.transcription.aio import TranscriptionClient
    from azure.ai.transcription.models import TranscriptionContent, TranscriptionOptions

    # Get configuration from environment variables
    endpoint = os.environ["AZURE_SPEECH_ENDPOINT"]
    api_key = os.environ["AZURE_SPEECH_API_KEY"]

    # Create the transcription client
    async with TranscriptionClient(endpoint=endpoint, credential=AzureKeyCredential(api_key)) as client:
        # Path to your audio file
        import pathlib

        audio_file_path = pathlib.Path(__file__).parent.parent / "assets" / "audio.wav"

        # Example 1: Mask profanity with asterisks
        with open(audio_file_path, "rb") as audio_file:
            options = TranscriptionOptions(locales=["en-US"], profanity_filter_mode="Masked")

            request_content = TranscriptionContent(definition=options, audio=audio_file)

            result = await client.transcribe(request_content)
            print(f"Transcription (with profanity masked): {result.combined_phrases[0].text}")

        # Example 2: Remove profanity completely
        with open(audio_file_path, "rb") as audio_file:
            options = TranscriptionOptions(locales=["en-US"], profanity_filter_mode="Removed")

            request_content = TranscriptionContent(definition=options, audio=audio_file)

            result = await client.transcribe(request_content)
            print(f"\nTranscription (with profanity removed): {result.combined_phrases[0].text}")

        # Example 3: Tag profanity with XML tags
        with open(audio_file_path, "rb") as audio_file:
            options = TranscriptionOptions(locales=["en-US"], profanity_filter_mode="Tags")

            request_content = TranscriptionContent(definition=options, audio=audio_file)

            result = await client.transcribe(request_content)
            print(f"\nTranscription (with profanity tagged): {result.combined_phrases[0].text}")
    # [END transcribe_with_profanity_filter_async]


if __name__ == "__main__":
    asyncio.run(sample_transcribe_with_profanity_filter_async())
