# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_transcribe_with_phrase_list.py

DESCRIPTION:
    This sample demonstrates how to transcribe an audio file with a custom phrase list
    to improve recognition accuracy for domain-specific terminology using the Azure AI Transcription client.

USAGE:
    python sample_transcribe_with_phrase_list.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SPEECH_ENDPOINT - the endpoint to your Speech resource.
    2) AZURE_SPEECH_API_KEY - your Speech API key.
"""

import os


def sample_transcribe_with_phrase_list():
    # [START transcribe_with_phrase_list]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.transcription import TranscriptionClient
    from azure.ai.transcription.models import (
        TranscriptionContent,
        TranscriptionOptions,
        PhraseListProperties,
    )

    # Get configuration from environment variables
    endpoint = os.environ["AZURE_SPEECH_ENDPOINT"]
    api_key = os.environ["AZURE_SPEECH_API_KEY"]

    # Create the transcription client
    client = TranscriptionClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

    # Path to your audio file with domain-specific terminology
    import pathlib

    audio_file_path = pathlib.Path(__file__).parent / "assets" / "audio.wav"

    # Open and read the audio file
    with open(audio_file_path, "rb") as audio_file:
        # Create a phrase list with custom terminology
        # This helps improve recognition accuracy for specific words
        phrase_list = PhraseListProperties(
            phrases=["Azure", "Cognitive Services", "Speech SDK", "TranscriptionClient", "Kubernetes", "microservices"],
            biasing_weight=5.0,  # Weight between 1.0 and 20.0 (higher = more bias)
        )

        # Create transcription options with phrase list
        options = TranscriptionOptions(locales=["en-US"], phrase_list=phrase_list)

        # Create the request content
        request_content = TranscriptionContent(definition=options, audio=audio_file)

        # Transcribe the audio
        result = client.transcribe(request_content)

        # Print the transcription result
        print("Transcription with custom phrase list:")
        print(f"{result.combined_phrases[0].text}")

        # Print individual phrases if available
        if result.phrases:
            print("\nDetailed phrases:")
            for phrase in result.phrases:
                print(f"  [{phrase.offset_milliseconds}ms]: {phrase.text}")
    # [END transcribe_with_phrase_list]


if __name__ == "__main__":
    sample_transcribe_with_phrase_list()
