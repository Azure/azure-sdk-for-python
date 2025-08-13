Azure AI VoiceLive client library for Python
=================================================

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
python -m pip install azure-ai-voicelive
# (optional for samples) audio + dotenv helpers
python -m pip install 'azure-ai-voicelive[websockets]' pyaudio python-dotenv
```

### Authenticate

You can authenticate with an **API key** or an **Azure Active Directory (AAD) token**.

**API key (quick start):**

Set environment variables (you can use a `.env` file):

```bash
AZURE_VOICELIVE_API_KEY="<your-api-key>"
AZURE_VOICELIVE_ENDPOINT="wss://<host>/openai/realtime"
```

**AAD (token credential):**

Use `DefaultAzureCredential` (or any `TokenCredential`) and ensure your identity
has access to the VoiceLive resource.

```python
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
```

---

Key concepts
------------

- **VoiceLiveConnection** – an active WebSocket connection to the service.  
- **SessionResource** – update conversation session parameters (voice, formats, VAD).  
- **ResponseResource** – create or cancel a model response.  
- **InputAudioBufferResource** – append/commit/clear captured audio you send to the service.  
- **OutputAudioBufferResource** – clear/stop generated audio output on the server.  
- **ConversationResource** – manage conversation items (create, retrieve, delete, truncate).  
- **Server events** – strongly-typed events published by the service (e.g., `SESSION_UPDATED`,
  `RESPONSE_AUDIO_DELTA`, `RESPONSE_DONE`, `ERROR`).

---

Examples
--------

### Minimal async example

```python
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import RequestSession, Modality, AudioFormat, ServerVad

API_KEY = "<your api key>"
ENDPOINT = "wss://<host>/openai/realtime"
MODEL = "gpt-4o-realtime-preview"

async def main():
    async with connect(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(API_KEY),
        model=MODEL,
    ) as conn:
        # Configure the session for text+audio conversation
        session = RequestSession(
            modalities=[Modality.TEXT, Modality.AUDIO],
            instructions="You are a helpful assistant.",
            input_audio_format=AudioFormat.PCM16,
            output_audio_format=AudioFormat.PCM16,
            turn_detection=ServerVad(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=500),
        )
        await conn.session.update(session=session)

        # Consume a few events
        async for evt in conn:
            print("event:", evt.type)
            if evt.type.endswith("done"):
                break

asyncio.run(main())
```

### Minimal sync example

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive import connect
from azure.ai.voicelive.models import RequestSession, Modality, AudioFormat

API_KEY = "<your api key>"
ENDPOINT = "wss://<host>/openai/realtime"
MODEL = "gpt-4o-realtime-preview"

with connect(endpoint=ENDPOINT, credential=AzureKeyCredential(API_KEY), model=MODEL) as conn:
    session = RequestSession(
        modalities=[Modality.TEXT, Modality.AUDIO],
        instructions="You are a helpful assistant.",
        input_audio_format=AudioFormat.PCM16,
        output_audio_format=AudioFormat.PCM16,
    )
    conn.session.update(session=session)

    for evt in conn:
        print("event:", evt.type)
        if evt.type.endswith("done"):
            break
```

> See the full-featured sample in `samples/basic_voice_assistant_async.py` for
> microphone capture, streaming, and audio playback with interruption handling.

---

Contributing
------------

This project follows the Azure SDK guidelines. If you would like to contribute:

1. Fork the repo and create a feature branch.
2. Run linters and tests locally.
3. Submit a pull request with a clear description of the change.

---

Release notes
-------------

Changelogs are available in the package directory.

License
-------

This project is released under the **MIT License**.
