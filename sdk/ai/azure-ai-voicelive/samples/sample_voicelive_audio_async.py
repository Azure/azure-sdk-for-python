#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_voicelive_audio_async.py

DESCRIPTION:
    This sample demonstrates how to use the Azure VoiceLive async client
    to interact with the VoiceLive API using audio input and output.

USAGE:
    python sample_voicelive_audio_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_VOICELIVE_API_KEY - The Azure VoiceLive key.

REQUIREMENTS:
    - websockets
    - azure-identity
    - base64
    - pyaudio (for capturing audio from microphone and playing audio output)
"""

import os
import asyncio
import base64
import argparse
import threading
from typing import Optional, List, Dict, Any
import time
import queue

try:
    import pyaudio
except ImportError:
    print("This sample requires pyaudio to be installed. Run 'pip install pyaudio'")
    exit(1)

from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential
from azure.ai.voicelive.aio import VoiceLiveClient
from azure.ai.voicelive.models import ServerEventSessionUpdated, RequestSession


class AudioProcessor:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        self.input_stream = None
        self.output_stream = None
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.output_buffer = b""
        self.playing_thread = None

    def start_recording(self):
        """Start recording audio from the microphone"""
        self.is_recording = True
        self.input_stream = self.p.open(
            format=self.audio_format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk
        )
        print("Started recording. Speak into the microphone.")

    def stop_recording(self):
        """Stop recording audio"""
        self.is_recording = False
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.input_stream = None
        print("Stopped recording")

    def read_audio_chunk(self):
        """Read a chunk of audio from the input stream"""
        if self.input_stream and self.is_recording:
            try:
                data = self.input_stream.read(self.chunk, exception_on_overflow=False)
                return data
            except Exception as e:
                print(f"Error recording audio: {e}")
        return None

    def setup_output_stream(self):
        """Set up the audio output stream"""
        if not self.output_stream:
            self.output_stream = self.p.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                output=True,
                frames_per_buffer=self.chunk,
            )

    def add_to_output_buffer(self, audio_data):
        """Add audio data to the output buffer"""
        self.output_buffer += audio_data
        if not self.playing_thread or not self.playing_thread.is_alive():
            self.playing_thread = threading.Thread(target=self._play_audio)
            self.playing_thread.daemon = True
            self.playing_thread.start()

    def _play_audio(self):
        """Play audio from the output buffer"""
        self.setup_output_stream()
        while len(self.output_buffer) > 0:
            chunk = self.output_buffer[: self.chunk]
            self.output_buffer = self.output_buffer[self.chunk :]
            if len(chunk) > 0:
                self.output_stream.write(chunk)
            else:
                break

    def close(self):
        """Clean up audio resources"""
        self.stop_recording()
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        self.p.terminate()


async def process_microphone_input(connection, audio_processor):
    """Process microphone input and send to the VoiceLive API"""
    try:
        while audio_processor.is_recording:
            chunk = audio_processor.read_audio_chunk()
            if chunk:
                # Encode audio chunk to base64
                audio_b64 = base64.b64encode(chunk).decode("utf-8")
                # Send to VoiceLive
                await connection.input_audio_buffer.append(audio=audio_b64)
            await asyncio.sleep(0.01)  # Short sleep to prevent CPU spinning
    except Exception as e:
        print(f"Error processing microphone input: {e}")


async def main():
    parser = argparse.ArgumentParser(
        description="Connect to Azure VoiceLive API and have a voice conversation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--api-key",
        help="Azure VoiceLive API key. If not provided, will use the AZURE_VOICELIVE_API_KEY environment variable.",
        type=str,
        default=os.environ.get("AZURE_VOICELIVE_API_KEY"),
    )
    parser.add_argument(
        "--use-token-credential",
        help="Use Azure token credential instead of API key",
        action="store_true",
    )
    parser.add_argument(
        "--model",
        help="VoiceLive model to use",
        type=str,
        default="gpt-4o",
    )
    parser.add_argument(
        "--voice",
        help="Voice to use for the assistant",
        type=str,
        default="alloy",
        choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
    )
    parser.add_argument(
        "--endpoint",
        help="Azure VoiceLive endpoint",
        type=str,
        default=os.environ.get("AZURE_VOICELIVE_ENDPOINT", "wss://api.voicelive.com/v1"),
    )
    parser.add_argument(
        "--api-version",
        help="API version to use",
        type=str,
        default=os.environ.get("VOICELIVE_API_VERSION", "2025-05-01-preview"),
    )
    args = parser.parse_args()

    # Validate arguments
    if not args.api_key and not args.use_token_credential:
        raise ValueError(
            "Please provide an API key using --api-key or set the AZURE_VOICELIVE_KEY environment variable, "
            "or use --use-token-credential to use Azure authentication."
        )

    # Create client with the appropriate credential
    if args.use_token_credential:
        credential = DefaultAzureCredential()
    else:
        credential = AzureKeyCredential(args.api_key)

    # Initialize the audio processor
    audio_processor = AudioProcessor()

    def setup_output_stream():
        """Set up the audio output stream"""
        if not audio_processor.output_stream:
            # List available devices first
            print("Available audio devices:")
            for i in range(audio_processor.p.get_device_count()):
                info = audio_processor.p.get_device_info_by_index(i)
                print(f"Device {i}: {info['name']} - Max Output Channels: {info['maxOutputChannels']}")

            audio_processor.output_stream = audio_processor.p.open(
                format=audio_processor.audio_format,
                channels=audio_processor.channels,
                rate=audio_processor.rate,
                output=True,
                frames_per_buffer=audio_processor.chunk,
                output_device_index=4,  # Try specifying your headphone device index here
            )

    setup_output_stream()

    try:
        # Initialize the client
        client = VoiceLiveClient(
            credential=credential,
            endpoint=args.endpoint,
        )

        # Connect to the WebSocket API
        print(f"Connecting to {args.endpoint} with model {args.model}")
        async with client.connect(
            model=args.model,
            api_version=args.api_version,
            connection_options={
                "max_size": 10 * 1024 * 1024,  # 10 MB
                "ping_interval": 20,  # 20 seconds
                "ping_timeout": 20,  # 20 seconds
            },
        ) as connection:
            # Set up the session
            print("Setting up session...")
            s = RequestSession(
                modalities=["audio", "text"],
                instructions="You are a helpful assistant. Keep your responses concise and natural.",
                turn_detection={
                    "type": "server_vad",
                    "threshold": 0.6,
                    "silence_duration_ms": 700,
                },
                input_audio_format="pcm16",
            )
            await connection.session.update(session=s)

            # Start recording
            audio_processor.start_recording()

            # Start a task to process microphone input
            input_task = asyncio.create_task(process_microphone_input(connection, audio_processor))

            # Process events
            print("Speak into the microphone to interact with the assistant...")
            try:
                async for event in connection:
                    # print(f"Received event: {event.type}")

                    if event.type == "session.updated":
                        print(f"Session initialized with ID: {event.session.id}")
                        print("Listening for your voice...")

                    elif event.type == "input_audio_buffer.speech_started":
                        print("Speech detected...")

                    elif event.type == "input_audio_buffer.speech_stopped":
                        print("Pause detected, processing your input...")

                    elif event.type == "conversation.item.created":
                        if hasattr(event, "item") and event.item.role == "assistant":
                            print("Assistant is responding...")

                    elif event.type == "response.text.delta":
                        print(event.delta, end="", flush=True)

                    elif event.type == "response.audio.delta":
                        # Process audio response
                        audio_data = base64.b64decode(event.delta)
                        audio_processor.add_to_output_buffer(audio_data)

                    elif event.type == "response.done":
                        print("\nResponse complete")
                        print("Listening for your voice...")

                    # Keep processing for 2 minutes then exit
                    if time.time() - start_time > 120:
                        print("\nDemo time limit reached. Exiting...")
                        break

            except KeyboardInterrupt:
                print("\nUser interrupted. Exiting...")
            finally:
                # Cleanup
                if not input_task.done():
                    input_task.cancel()
                    try:
                        await input_task
                    except asyncio.CancelledError:
                        pass
                audio_processor.stop_recording()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup audio resources
        audio_processor.close()


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
