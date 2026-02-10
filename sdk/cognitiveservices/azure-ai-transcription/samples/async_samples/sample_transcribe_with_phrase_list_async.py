# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_transcribe_with_phrase_list_async.py

DESCRIPTION:
    This sample demonstrates how to use custom phrase lists to improve transcription
    accuracy with the asynchronous Azure AI Transcription client.

    A phrase list allows you to provide domain-specific terms, product names,
    technical jargon, or other words that may not be well-recognized by the
    default speech model. This improves accuracy for specialized content.

    For example, without a phrase list:
    - "Jessie" might be recognized as "Jesse"
    - "Rehaan" might be recognized as "everyone"
    - "Contoso" might be recognized as "can't do so"

USAGE:
    python sample_transcribe_with_phrase_list_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SPEECH_ENDPOINT - the endpoint to your Speech resource.
    2) AZURE_SPEECH_API_KEY - your Speech API key.
"""

import asyncio
import os
import pathlib


async def sample_transcribe_with_phrase_list_async():
    """Transcribe audio with a custom phrase list to improve recognition accuracy."""
    # [START transcribe_with_phrase_list_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.transcription.aio import TranscriptionClient
    from azure.ai.transcription.models import (
        TranscriptionContent,
        TranscriptionOptions,
        PhraseListProperties,
    )

    # Get configuration from environment variables
    endpoint = os.environ["AZURE_SPEECH_ENDPOINT"]

    # We recommend using role-based access control (RBAC) for production scenarios
    api_key = os.environ.get("AZURE_SPEECH_API_KEY")
    if api_key:
        credential = AzureKeyCredential(api_key)
    else:
        from azure.identity.aio import DefaultAzureCredential

        credential = DefaultAzureCredential()

    # Create the transcription client
    async with TranscriptionClient(endpoint=endpoint, credential=credential) as client:
        # Path to your audio file with domain-specific terminology
        audio_file_path = pathlib.Path(__file__).parent.parent / "assets" / "audio.wav"

        # Open and read the audio file
        with open(audio_file_path, "rb") as audio_file:
            # Add custom phrases to improve recognition of names and domain-specific terms
            # For example, "Jessie" might be recognized as "Jesse", or "Contoso" as "can't do so"
            phrase_list = PhraseListProperties(
                phrases=["Contoso", "Jessie", "Rehaan"]
            )

            # Create transcription options with phrase list
            options = TranscriptionOptions(phrase_list=phrase_list)

            # Create the request content
            request_content = TranscriptionContent(definition=options, audio=audio_file)

            # Transcribe the audio
            result = await client.transcribe(request_content)

            # Print the transcription result
            print("Transcription with custom phrase list:")
            print(result.combined_phrases[0].text)
    # [END transcribe_with_phrase_list_async]


if __name__ == "__main__":
    asyncio.run(sample_transcribe_with_phrase_list_async())
