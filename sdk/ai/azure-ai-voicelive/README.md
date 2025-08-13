# Basic Voice Assistant (Python) — Azure AI VoiceLive

This sample shows how to build a **real-time, speech-to-speech voice assistant** with the Azure AI VoiceLive SDK. It opens a WebSocket connection, streams microphone audio, handles typed server events, and plays back the assistant’s audio responses with **interruption handling** (stop playback when the user starts speaking).

---

## Prerequisites

- **Python 3.10+**
- An **Azure subscription** and a **VoiceLive** resource
- A working **microphone** and **speakers/headphones**

> On first run, you may need system audio libraries (see “Install” below).

---

## Install

### 1) System audio libraries (for PyAudio)

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev libasound2-dev
```

**macOS (Homebrew):**
```bash
brew update
brew install portaudio
```

**Windows:**
Just `pip install pyaudio`. If it fails, install the latest Microsoft C++ Build Tools, or use Conda (`conda install pyaudio`).

### 2) Python packages

```bash
python -m pip install azure-ai-voicelive[websockets] pyaudio python-dotenv
```

---

## Configure authentication

This sample supports **API key** or **Azure AD token**.

### Option A — API key (recommended for quick start)

Set environment variables (you can use a `.env` file):

```bash
# .env
AZURE_VOICELIVE_API_KEY="<your-api-key>"
AZURE_VOICELIVE_ENDPOINT="<your-endpoint>"   # e.g., wss://<your-resource>.<region>.voice.azure.com/openai/realtime
```

### Option B — Azure AD (interactive login)

Run with `--use-token-credential` (uses InteractiveBrowserCredential by default).  
Make sure your identity has access to the VoiceLive resource.

---

## Run

From the sample directory:

```bash
python basic_voice_assistant_async.py   --model "gpt-4o-realtime-preview"   --voice "en-US-AvaNeural"   --verbose
```

You can also rely on defaults set via environment variables:
- `AZURE_VOICELIVE_API_KEY`
- `AZURE_VOICELIVE_ENDPOINT`
- `VOICELIVE_MODEL` (defaults to `gpt-4o-realtime-preview`)
- `VOICELIVE_VOICE` (defaults to `en-US-AvaNeural`)
- `VOICELIVE_INSTRUCTIONS`

---

## What this sample does

- Connects to the **VoiceLive WebSocket API** (`azure.ai.voicelive.aio.connect`)
- Configures a session with:
  - Modalities: **text** and **audio**
  - **Voice** (Azure or OpenAI voice names)
  - **PCM16** input/output formats at **24 kHz**
  - **Server VAD** (voice activity detection) for turn detection
- Captures microphone audio with **PyAudio** and streams base64 chunks
- Receives **typed server events**, including audio deltas, and plays them out
- Implements **barge-in/interrupt**: when user speech starts, playback is paused and any active response is canceled

---

## Command-line options

```
--api-key                API key (otherwise uses AZURE_VOICELIVE_API_KEY)
--endpoint               VoiceLive endpoint (or AZURE_VOICELIVE_ENDPOINT)
--model                  Model name (default: gpt-4o-realtime-preview)
--voice                  Voice name (e.g., alloy, onyx, en-US-AvaNeural, ...)
--instructions           System prompt for the assistant
--use-token-credential   Use Azure AD token auth instead of API key
--verbose                Enable debug logging
```

---

## Code highlights

- **AudioProcessor**: threads for capture/send/playback, queues for back-pressure
- **BasicVoiceAssistant**: sets up session, processes events, handles interruptions
- Uses **`ServerEventType`** to branch on event types (e.g., `SESSION_UPDATED`, `RESPONSE_AUDIO_DELTA`)

---

## Troubleshooting

- **PyAudio / PortAudio build errors**
  - Linux: `sudo apt-get install -y portaudio19-dev libasound2-dev`
  - macOS: `brew install portaudio`
  - Windows: try `pip install pyaudio`

- **No input/output devices**  
  Ensure your OS sees a microphone and speakers. On headless CI, you typically cannot run this sample.

- **WebSocket connection issues (1006/timeout)**
  - Recheck `AZURE_VOICELIVE_ENDPOINT`
  - Confirm your network allows WSS to the service

- **Auth errors**
  - For API key: confirm `AZURE_VOICELIVE_API_KEY`
  - For AAD: ensure your identity has access to the resource

---

## Next steps

- Explore all VoiceLive Python samples in "samples"