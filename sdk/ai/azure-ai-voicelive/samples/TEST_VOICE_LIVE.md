# Comprehensive Voice Assistant Sample

This sample demonstrates the advanced capabilities of the Azure VoiceLive SDK by creating a comprehensive voice assistant that can engage in natural conversation with proper interruption handling, function calling capabilities, and advanced audio processing features.

## Features

- **Real-time Voice Conversation**: Full duplex audio communication with the AI assistant
- **Advanced VAD Options**: Support for basic, semantic, and multilingual voice activity detection
- **Function Calling**: Built-in time and weather functions with extensible architecture
- **Audio File Processing**: Process pre-recorded audio files instead of live microphone input
- **Interruption Handling**: Graceful handling of user interruptions during assistant responses
- **Advanced Audio Processing**: Noise reduction, echo cancellation, and phrase list biasing
- **End-of-Utterance Detection**: Enhanced turn detection with semantic analysis
- **Multi-language Support**: Support for multiple languages with automatic detection
- **Agent-based Connections**: Support for Azure AI Foundry agent connections
- **Cross-platform Audio**: PCM16, 24kHz, mono audio format with platform-appropriate handling
- **Error Recovery**: Robust connection management with comprehensive error handling

## Prerequisites

- Python 3.8 or later
- Azure subscription with access to Azure AI VoiceLive
- Microphone and speakers/headphones (for live mode)
- Required Python packages (see installation below)

## Installation

1. **Install dependencies**:

   ```bash
   pip install -r ../dev_requirements.txt
   ```

   Or install individual packages:
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
   export AZURE_VOICELIVE_API_KEY="your-api-key"
   export AZURE_VOICELIVE_ENDPOINT="wss://your-endpoint.cognitiveservices.azure.com/voice-live/realtime"
   export VOICELIVE_MODEL="gpt-4o-realtime-preview"
   export VOICELIVE_VOICE="en-US-AvaNeural"
   ```

## Usage

### Basic Usage

Run the voice assistant with default settings:

```bash
python test_voice_live.py
```

### Function Calling Mode

Enable function calling capabilities for time and weather information:

```bash
python test_voice_live.py --enable-function-calling
```

### Audio File Processing

Process a pre-recorded audio file instead of live microphone input:

```bash
python test_voice_live.py --audio-file weather_question.wav
```

### Advanced Configuration

Customize the voice assistant with advanced options:

```bash
python test_voice_live.py \
    --model gpt-4o-realtime-preview \
    --voice en-US-JennyNeural \
    --vad-type semantic \
    --noise-reduction \
    --echo-cancellation \
    --eou-detection \
    --enable-function-calling \
    --instructions "You are a helpful AI assistant with access to real-time information."
```

### Agent-based Connection

Connect using Azure AI Foundry agent:

```bash
python test_voice_live.py \
    --agent-id "your-agent-id" \
    --agent-connection-string "your-connection-string" \
    --agent-access-token "your-access-token"
```

## Available Options

### Core Configuration
- `--api-key`: Azure VoiceLive API key (or use AZURE_VOICELIVE_API_KEY env var)
- `--endpoint`: VoiceLive endpoint URL
- `--model`: Model to use (default: gpt-4o-realtime-preview)
- `--voice`: Voice for the assistant (alloy, echo, fable, onyx, nova, shimmer, en-US-AvaNeural, etc.)
- `--instructions`: Custom system instructions for the AI
- `--use-token-credential`: Use Azure token authentication instead of API key

### Audio Processing
- `--noise-reduction`: Enable audio noise reduction for better speech recognition
- `--echo-cancellation`: Enable echo cancellation to reduce feedback
- `--phrase-list`: Comma-separated list of phrases to bias speech recognition

### Voice Activity Detection (VAD)
- `--vad-type`: VAD type - 'basic', 'semantic', or 'semantic-multilingual'
- `--silence-duration`: Silence duration in milliseconds before ending turn (200-1000ms)
- `--threshold`: Speech detection threshold (0.0-1.0, lower = more sensitive)
- `--remove-filler-words`: Remove filler words (um, uh, like) from speech detection
- `--languages`: Comma-separated list of languages for multilingual VAD
- `--speech-duration`: Minimum speech duration in milliseconds to trigger VAD

### End-of-Utterance Detection
- `--eou-detection`: Enable end-of-utterance detection for better turn detection
- `--eou-model`: EOU detection model - 'semantic' or 'multilingual'
- `--eou-threshold`: EOU detection threshold (0.0-1.0, lower = more sensitive)
- `--eou-timeout`: EOU detection timeout in seconds
- `--eou-secondary-threshold`: EOU secondary detection threshold
- `--eou-secondary-timeout`: EOU secondary timeout in seconds

### Advanced Features
- `--auto-truncate`: Enable auto-truncation of assistant responses when user speaks
- `--enable-function-calling`: Enable function calling capabilities
- `--audio-file`: Path to audio file to process instead of live microphone input
- `--verbose`: Enable detailed logging

### Agent Configuration
- `--agent-id`: Azure AI Foundry agent ID for agent-based connection
- `--agent-connection-string`: Agent connection string
- `--agent-access-token`: Agent access token

## Function Calling

When function calling is enabled, the assistant has access to:

### Time Function
- **Function**: `get_current_time`
- **Description**: Get the current time
- **Parameters**: 
  - `timezone` (optional): "UTC" or "local"
- **Example**: "What's the current time?" or "What time is it in UTC?"

### Weather Function
- **Function**: `get_current_weather`
- **Description**: Get the current weather in a given location
- **Parameters**:
  - `location` (required): City and state, e.g., "San Francisco, CA"
  - `unit` (optional): "celsius" or "fahrenheit"
- **Example**: "What's the weather in Seattle?" or "How's the weather in New York in Celsius?"

## How It Works

### 1. Session Setup
The assistant establishes a WebSocket connection and configures the session using strongly-typed objects:
- Bidirectional audio streaming (PCM16, 24kHz, mono)
- Configurable voice activity detection with multiple algorithms
- Strongly-typed session configuration (RequestSession)
- Azure voice configuration (AzureStandardVoice) or OpenAI voices
- Optional function tools for enhanced capabilities

### 2. Audio Processing
Real-time audio capture and playback using PyAudio with advanced threading:
- **Main thread**: Event loop and UI management
- **Capture thread**: PyAudio input stream reading
- **Send thread**: Async audio data transmission to VoiceLive
- **Playback thread**: PyAudio output stream writing
- Microphone input is captured in 1024-sample chunks
- Audio is base64-encoded and streamed to VoiceLive
- Response audio is decoded and played back immediately

### 3. Event Handling
Strongly-typed event handling for real-time communication:
- `session.updated`: Session ready, start audio capture
- `input_audio_buffer.speech_started`: User speaking, stop playback
- `input_audio_buffer.speech_stopped`: User finished, process input
- `input_audio_buffer.committed`: Audio file fully processed
- `response.audio.delta`: Stream response audio to speakers
- `response.audio.done`: Assistant finished speaking
- `conversation.item.created`: Handle function calls when enabled

### 4. Function Call Processing
Advanced function calling with proper event sequencing:
- Wait for function call arguments to be complete
- Execute function with parsed arguments
- Send results back to conversation
- Create new response to process function results
- Handle timeouts and errors gracefully

### 5. Interruption Support
Graceful handling of user interruptions:
- Automatic detection when user starts speaking
- Immediate cancellation of ongoing assistant responses
- Seamless resumption of conversation flow
- Different behavior for live vs. audio file modes

## Audio Requirements

- **Input**: Microphone capable of 24kHz sampling (for live mode)
- **Output**: Speakers or headphones
- **Format**: PCM16, 24kHz, mono
- **Latency**: Optimized for real-time conversation (< 300ms end-to-end)
- **File Support**: WAV, MP3, M4A, and other common audio formats

## Advanced Features

### Voice Activity Detection Types

1. **Basic VAD (ServerVad)**
   - Simple threshold-based detection
   - Fast and lightweight
   - Good for most use cases

2. **Semantic VAD (AzureSemanticVad)**
   - AI-powered speech detection
   - Better accuracy in noisy environments
   - Supports filler word removal
   - Language-specific optimization

3. **Multilingual Semantic VAD (AzureMultilingualSemanticVad)**
   - Support for multiple languages simultaneously
   - Up to 10 languages supported
   - Automatic language detection
   - Ideal for international applications

### End-of-Utterance Detection

Enhanced turn detection using semantic analysis:
- **Semantic Model**: Single-language semantic analysis
- **Multilingual Model**: Multi-language semantic analysis
- **Configurable Thresholds**: Primary and secondary detection levels
- **Timeout Management**: Automatic fallback mechanisms

### Audio Processing Enhancements

- **Noise Reduction**: Reduces background noise for better speech recognition
- **Echo Cancellation**: Prevents feedback and echo in voice conversations
- **Phrase List Biasing**: Improves recognition of specific terms or names
- **Auto-truncation**: Automatically stops assistant when user starts speaking

## Troubleshooting

### Audio Issues
- **No microphone detected**: Check microphone permissions and connections
- **No audio output**: Verify speaker/headphone setup and volume levels
- **Audio quality issues**: Ensure quiet environment and quality microphone
- **PyAudio installation**: May require additional system dependencies

### Connection Issues
- **Authentication errors**: Verify API key and endpoint configuration
- **Network timeouts**: Check internet connection and firewall settings
- **Connection drops**: SDK handles reconnection internally with appropriate retry logic
- **Agent connection issues**: Verify agent ID, connection string, and access token

### Function Calling Issues
- **Function not executing**: Check function name and argument format
- **Timeout errors**: Verify network connectivity and function implementation
- **Argument parsing errors**: Ensure function arguments match expected schema

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

### Advanced Configuration Example

The sample demonstrates proper use of advanced typed objects:

```python
# Advanced voice activity detection
turn_detection_config = AzureSemanticVad(
    threshold=0.5,
    silence_duration_ms=500,
    remove_filler_words=True,
    require_vowel=True,
    languages=["en-US"],
    speech_duration_ms=80,
    auto_truncate=True,
    end_of_utterance_detection=AzureSemanticDetection(
        threshold=0.1,
        timeout=4.0
    )
)

# Function tools configuration
function_tools = [
    FunctionTool(
        name="get_current_time",
        description="Get the current time",
        parameters={
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "The timezone to get the current time for"
                }
            }
        }
    )
]

# Complete session configuration
session_config = RequestSession(
    modalities=[Modality.TEXT, Modality.AUDIO],
    instructions=instructions,
    voice=voice_config,
    input_audio_format=InputAudioFormat.PCM16,
    output_audio_format=OutputAudioFormat.PCM16,
    turn_detection=turn_detection_config,
    input_audio_noise_reduction=AudioNoiseReduction(),
    input_audio_echo_cancellation=AudioEchoCancellation(),
    tools=function_tools,
    tool_choice=ToolChoiceLiteral.AUTO
)
```