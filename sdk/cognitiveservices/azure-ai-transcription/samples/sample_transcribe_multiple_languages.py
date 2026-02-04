# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_transcribe_multiple_languages.py

DESCRIPTION:
    This sample demonstrates how to transcribe audio with multilingual content
    using the Azure AI Transcription client.

    When your audio contains multilingual content that switches between different
    languages, use the multilingual transcription model by NOT specifying any
    locales. The service will automatically detect and transcribe each language
    segment.

    Supported locales:
    de-DE, en-AU, en-CA, en-GB, en-IN, en-US, es-ES, es-MX, fr-CA, fr-FR,
    it-IT, ja-JP, ko-KR, zh-CN

    Note: This feature is currently in preview. The multilingual model outputs
    the "major locale" for each language (e.g., always "en-US" for English
    regardless of accent).

USAGE:
    python sample_transcribe_multiple_languages.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SPEECH_ENDPOINT - the endpoint to your Speech resource.
    2) AZURE_SPEECH_API_KEY - your Speech API key.

RELATED RESOURCES:
    - Fast transcription - Multilingual transcription:
      https://learn.microsoft.com/azure/ai-services/speech-service/fast-transcription-create?tabs=multilingual-transcription-on
"""

import os
import pathlib


def sample_transcribe_multilingual():
    """Transcribe audio with multilingual content (Preview).

    For multilingual content, do not specify any locales. The service will
    automatically detect and transcribe each language segment.
    """
    # [START transcribe_multilingual]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.transcription import TranscriptionClient
    from azure.ai.transcription.models import TranscriptionContent, TranscriptionOptions

    # Get configuration from environment variables
    endpoint = os.environ["AZURE_SPEECH_ENDPOINT"]
    api_key = os.environ["AZURE_SPEECH_API_KEY"]

    # Create the transcription client
    client = TranscriptionClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

    # Path to your audio file with multilingual content
    audio_file_path = pathlib.Path(__file__).parent / "assets" / "audio.wav"

    # Open and read the audio file
    with open(audio_file_path, "rb") as audio_file:
        # For multilingual content, do NOT specify any locales
        # The service will automatically detect and transcribe each language
        options = TranscriptionOptions()

        # Create the request content
        request_content = TranscriptionContent(definition=options, audio=audio_file)

        # Transcribe the audio
        result = client.transcribe(request_content)

        # Print the transcription result with locale information
        print("Multilingual Transcription:\n")
        for phrase in result.phrases:
            locale = phrase.locale if phrase.locale else "auto-detected"
            print(f"[{locale}] {phrase.text}")
    # [END transcribe_multilingual]


if __name__ == "__main__":
    sample_transcribe_multilingual()
