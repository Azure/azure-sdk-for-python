# pylint: disable=line-too-long,useless-suppression
#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: async_function_calling_sample.py

DESCRIPTION:
    This sample demonstrates how to use the Azure AI Voice Live SDK asynchronously
    with function calling capabilities. It shows how to define functions,
    handle function calls from the AI model, and process the results.

USAGE:
    python async_function_calling_sample.py
    
    Set the environment variables with your own values before running the sample:
    1) AZURE_VOICELIVE_API_KEY - The Azure VoiceLive API key
    2) AZURE_VOICELIVE_ENDPOINT - The Azure VoiceLive endpoint
    
REQUIREMENTS:
    - azure-ai-voicelive
    - python-dotenv
    - pyaudio (for audio capture and playback)
"""

import os
import sys
import asyncio
import json
import datetime
import logging
import base64
import signal
import threading
import queue
from typing import Union, Optional, Dict, Any, Mapping, Callable, TYPE_CHECKING, cast
from concurrent.futures import ThreadPoolExecutor

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
    FunctionTool,
    FunctionCallItem,
    FunctionCallOutputItem,
    ItemType,
    ToolChoiceLiteral,
    AudioInputTranscriptionOptions,
    ResponseFunctionCallItem,
    ServerEventConversationItemCreated,
    ServerEventResponseFunctionCallArgumentsDone,
    ServerEventResponseCreated,
    Tool,
)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def _wait_for_event(conn, wanted_types: set, timeout_s: float = 10.0):
    """Wait until we receive any event whose type is in wanted_types."""

    async def _next():
        while True:
            evt = await conn.recv()
            if evt.type in wanted_types:
                return evt

    return await asyncio.wait_for(_next(), timeout=timeout_s)


async def _wait_for_match(
    conn,
    predicate: Callable[[Any], bool],
    timeout_s: float = 10.0,
):
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

    Responsibilities:
    - Captures audio input from the microphone using PyAudio.
    - Plays back audio output using PyAudio.
    - Manages threading for audio capture, sending, and playback.
    - Uses queues to buffer audio data between threads.
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


class AsyncFunctionCallingClient:
    """Async client for Azure Voice Live API with function calling capabilities and audio input."""

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, AsyncTokenCredential],
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
        self.function_call_in_progress: bool = False
        self.active_call_id: Optional[str] = None
        self.audio_processor: Optional[AudioProcessor] = None
        self.session_ready: bool = False

        # Define available functions
        self.available_functions: Dict[str, Callable[[Union[str, Mapping[str, Any]]], Mapping[str, Any]]] = {
            "get_current_time": self.get_current_time,
            "get_current_weather": self.get_current_weather,
        }

    async def run(self):
        """Run the async function calling client with audio input."""
        try:
            logger.info(f"Connecting to VoiceLive API with model {self.model}")

            # Connect to VoiceLive WebSocket API asynchronously
            async with connect(
                endpoint=self.endpoint,
                credential=self.credential,
                model=self.model,
            ) as connection:
                # Initialize audio processor
                self.audio_processor = AudioProcessor(connection)

                # Configure session with function tools
                await self._setup_session(connection)

                # Start audio playback system
                await self.audio_processor.start_playback()

                logger.info("Voice assistant with function calling ready! Start speaking...")
                print("\n" + "=" * 70)
                print("🎤 VOICE ASSISTANT WITH FUNCTION CALLING READY")
                print("Try saying:")
                print("  • 'What's the current time?'")
                print("  • 'What's the weather in Seattle?'")
                print("  • 'What time is it in UTC?'")
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

    async def _setup_session(self, connection):
        """Configure the VoiceLive session with function tools asynchronously."""
        logger.info("Setting up voice conversation session with function tools...")

        # Create voice configuration
        voice_config = AzureStandardVoice(name=self.voice)

        # Create turn detection configuration
        turn_detection_config = ServerVad(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=500)

        # Define available function tools
        function_tools: list[Tool] = [
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

        # Create session configuration with function tools
        session_config = RequestSession(
            modalities=[Modality.TEXT, Modality.AUDIO],
            instructions=self.instructions,
            voice=voice_config,
            input_audio_format=InputAudioFormat.PCM16,
            output_audio_format=OutputAudioFormat.PCM16,
            input_audio_echo_cancellation=AudioEchoCancellation(),
            turn_detection=turn_detection_config,
            tools=function_tools,
            tool_choice=ToolChoiceLiteral.AUTO,  # Let the model decide when to call functions
            input_audio_transcription=AudioInputTranscriptionOptions(model="whisper-1"),
        )

        # Send session configuration asynchronously
        await connection.session.update(session=session_config)
        logger.info("Session configuration with function tools sent")

    async def _process_events(self, connection):
        """Process events from the VoiceLive connection asynchronously."""
        try:
            async for event in connection:
                await self._handle_event(event, connection)
        except KeyboardInterrupt:
            logger.info("Event processing interrupted")
        except Exception as e:
            logger.error(f"Error processing events: {e}")
            raise

    async def _handle_event(self, event, connection):
        """Handle different types of events from VoiceLive asynchronously."""
        ap = self.audio_processor
        assert ap is not None, "AudioProcessor must be initialized"

        if event.type == ServerEventType.SESSION_UPDATED:
            self.session_id = event.session.id
            logger.info(f"Session ready: {self.session_id}")
            self.session_ready = True

            # Start audio capture once session is ready
            await ap.start_capture()
            print("🎤 Ready for voice input! Try asking about time or weather with your location...")

        elif event.type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED:
            logger.info("🎤 User started speaking - stopping playback")
            print("🎤 Listening...")

            # Stop current assistant audio playback (interruption handling)
            await ap.stop_playback()

            # Cancel any ongoing response
            try:
                await connection.response.cancel()
            except Exception as e:
                logger.debug(f"No response to cancel: {e}")

        elif event.type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED:
            logger.info("🎤 User stopped speaking")
            print("🤔 Processing...")

            # Restart playback system for response
            await ap.start_playback()

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
            self.function_call_in_progress = False
            self.active_call_id = None

        elif event.type == ServerEventType.ERROR:
            logger.error(f"❌ VoiceLive error: {event.error.message}")
            print(f"Error: {event.error.message}")

        elif event.type == ServerEventType.CONVERSATION_ITEM_CREATED:
            logger.info(f"Conversation item created: {event.item.id}")

            # Check if it's a function call item using the improved pattern from the test
            if event.item.type == ItemType.FUNCTION_CALL:
                print(f"🔧 Calling function: {event.item.name}")
                await self._handle_function_call_with_improved_pattern(event, connection)

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

                # Wait for the final response
                response = await _wait_for_match(
                    connection,
                    lambda e: e.type == ServerEventType.RESPONSE_OUTPUT_ITEM_DONE
                    and hasattr(e, "item")
                    and e.item.id != previous_item_id,
                )

                if hasattr(response, "item") and hasattr(response.item, "content") and response.item.content:
                    if hasattr(response.item.content[0], "transcript"):
                        transcript = response.item.content[0].transcript
                        logger.info(f"Final response transcript: {transcript}")

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
        # This is a simulated response similar to the test
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


async def main():
    """Main async function."""
    # Get credentials from environment variables
    api_key = os.environ.get("AZURE_VOICELIVE_API_KEY")
    endpoint = os.environ.get("AZURE_VOICELIVE_ENDPOINT", "https://test.voicelive.com/")

    if not api_key:
        print("❌ Error: No API key provided")
        print("Please set the AZURE_VOICELIVE_API_KEY environment variable.")
        sys.exit(1)

    # Option 1: API key authentication (simple, recommended for quick start)
    credential = AzureKeyCredential(api_key)

    # Option 2: Async AAD authentication (requires azure-identity)
    # from azure.identity.aio import AzureCliCredential, DefaultAzureCredential
    # credential = DefaultAzureCredential() or AzureCliCredential()
    #
    # 👉 Use this if you prefer AAD/MSAL-based auth.
    #    It will look for environment variables like:
    #      AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
    #    or fall back to managed identity if running in Azure.

    # Create and run the client
    client = AsyncFunctionCallingClient(
        endpoint=endpoint,
        credential=credential,
        model="gpt-4o-realtime-preview",
        voice="en-US-AvaNeural",
        instructions="You are a helpful AI assistant with access to functions. "
        "Use the functions when appropriate to provide accurate, real-time information. "
        "If you are asked about the weather, please respond with 'I will get the weather for you. Please wait a moment.' and then call the get_current_weather function. "
        "If you are asked about the time, please respond with 'I will get the time for you. Please wait a moment.' and then call the get_current_time function. "
        "Explain when you're using a function and include the results in your response naturally.",
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
        print("\n👋 Voice Live function calling client shut down.")
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

    print("🎙️  Voice Assistant with Function Calling - Azure VoiceLive SDK")
    print("=" * 65)

    # Run the async main function
    asyncio.run(main())
