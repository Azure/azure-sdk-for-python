# pylint: disable=line-too-long,useless-suppression
#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: supervisor_agent_sample.py

DESCRIPTION:
    This sample demonstrates how to use a supervisor agent powered by azure foundry in a voice live.
    The Supervisor pattern is a common multi-agent architecture where a central AI agent acts as a coordinator, managing and delegating tasks to specialized supervisor agents.
"""

import os
import sys
import asyncio
import logging
import base64
import signal
import threading
import queue
from typing import Union, Optional, cast
from concurrent.futures import ThreadPoolExecutor

from azure.identity.aio import AzureCliCredential, DefaultAzureCredential

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
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    RequestSession,
    ServerEventType,
    ServerVad,
    AudioEchoCancellation,
    AzureStandardVoice,
    Modality,
    InputAudioFormat,
    OutputAudioFormat,
    FoundryAgentTool,
    ToolChoiceLiteral,
    AudioInputTranscriptionOptions,
    ResponseFoundryAgentCallItem,
)

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


supervisor_agent_name = _get_required_env("SUPERVISOR_AGENT_NAME")
supervisor_agent_version = _get_required_env("SUPERVISOR_AGENT_VERSION")
supervisor_agent_project_name = _get_required_env("SUPERVISOR_AGENT_PROJECT_NAME")

supervisor_agent_description = "You are a supervisor agent that determines the next response whenever the agent faces a non-trivial decision"

chat_agent_instructions = f"""
You are a helpful agent. Your task is to maintain a natural conversation flow with the user.
By default, you must always use the {supervisor_agent_name} tool to get your next response, except when handling greetings (e.g., "hello", "hi there") or engaging in basic chitchat (e.g., "how are you?", "thank you").
Before calling {supervisor_agent_name}, you MUST ALWAYS say something to the user (e.g., "Let me look into that.", "Just a second."). Never call {supervisor_agent_name} without first saying something to the user.
"""

chat_agent_model = os.environ.get("CHAT_AGENT_MODEL", "gpt-realtime")

chat_agent_voice = os.environ.get("CHAT_AGENT_VOICE", "en-US-AvaMultilingualNeural")

class AudioProcessor:
    """
    Handles real-time audio capture and playback for the voice assistant.

    This class manages bidirectional audio streaming:
    - Captures audio input from the microphone using PyAudio
    - Plays back audio output through speakers using PyAudio
    - Uses separate threads for capture, sending, and playback to avoid blocking
    - Uses queues to buffer audio data between threads for thread-safe communication

    Audio format: PCM16, 24kHz, mono
    """

    def __init__(self, connection):
        self.connection = connection
        self.audio = pyaudio.PyAudio()

        # Audio configuration - PCM16, 24kHz, mono as specified
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 24000
        self.chunk_size = 1024

        # Capture and playback state
        self.is_capturing = False
        self.is_playing = False
        self.input_stream = None
        self.output_stream = None

        # Audio queues and threading
        self.audio_queue: "queue.Queue[bytes]" = queue.Queue()
        self.audio_send_queue: "queue.Queue[str]" = queue.Queue()  # base64 audio to send
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.capture_thread: Optional[threading.Thread] = None
        self.playback_thread: Optional[threading.Thread] = None
        self.send_thread: Optional[threading.Thread] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None  # Store the event loop

        logger.info("AudioProcessor initialized with 24kHz PCM16 mono audio")

    async def start_capture(self):
        """Start capturing audio from microphone."""
        if self.is_capturing:
            return

        # Store the current event loop for use in threads
        self.loop = asyncio.get_event_loop()

        self.is_capturing = True

        try:
            self.input_stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=None,
            )

            self.input_stream.start_stream()

            # Start capture thread
            self.capture_thread = threading.Thread(target=self._capture_audio_thread)
            self.capture_thread.daemon = True
            self.capture_thread.start()

            # Start audio send thread
            self.send_thread = threading.Thread(target=self._send_audio_thread)
            self.send_thread.daemon = True
            self.send_thread.start()

            logger.info("Started audio capture")

        except Exception as e:
            logger.error(f"Failed to start audio capture: {e}")
            self.is_capturing = False
            raise

    def _capture_audio_thread(self):
        """Audio capture thread - runs in background."""
        while self.is_capturing and self.input_stream:
            try:
                # Read audio data
                audio_data = self.input_stream.read(self.chunk_size, exception_on_overflow=False)

                if audio_data and self.is_capturing:
                    # Convert to base64 and queue for sending
                    audio_base64 = base64.b64encode(audio_data).decode("utf-8")
                    self.audio_send_queue.put(audio_base64)

            except Exception as e:
                if self.is_capturing:
                    logger.error(f"Error in audio capture: {e}")
                break

    def _send_audio_thread(self):
        """Audio send thread - handles async operations from sync thread."""
        while self.is_capturing:
            try:
                # Get audio data from queue (blocking with timeout)
                audio_base64 = self.audio_send_queue.get(timeout=0.1)

                if audio_base64 and self.is_capturing and self.loop:
                    # Schedule the async send operation in the main event loop
                    try:
                        future = asyncio.run_coroutine_threadsafe(
                            self.connection.input_audio_buffer.append(audio=audio_base64), self.loop
                        )
                        # Wait briefly to catch any immediate errors
                        try:
                            future.result(timeout=0.05)
                        except TimeoutError:
                            pass  # Expected - operation still running
                    except Exception as e:
                        if self.is_capturing:
                            logger.error(f"Error scheduling audio send: {e}")

            except queue.Empty:
                continue
            except Exception as e:
                if self.is_capturing:
                    logger.error(f"Error in send audio thread: {e}")
                break
        logger.debug("Send audio thread exiting")

    async def stop_capture(self):
        """Stop capturing audio."""
        if not self.is_capturing:
            return

        self.is_capturing = False

        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.input_stream = None

        if self.capture_thread:
            self.capture_thread.join(timeout=1.0)

        if self.send_thread:
            self.send_thread.join(timeout=1.0)

        # Clear the send queue
        while not self.audio_send_queue.empty():
            try:
                self.audio_send_queue.get_nowait()
            except queue.Empty:
                break

        logger.info("Stopped audio capture")

    async def start_playback(self):
        """Initialize audio playback system."""
        if self.is_playing:
            return

        self.is_playing = True

        try:
            self.output_stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                output=True,
                frames_per_buffer=self.chunk_size,
            )

            # Start playback thread
            self.playback_thread = threading.Thread(target=self._playback_audio_thread)
            self.playback_thread.daemon = True
            self.playback_thread.start()

            logger.info("Audio playback system ready")

        except Exception as e:
            logger.error(f"Failed to initialize audio playback: {e}")
            self.is_playing = False
            raise

    def _playback_audio_thread(self):
        """Audio playback thread - runs in background."""
        while self.is_playing:
            try:
                # Get audio data from queue (blocking with timeout)
                audio_data = self.audio_queue.get(timeout=0.1)

                # Double-check state before writing to prevent race condition
                if audio_data and self.is_playing:
                    stream = self.output_stream
                    if stream:
                        try:
                            stream.write(audio_data)
                        except OSError as e:
                            # Stream was closed, exit gracefully
                            if self.is_playing:
                                logger.debug(f"Stream write interrupted: {e}")
                            break

            except queue.Empty:
                continue
            except Exception as e:
                if self.is_playing:
                    logger.error(f"Error in audio playback: {e}")
                break
        logger.debug("Playback thread exiting")

    async def queue_audio(self, audio_data: bytes):
        """Queue audio data for playback."""
        if self.is_playing:
            self.audio_queue.put(audio_data)

    async def stop_playback(self):
        """Stop audio playback and clear queue."""
        if not self.is_playing:
            return

        self.is_playing = False

        # Clear the queue to help thread exit faster
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        # IMPORTANT: Join thread BEFORE closing stream to prevent race condition
        # where thread tries to write after stream is closed
        if self.playback_thread:
            self.playback_thread.join(timeout=2.0)
            self.playback_thread = None

        if self.output_stream:
            try:
                self.output_stream.stop_stream()
                self.output_stream.close()
            except Exception as e:
                logger.warning(f"Error closing output stream: {e}")
            finally:
                self.output_stream = None

        logger.info("Stopped audio playback")

    async def cleanup(self):
        """Clean up audio resources."""
        await self.stop_capture()
        await self.stop_playback()

        if self.audio:
            self.audio.terminate()

        self.executor.shutdown(wait=True)
        logger.info("Audio processor cleaned up")


class AsyncSupervisorAgentClient:
    """Async client for Azure Voice Live API with supervisor agent capabilities and audio input."""

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureCliCredential, DefaultAzureCredential],
        model: str,
        voice: str,
        instructions: str,
    ):
        self.endpoint = endpoint
        self.credential = credential
        self.model = model
        self.voice = voice
        self.instructions = instructions
        self.session_id: Optional[str] = None
        self.audio_processor: Optional[AudioProcessor] = None
        self.session_ready: bool = False


    async def run(self) -> None:
        """Run the voice assistant with supervisor agent capabilities.
        
        Establishes WebSocket connection, configures the session,
        and processes events until interrupted.
        """
        try:
            logger.info(f"Connecting to VoiceLive API with model {self.model}")

            # Connect to VoiceLive WebSocket API asynchronously
            async with connect(
                endpoint=self.endpoint,
                credential=self.credential,
                model=self.model,
                api_version="2026-01-01-preview",
            ) as connection:
                # Initialize audio processor
                self.audio_processor = AudioProcessor(connection)

                # Configure session with function tools
                await self._setup_session(connection)

                # Start audio playback system
                await self.audio_processor.start_playback()

                logger.info("Voice assistant with agent tools ready! Start speaking...")
                print("\n" + "=" * 70)
                print("🎤 VOICE ASSISTANT WITH SUPERVISOR AGENT READY")
                print("Try saying:")
                print("  • 'What production do you have?'")
                print("  • 'What color do you have?'")
                print("Press Ctrl+C to exit")
                print("=" * 70 + "\n")

                # Process events asynchronously
                await self._process_events(connection)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise
        finally:
            # Cleanup audio processor
            if self.audio_processor:
                await self.audio_processor.cleanup()

    async def _setup_session(self, connection) -> None:
        """Configure the VoiceLive session with supervisor agent capabilities."""
        logger.info("Setting up voice conversation session...")

        # Create voice configuration
        voice_config = AzureStandardVoice(name=self.voice)

        # Create turn detection configuration
        turn_detection_config = ServerVad(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=500)

        # Define available foundry agent tools
        foundry_agent_tools: list[FoundryAgentTool] = [
            FoundryAgentTool(
                agent_name=supervisor_agent_name,
                agent_version=supervisor_agent_version,
                project_name=supervisor_agent_project_name,
                description=supervisor_agent_description,
            )
        ]

        # Create session configuration with foundry agent tools
        session_config = RequestSession(
            modalities=[Modality.TEXT, Modality.AUDIO],
            instructions=self.instructions,
            voice=voice_config,
            input_audio_format=InputAudioFormat.PCM16,
            output_audio_format=OutputAudioFormat.PCM16,
            input_audio_echo_cancellation=AudioEchoCancellation(),
            turn_detection=turn_detection_config,
            tools=foundry_agent_tools,
            tool_choice=ToolChoiceLiteral.AUTO,  # Let the model decide when to call functions
            input_audio_transcription=AudioInputTranscriptionOptions(model="whisper-1"),
        )
        
        # Send session configuration asynchronously
        await connection.session.update(session=session_config)
        logger.info("Session configuration with agent tools sent")

    async def _process_events(self, connection) -> None:
        """Process events from the VoiceLive connection."""
        try:
            async for event in connection:
                await self._handle_event(event, connection)
        except KeyboardInterrupt:
            logger.info("Event processing interrupted")
        except Exception as e:
            logger.error(f"Error processing events: {e}")
            raise

    async def _handle_event(self, event, connection) -> None:
        """Handle different types of server events from VoiceLive."""
        ap = self.audio_processor
        assert ap is not None, "AudioProcessor must be initialized"

        if event.type == ServerEventType.SESSION_UPDATED:
            self.session_id = event.session.id
            logger.info(f"Session ready: {self.session_id}")
            self.session_ready = True

            # Start audio capture once session is ready
            await ap.start_capture()
            print("🎤 Ready for voice input! Try asking about zava productions...")

        elif event.type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED:
            logger.info("🎤 User started speaking - stopping playback")
            print("🎤 Listening...")

            # Stop current assistant audio playback (interruption handling)
            try:
                await ap.stop_playback()
            except Exception as e:
                logger.error(f"Error stopping playback: {e}")

        elif event.type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED:
            logger.info("🎤 User stopped speaking")
            print("🤔 Processing...")

            # Restart playback system for response
            try:
                await ap.start_playback()
            except Exception as e:
                logger.error(f"Error starting playback: {e}")

        elif event.type == ServerEventType.RESPONSE_CREATED:
            logger.info("🤖 Assistant response created")

        elif event.type == ServerEventType.RESPONSE_TEXT_DELTA:
            logger.info(f"Text response: {event.delta}")

        elif event.type == ServerEventType.RESPONSE_AUDIO_DELTA:
            # Stream audio response to speakers
            logger.debug("Received audio delta")
            await ap.queue_audio(event.delta)

        elif event.type == ServerEventType.RESPONSE_AUDIO_DONE:
            logger.info("🤖 Assistant finished speaking")
            print("🎤 Ready for next input...")

        elif event.type == ServerEventType.RESPONSE_DONE:
            logger.info("✅ Response complete")
        
        elif event.type == ServerEventType.CONVERSATION_ITEM_CREATED:
            if isinstance(event.item, ResponseFoundryAgentCallItem):
                logger.info(f"🛠️  Foundry Agent Call initiated with tool: {event.item.name}")

        elif event.type == ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_ARGUMENTS_DONE:
            logger.info(f"🛠️  Foundry Agent Call arguments: {event.arguments}")

        elif event.type == ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_IN_PROGRESS:
            if event.agent_response_id:
                logger.info(f"🛠️  Foundry Agent Call in progress with response ID: {event.agent_response_id}")
                
        elif event.type == ServerEventType.RESPONSE_OUTPUT_ITEM_DONE:
            if isinstance(event.item, ResponseFoundryAgentCallItem):
                logger.info(f"🛠️  Foundry Agent Call completed with output: {event.item.output}")

        elif event.type == ServerEventType.ERROR:
            logger.error(f"❌ VoiceLive error: {event.error.message}")
            print(f"Error: {event.error.message}")


async def main() -> None:
    """Main entry point for the supervisor agent sample."""
    # Get credentials from environment variables
    endpoint = os.environ.get("AZURE_VOICELIVE_ENDPOINT", "wss://api.voicelive.com/v1")

    
    credential = AzureCliCredential()

    # Create and run the supervisor agent client
    client = AsyncSupervisorAgentClient(
        endpoint=endpoint,
        credential=credential,
        model=chat_agent_model,
        voice=chat_agent_voice,
        instructions=chat_agent_instructions,
    )

    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        raise KeyboardInterrupt()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await client.run()
    except KeyboardInterrupt:
        print("\n👋 Supervisor Agent shut down.")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check for required dependencies
    dependencies = {
        "pyaudio": "Audio processing",
        "azure.ai.voicelive": "Azure VoiceLive SDK",
        "azure.core": "Azure Core libraries",
    }

    missing_deps = []
    for dep, description in dependencies.items():
        try:
            __import__(dep.replace("-", "_"))
        except ImportError:
            missing_deps.append(f"{dep} ({description})")

    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nInstall with:")
        print("  pip install azure-ai-voicelive python-dotenv")
        print("  For PyAudio:")
        print("    Linux: sudo apt-get install -y portaudio19-dev libasound2-dev && pip install pyaudio")
        print("    macOS: brew install portaudio && pip install pyaudio")
        print("    Windows: pip install pyaudio")
        sys.exit(1)

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

    print("🎙️  Voice Assistant with Supervisor Agent - Azure VoiceLive SDK")
    print("=" * 65)

    # Run the async main function
    asyncio.run(main())
