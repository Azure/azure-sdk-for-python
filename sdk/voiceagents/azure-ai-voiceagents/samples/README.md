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

These code samples show common HTTP-surface scenarios with the
`azure-ai-voiceagents` client library: managing voice agents, working with
agent versions, and reading back persisted conversations (transcript, items,
and audio recordings).

> [!NOTE]
> These samples cover the **request/response (HTTP)** surface only —
> voice-agent management and read-only conversation/audio playback. The
> **live realtime voice session** (the streaming WebSocket call) is established
> through a separate connect operation that is not part of this client library
> today, so it is intentionally not shown here.

> [!IMPORTANT]
> Voice agents are a **gated preview**. Every call opts in with the
> `VoiceAgents=V1Preview` feature flag (the samples pass it as `foundry_features`).
> The preview must also be **enabled for your subscription** and **served on your
> project's endpoint/region**. Until then, even a correct, authenticated request
> returns `404 NotFound` — the route simply isn't provisioned for your project
> yet. If you hit this, confirm preview enablement and a supported region with
> your service contact rather than changing the sample code.

**Manage voice agents** — these run standalone; you only need an endpoint.

| File | Description |
| ---- | ----------- |
| [sample_create_and_manage_voice_agent.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/voiceagents/azure-ai-voiceagents/samples/sample_create_and_manage_voice_agent.py) | Create (with a voice/audio config and conversation storage enabled), get, list, update, disable/enable, and delete a voice agent. |
| [sample_create_voice_agent_with_tools.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/voiceagents/azure-ai-voiceagents/samples/sample_create_voice_agent_with_tools.py) | Create an agent with tools (`function`, `system`, `mcp`, `toolbox`), input-audio config (turn detection + transcription), and bring-your-own-model (`self_deployed`). |
| [sample_generate_voice_agent.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/voiceagents/azure-ai-voiceagents/samples/sample_generate_voice_agent.py) | Guided authoring: generate and create a voice agent from a persona, use case, and a natural-language goal. |
| [sample_manage_voice_agent_versions.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/voiceagents/azure-ai-voiceagents/samples/sample_manage_voice_agent_versions.py) | Create and list immutable versions of a voice agent, including draft versions. |
| [async_samples/sample_create_and_manage_voice_agent_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/voiceagents/azure-ai-voiceagents/samples/async_samples/sample_create_and_manage_voice_agent_async.py) | Async version of the create/manage lifecycle. |

**Read conversations** — these need an existing agent and a conversation id from
a completed live session (see [Getting a conversation id](#getting-a-conversation-id)).

| File | Description |
| ---- | ----------- |
| [sample_read_conversation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/voiceagents/azure-ai-voiceagents/samples/sample_read_conversation.py) | Read a persisted conversation, its responses (and per-response items), and its items (with single get by id). |
| [sample_read_conversation_audio.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/voiceagents/azure-ai-voiceagents/samples/sample_read_conversation_audio.py) | Read the merged whole-call recording and a single turn's audio, streaming each to a WAV file. |

## Prerequisites

- Python 3.10 or later.
- An Azure subscription and a Foundry project endpoint.
- The following packages installed:

  ```bash
  python -m pip install azure-ai-voiceagents azure-identity
  # for the async sample, also install an async transport:
  python -m pip install aiohttp
  ```

## Setup

The samples read their inputs from environment variables. Only
`AZURE_VOICE_AGENTS_ENDPOINT` is required by every sample; the rest are needed
only by specific samples.

| Variable | Required by | Description |
| -------- | ----------- | ----------- |
| `AZURE_VOICE_AGENTS_ENDPOINT` | all samples | Foundry project endpoint: `https://<account>.services.ai.azure.com/api/projects/<project>` |
| `AZURE_VOICE_AGENTS_MODEL` | management samples (optional) | Realtime model deployment name. Defaults to `gpt-realtime`. |
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

## Running a sample

```bash
python sample_create_and_manage_voice_agent.py
```

## Troubleshooting

| Symptom | Likely cause and fix |
| ------- | -------------------- |
| `KeyError: 'AZURE_VOICE_AGENTS_...'` | A required environment variable is not set. See the table above. |
| `HttpResponseError` 401 / 403 | Not signed in, or your identity lacks access to the project. Run `az login` and confirm project permissions. |
| `ResourceNotFoundError` / 404 on a **management** call (create, list, generate) | The gated preview isn't enabled for your subscription, or isn't served on your project's endpoint/region yet. The request URL and auth are correct; the route just isn't provisioned. Confirm preview enablement and a supported region with your service contact. |
| `HttpResponseError` 404 on a **read** sample | The conversation was not persisted (agent ran with `store = false`) or the id is wrong. |
| `HttpResponseError` 409 on the audio sample | The session is still in progress, or the agent has no bring-your-own-storage account configured for audio. |
| Model / deployment not found | The `gpt-realtime` default deployment doesn't exist in your project. Set `AZURE_VOICE_AGENTS_MODEL` to a valid realtime deployment name. |

> [!NOTE]
> The management samples create and delete **real resources** in your project and
> may incur cost. Each sample deletes the agent it creates on the success path
> only; if a sample fails partway through, it may leave the agent behind, so
> check your project and delete any leftover agents manually.
