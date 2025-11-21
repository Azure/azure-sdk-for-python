# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_transcribe_with_diarization_async.py

DESCRIPTION:
    This sample demonstrates how to asynchronously transcribe an audio file with
    speaker diarization (speaker separation) using the Azure AI Transcription
    client. This identifies different speakers in the audio.

USAGE:
    python sample_transcribe_with_diarization_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SPEECH_ENDPOINT - the endpoint to your Speech resource.
    2) AZURE_SPEECH_API_KEY - your Speech API key.
"""

import asyncio
import os


async def sample_transcribe_with_diarization_async():
    # [START transcribe_with_diarization_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.transcription.aio import TranscriptionClient
    from azure.ai.transcription.models import (
        TranscriptionContent,
        TranscriptionOptions,
        TranscriptionDiarizationOptions,
    )

    # Get configuration from environment variables
    endpoint = os.environ["AZURE_SPEECH_ENDPOINT"]
    api_key = os.environ["AZURE_SPEECH_API_KEY"]

    # Create the transcription client
    async with TranscriptionClient(endpoint=endpoint, credential=AzureKeyCredential(api_key)) as client:
        # Path to your audio file with multiple speakers
        import pathlib

        audio_file_path = pathlib.Path(__file__).parent.parent / "assets" / "audio.wav"

        # Open and read the audio file
        with open(audio_file_path, "rb") as audio_file:
            # Create diarization options
            diarization_options = TranscriptionDiarizationOptions(
                max_speakers=5  # Hint for maximum number of speakers (2-35)
            )

            # Create transcription options with diarization
            options = TranscriptionOptions(locales=["en-US"], diarization_options=diarization_options)

            # Create the request content
            request_content = TranscriptionContent(definition=options, audio=audio_file)

            # Transcribe the audio
            result = await client.transcribe(request_content)

            # Print transcription with speaker information
            print("Transcription with speaker diarization:\n")
            if result.phrases:
                for phrase in result.phrases:
                    speaker = phrase.speaker if phrase.speaker is not None else "Unknown"
                    print(f"Speaker {speaker} [{phrase.offset_milliseconds}ms]: {phrase.text}")
            else:
                print(f"Full transcription: {result.combined_phrases[0].text}")
    # [END transcribe_with_diarization_async]


if __name__ == "__main__":
    asyncio.run(sample_transcribe_with_diarization_async())
