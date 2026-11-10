# Azure AI Projects client library for Python

The AI Projects client library is part of the Microsoft Foundry SDK, and provides easy access to
resources in your [Microsoft Foundry](https://ai.azure.com/) Project. Use it to:

* **Create and run Agents** using methods on the `.agents` client property. This includes **Hosted Agents**, which let you run your own containerized agent runtime while using Microsoft Foundry for managed hosting and scaling.
* **Build and run Voice Agents** for real-time, speech-to-speech conversational AI, reachable over a WebSocket (`.voice_agents.realtime`) or telephony (`.voice_agents.telephony`), with persisted conversation transcripts and audio through `.voice_agents.conversations`. Generate agents from a prompt with `.agents.create_from_prompt()`. These generally available features do not require preview opt-in.
* **Enhance Agents with specialized tools and toolbox tools** such as:
  * Agent-to-Agent (A2A)
  * Azure AI Search
  * Azure Functions
  * Bing Custom Search (Preview)
  * Bing Grounding
  * Browser Automation (Preview)
  * Code Interpreter
  * Computer
  * Computer Use (Preview)
  * Fabric IQ (Preview)
  * File Search
  * Function Tool
  * Image Generation
  * Memory Search (Preview)
  * Microsoft Fabric (Preview)
  * Microsoft SharePoint (Preview)
  * Model Context Protocol (MCP)
  * OpenAPI
  * Reminder Tool (Preview)
  * Toolbox Search
  * Web Search
  * Work IQ (Preview)
* **Get an OpenAI client** using `.get_openai_client()` method to run Responses, Conversations, Evaluations and Fine-Tuning operations with your Agent.
* **Create and version toolboxes** that bundle collections of tools and skills for your agents, using `.toolboxes` operations.
* **Fine-tune** AI Models on your data.
* **Enumerate AI Models** deployed to your Foundry Project using `.deployments` operations.
* **Enumerate connected Azure resources** in your Foundry project using `.connections` operations.
* **Upload documents and create Datasets** to reference them using `.datasets` operations.
* **Create and enumerate Search Indexes** using `.indexes` operations.
* **Explore additional evaluation tools (some in preview)** to assess the performance of your generative AI application, using `.evaluation_rules`,
`.beta.evaluation_taxonomies`, `.beta.evaluators`, `.beta.insights`, and `.beta.schedules` operations.
* **Manage memory stores (preview)** for Agent conversations, using `.beta.memory_stores` operations.
* **Register and manage local AI model weights (preview)** using `.beta.models` operations.
* **Run Red Team scans (preview)** to identify risks associated with your generative AI application, using `.beta.red_teams` operations.
* **Create and manage routines (preview)** that execute triggered actions based on configured conditions, using `.beta.routines` operations.
* **Manage skills (preview)** as reusable capabilities that can be included in toolboxes and agents, using `.beta.skills` operations.
* **Analyze agent traces** using `.agent_insight_monitors` operations to create monitors, run analyses, and manage insights.

**Important:** This stable package includes Preview features. Preview features available through stable methods require setting `allow_preview=True` when constructing the client, while Preview features exposed via the .beta sub-clients do not. Preview features may change or be removed in future versions and are not recommended for production use.

Voice Agents includes both generally available APIs and preview features:

| Voice Agents feature | Scope and client path |
|---|---|
| Realtime sessions and stored conversation/audio readback | GA: `.voice_agents.realtime` and `.voice_agents.conversations`; no preview opt-in |
| Generate a voice agent from a prompt | GA: `.agents.create_from_prompt()`; no automatic preview header |
| Teams Phone Extensibility and Twilio telephony | GA: `.voice_agents.telephony`; no preview opt-in |
| SIP, inline subagent handoff, and post-call delivery | Preview options on GA operations; set `allow_preview=True` |
| GPT-Live sessions and stored Live conversations | Preview: `.beta.voice_agents.live` and `.beta.voice_agents.live_conversations`; creating a GPT-Live definition also requires `allow_preview=True` |
| Outbound campaigns | Preview: `.beta.voice_agents.telephony`; operations automatically include the required preview header |

GA generation, conversation operations, and telephony reads do not automatically send preview headers,
even when the client has `allow_preview=True`. That setting enables opt-in on conditional telephony
writes for SIP; caller-supplied headers are preserved.

Realtime uses `Realtime`, `RealtimeConnection`, and `RealtimeConnectionManager` from
`azure.ai.projects.operations`. Their asynchronous counterparts are `AsyncRealtime`,
`AsyncRealtimeConnection`, and `AsyncRealtimeConnectionManager` from `azure.ai.projects.aio.operations`.
These GA types do not have `Beta` aliases.

The client library uses version `v1` of the Microsoft Foundry [data plane REST APIs](https://aka.ms/azsdk/azure-ai-projects-v2/api-reference-v1).

[Microsoft Foundry](https://ai.azure.com/)
| [Documentation](https://aka.ms/azsdk/azure-ai-projects-v2/product-doc)
| [Samples][samples]
| [API reference](https://aka.ms/azsdk/azure-ai-projects-v2/python/api-reference)
| [Package (PyPI)](https://aka.ms/azsdk/azure-ai-projects-v2/python/package)
| [SDK source code](https://aka.ms/azsdk/azure-ai-projects-v2/python/code)
| [Release history](https://aka.ms/azsdk/azure-ai-projects-v2/python/release-history)

## Reporting issues

To report an issue with the client library, or request additional features, please open a [GitHub issue here](https://github.com/Azure/azure-sdk-for-python/issues). Mention the package name "azure-ai-projects" in the title or content.

## Getting started

### Prerequisite

* Python 3.10 or later.
* An [Azure subscription][azure_sub].
* A [project in Microsoft Foundry](https://learn.microsoft.com/azure/foundry/how-to/create-projects).
* An [Application Insights resource connected to your Foundry project](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-setup) for agent tracing.
* A Foundry project endpoint URL of the form `https://your-ai-services-account-name.services.ai.azure.com/api/projects/your-project-name`. It can be found in your Microsoft Foundry Project home page. Below we will assume the environment variable `FOUNDRY_PROJECT_ENDPOINT` was defined to hold this value.
* Client authentication is done using Entra ID. To authenticate, your application needs an object that implements the [TokenCredential](https://learn.microsoft.com/python/api/azure-core/azure.core.credentials.tokencredential) interface. Code samples here use [DefaultAzureCredential](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential). To get that working, you will need:
  * An appropriate role assignment. See [Role-based access control in Microsoft Foundry portal](https://learn.microsoft.com/azure/foundry/concepts/rbac-foundry). Role assignment can be done via the "Access Control (IAM)" tab of your Azure AI Project resource in the Azure portal.
  * [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed.
  * You are logged into your Azure account by running `az login`.

### Install the package

```bash
pip install azure-ai-projects
```

Verify that you have version 2.3.0 or above installed by running:

```bash
pip show azure-ai-projects
```

## Key concepts

### Create and authenticate the client with Entra ID

Entra ID is the only authentication method currently supported by the client.

To construct a synchronous client using a context manager:

```python
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=credential
    ) as project_client,
):
```

To construct an asynchronous client, install the additional package [aiohttp](https://pypi.org/project/aiohttp/):

```bash
pip install aiohttp
```

and run:

```python
import os
import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

async with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=credential
    ) as project_client,
):
```

### Performing Responses operations using OpenAI client

Use the `.get_openai_client()` method to obtain an authenticated [OpenAI](https://github.com/openai/openai-python) client and run Responses, Conversations, Evaluations, Files, and Fine-Tuning operations. See the **responses**, **agents**, **evaluations**, **files**, and **finetuning** folders in the [samples][samples] for complete working examples.

The code below assumes the environment variable `FOUNDRY_MODEL_NAME` is defined. It's the deployment name of an AI model in your Foundry Project. See first column titled "Name" in the "Deployed models" table in your Foundry Project.

<!-- SNIPPET:sample_responses_basic.responses -->

```python
with project_client.get_openai_client() as openai_client:
    response = openai_client.responses.create(
        model=os.environ["FOUNDRY_MODEL_NAME"],
        input="What is the size of France in square miles?",
    )
    print(f"Response output: {response.output_text}")

    response = openai_client.responses.create(
        model=os.environ["FOUNDRY_MODEL_NAME"],
        input="And what is the capital city?",
        previous_response_id=response.id,
    )
    print(f"Response output: {response.output_text}")
```

<!-- END SNIPPET -->

See the **responses** folder in the [samples][samples] for additional samples including streaming responses.

### Agents

See Foundry documentation:

* **[Microsoft Foundry Agents overview](https://learn.microsoft.com/azure/foundry/agents/overview)** — concepts, setup, and quick-starts.
* **[Quickstart: Set up Microsoft Foundry resources](https://learn.microsoft.com/azure/foundry/tutorials/quickstart-create-foundry-resources)** — create a project, deploy a model, and connect Application Insights for agent tracing.
* **[Runtime components](https://learn.microsoft.com/azure/foundry/agents/concepts/runtime-components?tabs=python)** — deep-dive into agent architecture.
* **[Tool catalog](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-catalog)** — all available tools and agent capabilities.
* **[SDK samples folder][samples]** — fully runnable Python code for synchronous and asynchronous clients covering all operations below.

## Examples

The table below lists the operation groups supported by the client library, with links to Foundry documentation and relevant [samples][samples] sub-folder. Additional documentation and samples may have been added after this package was released to cover the empty cells below.

| Topic | Foundry documentation | Samples folder |
|---|---|---|
| Agents (create, run, stream) | [Agents overview](https://learn.microsoft.com/azure/foundry/agents/overview) | `samples/agents/` |
| Agent Insights (preview) | | [On-demand analysis and scheduled monitors](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/agent_insights) |
| Hosted agents | [Hosted agents concepts](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents), [Deploy your first hosted agent](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent) | `samples/hosted_agents/` |
| Agents tools | [Tool catalog](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-catalog) | `samples/agents/tools/` |
| Agents optimization | [Prompt optimizer](https://learn.microsoft.com/azure/foundry/observability/how-to/prompt-optimizer), [Agent optimizer overview](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-optimizer-overview) | `samples/agents/optimization/` |
| Connections | [Add a new connection to your project](https://learn.microsoft.com/azure/foundry/how-to/connections-add?tabs=foundry-portal)| `samples/connections/` |
| Client-side tracing | [Add client-side tracing to Foundry agents](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-client-side?tabs=python) | `samples/telemetry/` |
| Datasets | | `samples/datasets/` |
| Deployments | [Deployment types](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/deployment-types) | `samples/deployments/` |
| Evaluation | [Evaluate agents](https://learn.microsoft.com/azure/foundry/observability/how-to/evaluate-agent) | `samples/evaluations/` |
| Files (upload, retrieve, list, delete) | [OpenAI Files API](https://platform.openai.com/docs/api-reference/files) | `samples/files/` |
| Fine-tuning | [When to use fine-tuning](https://learn.microsoft.com/azure/foundry/openai/concepts/fine-tuning-considerations), [Fine-Tuning in AI Foundry (GitHub repo)](https://github.com/microsoft-foundry/fine-tuning) | `samples/finetuning/` |
| Indexes | [Azure AI Search](https://learn.microsoft.com/azure/search/search-what-is-azure-search) | `samples/indexes/` |
| Memory stores (preview) | [What is memory?](https://learn.microsoft.com/azure/foundry/agents/concepts/what-is-memory?tabs=conversational-agent) | `samples/memories/` |
| Models (preview) | | `samples/models/` |
| Red teams (preview) | | `samples/red_team/` |
| Responses | [Responses API](https://platform.openai.com/docs/api-reference/responses) | `samples/responses/` |
| Routines (preview) | [Routines overview](https://learn.microsoft.com/azure/foundry/agents/concepts/routines) | `samples/hosted_agents/` |
| Sessions | [Manage hosted sessions](https://learn.microsoft.com/azure/foundry/agents/how-to/manage-hosted-sessions?pivots=python) | `samples/hosted_agents/` |
| Skills (preview) | | `samples/skills/` |
| Toolboxes | [Curate intent-based toolbox in Foundry](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/toolbox?pivots=python) | `samples/hosted_agents/`, `samples/toolboxes/` |
| Voice agents | | [Voice Agents samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/agents/voice) |

### Voice Agent realtime transport

Use `project_client.voice_agents.realtime` for agents created with `VoiceAgentDefinition`.
Connections use WebSocket by default. You can also select the transport explicitly:

```python
from azure.ai.projects.models import VoiceAgentTransport

with project_client.voice_agents.realtime.connect(
    agent_name="my-voice-agent",
    transport=VoiceAgentTransport.WEBSOCKET,
) as connection:
    print("Voice Agent connection is ready.")
```

The asynchronous client uses the same keyword:

```python
async with async_project_client.voice_agents.realtime.connect(
    agent_name="my-voice-agent",
    transport=VoiceAgentTransport.WEBSOCKET,
) as connection:
    print("Voice Agent connection is ready.")
```

Use `transport`, not `extra_query`, to select a transport. `VoiceAgentTransport.WEBRTC` enables
WebRTC signaling over the WebSocket, but your app must handle the peer connection, audio/video,
and SDP offer/answer exchange (`rtc.call.sdp.create` and `rtc.call.sdp.created`).

Start with the [text conversation sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/voice/sample_voice_agent_realtime_text_conversation_async.py)
or [microphone sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/voice/sample_voice_agent_realtime_audio_conversation_async.py).
The [async interruption sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/voice/sample_voice_agent_realtime_interruption_async.py)
cancels a spoken response and confirms truncation over the WebSocket.
It requires no audio devices: because it plays no audio, it reports zero heard milliseconds.
A real player must report its actual playback position.
The separate [sync REST example](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/voice/sample_voice_agent_read_generated_audio.py)
reads an existing generated-audio artifact and optionally saves it to a new output file.
It requires the stored item ID from REST and a deployment that persists unheard audio.

### Voice Agent campaigns (preview)

The [campaign sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/voice/sample_voice_agent_campaign.py)
create an outbound campaign scheduled for the next day, wait for preparation, then cancel
and delete the sample campaign. They use `.beta.voice_agents.telephony` and the SDK's
automatic long-running-operation polling, including operation-guarded final reads and
conditional cancellation/deletion with fresh ETags.

Use an existing voice agent, an outbound-capable telephony connection, and phone numbers
you have permission to use. Creation authorizes dialing; if execution is interrupted before
cancellation, the campaign may place calls at its scheduled time. The samples preserve the
existing agent and connection.

### Voice Agent GPT-Live (preview)

Use `.beta.voice_agents.live` for GPT-Live sessions and `.beta.voice_agents.live_conversations`
for their stored conversations. Realtime uses separate clients and agent definitions.

**Get started**

1. Install the sample dependencies:

```powershell
pip install "azure-ai-projects[voice]" azure-identity python-dotenv
```

2. Set `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_VOICE_AGENT_MODEL` in your environment or `.env`.
   The model value must be your GPT-Live **deployment name**, not a model catalog ID.
3. Choose an example below and follow its `USAGE` instructions. Samples authenticate with
   `DefaultAzureCredential` and opt in to preview features.

**Choose an example**

| Task | Example | Additional settings |
|---|---|---|
| Open, update, and close a session | [Async connection](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/voice/sample_voice_agent_live_connection_async.py) | None |
| Send text messages | [Async text](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/voice/sample_voice_agent_live_text_conversation_async.py) | `FOUNDRY_MODEL_NAME` for the Responses backend |
| Run a local function tool | [Async function tool](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/voice/sample_voice_agent_live_function_tool_async.py) | `FOUNDRY_MODEL_NAME` for the Responses backend |
| Ask a same-project prompt agent a spoken question | [Async managed agent](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/voice/sample_voice_agent_live_managed_agent_async.py) | `FOUNDRY_MODEL_NAME` for the prompt agent |
| Send a WAV file or use a microphone | [Async audio](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/voice/sample_voice_agent_live_audio_conversation_async.py) | None; a spoken question is included |
| Read a stored conversation and download audio | [Sync REST readback](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/voice/sample_voice_agent_live_read_conversation.py) | Optional existing conversation and agent IDs |

**Inputs and cleanup**

- Audio examples use the included `audio/question.wav`; no input-path setting or audio device
  is needed. It asks, "What is two plus two? Please ask the backend agent to answer my question."
  To use your own **PCM16, mono, 24-kHz WAV**, set `FOUNDRY_VOICE_AUDIO_INPUT_PATH`.
  The managed-agent example accepts up to 30 seconds and creates both agents in the same project.
  For microphone mode, install `pyaudio` and set `USE_MICROPHONE = True`.
- For multiple text turns, set `TEXT_PROMPTS` in the text example. The examples delete only
  resources they create; existing agents and conversations are never changed by REST readback.
- To read an existing stored conversation, set `FOUNDRY_VOICE_AGENT_NAME` and
  `FOUNDRY_VOICE_CONVERSATION_ID`. Use the ID from `session.started.conversation_id`, not
  `session.id`, after a session with `store=True`. Without an ID, the REST example creates
  and cleans up its own greeting conversation.
- Audio is not saved by default. `SAVE_AUDIO = True` saves replies in the audio example;
  REST downloads use a unique temporary folder. These files contain conversation content;
  remove them when finished. Customer-storage (BYOS) audio requires your own storage credentials.

**Session notes**

- Wait for `session.started` before sending commands. Foundry starts the session automatically.
  To finish, send `session.close` and wait for `session.closed`; Live has no `response.cancel`.
- Keep input audio paced while waiting for context updates. The connection example sends
  silent frames for this purpose; it needs no microphone.
- Responses commands require a Responses backend. Foundry handles managed-agent delegation;
  the client must not answer those requests itself. Session updates cannot change the saved
  delegation target, frontend model, or audio format.
- Printed backend text is not proof that speech finished. Audio examples wait for three
  quiet seconds, so a long pause can end capture early. Unsupported REST routes return HTTP 404.

## Client-side tracing

See [Add client-side tracing to Foundry agents (preview)](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-client-side?tabs=python).
The same global Foundry tracing configuration applies to Voice Agents REST and realtime tracing.

**Important:** GenAI tracing instrumentation is an experimental preview feature. Spans, attributes, and events may be modified in future versions. 

Samples can be found in the sub-folders `agents/telemetry` and `telemetry` in the [Samples][samples] folder.

## Troubleshooting

### Exceptions

Client methods that make service calls raise an [HttpResponseError](https://learn.microsoft.com/python/api/azure-core/azure.core.exceptions.httpresponseerror) exception for a non-success HTTP status code response from the service. The exception's `status_code` will hold the HTTP response status code (with `reason` showing the friendly name). The exception's `error.message` contains a detailed message that may be helpful in diagnosing the issue:

```python
from azure.core.exceptions import HttpResponseError

...

try:
    result = project_client.connections.list()
except HttpResponseError as e:
    print(f"Status code: {e.status_code} ({e.reason})")
    print(e.message)
```

For example, when you provide wrong credentials:

```text
Status code: 401 (Unauthorized)
Operation returned an invalid status 'Unauthorized'
```

### Logging

The client uses the standard [Python logging library](https://docs.python.org/3/library/logging.html). Logs can include request, response, and transport details that are useful when troubleshooting or reporting an issue to Microsoft.

#### Default console logging

To turn on client console logging define the environment variable `AZURE_AI_PROJECTS_CONSOLE_LOGGING=true` before running your Python script. Authentication bearer tokens are automatically redacted from the log. Your log may contain other sensitive information, so be sure to remove it before sharing the log with others.

#### Customizing your log

Instead of using the above-mentioned environment variable, you can configure logging yourself and control the log level, format, and destination. You can optionally attach the same handler to the Azure SDK logger and, for `.get_openai_client()` scenarios, optionally attach it to the dedicated OpenAI transport logger as well:

```python
import sys
import logging

# Direct logging output to stdout:
handler = logging.StreamHandler(stream=sys.stdout)
# Or direct logging output to a file:
# handler = logging.FileHandler(filename="sample.log")

# Optional: logger for azure-ai-projects and azure-core.
logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

# Optional: additional logger for an openai client generated from `.get_openai_client()`.
openai_logger = logging.getLogger("azure.ai.projects.openai_transport")
openai_logger.setLevel(logging.DEBUG)
openai_logger.propagate = False
openai_logger.addHandler(handler)

# Optional: Voice Agent Realtime WebSocket transport logger.
# For GPT Live, use "azure.ai.projects.live" instead.
voice_logger = logging.getLogger("azure.ai.projects.realtime")
voice_logger.setLevel(logging.DEBUG)
voice_logger.propagate = False
voice_logger.addHandler(handler)

# Optional: change the default logging format. Here we add a timestamp.
# formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
# handler.setFormatter(formatter)
```

The `azure` logger includes logs from `azure-ai-projects` and `azure-core`, including Voice Agent WebSocket transport logs. The dedicated OpenAI and Voice Agent loggers shown above can be used when you want only those transport logs. The `azure.ai.projects.realtime` and `azure.ai.projects.live` loggers record connection and close events and the type and byte count of each event sent or received at `DEBUG` level. They do not log event payloads, URL query strings, request headers, or authentication tokens.

By default, logs redact URL query values, some HTTP request and response headers (including `Authorization`), and request and response payloads. To create HTTP pipeline logs without redaction, add `logging_enable=True` to the client constructor:

```python
project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    logging_enable=True
)
```

Note that the log level must be set to `logging.DEBUG` (see above code). Logs will be redacted with any other log level.

See the logging samples in the `samples/logs/` folder for complete end-to-end examples, including console logging, file logging, OpenAI transport logging, and Voice Agent realtime logging.

Be sure to protect non-redacted logs to avoid compromising security.

For more information, see [Configure logging in the Azure libraries for Python](https://aka.ms/azsdk/python/logging)

### Reporting issues

To report an issue with the client library, or request additional features, please open a [GitHub issue here](https://github.com/Azure/azure-sdk-for-python/issues). Mention the package name "azure-ai-projects" in the title or content.

## Next steps

Have a look at the [Samples][samples] folder, containing fully runnable Python code for synchronous and asynchronous clients.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information, see the Code of Conduct FAQ or contact opencode@microsoft.com with any additional questions or comments.

<!-- LINKS -->
[samples]: https://aka.ms/azsdk/azure-ai-projects-v2/python/samples/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[azure_sub]: https://azure.microsoft.com/free/
