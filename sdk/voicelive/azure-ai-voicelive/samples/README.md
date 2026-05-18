# Azure AI VoiceLive Samples

This directory contains sample applications demonstrating various capabilities of the Azure AI VoiceLive SDK.

> **Note:** All samples use async/await patterns as the SDK is now exclusively async.

## Prerequisites

- Python 3.9 or later
- An Azure subscription with access to Azure AI VoiceLive
- Azure AI VoiceLive API key

## Setup

1. **Install dependencies**:

   ```bash
   pip install azure-ai-voicelive[aiohttp] python-dotenv
   ```

2. **Install PyAudio** (required for audio samples):

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

3. **Configure environment variables**:

   Create a `.env` file at the root of the azure-ai-voicelive directory or in the samples directory with the following variables:

   ```ini
   AZURE_VOICELIVE_API_KEY=your-voicelive-api-key
   AZURE_VOICELIVE_ENDPOINT=wss://api.voicelive.com/v1
   AZURE_VOICELIVE_MODEL=gpt-realtime
   AZURE_VOICELIVE_VOICE=alloy
   AZURE_VOICELIVE_INSTRUCTIONS=You are a helpful assistant. Keep your responses concise.
   ```

   You can copy the `.env.template` file and fill in your values:

   ```bash
   cp ../.env.template ./.env
   ```

## Running the samples

### Quick Start: Basic Voice Assistant 🎤

For a complete voice conversation experience, start with the featured sample:

```bash
python basic_voice_assistant_async.py
```

This sample demonstrates:

- Real-time voice conversation with AI
- Automatic turn detection and interruption handling  
- Full duplex audio streaming
- Robust error handling and reconnection

See "BASIC_VOICE_ASSISTANT.md" for complete documentation.

### Using Visual Studio Code

1. Open the `azure-ai-voicelive` directory in VS Code
2. Configure your `.env` file as described above
3. Open the VS Code Run panel (Ctrl+Shift+D)
4. Select a sample configuration from the dropdown
5. Click the Run button or press F5 to run the sample in debug mode

### From the command line

Run any sample directly:

```bash
python basic_voice_assistant_async.py
```

Most samples support additional command-line arguments. For example:

```bash
python basic_voice_assistant_async.py --model gpt-realtime --voice alloy

# With telemetry tracing
python basic_voice_assistant_async.py --enable-tracing
```

Use the `--help` flag to see all available options:

```bash
python basic_voice_assistant_async.py --help
```

## Sample descriptions

- **basic_voice_assistant_async.py**: 🌟 **[Featured Sample]** Complete async voice assistant demonstrating real-time conversation, interruption handling, and server VAD. Supports optional OpenTelemetry tracing via `--enable-tracing`. Perfect starting point for voice applications. See "BASIC_VOICE_ASSISTANT.md" for detailed documentation.
- **agent_v2_sample.py**: Demonstrates how to connect to an Azure AI Foundry agent using the `AgentSessionConfig` TypedDict. Shows the new pattern where agents are configured at connection time rather than as tools in the session. Features callback-based audio streaming, sequence number based interrupt handling, and conversation logging.
- **async_function_calling_sample.py**: Demonstrates async function calling capabilities with the VoiceLive SDK, showing how to handle function calls from the AI model.

### Telemetry samples

These samples are in the `telemetry/` folder and demonstrate OpenTelemetry-based tracing:

| Sample | Description |
|---|---|
| `sample_voicelive_with_telemetry_enablement.py` | Minimal telemetry setup on top of existing VoiceLive code. Shows the smallest practical code delta to emit spans to console. |
| `sample_voicelive_with_console_tracing.py` | Basic tracing with console output. All connection, send, and receive operations produce OpenTelemetry spans printed to stdout. |
| `sample_voicelive_with_azure_monitor_tracing.py` | Traces exported to Azure Monitor / Application Insights. View results in the "Tracing" tab. |
| `sample_voicelive_with_console_tracing_custom_attributes.py` | Adds custom `SpanProcessor` to inject application-specific attributes (session ID, etc.) into every span. |
| `sample_voicelive_with_content_recording.py` | Enables content recording to capture full message payloads in span events. Useful for debugging; may contain personal data. |

**Prerequisites for telemetry samples:**

```bash
# Console tracing
pip install azure-ai-voicelive opentelemetry-sdk azure-core-tracing-opentelemetry

# Azure Monitor tracing
pip install azure-ai-voicelive azure-monitor-opentelemetry

# OTLP export (e.g., Aspire dashboard)
pip install opentelemetry-exporter-otlp-proto-grpc
```

Set `AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING=true` to enable tracing.

## Troubleshooting

- **PyAudio / PortAudio build errors**
  - Linux: `sudo apt-get install -y portaudio19-dev libasound2-dev`
  - macOS: `brew install portaudio`
  - Windows: try `pip install pyaudio`

- **No input/output devices**  
  Ensure your OS sees a microphone and speakers. On headless CI, you typically cannot run audio samples.

- **WebSocket connection issues (1006/timeout)**
  - Recheck `AZURE_VOICELIVE_ENDPOINT`
  - Confirm your network allows WSS to the service

- **Auth errors**
  - For API key: confirm `AZURE_VOICELIVE_API_KEY`
  - For AAD: ensure your identity has access to the resource

## Next steps

- Try the **Basic Voice Assistant** sample first, then explore the others for specific scenarios.
- Integrate the SDK into your own app by copying pieces from the samples (e.g., audio capture/playback or event handling loops).
- Visit the Azure SDK repo to see additional guidance, issues, and contributions.
