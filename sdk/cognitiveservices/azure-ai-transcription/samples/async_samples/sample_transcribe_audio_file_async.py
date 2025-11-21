# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_transcribe_audio_file_async.py

DESCRIPTION:
    This sample demonstrates how to asynchronously transcribe an audio file using
    the Azure AI Transcription client.

USAGE:
    python sample_transcribe_audio_file_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SPEECH_ENDPOINT - the endpoint to your Speech resource.
    2) AZURE_SPEECH_API_KEY - your Speech API key.
"""

import asyncio
import os


async def sample_transcribe_audio_file_async():
    # [START transcribe_audio_file_async]
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

        # Open and read the audio file
        with open(audio_file_path, "rb") as audio_file:
            # Create transcription options
            options = TranscriptionOptions(locales=["en-US"])  # Specify the language

            # Create the request content
            request_content = TranscriptionContent(definition=options, audio=audio_file)

            # Transcribe the audio
            result = await client.transcribe(request_content)

            # Print the transcription result
            print(f"Transcription: {result.combined_phrases[0].text}")

            # Print detailed phrase information
            if result.phrases:
                print("\nDetailed phrases:")
                for phrase in result.phrases:
                    print(
                        f"  [{phrase.offset_milliseconds}ms - "
                        f"{phrase.offset_milliseconds + phrase.duration_milliseconds}ms]: "
                        f"{phrase.text}"
                    )
    # [END transcribe_audio_file_async]


if __name__ == "__main__":
    asyncio.run(sample_transcribe_audio_file_async())
