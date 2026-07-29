---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-ai-foundry
urlFragment: voiceagents-samples
---

# Samples for the Azure AI Voice Agents client library for Python

These code samples are organized **by scenario**:

- **[`management/`](#management--manage-agents-and-read-conversations)** —
  request/response scenarios with the `azure-ai-voiceagents` client: managing
  voice agents, working with agent versions, and reading back persisted
  conversations (transcript, items, and audio recordings). Each scenario
  includes a sync sample and, where applicable, its async variant (files
  suffixed `_async`).
- **[`live/`](#live--hold-a-live-conversation)** — the live voice conversation
  scenario: create an agent with `azure-ai-voiceagents`, hold a live session,
  then read back and clean up with `azure-ai-voiceagents`.

> [!NOTE]
> The **management** scenarios cover voice-agent management and read-only
> conversation/audio playback over request/response (HTTP). The **live**
> scenario drives a realtime voice session with the `azure-ai-voicelive` SDK,
> which routes to the same voice-agent endpoint. It ships as
> two samples: `live/sample_live_text_conversation_async.py` (a headless typed
> turn) and `live/sample_live_audio_conversation_async.py` (a hands-free
> microphone conversation with barge-in). Each shows the full loop (create an
> agent → hold a live conversation and play the audio reply → read the persisted
> conversation back → delete everything).

> [!IMPORTANT]
> Voice agents are a **gated preview**. Every call opts in with the
> `VoiceAgents=V1Preview` feature flag (the samples pass it as `foundry_features`).
> The preview must also be **enabled for your subscription** and **served on your
> project's endpoint/region**. Until then, even a correct, authenticated request
> returns `404 NotFound` — the route simply isn't provisioned for your project
> yet. If you hit this, confirm preview enablement and a supported region with
> your service contact rather than changing the sample code.

## `management/` — manage agents and read conversations

**Manage voice agents** — these run standalone; you only need an endpoint.

| File | Description |
| ---- | ----------- |
| [management/sample_create_and_manage_voice_agent.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/voiceagents/azure-ai-voiceagents/samples/management/sample_create_and_manage_voice_agent.py) | Create (with a voice/audio config and conversation storage enabled), get, list, update, disable/enable, and delete a voice agent. |
| [management/sample_create_and_manage_voice_agent_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/voiceagents/azure-ai-voiceagents/samples/management/sample_create_and_manage_voice_agent_async.py) | Async version of the create/manage lifecycle. |
| [management/sample_create_voice_agent_with_tools.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/voiceagents/azure-ai-voiceagents/samples/management/sample_create_voice_agent_with_tools.py) | Create an agent with tools (`function`, `system`, `mcp`, `toolbox`), input-audio config (turn detection + transcription), and bring-your-own-model (`self_deployed`). |
| [management/sample_generate_voice_agent.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/voiceagents/azure-ai-voiceagents/samples/management/sample_generate_voice_agent.py) | Guided authoring: generate and create a voice agent from a persona, use case, and a natural-language goal. |
| [management/sample_manage_voice_agent_versions.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/voiceagents/azure-ai-voiceagents/samples/management/sample_manage_voice_agent_versions.py) | Create and list immutable versions of a voice agent, including draft versions. |

**Read conversations** — these need an existing agent and a conversation id from
a completed live session (see [Getting a conversation id](#getting-a-conversation-id)).

| File | Description |
| ---- | ----------- |
| [management/sample_read_conversation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/voiceagents/azure-ai-voiceagents/samples/management/sample_read_conversation.py) | Read a persisted conversation, its responses (and per-response items), and its items (with single get by id). |
| [management/sample_read_conversation_audio.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/voiceagents/azure-ai-voiceagents/samples/management/sample_read_conversation_audio.py) | Read the merged whole-call recording and a single turn's audio, streaming each to a WAV file. |

## `live/` — hold a live conversation

| File | Description |
| ---- | ----------- |
| [live/sample_live_text_conversation_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/voiceagents/azure-ai-voiceagents/samples/live/sample_live_text_conversation_async.py) | End to end with **typed** turns: create an agent, publish a version, then type prompts in a loop — each is sent via `azure-ai-voicelive` and the spoken reply is streamed back (optionally played through your speakers). Reads the persisted conversation back, then deletes everything. Runs headless — no microphone needed. |
| [live/sample_live_audio_conversation_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/voiceagents/azure-ai-voiceagents/samples/live/sample_live_audio_conversation_async.py) | End to end with your **microphone**: stream live audio to the agent, let server VAD detect your turns, and talk over the agent to **barge in** (cancel its in-flight reply). Requires `pyaudio`. Runs until you press Ctrl-C. |

## Prerequisites

- Python 3.10 or later.
- An Azure subscription and a Foundry project endpoint.
- The following packages installed:

  ```bash
  python -m pip install azure-ai-voiceagents azure-identity
  # for the async samples, also install an async transport:
  python -m pip install aiohttp
  # for the live samples, install the realtime SDK (with its aiohttp transport):
  python -m pip install "azure-ai-voicelive[aiohttp]"
  # optional: to hear the live sample's audio reply through your speakers:
  python -m pip install pyaudio
  ```

## Setup

The samples read their inputs from environment variables. Only
`AZURE_VOICE_AGENTS_ENDPOINT` is required by every sample; the rest are needed
only by specific samples.

| Variable | Required by | Description |
| -------- | ----------- | ----------- |
| `AZURE_VOICE_AGENTS_ENDPOINT` | all samples | Foundry project endpoint: `https://<account>.services.ai.azure.com/api/projects/<project>` |
| `AZURE_VOICE_AGENTS_MODEL` | management & live samples (optional) | Realtime model deployment name. Defaults to `gpt-realtime`. |
| `AZURE_VOICE_AGENTS_MODEL_TYPE` | `sample_create_voice_agent_with_tools.py` (optional) | `managed` (default) for a service-hosted model, or `self_deployed` to bring your own Foundry deployment. |
| `AZURE_VOICE_AGENTS_AGENT_NAME` | `sample_read_conversation*.py` | Name of the voice agent that held the conversation. |
| `AZURE_VOICE_AGENTS_CONVERSATION_ID` | `sample_read_conversation*.py` | Id of a persisted conversation (see below). |

```bash
# bash
export AZURE_VOICE_AGENTS_ENDPOINT="https://<account>.services.ai.azure.com/api/projects/<project>"
```

```powershell
# PowerShell
$env:AZURE_VOICE_AGENTS_ENDPOINT = "https://<account>.services.ai.azure.com/api/projects/<project>"
```

The samples authenticate with
[`DefaultAzureCredential`](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential),
so sign in first (for example, with `az login`) or configure the appropriate
environment variables. Your identity needs access to the Foundry project.

### Getting a conversation id

The read samples don't create conversations — this client can only *read* them.
A conversation is created by the **voice orchestrator during a live session**,
and it is persisted only when the agent was created with `store = true` (the
management samples turn this on). During the live session the service emits a
`conversation.created` event whose id you pass as
`AZURE_VOICE_AGENTS_CONVERSATION_ID`. Audio additionally requires the session to
have ended.

The `live/` samples do this end to end for you: each creates an agent, opens a
live session with `azure-ai-voicelive`, captures the conversation id from that
session, and reads the conversation back — no manual id wiring required. Use
`sample_live_text_conversation_async.py` for a headless typed turn, or
`sample_live_audio_conversation_async.py` for a hands-free microphone
conversation with barge-in.

## Running a sample

```bash
python management/sample_create_and_manage_voice_agent.py
```

## Troubleshooting

| Symptom | Likely cause and fix |
| ------- | -------------------- |
| `KeyError: 'AZURE_VOICE_AGENTS_...'` | A required environment variable is not set. See the table above. |
| `HttpResponseError` 401 / 403 | Not signed in, or your identity lacks access to the project. Run `az login` and confirm project permissions. |
| `ResourceNotFoundError` / 404 on a **management** call (create, list, generate) | The gated preview isn't enabled for your subscription, or isn't served on your project's endpoint/region yet. The request URL and auth are correct; the route just isn't provisioned. Confirm preview enablement and a supported region with your service contact. |
| `HttpResponseError` 404 on a **read** sample | The conversation was not persisted (agent ran with `store = false`) or the id is wrong. |
| `HttpResponseError` 409 on the audio sample | Either the session is still in progress, or the recording lives in your own bring-your-own-storage (BYOS) account — its bytes aren't streamed through the service and must be downloaded directly from the `blob_path` returned by the metadata route. Foundry-managed audio streams normally. |
| Model / deployment not found | The `gpt-realtime` default deployment doesn't exist in your project. Set `AZURE_VOICE_AGENTS_MODEL` to a valid realtime deployment name. |

> [!NOTE]
> The management samples create and delete **real resources** in your project and
> may incur cost. Each sample deletes the agent it creates on the success path
> only; if a sample fails partway through, it may leave the agent behind, so
> check your project and delete any leftover agents manually.
