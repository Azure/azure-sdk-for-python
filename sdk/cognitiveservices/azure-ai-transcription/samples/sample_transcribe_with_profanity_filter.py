# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_transcribe_with_profanity_filter.py

DESCRIPTION:
    This sample demonstrates how to transcribe an audio file with profanity filtering
    using the Azure AI Transcription client. Profanity can be removed, masked,
    or tagged.

USAGE:
    python sample_transcribe_with_profanity_filter.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SPEECH_ENDPOINT - the endpoint to your Speech resource.
    2) AZURE_SPEECH_API_KEY - your Speech API key.
"""

import os


def sample_transcribe_with_profanity_filter():
    # [START transcribe_with_profanity_filter]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.transcription import TranscriptionClient
    from azure.ai.transcription.models import TranscriptionContent, TranscriptionOptions

    # Get configuration from environment variables
    endpoint = os.environ["AZURE_SPEECH_ENDPOINT"]
    api_key = os.environ["AZURE_SPEECH_API_KEY"]

    # Create the transcription client
    client = TranscriptionClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

    # Path to your audio file
    import pathlib

    audio_file_path = pathlib.Path(__file__).parent / "assets" / "audio.wav"

    # Open and read the audio file
    with open(audio_file_path, "rb") as audio_file:
        # Create transcription options with profanity filtering
        # Options: "None", "Removed", "Masked", "Tags"
        options = TranscriptionOptions(
            locales=["en-US"], profanity_filter_mode="Masked"  # Replace profanity with asterisks
        )

        # Create the request content
        request_content = TranscriptionContent(definition=options, audio=audio_file)

        # Transcribe the audio
        result = client.transcribe(request_content)

        # Print the transcription result
        print(f"Transcription (with profanity masked): {result.combined_phrases[0].text}")

    # Example: Remove profanity completely
    with open(audio_file_path, "rb") as audio_file:
        options = TranscriptionOptions(locales=["en-US"], profanity_filter_mode="Removed")  # Remove profanity entirely

        request_content = TranscriptionContent(definition=options, audio=audio_file)

        result = client.transcribe(request_content)
        print(f"\nTranscription (with profanity removed): {result.combined_phrases[0].text}")

    # Example: Tag profanity with XML tags
    with open(audio_file_path, "rb") as audio_file:
        options = TranscriptionOptions(
            locales=["en-US"], profanity_filter_mode="Tags"  # Wrap profanity in <profanity> tags
        )

        request_content = TranscriptionContent(definition=options, audio=audio_file)

        result = client.transcribe(request_content)
        print(f"\nTranscription (with profanity tagged): {result.combined_phrases[0].text}")
    # [END transcribe_with_profanity_filter]


if __name__ == "__main__":
    sample_transcribe_with_profanity_filter()
