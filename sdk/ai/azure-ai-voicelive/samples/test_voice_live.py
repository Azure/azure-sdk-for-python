#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: test_voice_live.py

DESCRIPTION:
    This sample demonstrates the fundamental capabilities of the VoiceLive SDK by creating
    a comprehensive voice assistant that can engage in natural conversation with proper interruption
    handling. It includes advanced audio processing features and optional function calling
    capabilities for time and weather information. This serves as the foundational example 
    that showcases the core value proposition of unified speech-to-speech interaction.

USAGE:
    python test_voice_live.py
    python test_voice_live.py --enable-function-calling
    
    Set the environment variables with your own values before running the sample:
    1) AZURE_VOICELIVE_KEY - The Azure VoiceLive API key
    2) AZURE_VOICELIVE_ENDPOINT - The Azure VoiceLive endpoint
    
    Or copy .env.template to .env and fill in your values.

REQUIREMENTS:
    - azure-ai-voicelive
    - python-dotenv
    - pyaudio (for audio capture and playback)
"""

import os
import sys
import asyncio
import base64
import argparse
import signal
import threading
import queue
import json
import datetime
from azure.ai.voicelive.models import ServerEventType
from typing import Union, Optional, TYPE_CHECKING, cast, Dict, Any, Mapping, Callable
from concurrent.futures import ThreadPoolExecutor
import logging

# Audio processing imports
try:
    import pyaudio
except ImportError:
    print("This sample requires pyaudio. Install with: pip install pyaudio")
    sys.exit(1)

# Environment variable loading
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("Note: python-dotenv not installed. Using existing environment variables.")

# Azure VoiceLive SDK imports
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential

from azure.ai.voicelive.aio import connect

if TYPE_CHECKING:
    # Only needed for type checking; avoids runtime import issues
    from azure.ai.voicelive.aio import VoiceLiveConnection

from azure.ai.voicelive.models import (
    RequestSession,
    ServerVad,
    AzureSemanticVad,
    AzureMultilingualSemanticVad,
    AzureSemanticDetection,
    AzureSemanticDetectionMultilingual,
    AzureStandardVoice,
    Modality,
    InputAudioFormat,
    OutputAudioFormat,
    AudioInputTranscriptionSettings,
    AudioNoiseReduction,
    AudioEchoCancellation,
    FunctionTool,
    FunctionCallItem,
    FunctionCallOutputItem,
    ItemType,
    ToolChoiceLiteral,
    ResponseFunctionCallItem,
    ServerEventConversationItemCreated,
    ServerEventResponseFunctionCallArgumentsDone,
    Tool,
)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _load_audio_b64(path: str) -> str:
    """Load audio file and return base64 encoded string."""
    with open(path, "rb") as f:
        audio_bytes = f.read()
    return base64.b64encode(audio_bytes).decode("utf-8")


async def _wait_for_event(conn, wanted_types: set, timeout_s: float = 10.0):
    """Wait until we receive any event whose type is in wanted_types."""
    async def _next():
        while True:
            evt = await conn.recv()
            if evt.type in wanted_types:
                return evt
    return await asyncio.wait_for(_next(), timeout=timeout_s)


async def _wait_for_match(conn, predicate: Callable[[Any], bool], timeout_s: float = 10.0):
    """Wait until we receive an event that satisfies the given predicate."""
    async def _next():
        while True:
            evt = await conn.recv()
            if predicate(evt):
                return evt
    return await asyncio.wait_for(_next(), timeout=timeout_s)


class AudioProcessor:
    """
    Handles real-time audio capture and playback for the voice assistant.

    Threading Architecture:
    - Main thread: Event loop and UI
    - Capture thread: PyAudio input stream reading
    - Send thread: Async audio data transmission to VoiceLive
    - Playback thread: PyAudio output stream writing
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
                    future = asyncio.run_coroutine_threadsafe(
                        self.connection.input_audio_buffer.append(audio=audio_base64), self.loop
                    )
                    # Don't wait for completion to avoid blocking

            except queue.Empty:
                continue
            except Exception as e:
                if self.is_capturing:
                    logger.error(f"Error sending audio: {e}")
                break

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

                if audio_data and self.output_stream and self.is_playing:
                    self.output_stream.write(audio_data)

            except queue.Empty:
                continue
            except Exception as e:
                if self.is_playing:
                    logger.error(f"Error in audio playback: {e}")
                break

    async def queue_audio(self, audio_data: bytes):
        """Queue audio data for playback."""
        if self.is_playing:
            self.audio_queue.put(audio_data)

    async def stop_playback(self):
        """Stop audio playback and clear queue."""
        if not self.is_playing:
            return

        self.is_playing = False

        # Clear the queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            self.output_stream = None

        if self.playback_thread:
            self.playback_thread.join(timeout=1.0)

        logger.info("Stopped audio playback")

    async def cleanup(self):
        """Clean up audio resources."""
        await self.stop_capture()
        await self.stop_playback()

        if self.audio:
            self.audio.terminate()

        self.executor.shutdown(wait=True)
        logger.info("Audio processor cleaned up")


class BasicVoiceAssistant:
    """Basic voice assistant implementing the VoiceLive SDK patterns."""

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, TokenCredential],
        model: str,
        voice: str,
        instructions: str,
        language: str = "en-US",
        noise_reduction: bool = False,
        echo_cancellation: bool = False,
        vad_type: str = "basic",
        silence_duration: int = 500,
        threshold: float = 0.5,
        remove_filler_words: bool = False,
        languages: Optional[str] = None,
        speech_duration: int = 80,
        auto_truncate: bool = False,
        eou_detection: bool = False,
        eou_model: str = "semantic",
        eou_threshold: float = 0.1,
        eou_timeout: float = 4.0,
        eou_secondary_threshold: Optional[float] = None,
        eou_secondary_timeout: Optional[float] = None,
        # Agent parameters
        agent_id: Optional[str] = None,
        agent_connection_string: Optional[str] = None,
        agent_access_token: Optional[str] = None,
        phrase_list: Optional[str] = None,
        audio_file: Optional[str] = None,
        # Function calling parameters
        enable_function_calling: bool = False,
    ):

        self.endpoint = endpoint
        self.credential = credential
        self.model = model
        self.voice = voice
        self.instructions = instructions
        self.language = language
        self.noise_reduction = noise_reduction
        self.echo_cancellation = echo_cancellation
        self.vad_type = vad_type
        self.silence_duration = silence_duration
        self.threshold = threshold
        self.remove_filler_words = remove_filler_words
        self.languages = languages
        self.speech_duration = speech_duration
        self.auto_truncate = auto_truncate
        self.eou_detection = eou_detection
        self.eou_model = eou_model
        self.eou_threshold = eou_threshold
        self.eou_timeout = eou_timeout
        self.eou_secondary_threshold = eou_secondary_threshold
        self.eou_secondary_timeout = eou_secondary_timeout
        self.agent_id = agent_id
        self.agent_connection_string = agent_connection_string
        self.agent_access_token = agent_access_token
        self.phrase_list = phrase_list
        self.audio_file = audio_file
        self.enable_function_calling = enable_function_calling
        self.connection: Optional["VoiceLiveConnection"] = None
        self.audio_processor: Optional[AudioProcessor] = None
        self.session_ready = False
        self.conversation_started = False
        
        # Function calling state
        self.function_call_in_progress: bool = False
        self.active_call_id: Optional[str] = None
        
        # Define available functions
        self.available_functions: Dict[str, Callable[[Union[str, Mapping[str, Any]]], Mapping[str, Any]]] = {
            "get_current_time": self.get_current_time,
            "get_current_weather": self.get_current_weather,
        }

    async def start(self):
        """Start the voice assistant session."""
        try:
            # Determine connection mode and parameters
            if self.agent_id and self.agent_connection_string and self.agent_access_token:
                # Agent-based connection
                logger.info(f"Connecting to VoiceLive API with agent {self.agent_id}")
                query_params = {
                    "agent-connection-string": self.agent_connection_string,
                    "agent-id": self.agent_id,
                    "agent-access-token": self.agent_access_token
                }
            else:
                # Model-based connection (existing behavior)
                logger.info(f"Connecting to VoiceLive API with model {self.model}")
                query_params = {}

            # Connect to VoiceLive WebSocket API
            async with connect(
                endpoint=self.endpoint,
                credential=self.credential,
                model=self.model,
                query=query_params,
                connection_options={
                    "max_msg_size": 10 * 1024 * 1024,
                    "heartbeat": 20,
                    "timeout": 20,
                },
            ) as connection:
                conn = connection
                self.connection = conn

                # Initialize audio processor
                ap = AudioProcessor(conn)
                self.audio_processor = ap

                # Configure session for voice conversation
                await self._setup_session()

                # Start audio systems
                await ap.start_playback()

                if self.audio_file:
                    # Audio file mode
                    logger.info(f"Audio file mode: {self.audio_file}")
                    print("\n" + "=" * 60)
                    print("🎵 AUDIO FILE MODE")
                    print(f"Processing audio file: {self.audio_file}")
                    print("Press Ctrl+C to exit")
                    print("=" * 60 + "\n")
                else:
                    # Live microphone mode
                    logger.info("Voice assistant ready! Start speaking...")
                    print("\n" + "=" * 60)
                    if self.enable_function_calling:
                        print("🎤 VOICE ASSISTANT WITH FUNCTION CALLING READY")
                        print("Try saying:")
                        print("  • 'What's the current time?'")
                        print("  • 'What's the weather in Seattle?'")
                        print("  • 'What time is it in UTC?'")
                    else:
                        print("🎤 VOICE ASSISTANT READY")
                        print("Start speaking to begin conversation")
                    print("Press Ctrl+C to exit")
                    print("=" * 60 + "\n")

                # Process events
                await self._process_events()

        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")

        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise

        # Cleanup
        if self.audio_processor:
            await self.audio_processor.cleanup()

    async def _setup_session(self):
        """Configure the VoiceLive session for audio conversation."""
        logger.info(f"Setting up voice conversation session for language: {self.language}")

        # Create strongly typed voice configuration
        voice_config: Union[AzureStandardVoice, str]
        if self.voice.startswith("en-US-") or self.voice.startswith("en-CA-") or "-" in self.voice:
            # Azure voice
            voice_config = AzureStandardVoice(name=self.voice, type="azure-standard")
        else:
            # OpenAI voice (alloy, echo, fable, onyx, nova, shimmer)
            voice_config = self.voice

        # Create EOU detection configuration if enabled
        eou_detection_config = self._get_eou_detection_config()

        # Create turn detection configuration based on VAD type
        if self.vad_type == "semantic-multilingual":
            # Parse languages if provided
            language_list = None
            if self.languages:
                language_list = [lang.strip() for lang in self.languages.split(",")]
            elif self.language != "en-US":
                language_list = [self.language]
            
            turn_detection_config = AzureMultilingualSemanticVad(
                threshold=self.threshold,
                silence_duration_ms=self.silence_duration,
                remove_filler_words=self.remove_filler_words,
                require_vowel=True,
                languages=language_list,
                speech_duration_ms=self.speech_duration,
                auto_truncate=self.auto_truncate,
                end_of_utterance_detection=eou_detection_config,
            )
        elif self.vad_type == "semantic":
            turn_detection_config = AzureSemanticVad(
                threshold=self.threshold,
                silence_duration_ms=self.silence_duration,
                remove_filler_words=self.remove_filler_words,
                require_vowel=True,
                languages=[self.language] if self.language != "en-US" else None,
                speech_duration_ms=self.speech_duration,
                auto_truncate=self.auto_truncate,
                end_of_utterance_detection=eou_detection_config,
            )
        else:  # basic
            turn_detection_config = ServerVad(
                threshold=self.threshold,
                prefix_padding_ms=300,
                silence_duration_ms=self.silence_duration,
                auto_truncate=self.auto_truncate,
                end_of_utterance_detection=eou_detection_config,
            )

        # Create input audio transcription configuration based on model and language
        input_audio_transcription = self._get_input_audio_transcription_config()
        
        # Create noise reduction configuration if enabled
        input_audio_noise_reduction = None
        if self.noise_reduction:
            input_audio_noise_reduction = AudioNoiseReduction()
        
        # Create echo cancellation configuration if enabled
        input_audio_echo_cancellation = None
        if self.echo_cancellation:
            input_audio_echo_cancellation = AudioEchoCancellation()
        
        # Create input audio configuration with phrase list biasing if provided
        input_audio = None
        if self.phrase_list:
            # Parse phrase list from comma-separated string
            phrases = [phrase.strip() for phrase in self.phrase_list.split(",") if phrase.strip()]
            if phrases:
               # input_audio = InputAudio(phrase_list=phrases)
                logger.info(f"Phrase list biasing enabled with {len(phrases)} phrases: {phrases}")
            else:
                logger.warning("⚠️  Empty phrase list provided")
        
        # Create function tools if function calling is enabled
        function_tools: Optional[list[Tool]] = None
        if self.enable_function_calling:
            function_tools = [
                FunctionTool(
                    name="get_current_time",
                    description="Get the current time",
                    parameters={
                        "type": "object",
                        "properties": {
                            "timezone": {
                                "type": "string",
                                "description": "The timezone to get the current time for, e.g., 'UTC', 'local'",
                            }
                        },
                        "required": [],
                    },
                ),
                FunctionTool(
                    name="get_current_weather",
                    description="Get the current weather in a given location",
                    parameters={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g., 'San Francisco, CA'",
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"],
                                "description": "The unit of temperature to use (celsius or fahrenheit)",
                            },
                        },
                        "required": ["location"],
                    },
                ),
            ]
            logger.info("Function calling enabled with time and weather functions")
        
        # Debug logging
        logger.info(f"Language: {self.language}")
        logger.info(f" Model: {self.model}")
        logger.info(f" VAD type: {self.vad_type}")
        logger.info(f" Threshold: {self.threshold}")
        logger.info(f" Silence duration: {self.silence_duration}ms")
        logger.info(f" Noise reduction: {self.noise_reduction}")
        logger.info(f" Echo cancellation: {self.echo_cancellation}")
        logger.info(f" Remove filler words: {self.remove_filler_words}")
        logger.info(f" Languages: {self.languages}")
        logger.info(f" Speech duration: {self.speech_duration}ms")
        logger.info(f" Auto truncate: {self.auto_truncate}")
        logger.info(f" EOU detection: {self.eou_detection}")
        logger.info(f" EOU model: {self.eou_model}")
        logger.info(f" EOU threshold: {self.eou_threshold}")
        logger.info(f" EOU timeout: {self.eou_timeout}s")
        logger.info(f" EOU secondary threshold: {self.eou_secondary_threshold}")
        logger.info(f" EOU secondary timeout: {self.eou_secondary_timeout}")
        logger.info(f" Input audio transcription config: {input_audio_transcription}")
        logger.info(f" EOU detection config: {eou_detection_config}")

        # Create strongly typed session configuration
        session_config = RequestSession(
            modalities=[Modality.TEXT, Modality.AUDIO],
            instructions=self.instructions,
            voice=voice_config,
            input_audio_format=InputAudioFormat.PCM16,
            output_audio_format=OutputAudioFormat.PCM16,
            turn_detection=turn_detection_config,
            input_audio_transcription=input_audio_transcription,
            input_audio_noise_reduction=input_audio_noise_reduction,
            input_audio_echo_cancellation=input_audio_echo_cancellation,
            tools=function_tools,
            tool_choice=ToolChoiceLiteral.AUTO if function_tools else None,
        )

        conn = self.connection
        assert conn is not None, "Connection must be established before setting up session"
        await conn.session.update(session=session_config)

        logger.info("Session configuration sent")

    async def _send_audio_file(self):
        """Send audio file to the VoiceLive service."""
        if not self.audio_file:
            return
            
        try:
            # Check if file exists
            if not os.path.exists(self.audio_file):
                logger.error(f"Audio file not found: {self.audio_file}")
                return
                
            logger.info(f"Loading audio file: {self.audio_file}")
            audio_b64 = _load_audio_b64(self.audio_file)
            
            conn = self.connection
            assert conn is not None, "Connection must be established before sending audio"
            
            logger.info("Sending audio file to VoiceLive service...")
            await conn.input_audio_buffer.append(audio=audio_b64)
            logger.info("Audio file sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending audio file: {e}")
            raise

    def _get_input_audio_transcription_config(self):
        """Get input audio transcription configuration based on model and language."""
        # For English, no language configuration needed (automatic multilingual)
        if self.language == "en-US":
            return None
            
        # Use whisper-1 for language support
        return AudioInputTranscriptionSettings(
            model="whisper-1",
            language=self.language
        )

    def _get_eou_detection_config(self):
        """Get end-of-utterance detection configuration."""
        if not self.eou_detection:
            return None
        
        # Create EOU detection configuration based on model type
        if self.eou_model == "multilingual":
            return AzureSemanticDetectionMultilingual(
                threshold=self.eou_threshold,
                timeout=self.eou_timeout,
                secondary_threshold=self.eou_secondary_threshold,
                secondary_timeout=self.eou_secondary_timeout,
            )
        else:  # semantic
            return AzureSemanticDetection(
                threshold=self.eou_threshold,
                timeout=self.eou_timeout,
                secondary_threshold=self.eou_secondary_threshold,
                secondary_timeout=self.eou_secondary_timeout,
            )

    async def _process_events(self):
        """Process events from the VoiceLive connection."""
        try:
            conn = self.connection
            assert conn is not None, "Connection must be established before processing events"
            async for event in conn:
                await self._handle_event(event)

        except KeyboardInterrupt:
            logger.info("Event processing interrupted")
        except Exception as e:
            logger.error(f"Error processing events: {e}")
            raise

    async def _handle_event(self, event):
        """Handle different types of events from VoiceLive."""
        logger.debug(f"Received event: {event.type}")
        ap = self.audio_processor
        conn = self.connection
        assert ap is not None, "AudioProcessor must be initialized"
        assert conn is not None, "Connection must be established"

        if event.type == ServerEventType.SESSION_UPDATED:
            logger.info(f"Session ready: {event.session.id}")
            self.session_ready = True

            if self.audio_file:
                # In audio file mode, send the file after session is ready
                await self._send_audio_file()
            else:
                # Start audio capture once session is ready (live mode)
                await ap.start_capture()

        elif event.type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED:
            logger.info("🎤 User started speaking - stopping playback")
            print("🎤 Listening...")

            # Stop current assistant audio playback (interruption handling)
            await ap.stop_playback()

            # Only cancel response in live mode, not in audio file mode
            if not self.audio_file:
                try:
                    await conn.response.cancel()
                except Exception as e:
                    logger.debug(f"No response to cancel: {e}")

        elif event.type == ServerEventType.INPUT_AUDIO_BUFFER_COMMITTED:
            logger.info("🎵 Audio buffer committed - entire audio file processed")
            print("🎵 Audio file fully processed!")

        elif event.type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED:
            logger.info("🎤 User stopped speaking")
            print("🤔 Processing...")

            # Restart playback system for response
            await ap.start_playback()

        elif event.type == ServerEventType.RESPONSE_CREATED:
            logger.info("🤖 Assistant response created")

        elif event.type == ServerEventType.RESPONSE_AUDIO_DELTA:
            # Stream audio response to speakers
            logger.debug("Received audio delta")
            await ap.queue_audio(event.delta)

        elif event.type == ServerEventType.RESPONSE_AUDIO_DONE:
            logger.info("🤖 Assistant finished speaking")
            print("🎤 Ready for next input...")

        elif event.type == ServerEventType.RESPONSE_DONE:
            logger.info("✅ Response complete")

        elif event.type == ServerEventType.ERROR:
            logger.error(f"❌ VoiceLive error: {event.error.message}")
            print(f"Error: {event.error.message}")

        elif event.type == ServerEventType.CONVERSATION_ITEM_CREATED:
            logger.debug(f"Conversation item created: {event.item.id}")
            
            # Handle function calls if function calling is enabled
            if self.enable_function_calling and event.item.type == ItemType.FUNCTION_CALL:
                print(f"🔧 Calling function: {event.item.name}")
                await self._handle_function_call_with_improved_pattern(event, conn)

        else:
            logger.debug(f"Unhandled event type: {event.type}")

    async def _handle_function_call_with_improved_pattern(self, conversation_created_event, connection):
        """Handle function call using the improved pattern from the test."""
        # Validate the event structure
        if not isinstance(conversation_created_event, ServerEventConversationItemCreated):
            logger.error("Expected ServerEventConversationItemCreated")
            return

        if not isinstance(conversation_created_event.item, ResponseFunctionCallItem):
            logger.error("Expected ResponseFunctionCallItem")
            return

        function_call_item = conversation_created_event.item
        function_name = function_call_item.name
        call_id = function_call_item.call_id
        previous_item_id = function_call_item.id

        logger.info(f"Function call detected: {function_name} with call_id: {call_id}")

        try:
            # Set tracking variables
            self.function_call_in_progress = True
            self.active_call_id = call_id

            # Wait for the function arguments to be complete
            function_done = await _wait_for_event(connection, {ServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE})

            if not isinstance(function_done, ServerEventResponseFunctionCallArgumentsDone):
                logger.error("Expected ServerEventResponseFunctionCallArgumentsDone")
                return

            if function_done.call_id != call_id:
                logger.warning(f"Call ID mismatch: expected {call_id}, got {function_done.call_id}")
                return

            arguments = function_done.arguments
            logger.info(f"Function arguments received: {arguments}")

            # Wait for response to be done before proceeding
            await _wait_for_event(connection, {ServerEventType.RESPONSE_DONE})

            # Execute the function if we have it
            if function_name in self.available_functions:
                logger.info(f"Executing function: {function_name}")
                result = self.available_functions[function_name](arguments)

                # Create function call output item
                function_output = FunctionCallOutputItem(call_id=call_id, output=json.dumps(result))

                # Send the result back to the conversation with proper previous_item_id
                await connection.conversation.item.create(previous_item_id=previous_item_id, item=function_output)
                logger.info(f"Function result sent: {result}")

                # Create a new response to process the function result
                await connection.response.create()
                logger.info("Function result response created - audio will be generated automatically")

            else:
                logger.error(f"Unknown function: {function_name}")

        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for function call completion for {function_name}")
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {e}")
        finally:
            self.function_call_in_progress = False
            self.active_call_id = None

    def get_current_time(self, arguments: Optional[Union[str, Mapping[str, Any]]] = None) -> Dict[str, Any]:
        """Get the current time."""
        # Parse arguments if provided as string
        if isinstance(arguments, str):
            try:
                args = json.loads(arguments)
            except json.JSONDecodeError:
                args = {}
        elif isinstance(arguments, dict):
            args = arguments
        else:
            args = {}

        timezone = args.get("timezone", "local")
        now = datetime.datetime.now()

        if timezone.lower() == "utc":
            now = datetime.datetime.now(datetime.timezone.utc)
            timezone_name = "UTC"
        else:
            timezone_name = "local"

        formatted_time = now.strftime("%I:%M:%S %p")
        formatted_date = now.strftime("%A, %B %d, %Y")

        return {"time": formatted_time, "date": formatted_date, "timezone": timezone_name}

    def get_current_weather(self, arguments: Union[str, Mapping[str, Any]]):
        """Get the current weather for a location."""
        # Parse arguments if provided as string
        if isinstance(arguments, str):
            try:
                args = json.loads(arguments)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse weather arguments: {arguments}")
                return {"error": "Invalid arguments"}
        elif isinstance(arguments, dict):
            args = arguments
        else:
            return {"error": "No arguments provided"}

        location = args.get("location", "Unknown")
        unit = args.get("unit", "celsius")

        # In a real application, you would call a weather API
        # This is a simulated response
        try:
            weather_data = {
                "location": location,
                "temperature": 22 if unit == "celsius" else 72,
                "unit": unit,
                "condition": "Partly Cloudy",
                "humidity": 65,
                "wind_speed": 10,
            }

            return weather_data

        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return {"error": str(e)}


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Voice Assistant using Azure VoiceLive SDK with optional function calling",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--api-key",
        help="Azure VoiceLive API key. If not provided, will use AZURE_VOICELIVE_API_KEY environment variable.",
        type=str,
        default=os.environ.get("AZURE_VOICELIVE_API_KEY"),
    )

    parser.add_argument(
        "--endpoint",
        help="Azure VoiceLive endpoint",
        type=str,
        default=os.environ.get("AZURE_VOICELIVE_ENDPOINT", "wss://your-endpoint.cognitiveservices.azure.com/voice-live/realtime"),
    )

    parser.add_argument(
        "--model",
        help="VoiceLive model to use",
        type=str,
        default=os.environ.get("VOICELIVE_MODEL", "gpt-4o-realtime-preview"),
    )

    parser.add_argument(
        "--language",
        help="Language for the assistant (e.g., 'es-ES', 'fr-FR', 'de-DE'). For English, use 'en-US' for automatic multilingual detection.",
        type=str,
        default=os.environ.get("VOICELIVE_LANGUAGE", "en-US"),
    )

    parser.add_argument(
        "--noise-reduction",
        help="Enable audio noise reduction for better speech recognition in noisy environments",
        action="store_true",
        default=os.environ.get("VOICELIVE_NOISE_REDUCTION", "false").lower() == "true",
    )

    parser.add_argument(
        "--echo-cancellation",
        help="Enable echo cancellation to reduce echo and feedback during voice conversations",
        action="store_true",
        default=os.environ.get("VOICELIVE_ECHO_CANCELLATION", "false").lower() == "true",
    )

    parser.add_argument(
        "--vad-type",
        help="Voice Activity Detection type: 'basic' (ServerVad), 'semantic' (AzureSemanticVad), or 'semantic-multilingual' (AzureMultilingualSemanticVad)",
        type=str,
        choices=["basic", "semantic", "semantic-multilingual"],
        default=os.environ.get("VOICELIVE_VAD_TYPE", "basic"),
    )

    parser.add_argument(
        "--silence-duration",
        help="Silence duration in milliseconds before ending turn (200-1000ms)",
        type=int,
        default=int(os.environ.get("VOICELIVE_SILENCE_DURATION", "500")),
    )

    parser.add_argument(
        "--threshold",
        help="Speech detection threshold (0.0-1.0, lower = more sensitive)",
        type=float,
        default=float(os.environ.get("VOICELIVE_THRESHOLD", "0.5")),
    )

    parser.add_argument(
        "--remove-filler-words",
        help="Remove filler words (um, uh, like) from speech detection (semantic VAD only)",
        action="store_true",
        default=os.environ.get("VOICELIVE_REMOVE_FILLER_WORDS", "false").lower() == "true",
    )

    parser.add_argument(
        "--languages",
        help="Comma-separated list of languages for multilingual VAD (e.g., 'en-US,es-ES,fr-FR'). Up to 10 languages supported.",
        type=str,
        default=os.environ.get("VOICELIVE_LANGUAGES"),
    )

    parser.add_argument(
        "--speech-duration",
        help="Minimum speech duration in milliseconds to trigger VAD (semantic VAD only, default: 80ms)",
        type=int,
        default=int(os.environ.get("VOICELIVE_SPEECH_DURATION", "80")),
    )

    parser.add_argument(
        "--auto-truncate",
        help="Enable auto-truncation of assistant responses when user speaks",
        action="store_true",
        default=os.environ.get("VOICELIVE_AUTO_TRUNCATE", "false").lower() == "true",
    )



    parser.add_argument(
        "--eou-detection",
        help="Enable end-of-utterance detection for better turn detection",
        action="store_true",
        default=os.environ.get("VOICELIVE_EOU_DETECTION", "false").lower() == "true",
    )

    parser.add_argument(
        "--eou-model",
        help="EOU detection model: 'semantic' (AzureSemanticDetection) or 'multilingual' (AzureSemanticDetectionMultilingual)",
        type=str,
        choices=["semantic", "multilingual"],
        default=os.environ.get("VOICELIVE_EOU_MODEL", "semantic"),
    )

    parser.add_argument(
        "--eou-threshold",
        help="EOU detection threshold (0.0-1.0, lower = more sensitive)",
        type=float,
        default=float(os.environ.get("VOICELIVE_EOU_THRESHOLD", "0.1")),
    )

    parser.add_argument(
        "--eou-timeout",
        help="EOU detection timeout in seconds (default: 4.0)",
        type=float,
        default=float(os.environ.get("VOICELIVE_EOU_TIMEOUT", "4.0")),
    )

    parser.add_argument(
        "--eou-secondary-threshold",
        help="EOU secondary detection threshold (0.0-1.0)",
        type=float,
        default=float(os.environ.get("VOICELIVE_EOU_SECONDARY_THRESHOLD")) if os.environ.get("VOICELIVE_EOU_SECONDARY_THRESHOLD") else None,
    )

    parser.add_argument(
        "--eou-secondary-timeout",
        help="EOU secondary timeout in seconds",
        type=float,
        default=float(os.environ.get("VOICELIVE_EOU_SECONDARY_TIMEOUT")) if os.environ.get("VOICELIVE_EOU_SECONDARY_TIMEOUT") else None,
    )

    parser.add_argument(
        "--voice",
        help="Voice to use for the assistant",
        type=str,
        default=os.environ.get("VOICELIVE_VOICE", "en-US-AvaNeural"),
        choices=[
            "alloy",
            "echo",
            "fable",
            "onyx",
            "nova",
            "shimmer",
            "en-US-AvaNeural",
            "en-US-JennyNeural",
            "en-US-GuyNeural",
        ],
    )

    parser.add_argument(
        "--instructions",
        help="System instructions for the AI assistant",
        type=str,
        default=os.environ.get(
            "VOICELIVE_INSTRUCTIONS",
            "You are a helpful AI assistant. Respond naturally and conversationally. "
            "Keep your responses concise but engaging.",
        ),
    )

    parser.add_argument(
        "--use-token-credential", help="Use Azure token credential instead of API key", action="store_true"
    )

    # Agent parameters
    parser.add_argument(
        "--agent-id",
        help="Azure AI Foundry agent ID for agent-based connection",
        type=str,
        default=os.environ.get("AI_FOUNDRY_AGENT_ID"),
    )

    parser.add_argument(
        "--agent-connection-string",
        help="Agent connection string for agent-based connection",
        type=str,
        default=os.environ.get("AI_FOUNDRY_AGENT_CONNECTION_STRING"),
    )

    parser.add_argument(
        "--agent-access-token",
        help="Agent access token for agent-based connection",
        type=str,
        default=os.environ.get("AI_FOUNDRY_AGENT_ACCESS_TOKEN"),
    )

    # Phrase list biasing
    parser.add_argument(
        "--phrase-list",
        help="Comma-separated list of phrases to bias speech recognition (e.g., 'Azure,Microsoft,AI,GPT')",
        type=str,
        default=os.environ.get("VOICELIVE_PHRASE_LIST"),
    )

    parser.add_argument("--verbose", help="Enable verbose logging", action="store_true")

    # Audio file input
    parser.add_argument(
        "--audio-file",
        help="Path to audio file to send instead of live microphone input (supports .wav, .mp3, .m4a, etc.)",
        type=str,
        default=None,
    )

    # Function calling
    parser.add_argument(
        "--enable-function-calling",
        help="Enable function calling capabilities (time and weather functions)",
        action="store_true",
        default=os.environ.get("VOICELIVE_ENABLE_FUNCTION_CALLING", "false").lower() == "true",
    )

    return parser.parse_args()


async def main():
    """Main function."""
    args = parse_arguments()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate credentials
    if not args.api_key and not args.use_token_credential:
        print("❌ Error: No authentication provided")
        print("Please provide an API key using --api-key or set AZURE_VOICELIVE_API_KEY environment variable,")
        print("or use --use-token-credential for Azure authentication.")
        sys.exit(1)

    # Validate audio file if provided
    if args.audio_file and not os.path.exists(args.audio_file):
        print(f"❌ Error: Audio file not found: {args.audio_file}")
        sys.exit(1)

    try:
        # Create client with appropriate credential
        credential: Union[AzureKeyCredential, TokenCredential]
        if args.use_token_credential:
            credential = InteractiveBrowserCredential()  # or DefaultAzureCredential() if needed
            logger.info("Using Azure token credential")
        else:
            credential = AzureKeyCredential(args.api_key)
            logger.info("Using API key credential")

        # Modify instructions if function calling is enabled
        instructions = args.instructions
        if args.enable_function_calling:
            instructions += " You have access to functions for getting the current time and weather information. Use these functions when appropriate to provide accurate, real-time information."

        # Create and start voice assistant
        assistant = BasicVoiceAssistant(
            endpoint=args.endpoint,
            credential=credential,
            model=args.model,
            voice=args.voice,
            instructions=instructions,
            language=args.language,
            noise_reduction=args.noise_reduction,
            echo_cancellation=args.echo_cancellation,
            vad_type=args.vad_type,
            silence_duration=args.silence_duration,
            threshold=args.threshold,
            remove_filler_words=args.remove_filler_words,
            languages=args.languages,
            speech_duration=args.speech_duration,
            auto_truncate=args.auto_truncate,
            eou_detection=args.eou_detection,
            eou_model=args.eou_model,
            eou_threshold=args.eou_threshold,
            eou_timeout=args.eou_timeout,
            eou_secondary_threshold=args.eou_secondary_threshold,
            eou_secondary_timeout=args.eou_secondary_timeout,
            agent_id=args.agent_id,
            agent_connection_string=args.agent_connection_string,
            agent_access_token=args.agent_access_token,
            phrase_list=args.phrase_list,
            audio_file=args.audio_file,
            enable_function_calling=args.enable_function_calling,
        )

        # Setup signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            logger.info("Received shutdown signal")
            raise KeyboardInterrupt()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start the assistant
        await assistant.start()

    except KeyboardInterrupt:
        print("\n👋 Voice assistant shut down. Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Error: {e}")
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
        print("\nInstall with: pip install azure-ai-voicelive pyaudio python-dotenv")
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

    print("🎙️  Basic Voice Assistant with Azure VoiceLive SDK")
    print("=" * 50)

    # Run the assistant
    asyncio.run(main())