#!/usr/bin/env python
# pylint: disable=line-too-long,useless-suppression

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: agent_v2_sample.py

DESCRIPTION:
    This sample demonstrates how to connect to an Azure AI Foundry agent using
    the AgentSessionConfig TypedDict. Instead of configuring the agent as a tool
    in the session, the agent is specified at connection time through the
    agent_config parameter. This allows the agent to be the primary responder
    for the voice session.

    The AgentSessionConfig TypedDict supports the following fields:
    - agent_name (required): The name of the agent in Azure AI Foundry
    - project_name (required): The name of the Foundry project containing the agent
    - agent_version (optional): The version of the agent to use
    - conversation_id (optional): ID to continue an existing conversation
    - authentication_identity_client_id (optional): Client ID for authentication
    - foundry_resource_override (optional): Override for the Foundry resource URL

    This sample also demonstrates:
    - Callback-based audio streaming for efficient capture and playback
    - Sequence number based audio packet system for proper interrupt handling
    - Conversation logging to file
    - Proper audio device validation

USAGE:
    python agent_v2_sample.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_VOICELIVE_ENDPOINT - The Azure VoiceLive endpoint
    2) AGENT_NAME - The name of your Azure AI Foundry agent
    3) AGENT_PROJECT_NAME - The name of the Foundry project containing the agent

    Optional environment variables:
    - AGENT_VERSION - The version of the agent (if not specified, uses latest)
    - AGENT_VOICE - Voice to use (default: en-US-Ava:DragonHDLatestNeural)
    - FOUNDRY_RESOURCE_OVERRIDE - Override for the Foundry resource URL
    - AGENT_AUTH_IDENTITY_CLIENT_ID - Client ID for agent authentication
"""

from __future__ import annotations

import asyncio
import base64
import logging
import os
import pathlib
import queue
import signal
import sys
from datetime import datetime
from typing import Optional, Union, cast

# Audio processing imports
try:
    import pyaudio
except ImportError:
    print("This sample requires pyaudio. Install with:")
    print("  Linux: sudo apt-get install -y portaudio19-dev libasound2-dev && pip install pyaudio")
    print("  macOS: brew install portaudio && pip install pyaudio")
    print("  Windows: pip install pyaudio")
    sys.exit(1)

# Environment variable loading
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("Note: python-dotenv not installed. Using existing environment variables.")

# Azure VoiceLive SDK imports
from azure.ai.voicelive.aio import VoiceLiveConnection, connect, AgentSessionConfig
from azure.ai.voicelive.models import (
    AudioEchoCancellation,
    AudioNoiseReduction,
    AzureStandardVoice,
    InputAudioFormat,
    Modality,
    OutputAudioFormat,
    RequestSession,
    ServerEventType,
    ServerVad,
)
from azure.core.credentials_async import AsyncTokenCredential
from azure.identity.aio import DefaultAzureCredential

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _get_required_env(name: str) -> str:
    """Get a required environment variable or exit with error."""
    value = os.environ.get(name)
    if not value:
        print(f"❌ Error: No {name} provided")
        print(f"Please set the {name} environment variable.")
        sys.exit(1)
    return value


# Configuration from environment variables
endpoint = _get_required_env("AZURE_VOICELIVE_ENDPOINT")
agent_name = _get_required_env("AGENT_NAME")
agent_project_name = _get_required_env("AGENT_PROJECT_NAME")

# Optional configuration
agent_version = os.environ.get("AGENT_VERSION")  # Optional
agent_voice = os.environ.get("AGENT_VOICE", "en-US-Ava:DragonHDLatestNeural")
foundry_resource_override = os.environ.get("FOUNDRY_RESOURCE_OVERRIDE")  # Optional
agent_auth_identity_client_id = os.environ.get("AGENT_AUTH_IDENTITY_CLIENT_ID")  # Optional

# Set up logging directory
pathlib.Path("logs").mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logfilename = f"{timestamp}_agent_v2_conversation.log"


class AudioProcessor:
    """
    Handles real-time audio capture and playback for the voice assistant.

    Uses callback-based audio streaming for efficient capture and playback.
    Implements sequence number based audio packet system for proper interrupt handling.

    Threading Architecture:
    - Main thread: Event loop and UI
    - PyAudio callback threads: Handle audio I/O in real-time
    """

    loop: asyncio.AbstractEventLoop

    class AudioPlaybackPacket:
        """Represents a packet that can be sent to the audio playback queue."""

        def __init__(self, seq_num: int, data: Optional[bytes]):
            self.seq_num = seq_num
            self.data = data

    def __init__(self, connection: VoiceLiveConnection):
        self.connection = connection
        self.audio = pyaudio.PyAudio()

        # Audio configuration - PCM16, 24kHz, mono
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 24000
        self.chunk_size = 1200  # 50ms chunks

        # Capture and playback state
        self.input_stream: Optional[pyaudio.Stream] = None

        # Playback with sequence numbers for interrupt handling
        self.playback_queue: queue.Queue[AudioProcessor.AudioPlaybackPacket] = queue.Queue()
        self.playback_base = 0
        self.next_seq_num = 0
        self.output_stream: Optional[pyaudio.Stream] = None

        logger.info("AudioProcessor initialized with 24kHz PCM16 mono audio")

    def start_capture(self):
        """Start capturing audio from microphone using callback."""

        def _capture_callback(
            in_data, _frame_count, _time_info, _status_flags  # data  # number of frames  # dictionary
        ):
            """Audio capture callback - runs in PyAudio thread."""
            audio_base64 = base64.b64encode(in_data).decode("utf-8")
            asyncio.run_coroutine_threadsafe(self.connection.input_audio_buffer.append(audio=audio_base64), self.loop)
            return (None, pyaudio.paContinue)

        if self.input_stream:
            return

        # Store the current event loop for use in callbacks
        self.loop = asyncio.get_event_loop()

        try:
            self.input_stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=_capture_callback,
            )
            logger.info("Started audio capture")

        except Exception:
            logger.exception("Failed to start audio capture")
            raise

    def start_playback(self):
        """Initialize audio playback system using callback."""
        if self.output_stream:
            return

        remaining = bytes()

        def _playback_callback(_in_data, frame_count, _time_info, _status_flags):
            nonlocal remaining
            frame_count *= pyaudio.get_sample_size(pyaudio.paInt16)

            out = remaining[:frame_count]
            remaining = remaining[frame_count:]

            while len(out) < frame_count:
                try:
                    packet = self.playback_queue.get_nowait()
                except queue.Empty:
                    out = out + bytes(frame_count - len(out))
                    continue
                except Exception:
                    logger.exception("Error in audio playback")
                    raise

                if not packet or not packet.data:
                    # None packet indicates end of stream
                    logger.info("End of playback queue.")
                    break

                if packet.seq_num < self.playback_base:
                    # Skip requested - ignore skipped packet and clear remaining
                    if len(remaining) > 0:
                        remaining = bytes()
                    continue

                num_to_take = frame_count - len(out)
                out = out + packet.data[:num_to_take]
                remaining = packet.data[num_to_take:]

            if len(out) >= frame_count:
                return (out, pyaudio.paContinue)
            else:
                return (out, pyaudio.paComplete)

        try:
            self.output_stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                output=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=_playback_callback,
            )
            logger.info("Audio playback system ready")
        except Exception:
            logger.exception("Failed to initialize audio playback")
            raise

    def _get_and_increase_seq_num(self):
        seq = self.next_seq_num
        self.next_seq_num += 1
        return seq

    def queue_audio(self, audio_data: Optional[bytes]) -> None:
        """Queue audio data for playback."""
        self.playback_queue.put(
            AudioProcessor.AudioPlaybackPacket(seq_num=self._get_and_increase_seq_num(), data=audio_data)
        )

    def skip_pending_audio(self):
        """Skip current audio in playback queue (used during interrupts)."""
        self.playback_base = self._get_and_increase_seq_num()

    def shutdown(self):
        """Clean up audio resources."""
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.input_stream = None

        logger.info("Stopped audio capture")

        # Inform thread to complete
        if self.output_stream:
            self.skip_pending_audio()
            self.queue_audio(None)
            self.output_stream.stop_stream()
            self.output_stream.close()
            self.output_stream = None

        logger.info("Stopped audio playback")

        if self.audio:
            self.audio.terminate()

        logger.info("Audio processor cleaned up")


class AgentV2VoiceAssistant:
    """
    Voice assistant using Azure AI Foundry agent with AgentSessionConfig.

    This demonstrates the new pattern where the agent is configured at
    connection time using AgentSessionConfig, rather than as a tool in the session.
    This sample also collects a conversation log of user and agent interactions.
    """

    def __init__(
        self,
        endpoint: str,
        credential: AsyncTokenCredential,
        agent_config: AgentSessionConfig,
        voice: str,
    ) -> None:
        self.endpoint = endpoint
        self.credential = credential
        self.agent_config = agent_config
        self.voice = voice
        self.connection: Optional[VoiceLiveConnection] = None
        self.audio_processor: Optional[AudioProcessor] = None
        self.session_ready = False

    async def start(self):
        """Start the voice assistant session."""
        try:
            logger.info(
                "Connecting to VoiceLive API with agent %s for project %s",
                self.agent_config.get("agent_name"),
                self.agent_config.get("project_name"),
            )

            # Connect using AgentSessionConfig
            async with connect(
                endpoint=self.endpoint,
                credential=self.credential,
                agent_config=self.agent_config,  # Agent configured at connection time
            ) as connection:
                conn = connection
                self.connection = conn

                # Initialize audio processor
                ap = AudioProcessor(conn)
                self.audio_processor = ap

                # Configure session for voice conversation
                await self._setup_session()

                # Start audio systems
                ap.start_playback()

                logger.info("Voice assistant ready! Start speaking...")
                print("\n" + "=" * 60)
                print("🎤 AGENT V2 VOICE ASSISTANT READY")
                print(f"Agent: {self.agent_config.get('agent_name')}")
                print(f"Project: {self.agent_config.get('project_name')}")
                if self.agent_config.get("agent_version"):
                    print(f"Version: {self.agent_config.get('agent_version')}")
                print("Start speaking to begin conversation")
                print("Press Ctrl+C to exit")
                print("=" * 60 + "\n")

                # Process events
                await self._process_events()
        except Exception:
            logger.exception("Voice assistant encountered an error")
            raise
        finally:
            if self.audio_processor:
                self.audio_processor.shutdown()

    async def _setup_session(self):
        """Configure the VoiceLive session for audio conversation."""
        logger.info("Setting up voice conversation session...")

        voice_config = AzureStandardVoice(name=self.voice)

        # Create turn detection configuration
        turn_detection_config = ServerVad(
            threshold=0.5,
            prefix_padding_ms=300,
            silence_duration_ms=500,
        )

        # Create session configuration
        session_config = RequestSession(
            modalities=[Modality.TEXT, Modality.AUDIO],
            voice=voice_config,
            input_audio_format=InputAudioFormat.PCM16,
            output_audio_format=OutputAudioFormat.PCM16,
            turn_detection=turn_detection_config,
            input_audio_echo_cancellation=AudioEchoCancellation(),
            input_audio_noise_reduction=AudioNoiseReduction(type="azure_deep_noise_suppression"),
        )

        conn = self.connection
        assert conn is not None, "Connection must be established before setting up session"
        await conn.session.update(session=session_config)

        logger.info("Session configuration sent")

    async def _process_events(self):
        """Process events from the VoiceLive connection."""
        try:
            conn = self.connection
            assert conn is not None, "Connection must be established before processing events"
            async for event in conn:
                await self._handle_event(event)
        except Exception:
            logger.exception("Error processing events")
            raise

    async def _handle_event(self, event):
        """Handle different types of events from VoiceLive."""
        logger.debug("Received event: %s", event.type)
        ap = self.audio_processor
        assert ap is not None, "AudioProcessor must be initialized"

        if event.type == ServerEventType.SESSION_UPDATED:
            logger.info("Session ready: %s", event.session.id)
            await write_conversation_log(f"SessionID: {event.session.id}")
            await write_conversation_log(f"Model: {event.session.model}")
            await write_conversation_log(f"Voice: {event.session.voice}")
            await write_conversation_log("")
            self.session_ready = True

            # Start audio capture once session is ready
            ap.start_capture()

        elif event.type == ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED:
            user_transcript = f'User Input:\t{event.get("transcript", "")}'
            print("👤 You said: ", user_transcript)
            await write_conversation_log(user_transcript)

        elif event.type == ServerEventType.RESPONSE_TEXT_DONE:
            agent_text = f'Agent Text Response:\t{event.get("text", "")}'
            print("🤖 Agent responded with text: ", agent_text)
            await write_conversation_log(agent_text)

        elif event.type == ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE:
            agent_audio = f'Agent Audio Response:\t{event.get("transcript", "")}'
            print("🤖 Agent responded with audio transcript: ", agent_audio)
            await write_conversation_log(agent_audio)

        elif event.type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED:
            logger.info("User started speaking - stopping playback")
            print("🎤 Listening...")

            # Skip queued audio
            ap.skip_pending_audio()

        elif event.type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED:
            logger.info("🎤 User stopped speaking")
            print("🤔 Processing...")

        elif event.type == ServerEventType.RESPONSE_CREATED:
            logger.info("🤖 Assistant response created")

        elif event.type == ServerEventType.RESPONSE_AUDIO_DELTA:
            # Stream audio response to speakers
            logger.debug("Received audio delta")
            ap.queue_audio(event.delta)

        elif event.type == ServerEventType.RESPONSE_AUDIO_DONE:
            logger.info("🤖 Assistant finished speaking")

        elif event.type == ServerEventType.RESPONSE_DONE:
            logger.info("✅ Response complete")
            print("🎤 Ready for next input...")

        elif event.type == ServerEventType.ERROR:
            logger.error("❌ VoiceLive error: %s", event.error.message)
            print(f"Service returns error: {event.error}")

        elif event.type == ServerEventType.WARNING:
            logger.warning("⚠️ VoiceLive warning: %s", event.warning.message)
            print(f"Service returns warning: {event.warning}")

        elif event.type == ServerEventType.CONVERSATION_ITEM_CREATED:
            logger.debug("Conversation item created: %s", event.item.id)

        else:
            logger.debug("Unhandled event type: %s", event.type)


async def write_conversation_log(message: str) -> None:
    """Write a message to the conversation log."""

    def _write_to_file():
        with open(f"logs/{logfilename}", "a", encoding="utf-8") as conversation_log:
            conversation_log.write(message + "\n")

    await asyncio.to_thread(_write_to_file)


async def run_assistant():
    """Run the voice assistant."""
    # Create AgentSessionConfig from environment variables
    agent_config: AgentSessionConfig = {
        "agent_name": agent_name,
        "project_name": agent_project_name,
    }

    # Add optional fields if provided
    if agent_version:
        agent_config["agent_version"] = agent_version
    if foundry_resource_override:
        agent_config["foundry_resource_override"] = foundry_resource_override
    if agent_auth_identity_client_id:
        agent_config["authentication_identity_client_id"] = agent_auth_identity_client_id

    # Create client with token credential (required for Agent mode)
    credential: AsyncTokenCredential = DefaultAzureCredential()
    logger.info("Using DefaultAzureCredential")

    # Create and start voice assistant
    assistant = AgentV2VoiceAssistant(
        endpoint=endpoint,
        credential=credential,
        agent_config=agent_config,
        voice=agent_voice,
    )

    await assistant.start()


def main():
    """Main function."""

    # Setup signal handlers for graceful shutdown
    def signal_handler(_sig, _frame):
        logger.info("Received shutdown signal")
        raise KeyboardInterrupt()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start the assistant
    try:
        asyncio.run(run_assistant())
    except KeyboardInterrupt:
        print("\n👋 Voice assistant shut down. Goodbye!")
    except Exception as e:
        print("Fatal Error: ", e)


if __name__ == "__main__":
    # Check audio system
    try:
        p = pyaudio.PyAudio()
        # Check for input devices
        input_devices = [
            i
            for i in range(p.get_device_count())
            if cast(Union[int, float], p.get_device_info_by_index(i).get("maxInputChannels", 0) or 0) > 0
        ]
        # Check for output devices
        output_devices = [
            i
            for i in range(p.get_device_count())
            if cast(Union[int, float], p.get_device_info_by_index(i).get("maxOutputChannels", 0) or 0) > 0
        ]
        p.terminate()

        if not input_devices:
            print("❌ No audio input devices found. Please check your microphone.")
            sys.exit(1)
        if not output_devices:
            print("❌ No audio output devices found. Please check your speakers.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Audio system check failed: {e}")
        sys.exit(1)

    print("🎙️  Agent V2 Voice Assistant with Azure VoiceLive SDK")
    print("=" * 50)
    print(f"Agent: {agent_name}")
    print(f"Project: {agent_project_name}")
    if agent_version:
        print(f"Version: {agent_version}")
    print("Using AgentSessionConfig for agent configuration")
    print("=" * 50)

    # Run the assistant
    main()
