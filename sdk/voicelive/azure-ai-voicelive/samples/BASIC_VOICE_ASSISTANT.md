# Basic Voice Assistant

This sample demonstrates a complete voice assistant implementation using the Azure AI VoiceLive SDK with async patterns. It provides real-time speech-to-speech interaction with interruption handling and server-side voice activity detection.

## Features

- **Real-time Speech Streaming**: Continuous audio capture and playback
- **Server-Side Voice Activity Detection (VAD)**: Automatic detection of speech start/end
- **Interruption Handling**: Users can interrupt the AI assistant mid-response
- **High-Quality Audio Processing**: 24kHz PCM16 mono audio for optimal quality
- **Robust Error Handling**: Connection error recovery and graceful shutdown
- **Async Architecture**: Non-blocking operations for responsive interaction
- **Optional Telemetry Tracing**: Built-in OpenTelemetry support via `--enable-tracing` flag

## Prerequisites

- Python 3.9+
- Microphone and speakers/headphones
- Azure AI VoiceLive API key and endpoint

## Installation

1. **Install the SDK**:
   ```bash
   pip install azure-ai-voicelive python-dotenv
   ```

2. **Install PyAudio** (required for audio capture/playback):

   PyAudio requires PortAudio to be installed on your system:

   - **Linux (Ubuntu/Debian)**:
     ```bash
     sudo apt-get install -y portaudio19-dev libasound2-dev
     pip install pyaudio
     ```
   - **macOS**:
     ```bash
     brew install portaudio
     pip install pyaudio
     ```
   - **Windows**:
     ```bash
     pip install pyaudio
     ```

## Configuration

Create a `.env` file with your credentials:

```bash
AZURE_VOICELIVE_API_KEY=your-api-key
AZURE_VOICELIVE_ENDPOINT=your-endpoint
AZURE_VOICELIVE_MODEL=gpt-realtime
AZURE_VOICELIVE_VOICE=en-US-AvaNeural
AZURE_VOICELIVE_INSTRUCTIONS=You are a helpful AI assistant. Respond naturally and conversationally.
```

## Running the Sample

```bash
python basic_voice_assistant_async.py
```

Optional command-line arguments:

```bash
python basic_voice_assistant_async.py \
    --model gpt-realtime \
    --voice en-US-AvaNeural \
    --instructions "You are a helpful assistant" \
    --verbose
```

## How It Works

### 1. Connection Setup
The sample establishes an async WebSocket connection to the Azure VoiceLive service:

```python
async with connect(
    endpoint=endpoint,
    credential=credential,
    model=model
) as connection:
    # Voice assistant logic here
```

### 2. Session Configuration
Configures audio formats, voice settings, and VAD parameters:

```python
session_config = RequestSession(
    modalities=[Modality.TEXT, Modality.AUDIO],
    instructions=instructions,
    voice=voice_config,
    input_audio_format=InputAudioFormat.PCM16,
    output_audio_format=OutputAudioFormat.PCM16,
    turn_detection=ServerVad(
        threshold=0.5,
        prefix_padding_ms=300,
        silence_duration_ms=500
    ),
)
```

### 3. Audio Processing
- **Input**: Captures microphone audio in real-time using PyAudio
- **Streaming**: Sends base64-encoded audio chunks to the service
- **Output**: Receives and plays AI-generated speech responses

### 4. Event Handling
Processes various server events:

- `SESSION_UPDATED`: Session is ready for interaction
- `INPUT_AUDIO_BUFFER_SPEECH_STARTED`: User starts speaking (interrupt AI)
- `INPUT_AUDIO_BUFFER_SPEECH_STOPPED`: User stops speaking (process input)
- `RESPONSE_AUDIO_DELTA`: Receive AI speech audio chunks
- `RESPONSE_DONE`: AI response complete
- `ERROR`: Handle service errors

## Threading Architecture

The sample uses a multi-threaded approach for real-time audio processing:

- **Main Thread**: Async event loop and UI
- **Capture Thread**: PyAudio input stream reading
- **Send Thread**: Audio data transmission to service
- **Playback Thread**: PyAudio output stream writing

## Key Classes

### AudioProcessor
Manages real-time audio capture and playback with proper threading and queue management.

### BasicVoiceAssistant
Main application class that coordinates WebSocket connection, session management, and audio processing.

## Supported Voices

### Azure Neural Voices
- `en-US-AvaNeural` - Female, natural and professional
- `en-US-JennyNeural` - Female, conversational  
- `en-US-GuyNeural` - Male, professional

### OpenAI Voices
- `alloy` - Versatile, neutral
- `echo` - Precise, clear
- `fable` - Animated, expressive
- `onyx` - Deep, authoritative
- `nova` - Warm, conversational
- `shimmer` - Optimistic, friendly

## Troubleshooting

### Audio Issues
- **No microphone detected**: Check device connections and permissions
- **No audio output**: Verify speakers/headphones are connected
- **Audio quality issues**: Ensure 24kHz sample rate support

### Connection Issues
- **WebSocket errors**: Verify endpoint and credentials
- **API errors**: Check model availability and account permissions
- **Network timeouts**: Check firewall settings and network connectivity

### PyAudio Installation Issues
- **Linux**: `sudo apt-get install -y portaudio19-dev libasound2-dev`
- **macOS**: `brew install portaudio`
- **Windows**: Usually installs without issues

## Advanced Usage

### Custom Instructions
Modify the AI assistant's behavior by customizing the instructions:

```bash
python basic_voice_assistant_async.py --instructions "You are a coding assistant that helps with Python programming questions."
```

### Voice Selection
Choose different voices for varied experience:

```bash
# Azure Neural Voice
python basic_voice_assistant_async.py --voice en-US-JennyNeural

# OpenAI Voice  
python basic_voice_assistant_async.py --voice nova
```

### Debug Mode
Enable verbose logging for troubleshooting:

```bash
python basic_voice_assistant_async.py --verbose
```

### Telemetry Tracing
Enable OpenTelemetry tracing to emit spans for all connection, send, and receive operations:

```bash
# Console tracing (spans printed to stdout)
python basic_voice_assistant_async.py --enable-tracing

# With full message content in traces (may contain personal data)
python basic_voice_assistant_async.py --enable-tracing --enable-content-recording
```

This requires additional dependencies:
```bash
pip install opentelemetry-sdk azure-core-tracing-opentelemetry
```

When enabled, the following are traced automatically:
- **connect** span covering the entire WebSocket session lifetime
- **send** spans for each message sent (session.update, response.create, etc.)
- **recv** spans for each message received (session.created, response.done, etc.)
- **close** span when the session ends
- Session-level metrics: turn count, audio bytes, first-token latency, interruptions

See the `telemetry/` folder for more advanced tracing examples (Azure Monitor export, custom attributes, OTLP).

## Code Structure

```
basic_voice_assistant_async.py
├── AudioProcessor class
│   ├── Audio capture (microphone input)
│   ├── Audio streaming (to service)
│   └── Audio playback (AI responses)
├── BasicVoiceAssistant class
│   ├── WebSocket connection management
│   ├── Session configuration
│   └── Event processing
└── Main execution
    ├── Argument parsing
    ├── Telemetry setup (optional, --enable-tracing)
    ├── Environment setup
    └── Assistant initialization
```

## Next Steps

- Explore `async_function_calling_sample.py` for function calling capabilities
- Check out other samples in the `samples/` directory
- Read the main SDK documentation in `README.md`
- Review the API reference for advanced usage patterns