Azure AI VoiceLive client library for Python
============================================

This package provides a **real-time, speech-to-speech** client for Azure AI VoiceLive.
It opens a WebSocket session to stream microphone audio to the service and receive
typed server events (including audio) for responsive, interruptible conversations.

> **Status:** Preview. APIs are subject to change.

---

Getting started
---------------

### Prerequisites

- **Python 3.9+**
- An **Azure subscription**
- A **VoiceLive** resource and endpoint
- A working **microphone** and **speakers/headphones** if you run the voice samples

### Install

```bash
# Base install (core client only)
python -m pip install azure-ai-voicelive

# For synchronous streaming (uses websockets)
python -m pip install "azure-ai-voicelive[websockets]"

# For asynchronous streaming (uses aiohttp)
python -m pip install "azure-ai-voicelive[aiohttp]"

# For both sync + async scenarios (recommended if unsure)
python -m pip install "azure-ai-voicelive[all-websockets]" pyaudio python-dotenv
```

WebSocket streaming features require additional dependencies.
Install them with:
    pip install "azure-ai-voicelive[websockets]"   # for sync
    pip install "azure-ai-voicelive[aiohttp]"     # for async
    pip install "azure-ai-voicelive[all-websockets]"  # for both

### Authenticate

You can authenticate with an **API key** or an **Azure Active Directory (AAD) token**.

#### API Key Authentication (Quick Start)

Set environment variables in a `.env` file or directly in your environment:

```bash
# In your .env file or environment variables
AZURE_VOICELIVE_API_KEY="your-api-key"
AZURE_VOICELIVE_ENDPOINT="your-endpoint"
```

Then, use the key in your code:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive import connect

connection = connect(
    endpoint="your-endpoint",
    credential=AzureKeyCredential("your-api-key"),
    model="gpt-4o-realtime-preview"
)
```

#### AAD Token Authentication

For production applications, AAD authentication is recommended:

```python
from azure.identity import DefaultAzureCredential
from azure.ai.voicelive import connect

credential = DefaultAzureCredential()

connection = connect(
    endpoint="your-endpoint",
    credential=credential,
    model="gpt-4o-realtime-preview"
)
```

---

Key concepts
------------

- **VoiceLiveConnection** – Manages an active WebSocket connection to the service
- **Session Management** – Configure conversation parameters:
  - **SessionResource** – Update session parameters (voice, formats, VAD)
  - **RequestSession** – Strongly-typed session configuration
  - **ServerVad** – Configure voice activity detection
  - **AzureStandardVoice** – Configure voice settings
- **Audio Handling**:
  - **InputAudioBufferResource** – Manage audio input to the service
  - **OutputAudioBufferResource** – Control audio output from the service
- **Conversation Management**:
  - **ResponseResource** – Create or cancel model responses
  - **ConversationResource** – Manage conversation items
- **Strongly-Typed Events** – Process service events with type safety:
  - `SESSION_UPDATED`, `RESPONSE_AUDIO_DELTA`, `RESPONSE_DONE`
  - `INPUT_AUDIO_BUFFER_SPEECH_STARTED`, `INPUT_AUDIO_BUFFER_SPEECH_STOPPED`
  - `ERROR`, and more

---

Examples
--------

### Basic async Voice Assistant (Featured Sample)

The Basic async Voice Assistant sample demonstrates full-featured voice interaction with:

- Real-time speech streaming
- Server-side voice activity detection
- Interruption handling
- High-quality audio processing

```bash
# Run the basic voice assistant sample
# Requires [aiohttp] for async (easiest: [all-websockets])
python samples/basic_voice_assistant_async.py

# With custom parameters
python samples/basic_voice_assistant_async.py --model gpt-4o-realtime-preview --voice alloy --instructions "You're a helpful assistant"
```

### Minimal async example

```python
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    RequestSession, Modality, AudioFormat, ServerVad, ServerEventType
)

API_KEY = "your-api-key"
ENDPOINT = "wss://your-endpoint.com/openai/realtime"
MODEL = "gpt-4o-realtime-preview"

async def main():
    async with connect(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(API_KEY),
        model=MODEL,
    ) as conn:
        session = RequestSession(
            modalities=[Modality.TEXT, Modality.AUDIO],
            instructions="You are a helpful assistant.",
            input_audio_format=AudioFormat.PCM16,
            output_audio_format=AudioFormat.PCM16,
            turn_detection=ServerVad(
                threshold=0.5, 
                prefix_padding_ms=300, 
                silence_duration_ms=500
            ),
        )
        await conn.session.update(session=session)

        # Process events
        async for evt in conn:
            print(f"Event: {evt.type}")
            if evt.type == ServerEventType.RESPONSE_DONE:
                break

asyncio.run(main())
```

### Minimal sync example

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive import connect
from azure.ai.voicelive.models import (
    RequestSession, Modality, AudioFormat, ServerVad, ServerEventType
)

API_KEY = "your-api-key"
ENDPOINT = "your-endpoint"
MODEL = "gpt-4o-realtime-preview"

with connect(
    endpoint=ENDPOINT,
    credential=AzureKeyCredential(API_KEY),
    model=MODEL
) as conn:
    session = RequestSession(
        modalities=[Modality.TEXT, Modality.AUDIO],
        instructions="You are a helpful assistant.",
        input_audio_format=AudioFormat.PCM16,
        output_audio_format=AudioFormat.PCM16,
        turn_detection=ServerVad(
            threshold=0.5, 
            prefix_padding_ms=300, 
            silence_duration_ms=500
        ),
    )
    conn.session.update(session=session)

    # Process events
    for evt in conn:
        print(f"Event: {evt.type}")
        if evt.type == ServerEventType.RESPONSE_DONE:
            break
```

Available Voice Options
-----------------------

### Azure Neural Voices

```python
# Use Azure Neural voices
voice_config = AzureStandardVoice(
    name="en-US-AvaNeural",  # Or another voice name
    type="azure-standard"
)
```

Popular voices include:

- `en-US-AvaNeural` - Female, natural and professional
- `en-US-JennyNeural` - Female, conversational
- `en-US-GuyNeural` - Male, professional

### OpenAI Voices

```python
# Use OpenAI voices (as string)
voice_config = "alloy"  # Or another OpenAI voice
```

Available OpenAI voices:

- `alloy` - Versatile, neutral
- `echo` - Precise, clear
- `fable` - Animated, expressive
- `onyx` - Deep, authoritative
- `nova` - Warm, conversational
- `shimmer` - Optimistic, friendly

---

Handling Events
---------------

```python
async for event in connection:
    if event.type == ServerEventType.SESSION_UPDATED:
        print(f"Session ready: {event.session.id}")
        # Start audio capture
        
    elif event.type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED:
        print("User started speaking")
        # Stop playback and cancel any current response
        
    elif event.type == ServerEventType.RESPONSE_AUDIO_DELTA:
        # Play the audio chunk
        audio_bytes = event.delta
        
    elif event.type == ServerEventType.ERROR:
        print(f"Error: {event.error.message}")
```

---

Troubleshooting
---------------

### Connection Issues

- **WebSocket connection errors (1006/timeout):**  
  Verify `AZURE_VOICELIVE_ENDPOINT`, network rules, and that your credential has access.

- **Missing WebSocket dependencies:**  
  If you see:
    WebSocket streaming features require additional dependencies.
    Install them with:
        pip install "azure-ai-voicelive[websockets]"   # for sync
        pip install "azure-ai-voicelive[aiohttp]"     # for async
        pip install "azure-ai-voicelive[all-websockets]"  # for both

- **Auth failures:**  
  For API key, double-check `AZURE_VOICELIVE_API_KEY`. For AAD, ensure the identity is authorized.

### Audio Device Issues

- **No microphone/speaker detected:**  
  Check device connections and permissions. On headless CI environments, audio samples can't run.

- **Audio library installation problems:**  
  On Linux/macOS you may need PortAudio:

  ```bash
  # Debian/Ubuntu
  sudo apt-get install -y portaudio19-dev libasound2-dev
  # macOS (Homebrew)
  brew install portaudio
  ```

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

Next steps
----------

1. **Run the featured sample:**
   - Try `samples/basic_voice_assistant_async.py` for a complete voice assistant implementation

2. **Customize your implementation:**
   - Experiment with different voices and parameters
   - Add custom instructions for specialized assistants
   - Integrate with your own audio capture/playback systems

3. **Advanced scenarios:**
   - Add function calling support
   - Implement tool usage
   - Create multi-turn conversations with history

4. **Explore other samples:**
   - Check the `samples/` directory for specialized examples
   - See `samples/README.md` for a full list of samples

---

Contributing
------------

This project follows the Azure SDK guidelines. If you'd like to contribute:

1. Fork the repo and create a feature branch
2. Run linters and tests locally
3. Submit a pull request with a clear description of the change

---

Release notes
-------------

Changelogs are available in the package directory.

---

License
-------

This project is released under the **MIT License**.
