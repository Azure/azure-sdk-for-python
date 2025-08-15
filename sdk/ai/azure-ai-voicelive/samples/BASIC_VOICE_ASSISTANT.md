# Basic Voice Assistant Sample

This sample demonstrates the fundamental capabilities of the Azure VoiceLive SDK by creating a basic voice assistant that can engage in natural conversation with proper interruption handling.

## Features

- **Real-time Voice Conversation**: Full duplex audio communication with the AI assistant
- **Server VAD**: Automatic turn detection using server-side voice activity detection
- **Interruption Handling**: Graceful handling of user interruptions during assistant responses
- **Cross-platform Audio**: PCM16, 24kHz, mono audio format with platform-appropriate handling
- **Error Recovery**: Robust connection management with exponential backoff retry logic
- **Environment Configuration**: Easy setup using .env files

## Prerequisites

- Python 3.8 or later
- Azure subscription with access to Azure AI VoiceLive
- Microphone and speakers/headphones
- Required Python packages (see installation below)

## Installation

1. **Install required packages**:
   ```bash
   pip install azure-ai-voicelive pyaudio python-dotenv
   ```

2. **Set up environment variables**:
   
   Copy the `.env.template` file to `.env` and fill in your values:
   ```bash
   cp ../.env.template .env
   ```
   
   Or set environment variables directly:
   ```bash
   export AZURE_VOICELIVE_KEY="your-api-key"
   export AZURE_VOICELIVE_ENDPOINT="wss://api.voicelive.com/v1"
   export VOICELIVE_MODEL="gpt-4o-realtime-preview"
   export VOICELIVE_VOICE="en-US-AvaNeural"
   ```

## Usage

### Basic Usage

Run the voice assistant with default settings:

```bash
python basic_voice_assistant.py
```

### Advanced Usage

Customize the voice assistant with command-line options:

```bash
python basic_voice_assistant.py \
    --model gpt-4o-realtime-preview \
    --voice en-US-JennyNeural \
    --instructions "You are a helpful coding assistant. Keep responses technical but friendly."
```

### Available Options

- `--api-key`: Azure VoiceLive API key (or use AZURE_VOICELIVE_KEY env var)
- `--endpoint`: VoiceLive endpoint URL
- `--model`: Model to use (default: gpt-4o-realtime-preview)
- `--voice`: Voice for the assistant (alloy, echo, fable, onyx, nova, shimmer, en-US-AvaNeural, etc.)
- `--instructions`: Custom system instructions for the AI
- `--use-token-credential`: Use Azure token authentication instead of API key
- `--verbose`: Enable detailed logging

## How It Works

### 1. Session Setup
The assistant establishes a WebSocket connection and configures the session using strongly-typed objects:
- Bidirectional audio streaming (PCM16, 24kHz, mono)
- Server-side voice activity detection with configurable thresholds
- Strongly-typed session configuration (RequestSession)
- Azure voice configuration (AzureStandardVoice) or OpenAI voices

### 2. Audio Processing
Real-time audio capture and playback using PyAudio:
- Microphone input is captured in 1024-sample chunks
- Audio is base64-encoded and streamed to VoiceLive
- Response audio is decoded and played back immediately

### 3. Event Handling
Strongly-typed event handling for real-time communication:
- `session.updated`: Session ready, start audio capture
- `input_audio_buffer.speech_started`: User speaking, stop playback
- `input_audio_buffer.speech_stopped`: User finished, process input  
- `response.audio.delta`: Stream response audio to speakers
- `response.audio.done`: Assistant finished speaking

### 4. Interruption Support
Graceful handling of user interruptions:
- Automatic detection when user starts speaking
- Immediate cancellation of ongoing assistant responses
- Seamless resumption of conversation flow

## Audio Requirements

- **Input**: Microphone capable of 24kHz sampling
- **Output**: Speakers or headphones
- **Format**: PCM16, 24kHz, mono
- **Latency**: Optimized for real-time conversation (< 300ms end-to-end)

## Troubleshooting

### Audio Issues
- **No microphone detected**: Check microphone permissions and connections
- **No audio output**: Verify speaker/headphone setup and volume levels
- **Audio quality issues**: Ensure quiet environment and quality microphone

### Connection Issues
- **Authentication errors**: Verify API key and endpoint configuration
- **Network timeouts**: Check internet connection and firewall settings
- **Connection drops**: SDK handles reconnection internally with appropriate retry logic

### Dependencies
- **PyAudio installation**: On some systems, may require additional setup:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install portaudio19-dev
  pip install pyaudio
  
  # macOS
  brew install portaudio
  pip install pyaudio
  
  # Windows
  pip install pyaudio
  ```

## Key Learning Outcomes

After running this sample, developers will understand:

1. **SDK Integration**: How to integrate VoiceLive SDK into applications
2. **Strongly-Typed Configuration**: Using typed objects for session setup instead of raw JSON
3. **Event-Driven Architecture**: Handling real-time events with strong typing
4. **Audio Processing**: Platform-specific audio handling through SDK abstractions
5. **Connection Management**: Letting the SDK handle connection retry logic internally
6. **Real-Time Applications**: Building responsive voice-enabled applications

### Strongly-Typed Configuration Example

The sample demonstrates proper use of typed objects:

```python
# Strongly-typed voice configuration
voice_config = AzureStandardVoice(
    name="en-US-AvaNeural",
    type="azure-standard"
)

# Strongly-typed turn detection
turn_detection_config = ServerVad(
    threshold=0.5,
    prefix_padding_ms=300,
    silence_duration_ms=500
)

# Strongly-typed session configuration
session_config = RequestSession(
    modalities=[Modality.TEXT, Modality.AUDIO],
    instructions=instructions,
    voice=voice_config,
    input_audio_format=AudioFormat.PCM16,
    output_audio_format=AudioFormat.PCM16,
    turn_detection=turn_detection_config
)

await connection.session.update(session=session_config)
```

## Next Steps

This foundational sample can be extended with:

- **Custom voice selection**: Different voice options and characteristics
- **Audio controls**: Volume adjustment and quality settings
- **Session persistence**: Conversation history and context management
- **Multi-language support**: Language detection and switching
- **Custom instructions**: Dynamic instruction updates during conversation

## Related Samples

- `audio_streaming_sample.py`: Low-level audio streaming patterns
- `typed_event_handling_sample.py`: Advanced event handling techniques
- `session_management_sample.py`: Session configuration and management