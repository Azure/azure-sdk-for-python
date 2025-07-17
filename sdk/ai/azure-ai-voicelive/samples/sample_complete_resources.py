# pylint: disable=too-many-statements
"""Examples for using the VoiceLive API with WebSocket connections.

This module provides examples for interacting with all resources of the Azure VoiceLive SDK:
- Session management
- Audio buffer handling
- Response creation and management
- Conversation interaction
- Transcription session updates
"""

import asyncio
import base64
import os
import logging
import time
from typing import Dict, Any

from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive import VoiceLiveClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voicelive-examples")


def session_example():
    """Example for Session Resource interaction."""

    # Create a client instance
    endpoint = os.environ.get("VOICELIVE_ENDPOINT", "https://api.cognitive.microsoft.com/voicelive")
    api_key = os.environ.get("VOICELIVE_API_KEY", "your-api-key")

    client = VoiceLiveClient(endpoint, AzureKeyCredential(api_key))

    # Connect to the VoiceLive service
    with client.connect(model="gpt-4o-realtime-preview") as connection:
        # Update session
        connection.session.update(session={"modalities": ["audio", "text"], "turn_detection": {"type": "server_vad"}})

        # Handle session events
        for event in connection:
            if event.type == "session.updated":
                logger.info(f"Session updated: {event.session.id}")
                break


def input_audio_buffer_example():
    """Example for Input Audio Buffer Resource interaction."""

    # Create a client instance
    endpoint = os.environ.get("VOICELIVE_ENDPOINT", "https://api.cognitive.microsoft.com/voicelive")
    api_key = os.environ.get("VOICELIVE_API_KEY", "your-api-key")

    client = VoiceLiveClient(endpoint, AzureKeyCredential(api_key))

    # Sample audio data (replace with actual audio data)
    sample_audio_data = b"\x00\x00" * 1600  # Empty PCM audio sample

    # Connect to the VoiceLive service
    with client.connect(model="gpt-4o-realtime-preview") as connection:
        # Configure session
        connection.session.update(session={"modalities": ["audio", "text"], "turn_detection": {"type": "server_vad"}})

        # Wait for session to be ready
        for event in connection:
            if event.type == "session.updated":
                logger.info("Session ready")
                break

        # Encode the audio data as base64
        base64_audio = base64.b64encode(sample_audio_data).decode("utf-8")

        # Append audio to buffer
        connection.input_audio_buffer.append(audio=base64_audio)
        logger.info("Audio appended to buffer")

        # In manual mode, you would commit the buffer
        if False:  # Set to True for manual commit
            connection.input_audio_buffer.commit()
            logger.info("Audio buffer committed manually")

        # Process events
        for event in connection:
            if event.type == "input_audio_buffer.speech_started":
                logger.info("Speech detected")
            elif event.type == "input_audio_buffer.speech_stopped":
                logger.info("Speech stopped")
            elif event.type == "input_audio_buffer.committed":
                logger.info("Audio buffer committed automatically")
                # Exit after buffer is committed
                break


def output_audio_buffer_example():
    """Example for Output Audio Buffer Resource interaction."""

    # Create a client instance
    endpoint = os.environ.get("VOICELIVE_ENDPOINT", "https://api.cognitive.microsoft.com/voicelive")
    api_key = os.environ.get("VOICELIVE_API_KEY", "your-api-key")

    client = VoiceLiveClient(endpoint, AzureKeyCredential(api_key))

    # Connect to the VoiceLive service
    with client.connect(model="gpt-4o-realtime-preview") as connection:
        # Configure session
        connection.session.update(session={"modalities": ["audio", "text"], "turn_detection": {"type": "server_vad"}})

        # Wait for session to be ready
        for event in connection:
            if event.type == "session.updated":
                logger.info("Session ready")
                break

        # Trigger a response to get output audio
        connection.response.create()

        # Process events and clear buffer after some audio is received
        audio_chunks_received = 0
        for event in connection:
            if event.type == "response.audio.delta":
                audio_chunks_received += 1
                logger.info(f"Received audio chunk {audio_chunks_received}")

                # After receiving some chunks, clear the buffer to stop audio
                if audio_chunks_received >= 3:
                    connection.output_audio_buffer.clear()
                    logger.info("Output audio buffer cleared")

            elif event.type == "output_audio_buffer.cleared":
                logger.info("Server confirmed output buffer cleared")
                break


def response_example():
    """Example for Response Resource interaction."""

    # Create a client instance
    endpoint = os.environ.get("VOICELIVE_ENDPOINT", "https://api.cognitive.microsoft.com/voicelive")
    api_key = os.environ.get("VOICELIVE_API_KEY", "your-api-key")

    client = VoiceLiveClient(endpoint, AzureKeyCredential(api_key))

    # Connect to the VoiceLive service
    with client.connect(model="gpt-4o-realtime-preview") as connection:
        # Configure session
        connection.session.update(session={"modalities": ["audio", "text"], "turn_detection": {"type": "server_vad"}})

        # Wait for session to be ready
        for event in connection:
            if event.type == "session.updated":
                logger.info("Session ready")
                break

        # Create a conversation item to give context to the model
        connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "text", "text": "What is the weather like today?"}],
            }
        )

        # Wait for the item to be created
        for event in connection:
            if event.type == "conversation.item.created":
                logger.info(f"Conversation item created with ID: {event.item_id}")
                break

        # Create a response
        connection.response.create()
        logger.info("Response requested")

        # Process response events
        response_id = None
        full_text = ""

        for event in connection:
            if event.type == "response.created":
                response_id = event.response_id
                logger.info(f"Response created with ID: {response_id}")

            elif event.type == "response.text.delta":
                full_text += event.delta
                logger.info(f"Text delta: {event.delta}")

            elif event.type == "response.done":
                logger.info("Response complete")
                logger.info(f"Full response text: {full_text}")
                break

            # Optional: cancel a response midway
            if full_text and len(full_text) > 100 and response_id:
                connection.response.cancel(response_id=response_id)
                logger.info("Response cancelled")
                break


def conversation_example():
    """Example for Conversation Resource interaction."""

    # Create a client instance
    endpoint = os.environ.get("VOICELIVE_ENDPOINT", "https://api.cognitive.microsoft.com/voicelive")
    api_key = os.environ.get("VOICELIVE_API_KEY", "your-api-key")

    client = VoiceLiveClient(endpoint, AzureKeyCredential(api_key))

    # Connect to the VoiceLive service
    with client.connect(model="gpt-4o-realtime-preview") as connection:
        # Configure session
        connection.session.update(session={"modalities": ["audio", "text"], "turn_detection": {"type": "server_vad"}})

        # Wait for session to be ready
        for event in connection:
            if event.type == "session.updated":
                logger.info("Session ready")
                break

        # Create a system message
        connection.conversation.item.create(
            item={
                "type": "message",
                "role": "system",
                "content": [{"type": "text", "text": "You are a helpful assistant."}],
            }
        )

        # Wait for the system message to be created
        system_item_id = None
        for event in connection:
            if event.type == "conversation.item.created":
                system_item_id = event.item_id
                logger.info(f"System message created with ID: {system_item_id}")
                break

        # Create a user message
        connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "text", "text": "Tell me about the solar system"}],
            }
        )

        # Wait for the user message to be created
        user_item_id = None
        for event in connection:
            if event.type == "conversation.item.created":
                user_item_id = event.item_id
                logger.info(f"User message created with ID: {user_item_id}")
                break

        # Create a response to generate assistant message
        connection.response.create()

        # Wait for the assistant message
        assistant_item_id = None
        for event in connection:
            if event.type == "response.output_item.added":
                assistant_item_id = event.item_id
                logger.info(f"Assistant message created with ID: {assistant_item_id}")
                break

            elif event.type == "response.done":
                logger.info("Response complete")
                break

        # Retrieve a conversation item
        if assistant_item_id:
            connection.conversation.item.retrieve(item_id=assistant_item_id)

            # Wait for the retrieved item
            for event in connection:
                if event.type == "conversation.item.retrieved":
                    logger.info(f"Retrieved assistant message: {event.item}")
                    break

        # Delete a conversation item
        if user_item_id:
            connection.conversation.item.delete(item_id=user_item_id)

            # Wait for the deletion confirmation
            for event in connection:
                if event.type == "conversation.item.deleted":
                    logger.info(f"Deleted user message with ID: {user_item_id}")
                    break


def transcription_session_example():
    """Example for Transcription Session Resource interaction."""

    # Create a client instance
    endpoint = os.environ.get("VOICELIVE_ENDPOINT", "https://api.cognitive.microsoft.com/voicelive")
    api_key = os.environ.get("VOICELIVE_API_KEY", "your-api-key")

    client = VoiceLiveClient(endpoint, AzureKeyCredential(api_key))

    # Connect to the VoiceLive service
    with client.connect(model="gpt-4o-realtime-preview") as connection:
        # Configure session
        connection.session.update(session={"modalities": ["audio", "text"], "turn_detection": {"type": "server_vad"}})

        # Wait for session to be ready
        for event in connection:
            if event.type == "session.updated":
                logger.info("Session ready")
                break

        # Update transcription session
        connection.transcription_session.update(
            session={"model": "whisper-1", "noise_reduction": {"type": "near_field"}}
        )

        # Wait for transcription session update
        for event in connection:
            if event.type == "transcription_session.updated":
                logger.info("Transcription session updated")
                break


def full_conversation_example():
    """Example for a full conversation with audio input and output."""

    # Create a client instance
    endpoint = os.environ.get("VOICELIVE_ENDPOINT", "https://api.cognitive.microsoft.com/voicelive")
    api_key = os.environ.get("VOICELIVE_API_KEY", "your-api-key")

    client = VoiceLiveClient(endpoint, AzureKeyCredential(api_key))

    # Sample audio data (replace with actual audio data)
    sample_audio_data = b"\x00\x00" * 1600  # Empty PCM audio sample

    # Connect to the VoiceLive service
    with client.connect(model="gpt-4o-realtime-preview") as connection:
        # Configure session with server-side voice activity detection
        connection.session.update(session={"modalities": ["audio", "text"], "turn_detection": {"type": "server_vad"}})

        # Wait for session to be ready
        for event in connection:
            if event.type == "session.updated":
                logger.info("Session ready")
                break

        # Set up system message
        connection.conversation.item.create(
            item={
                "type": "message",
                "role": "system",
                "content": [{"type": "text", "text": "You are a helpful assistant. Keep responses brief."}],
            }
        )

        # Wait for system message to be created
        for event in connection:
            if event.type == "conversation.item.created":
                logger.info("System message created")
                break

        # Send some audio data
        base64_audio = base64.b64encode(sample_audio_data).decode("utf-8")
        connection.input_audio_buffer.append(audio=base64_audio)

        # Process events until conversation is complete
        processed_speech = False
        response_complete = False

        while not (processed_speech and response_complete):
            for event in connection:
                if event.type == "input_audio_buffer.speech_started":
                    logger.info("User started speaking")

                elif event.type == "input_audio_buffer.speech_stopped":
                    logger.info("User stopped speaking")

                elif event.type == "input_audio_buffer.committed":
                    logger.info("Audio committed to conversation")
                    processed_speech = True

                elif event.type == "conversation.item.input_audio_transcription.delta":
                    logger.info(f"Transcription: {event.delta}")

                elif event.type == "response.created":
                    logger.info(f"Response created with ID: {event.response_id}")

                elif event.type == "response.text.delta":
                    logger.info(f"Text: {event.delta}")

                elif event.type == "response.audio.delta":
                    logger.info("Received audio chunk")

                elif event.type == "response.done":
                    logger.info("Response complete")
                    response_complete = True
                    break

                # If we've processed the speech but no response yet, send more audio
                if processed_speech and not response_complete:
                    # Wait for response to start
                    time.sleep(0.5)
                    break


async def async_example():
    """Example using the async client."""

    from azure.ai.voicelive.aio import VoiceLiveClient

    # Create a client instance
    endpoint = os.environ.get("VOICELIVE_ENDPOINT", "https://api.cognitive.microsoft.com/voicelive")
    api_key = os.environ.get("VOICELIVE_API_KEY", "your-api-key")

    client = VoiceLiveClient(endpoint, AzureKeyCredential(api_key))

    # Connect to the VoiceLive service
    async with client.connect(model="gpt-4o-realtime-preview") as connection:
        # Configure session
        await connection.session.update(
            session={"modalities": ["audio", "text"], "turn_detection": {"type": "server_vad"}}
        )

        # Create a conversation item
        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "text", "text": "What is the capital of France?"}],
            }
        )

        # Create a response
        await connection.response.create()

        # Process events
        full_text = ""
        async for event in connection:
            if event.type == "response.text.delta":
                full_text += event.delta
                logger.info(f"Text delta: {event.delta}")

            elif event.type == "response.done":
                logger.info("Response complete")
                logger.info(f"Full response text: {full_text}")
                break


if __name__ == "__main__":
    # Choose which example to run
    example_to_run = "session"  # Change to run different examples

    examples = {
        "session": session_example,
        "input_audio": input_audio_buffer_example,
        "output_audio": output_audio_buffer_example,
        "response": response_example,
        "conversation": conversation_example,
        "transcription": transcription_session_example,
        "full": full_conversation_example,
    }

    if example_to_run == "async":
        # Run the async example
        asyncio.run(async_example())
    elif example_to_run in examples:
        # Run the selected synchronous example
        examples[example_to_run]()
    else:
        logger.error(f"Unknown example: {example_to_run}")
