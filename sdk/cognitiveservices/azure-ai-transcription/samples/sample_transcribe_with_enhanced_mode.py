# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_transcribe_with_enhanced_mode.py

DESCRIPTION:
    This sample demonstrates how to transcribe an audio file with enhanced mode enabled.
    Enhanced mode provides advanced capabilities such as translation or summarization
    during transcription using the Azure AI Transcription client.

USAGE:
    python sample_transcribe_with_enhanced_mode.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SPEECH_ENDPOINT - the endpoint to your Speech resource.
    2) AZURE_SPEECH_API_KEY - your Speech API key.
"""

import os


def sample_transcribe_with_enhanced_mode():
    # [START transcribe_with_enhanced_mode]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.transcription import TranscriptionClient
    from azure.ai.transcription.models import (
        TranscriptionContent,
        TranscriptionOptions,
        EnhancedModeProperties,
    )

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
        # Create enhanced mode properties
        # Enable enhanced mode for advanced processing capabilities
        enhanced_mode = EnhancedModeProperties(
            task="translation",  # Specify the task type (e.g., "translation", "summarization")
            target_language="es-ES",  # Target language for translation
            prompt=[
                "Translate the following audio to Spanish",
                "Focus on technical terminology",
            ],  # Optional prompts to guide the enhanced mode
        )

        # Create transcription options with enhanced mode
        options = TranscriptionOptions(locales=["en-US"], enhanced_mode=enhanced_mode)

        # Create the request content
        request_content = TranscriptionContent(definition=options, audio=audio_file)

        # Transcribe the audio with enhanced mode
        result = client.transcribe(request_content)

        # Print the transcription result
        print("Transcription with enhanced mode:")
        print(f"{result.combined_phrases[0].text}")

        # Print individual phrases if available
        if result.phrases:
            print("\nDetailed phrases:")
            for phrase in result.phrases:
                print(f"  [{phrase.offset_milliseconds}ms]: {phrase.text}")
    # [END transcribe_with_enhanced_mode]


if __name__ == "__main__":
    sample_transcribe_with_enhanced_mode()
