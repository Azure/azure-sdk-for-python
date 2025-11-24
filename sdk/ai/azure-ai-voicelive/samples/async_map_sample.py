# pylint: disable=line-too-long,useless-suppression
#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: async_mcp_sample.py

DESCRIPTION:
    This sample demonstrates how to use the Azure AI Voice Live SDK asynchronously
    with MCP capabilities. It shows how to define mcp servers, handle mcp call events.

USAGE:
    python async_mcp_sample.py
    
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
from typing import Union, Optional, Dict, Any, Callable, TYPE_CHECKING, cast
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
    MCPServer,
    ItemType,
    ToolChoiceLiteral,
    AudioInputTranscriptionOptions,
    ResponseMCPCallItem,
    ResponseMCPApprovalRequestItem,
    MCPApprovalResponseRequestItem,
    ServerEventConversationItemCreated,
    ServerEventResponseMcpCallArgumentsDone,
    ServerEventResponseCreated,
    ResponseMCPListToolItem,
    ServerEventResponseOutputItemDone,
    ServerEventResponseMcpCallCompleted,
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


class AsyncMCPCallClient:
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
        self.audio_processor: Optional[AudioProcessor] = None
        self.session_ready: bool = False


    async def run(self):
        """Run the async MCP call client with audio input."""
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

                logger.info("Voice assistant with MCP ready! Start speaking...")
                print("\n" + "=" * 70)
                print("🎤 VOICE ASSISTANT WITH MCP READY")
                print("Try saying:")
                print("  • 'Can you summary github repo azure sdk for python?'")
                print("  • 'Can you summary azure docs about voice live?'")
                print("You may need to approve some MCP calls interactively, see the console output for details.")
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
        """Configure the VoiceLive session with MCP tools asynchronously."""
        logger.info("Setting up voice conversation session with MCP tools...")

        # Create voice configuration
        voice_config = AzureStandardVoice(name=self.voice)

        # Create turn detection configuration
        turn_detection_config = ServerVad(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=500)

        # Define available MCP tools
        mcp_tools: list[Tool] = [
            MCPServer(
                server_label="deepwiki",
                server_url="https://mcp.deepwiki.com/mcp",
                allowed_tools= [
                    "read_wiki_structure",
                    "ask_question"
                ],
                require_approval="never",
            ),
            MCPServer(
                server_label="azure_doc",
                server_url="https://learn.microsoft.com/api/mcp",
                require_approval="always",
            )
        ]

        # Create session configuration with MCP tools
        session_config = RequestSession(
            modalities=[Modality.TEXT, Modality.AUDIO],
            instructions=self.instructions,
            voice=voice_config,
            input_audio_format=InputAudioFormat.PCM16,
            output_audio_format=OutputAudioFormat.PCM16,
            input_audio_echo_cancellation=AudioEchoCancellation(),
            turn_detection=turn_detection_config,
            tools=mcp_tools,
            tool_choice=ToolChoiceLiteral.AUTO,  # Let the model decide when to call functions
            input_audio_transcription=AudioInputTranscriptionOptions(model="whisper-1"),
        )

        # Send session configuration asynchronously
        await connection.session.update(session=session_config)
        logger.info("Session configuration with MCP tools sent")

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
            print("🎤 Ready for voice input! Try asking about github repo or azure documentation...")

        elif event.type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED:
            logger.info("🎤 User started speaking - stopping playback")
            print("🎤 Listening...")

            # Stop current assistant audio playback (interruption handling)
            await ap.stop_playback()

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

        elif event.type == ServerEventType.ERROR:
            logger.error(f"❌ VoiceLive error: {event.error.message}")
            print(f"Error: {event.error.message}")

        elif event.type == ServerEventType.MCP_LIST_TOOLS_IN_PROGRESS:
            logger.info(f"MCP list tools in progress for {event.item_id}")
        elif event.type == ServerEventType.MCP_LIST_TOOLS_COMPLETED:
            logger.info(f"MCP list tools completed for {event.item_id}.")
        elif event.type == ServerEventType.MCP_LIST_TOOLS_FAILED:
            logger.error(f"MCP list tools failed for {event.item_id}.")

        elif event.type == ServerEventType.RESPONSE_MCP_CALL_IN_PROGRESS:
            logger.info(f"MCP call in progress for {event.item_id}, please wait...")
        elif event.type == ServerEventType.RESPONSE_MCP_CALL_COMPLETED:
            logger.info(f"MCP call completed for {event.item_id}.")
            await self._handle_mcp_call_completed(event, connection)
        elif event.type == ServerEventType.RESPONSE_MCP_CALL_FAILED:
            logger.error(f"MCP call failed for {event.item_id}.")
    
        elif event.type == ServerEventType.CONVERSATION_ITEM_CREATED:
            logger.info(f"Conversation item created: id={event.item.id}, type={event.item.type}")
            if event.item.type == ItemType.MCP_LIST_TOOLS:
                logger.info(f"Received MCP list tools item: id={event.item.id}, server_label={event.item.server_label}")
            elif event.item.type == ItemType.MCP_CALL:
                await self._handle_mcp_call_arguments(event, connection)
            elif event.item.type == ItemType.MCP_APPROVAL_REQUEST:
                await self._handle_mcp_approval_request(event, connection)

    async def _handle_mcp_approval_request(self, conversation_created_event, connection):
        """Handle MCP approval request events."""
        # validate the event structure
        if not isinstance(conversation_created_event, ServerEventConversationItemCreated):
            logger.error("Expected ServerEventConversationItemCreated")
            return
        if not isinstance(conversation_created_event.item, ResponseMCPApprovalRequestItem):
            logger.error("Expected ResponseMCPApprovalRequestItem")
            return

        mcp_approval_item = conversation_created_event.item
        approval_id = mcp_approval_item.id
        server_label = mcp_approval_item.server_label
        function_name = mcp_approval_item.name
        arguments = mcp_approval_item.arguments
        if not approval_id:
            logger.error("MCP approval item missing ID")
            return

        logger.info(f"MCP Approval Request received: id={approval_id}, server_label={server_label}, function_name={function_name}, arguments={arguments}")

        # wait for user input to approve or deny
        approval_response = False
        while True:
            user_input = input("Approve MCP call? (y/n): ").strip().lower()
            if user_input == "y":
                approval_response = True
                break
            elif user_input == "n":
                approval_response = False
                break
            else:
                print("Invalid input. Please type 'y' to approve or 'n' to deny.")

        # Send approval response
        approval_response_item = MCPApprovalResponseRequestItem(
            approval_request_id=approval_id,
            approve=approval_response
        )
        await connection.conversation.item.create(item=approval_response_item)

    async def _handle_mcp_call_completed(self, mcp_call_completed_event: str, connection):
        """Handle MCP call completed events."""
        # validate the event structure
        if not isinstance(mcp_call_completed_event, ServerEventResponseMcpCallCompleted):
            logger.error("Expected ServerEventResponseMcpCallCompleted")
            return

        # print output item when MCP call is completed
        mcp_call_item_id = mcp_call_completed_event.item_id
        mcp_call_done = await _wait_for_event(connection, {ServerEventType.RESPONSE_OUTPUT_ITEM_DONE})
        if not isinstance(mcp_call_done, ServerEventResponseOutputItemDone):
            logger.error("Expected ServerEventResponseOutputItemDone")
            return
        if not isinstance(mcp_call_done.item, ResponseMCPCallItem):
            logger.error("Expected ResponseMCPCallItem")
            return
        if mcp_call_done.item.id != mcp_call_item_id:
            logger.error(f"Item ID mismatch: expected {mcp_call_item_id}, got {mcp_call_done.item.id}")
            return
        mcp_output = mcp_call_done.item.output
        logger.info(f"MCP Call output received: {mcp_output}")
        
        # Create a new response to process the MCP output
        await connection.response.create()

    async def _handle_mcp_call_arguments(self, conversation_created_event, connection):
        """Handle MCP call events."""
        # validate the event structure
        if not isinstance(conversation_created_event, ServerEventConversationItemCreated):
            logger.error("Expected ServerEventConversationItemCreated")
            return
        if not isinstance(conversation_created_event.item, ResponseMCPCallItem):
            logger.error("Expected ResponseMCPCallItem")
            return

        mcp_call_item = conversation_created_event.item
        server_label = mcp_call_item.server_label
        function_name = mcp_call_item.name
        arguments = mcp_call_item.arguments
        
        logger.info(f"MCP Call triggered: server_label={server_label}, function_name={function_name}")
        try:
            # Wait for the MCP call arguments to be complete
            mcp_arguments_done = await _wait_for_event(connection, {ServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DONE})
            if not isinstance(mcp_arguments_done, ServerEventResponseMcpCallArgumentsDone):
                logger.error("Expected ServerEventResponseMcpCallArgumentsDone")
                return
            if mcp_arguments_done.item_id != mcp_call_item.id:
                logger.warning(f"Item ID mismatch: expected {mcp_call_item.id}, got {mcp_arguments_done.item_id}")
                return
            arguments = mcp_arguments_done.arguments or "{}"
            logger.info(f"MCP Call arguments received: {arguments}")

            # Wait for response to be done before proceeding
            await _wait_for_event(connection, {ServerEventType.RESPONSE_DONE})

        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for MCP call arguments done for {function_name}")
            return
        except Exception as e:
            logger.error(f"Error waiting for MCP call arguments done: {e}")
            return

async def main():
    """Main async function."""
    # Get credentials from environment variables
    api_key = os.environ.get("AZURE_VOICELIVE_API_KEY")
    # important, PLEASE SET the features=mcp_preview:true in query params to enable mcp features
    endpoint = os.environ.get("AZURE_VOICELIVE_ENDPOINT", "wss://api.voicelive.com/v1?features=mcp_preview:true")

    if not api_key:
        print("❌ Error: No API key provided")
        print("Please set the AZURE_VOICELIVE_API_KEY environment variable.")
        sys.exit(1)

    # Option 1: API key authentication (simple, recommended for quick start)
    credential: Union[AzureKeyCredential, AsyncTokenCredential] = AzureKeyCredential(api_key)

    # Option 2: Async AAD authentication (requires azure-identity)
    # Uncomment the lines below to use AAD authentication instead:
    # from azure.identity.aio import AzureCliCredential, DefaultAzureCredential
    # credential = AzureCliCredential()

    # Create and run the client
    client = AsyncMCPCallClient(
        endpoint=endpoint,
        credential=credential,
        model="gpt-4o-realtime-preview",
        voice="en-US-AvaNeural",
        instructions="You are a helpful AI assistant with access to some mcp server. "
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
        print("\n👋 Voice Live MCP shut down.")
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

    print("🎙️  Voice Assistant with MCP - Azure VoiceLive SDK")
    print("=" * 65)

    # Run the async main function
    asyncio.run(main())
