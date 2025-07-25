#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: basic_voice_assistant.py

DESCRIPTION:
    This sample demonstrates the fundamental capabilities of the VoiceLive SDK by creating
    a basic voice assistant that can engage in natural conversation with proper interruption
    handling. This serves as the foundational example that showcases the core value 
    proposition of unified speech-to-speech interaction.

USAGE:
    python basic_voice_assistant.py
    
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
from typing import Optional, Dict, Any
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
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential
from azure.ai.voicelive.aio import VoiceLiveClient
from azure.ai.voicelive.models import (
    VoiceLiveServerEventSessionUpdated,
    VoiceLiveServerEventInputAudioBufferSpeechStarted,
    VoiceLiveServerEventInputAudioBufferSpeechStopped,
    VoiceLiveServerEventResponseAudioDelta,
    VoiceLiveServerEventResponseAudioDone,
    VoiceLiveServerEventError,
    VoiceLiveServerEventResponseCreated,
    VoiceLiveServerEventResponseDone,
    VoiceLiveServerEventConversationItemCreated,
    VoiceLiveRequestSession,
    VoiceLiveServerVad,
    AzureStandardVoice,
    VoiceLiveModality,
    VoiceLiveAudioFormat,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
        self.audio_queue = queue.Queue()
        self.audio_send_queue = queue.Queue()  # Queue for audio data to send
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.capture_thread = None
        self.playback_thread = None
        self.send_thread = None
        self.loop = None  # Store the event loop
        
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
                stream_callback=None
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
                audio_data = self.input_stream.read(
                    self.chunk_size, 
                    exception_on_overflow=False
                )
                
                if audio_data and self.is_capturing:
                    # Convert to base64 and queue for sending
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
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
                        self.connection.input_audio_buffer.append(audio=audio_base64),
                        self.loop
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
                frames_per_buffer=self.chunk_size
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
    
    def __init__(self, client: VoiceLiveClient, model: str, voice: str, instructions: str):
        self.client = client
        self.model = model
        self.voice = voice
        self.instructions = instructions
        self.connection = None
        self.audio_processor = None
        self.session_ready = False
        self.conversation_started = False
        
    async def start(self):
        """Start the voice assistant session."""
        try:
            logger.info(f"Connecting to VoiceLive API with model {self.model}")
            
            # Connect to VoiceLive WebSocket API
            async with self.client.connect(
                model=self.model,
                connection_options={
                    "max_size": 10 * 1024 * 1024,  # 10 MB
                    "ping_interval": 20,  # 20 seconds
                    "ping_timeout": 20,  # 20 seconds
                }
            ) as connection:
                self.connection = connection
                
                # Initialize audio processor
                self.audio_processor = AudioProcessor(connection)
                
                # Configure session for voice conversation
                await self._setup_session()
                
                # Start audio systems
                await self.audio_processor.start_playback()
                
                logger.info("Voice assistant ready! Start speaking...")
                print("\n" + "="*60)
                print("🎤 VOICE ASSISTANT READY")
                print("Start speaking to begin conversation")
                print("Press Ctrl+C to exit")
                print("="*60 + "\n")
                
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
        logger.info("Setting up voice conversation session...")
        
        # Create strongly typed voice configuration
        if self.voice.startswith("en-US-") or self.voice.startswith("en-CA-") or "-" in self.voice:
            # Azure voice
            voice_config = AzureStandardVoice(
                name=self.voice,
                type="azure-standard"
            )
        else:
            # OpenAI voice (alloy, echo, fable, onyx, nova, shimmer)
            voice_config = self.voice
        
        # Create strongly typed turn detection configuration
        turn_detection_config = VoiceLiveServerVad(
            threshold=0.5,
            prefix_padding_ms=300,
            silence_duration_ms=500
        )
        
        # Create strongly typed session configuration
        session_config = VoiceLiveRequestSession(
            modalities=[VoiceLiveModality.TEXT, VoiceLiveModality.AUDIO],
            instructions=self.instructions,
            voice=voice_config,
            input_audio_format=VoiceLiveAudioFormat.PCM16,
            output_audio_format=VoiceLiveAudioFormat.PCM16,
            turn_detection=turn_detection_config
        )
        
        await self.connection.session.update(session=session_config)
        
        logger.info("Session configuration sent")
    
    async def _process_events(self):
        """Process events from the VoiceLive connection."""
        try:
            async for event in self.connection:
                await self._handle_event(event)
                
        except KeyboardInterrupt:
            logger.info("Event processing interrupted")
        except Exception as e:
            logger.error(f"Error processing events: {e}")
            raise
    
    async def _handle_event(self, event):
        """Handle different types of events from VoiceLive."""
        logger.debug(f"Received event: {event.type}")
        
        if isinstance(event, VoiceLiveServerEventSessionUpdated):
            logger.info(f"Session ready: {event.session.id}")
            self.session_ready = True
            
            # Start audio capture once session is ready
            await self.audio_processor.start_capture()
            
        elif isinstance(event, VoiceLiveServerEventInputAudioBufferSpeechStarted):
            logger.info("🎤 User started speaking - stopping playback")
            print("🎤 Listening...")
            
            # Stop current assistant audio playback (interruption handling)
            await self.audio_processor.stop_playback()
            
            # Cancel any ongoing response
            try:
                await self.connection.response.cancel()
            except Exception as e:
                logger.debug(f"No response to cancel: {e}")
            
        elif isinstance(event, VoiceLiveServerEventInputAudioBufferSpeechStopped):
            logger.info("🎤 User stopped speaking")
            print("🤔 Processing...")
            
            # Restart playback system for response
            await self.audio_processor.start_playback()
            
        elif isinstance(event, VoiceLiveServerEventResponseCreated):
            logger.info("🤖 Assistant response created")
            
        elif isinstance(event, VoiceLiveServerEventResponseAudioDelta):
            # Stream audio response to speakers
            logger.debug("Received audio delta")
            await self.audio_processor.queue_audio(event.delta)
            
        elif isinstance(event, VoiceLiveServerEventResponseAudioDone):
            logger.info("🤖 Assistant finished speaking")
            print("🎤 Ready for next input...")
            
        elif isinstance(event, VoiceLiveServerEventResponseDone):
            logger.info("✅ Response complete")
            
        elif isinstance(event, VoiceLiveServerEventError):
            logger.error(f"❌ VoiceLive error: {event.error.message}")
            print(f"Error: {event.error.message}")
            
        elif isinstance(event, VoiceLiveServerEventConversationItemCreated):
            logger.debug(f"Conversation item created: {event.item.id}")
            
        else:
            logger.debug(f"Unhandled event type: {event.type}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Basic Voice Assistant using Azure VoiceLive SDK",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--api-key",
        help="Azure VoiceLive API key. If not provided, will use AZURE_VOICELIVE_API_KEY environment variable.",
        type=str,
        default=os.environ.get("AZURE_VOICELIVE_API_KEY")
    )
    
    parser.add_argument(
        "--endpoint",
        help="Azure VoiceLive endpoint",
        type=str,
        default=os.environ.get("AZURE_VOICELIVE_ENDPOINT", "wss://api.voicelive.com/v1")
    )
    
    parser.add_argument(
        "--model",
        help="VoiceLive model to use",
        type=str,
        default=os.environ.get("VOICELIVE_MODEL", "gpt-4o-realtime-preview")
    )
    
    parser.add_argument(
        "--voice",
        help="Voice to use for the assistant",
        type=str,
        default=os.environ.get("VOICELIVE_VOICE", "en-US-AvaNeural"),
        choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer", 
                "en-US-AvaNeural", "en-US-JennyNeural", "en-US-GuyNeural"]
    )
    
    parser.add_argument(
        "--instructions",
        help="System instructions for the AI assistant",
        type=str,
        default=os.environ.get("VOICELIVE_INSTRUCTIONS", 
                             "You are a helpful AI assistant. Respond naturally and conversationally. "
                             "Keep your responses concise but engaging.")
    )
    
    parser.add_argument(
        "--use-token-credential",
        help="Use Azure token credential instead of API key",
        action="store_true"
    )
    
    parser.add_argument(
        "--verbose",
        help="Enable verbose logging",
        action="store_true"
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
    
    try:
        # Create client with appropriate credential
        if args.use_token_credential:
            credential = DefaultAzureCredential()
            logger.info("Using Azure token credential")
        else:
            credential = AzureKeyCredential(args.api_key)
            logger.info("Using API key credential")
        
        # Initialize VoiceLive client
        client = VoiceLiveClient(
            credential=credential,
            endpoint=args.endpoint,
        )
        
        # Create and start voice assistant
        assistant = BasicVoiceAssistant(
            client=client,
            model=args.model,
            voice=args.voice,
            instructions=args.instructions
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
        'pyaudio': 'Audio processing',
        'azure.ai.voicelive': 'Azure VoiceLive SDK',
        'azure.core': 'Azure Core libraries'
    }
    
    missing_deps = []
    for dep, description in dependencies.items():
        try:
            __import__(dep.replace('-', '_'))
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
        input_devices = [i for i in range(p.get_device_count()) 
                        if p.get_device_info_by_index(i)['maxInputChannels'] > 0]
        # Check for output devices  
        output_devices = [i for i in range(p.get_device_count())
                         if p.get_device_info_by_index(i)['maxOutputChannels'] > 0]
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