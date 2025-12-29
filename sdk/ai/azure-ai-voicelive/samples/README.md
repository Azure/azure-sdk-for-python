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
   pip install azure-ai-voicelive[aiohttp] pyaudio python-dotenv
   ```

2. **Configure environment variables**:

   Create a `.env` file at the root of the azure-ai-voicelive directory or in the samples directory with the following variables:

   ```ini
   AZURE_VOICELIVE_API_KEY=your-voicelive-api-key
   AZURE_VOICELIVE_ENDPOINT=wss://api.voicelive.com/v1
   AZURE_VOICELIVE_MODEL=gpt-4o-realtime-preview
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
python basic_voice_assistant_async.py --model gpt-4o-realtime-preview --voice alloy
```

Use the `--help` flag to see all available options:

```bash
python basic_voice_assistant_async.py --help
```

## Sample descriptions

- **basic_voice_assistant_async.py**: 🌟 **[Featured Sample]** Complete async voice assistant demonstrating real-time conversation, interruption handling, and server VAD. Perfect starting point for voice applications. See "BASIC_VOICE_ASSISTANT.md" for detailed documentation.
- **async_function_calling_sample.py**: Demonstrates async function calling capabilities with the VoiceLive SDK, showing how to handle function calls from the AI model.

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
