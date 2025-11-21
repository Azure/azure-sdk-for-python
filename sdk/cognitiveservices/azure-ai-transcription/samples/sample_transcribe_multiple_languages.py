# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_transcribe_multiple_languages.py

DESCRIPTION:
    This sample demonstrates how to transcribe an audio file with multiple language
    detection using the Azure AI Transcription client. This is useful for
    multilingual content.

USAGE:
    python sample_transcribe_multiple_languages.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SPEECH_ENDPOINT - the endpoint to your Speech resource.
    2) AZURE_SPEECH_API_KEY - your Speech API key.
"""

import os


def sample_transcribe_multiple_languages():
    # [START transcribe_multiple_languages]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.transcription import TranscriptionClient
    from azure.ai.transcription.models import TranscriptionContent, TranscriptionOptions

    # Get configuration from environment variables
    endpoint = os.environ["AZURE_SPEECH_ENDPOINT"]
    api_key = os.environ["AZURE_SPEECH_API_KEY"]

    # Create the transcription client
    client = TranscriptionClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

    # Path to your audio file with multiple languages
    import pathlib

    audio_file_path = pathlib.Path(__file__).parent / "assets" / "audio.wav"

    # Open and read the audio file
    with open(audio_file_path, "rb") as audio_file:
        # Create transcription options with multiple language candidates
        # The service will detect which language is being spoken
        options = TranscriptionOptions(locales=["en-US", "es-ES", "fr-FR", "de-DE"])  # Multiple language candidates

        # Create the request content
        request_content = TranscriptionContent(definition=options, audio=audio_file)

        # Transcribe the audio
        result = client.transcribe(request_content)

        # Print the transcription result with locale information
        print("Transcription with language detection:\n")
        if result.phrases:
            for phrase in result.phrases:
                locale = phrase.locale if hasattr(phrase, "locale") and phrase.locale else "detected"
                print(f"[{locale}] {phrase.text}")
        else:
            print(f"Full transcription: {result.combined_phrases[0].text}")
    # [END transcribe_multiple_languages]


if __name__ == "__main__":
    sample_transcribe_multiple_languages()
