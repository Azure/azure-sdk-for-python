#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: audio_streaming_sample.py
DESCRIPTION:
    This sample demonstrates how to use WebSocket connections for audio streaming
    with the Azure VoiceLive SDK.
USAGE:
    python audio_streaming_sample.py
    
    Set the environment variables with your own values before running the sample:
    1) AZURE_VOICELIVE_API_KEY - The API key for your VoiceLive resource.
    2) AZURE_VOICELIVE_ENDPOINT - The endpoint for your VoiceLive resource.
"""

import os
import base64
import time
import wave
import sys
from typing import Iterator, Optional

# Add the parent directory to sys.path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from samples.utils import load_env_vars, check_samples_prerequisites

from azure.ai.voicelive import VoiceLiveClient, WebsocketConnectionOptions
from azure.core.credentials import AzureKeyCredential

# Check prerequisites
check_samples_prerequisites()

# Load environment variables from .env file if available
load_env_vars()


# Helper function to stream audio data from a WAV file
def stream_audio_file(filepath: str, chunk_size: int = 4000) -> Iterator[bytes]:
    """Streams audio data from a WAV file in chunks."""
    with wave.open(filepath, "rb") as wav_file:
        # Get file info
        n_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        framerate = wav_file.getframerate()
        n_frames = wav_file.getnframes()

        print(f"Audio file: {n_channels} channels, {sample_width} bytes per sample, {framerate} Hz, {n_frames} frames")

        # Read and yield data in chunks
        while True:
            data = wav_file.readframes(chunk_size)
            if not data:
                break
            yield data
            time.sleep(0.1)  # Simulate real-time streaming


def main():
    # Get credentials from environment variables
    api_key = os.environ.get("AZURE_VOICELIVE_KEY", "your-api-key")
    endpoint = os.environ.get("AZURE_VOICELIVE_ENDPOINT", "wss://api.voicelive.com/v1")

    # Default test audio file path (should be replaced with actual file)
    audio_file = os.environ.get("AUDIO_FILE", "test_audio.wav")

    # Define model to use
    model = os.environ.get("VOICELIVE_MODEL", "voicelive-model-name")  # Replace with actual model name

    print(f"Using endpoint: {endpoint}")

    # Create client
    client = VoiceLiveClient(credential=AzureKeyCredential(api_key), endpoint=endpoint)

    # Define WebSocket options
    ws_options: WebsocketConnectionOptions = {
        "max_size": 10 * 1024 * 1024,  # 10MB max message size
    }

    print("Connecting to WebSocket...")
    try:
        # Connect to the WebSocket API
        with client.connect(
            model=model, extra_query={"language": "en-US"}, connection_options=ws_options
        ) as connection:
            # Start a session
            connection.send(
                {
                    "type": "session.update",
                    "session": {"modalities": ["audio"], "audio": {"format": "wav", "sample_rate": 16000}},
                }
            )

            print("Session started. Waiting for server response...")

            # Wait for session.updated event
            session_id: Optional[str] = None
            for event in connection:
                print(f"Received event: {event.get('type')}")

                if event.get("type") == "session.updated":
                    session_id = event.get("session", {}).get("id")
                    print(f"Session established with ID: {session_id}")
                    break

            if not session_id:
                print("Failed to establish session")
                return

            # Stream audio data
            print(f"Streaming audio from {audio_file}")
            for i, chunk in enumerate(stream_audio_file(audio_file)):
                # Encode audio data as base64
                encoded_chunk = base64.b64encode(chunk).decode("utf-8")

                # Send audio data
                connection.send({"type": "audio.data", "audio": {"data": encoded_chunk}})

                print(f"Sent chunk {i+1}")

                # Check for any server events
                # This is a non-blocking way to check for events
                try:
                    event = connection.recv()
                    print(f"Received event during streaming: {event.get('type')}")
                except Exception:
                    # No events available
                    pass

            # Send end of audio stream
            connection.send({"type": "audio.end"})

            print("Audio streaming complete")

            # Wait for final events
            timeout = time.time() + 5  # 5 second timeout
            while time.time() < timeout:
                try:
                    event = connection.recv()
                    print(f"Received final event: {event.get('type')}")

                    # If we get a completion event, we're done
                    if event.get("type") == "session.completed":
                        break
                except Exception:
                    # No more events
                    break

    except ImportError:
        print("You need to install the websockets package to run this sample:")
        print("pip install azure-ai-voicelive[websockets]")
    except FileNotFoundError:
        print(f"Audio file not found: {audio_file}")
        print("Please specify a valid audio file path using the AUDIO_FILE environment variable")
    except Exception as e:
        print(f"Error during WebSocket connection: {e}")


if __name__ == "__main__":
    main()
