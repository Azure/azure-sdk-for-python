# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_transcribe_with_enhanced_mode_async.py

DESCRIPTION:
    This sample demonstrates how to use LLM-powered Enhanced Mode for transcription
    and translation using the asynchronous Azure AI Transcription client. Enhanced
    Mode uses LLM-powered speech recognition to provide improved transcription
    accuracy, real-time translation, prompt-based customization, and multilingual
    support with GPU acceleration.

    Supported Tasks:
    +-------------+--------------------------------------------------------------+
    | Task        | Description                                                  |
    +-------------+--------------------------------------------------------------+
    | transcribe  | Transcribe audio in the input language (auto-detected or    |
    |             | specified)                                                   |
    | translate   | Translate audio to a specified target language               |
    +-------------+--------------------------------------------------------------+

    Limitations:
    - `confidence` is not available and always returns 0
    - Word-level timing (offset_milliseconds, duration_milliseconds) is not
      supported for the `translate` task
    - Diarization is not supported for the `translate` task (only speaker1
      label is returned)
    - `locales` and `phrase_lists` options are not required or applicable
      with Enhanced Mode

USAGE:
    python sample_transcribe_with_enhanced_mode_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SPEECH_ENDPOINT - the endpoint to your Speech resource.
    2) AZURE_SPEECH_API_KEY - your Speech API key.

RELATED RESOURCES:
    - LLM speech for speech transcription and translation (preview):
      https://learn.microsoft.com/azure/ai-services/speech-service/llm-speech
    - Fast transcription:
      https://learn.microsoft.com/azure/ai-services/speech-service/fast-transcription-create
"""

import asyncio
import os
import pathlib


async def sample_transcribe_with_enhanced_mode_async():
    """Transcribe audio using Enhanced Mode for improved quality.

    Use Enhanced Mode for improved transcription quality with LLM-powered
    speech recognition.
    """
    # [START transcribe_with_enhanced_mode_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.transcription.aio import TranscriptionClient
    from azure.ai.transcription.models import (
        TranscriptionContent,
        TranscriptionOptions,
        EnhancedModeProperties,
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
        # Path to your audio file
        audio_file_path = pathlib.Path(__file__).parent.parent / "assets" / "audio.wav"

        # Open and read the audio file
        with open(audio_file_path, "rb") as audio_file:
            # Enhanced mode is automatically enabled when task is specified
            enhanced_mode = EnhancedModeProperties(task="transcribe")

            # Create transcription options with enhanced mode
            options = TranscriptionOptions(enhanced_mode=enhanced_mode)

            # Create the request content
            request_content = TranscriptionContent(definition=options, audio=audio_file)

            # Transcribe the audio with enhanced mode
            result = await client.transcribe(request_content)

            # Print the transcription result
            print(result.combined_phrases[0].text)
    # [END transcribe_with_enhanced_mode_async]


async def sample_translate_with_enhanced_mode_async():
    """Translate speech to another language using Enhanced Mode.

    Translate speech to a target language during transcription. Specify the
    target language using the language code (e.g., `en` for English, `ko` for
    Korean, `es` for Spanish).
    """
    # [START translate_with_enhanced_mode_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.transcription.aio import TranscriptionClient
    from azure.ai.transcription.models import (
        TranscriptionContent,
        TranscriptionOptions,
        EnhancedModeProperties,
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
        # Path to your audio file (e.g., Chinese audio)
        audio_file_path = pathlib.Path(__file__).parent.parent / "assets" / "sample-howstheweather-cn.wav"

        # Open and read the audio file
        with open(audio_file_path, "rb") as audio_file:
            # Translate Chinese speech to Korean
            enhanced_mode = EnhancedModeProperties(
                task="translate",
                target_language="ko",  # Translate to Korean
            )

            # Create transcription options with enhanced mode
            options = TranscriptionOptions(enhanced_mode=enhanced_mode)

            # Create the request content
            request_content = TranscriptionContent(definition=options, audio=audio_file)

            # Transcribe and translate the audio
            result = await client.transcribe(request_content)

            # Print the translated result
            print("Translated to Korean:")
            print(result.combined_phrases[0].text)
    # [END translate_with_enhanced_mode_async]


async def sample_enhanced_mode_with_prompts_async():
    """Use prompts to guide output format and improve recognition.

    Provide prompts to improve recognition or control output format. Prompts
    are optional text that guides the output style for `transcribe` or
    `translate` tasks.
    """
    # [START enhanced_mode_with_prompts_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.transcription.aio import TranscriptionClient
    from azure.ai.transcription.models import (
        TranscriptionContent,
        TranscriptionOptions,
        EnhancedModeProperties,
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
        # Path to your audio file
        audio_file_path = pathlib.Path(__file__).parent.parent / "assets" / "sample-whatstheweatherlike-en.mp3"

        # Open and read the audio file
        with open(audio_file_path, "rb") as audio_file:
            # Guide output formatting using prompts
            enhanced_mode = EnhancedModeProperties(
                task="transcribe",
                prompt=["Output must be in lexical format."],
            )

            # Create transcription options with enhanced mode
            options = TranscriptionOptions(enhanced_mode=enhanced_mode)

            # Create the request content
            request_content = TranscriptionContent(definition=options, audio=audio_file)

            # Transcribe the audio with enhanced mode
            result = await client.transcribe(request_content)

            # Print the transcription result
            print(result.combined_phrases[0].text)
    # [END enhanced_mode_with_prompts_async]


async def sample_enhanced_mode_with_diarization_async():
    """Combine Enhanced Mode with diarization and profanity filtering.

    Enhanced Mode can be combined with other transcription options like
    `diarization`, `profanity_filter_mode`, and `channels` for comprehensive
    transcription scenarios such as meeting transcription.

    Note: Diarization is only supported for the `transcribe` task, not for
    `translate`.
    """
    # [START enhanced_mode_with_diarization_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.transcription.aio import TranscriptionClient
    from azure.ai.transcription.models import (
        TranscriptionContent,
        TranscriptionOptions,
        EnhancedModeProperties,
        TranscriptionDiarizationOptions,
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
        # Path to your audio file (e.g., a meeting recording)
        audio_file_path = pathlib.Path(__file__).parent.parent / "assets" / "audio.wav"

        # Open and read the audio file
        with open(audio_file_path, "rb") as audio_file:
            # Configure enhanced mode with prompts
            enhanced_mode = EnhancedModeProperties(
                task="transcribe",
                prompt=["Output must be in lexical format."],
            )

            # Configure diarization to identify different speakers
            diarization_options = TranscriptionDiarizationOptions(max_speakers=2)

            # Create transcription options with enhanced mode, diarization, and profanity filter
            options = TranscriptionOptions(
                enhanced_mode=enhanced_mode,
                profanity_filter_mode="Masked",
                diarization_options=diarization_options,
            )

            # Create the request content
            request_content = TranscriptionContent(definition=options, audio=audio_file)

            # Transcribe the audio with enhanced mode
            result = await client.transcribe(request_content)

            # Print transcription with speaker information
            for phrase in result.phrases:
                speaker = phrase.speaker if phrase.speaker is not None else "Unknown"
                print(f"[Speaker {speaker}] {phrase.text}")
    # [END enhanced_mode_with_diarization_async]


async def main():
    print("=" * 60)
    print("Sample 1: Transcribe with Enhanced Mode (Async)")
    print("=" * 60)
    await sample_transcribe_with_enhanced_mode_async()

    print("\n" + "=" * 60)
    print("Sample 2: Translate with Enhanced Mode (Async)")
    print("=" * 60)
    await sample_translate_with_enhanced_mode_async()

    print("\n" + "=" * 60)
    print("Sample 3: Enhanced Mode with Prompt Tuning (Async)")
    print("=" * 60)
    await sample_enhanced_mode_with_prompts_async()

    print("\n" + "=" * 60)
    print("Sample 4: Combine Enhanced Mode with Other Options (Async)")
    print("=" * 60)
    await sample_enhanced_mode_with_diarization_async()


if __name__ == "__main__":
    asyncio.run(main())
