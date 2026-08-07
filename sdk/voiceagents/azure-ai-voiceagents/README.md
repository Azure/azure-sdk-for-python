# Azure AI Voice Agents client library for Python

The Azure AI Voice Agents client library provides APIs for creating and managing
voice agents in an Azure AI Foundry project, reading persisted voice
conversations, and connecting to a voice agent over a realtime WebSocket session.

Use this package to:

- Generate or create voice agents with model, instruction, voice, and tool settings.
- Manage voice agent versions and operational state.
- Stream live microphone audio to an existing voice agent and receive spoken responses.
- Read persisted conversation transcripts and audio when an agent is configured to store them.

## Getting started

### Install the package

```bash
python -m pip install azure-ai-voiceagents
```

### Prerequisites

- Python 3.10 or later is required to use this package.
- You need an Azure subscription.
- You need an Azure AI Foundry project endpoint, for example
  `https://<account>.services.ai.azure.com/api/projects/<project>`.
- For Microsoft Entra ID authentication, install [`azure-identity`][azure_identity_pip].
- For realtime async WebSocket sessions, install an async transport such as `aiohttp`.

### Authenticate the client

The client supports token credentials from the
[`azure-identity`][azure_identity_credentials] library. For example,
[`DefaultAzureCredential`][default_azure_credential] can authenticate from your
developer environment or configured application identity.

```python
from azure.ai.voiceagents import VoiceAgentsClient
from azure.identity import DefaultAzureCredential

client = VoiceAgentsClient(
    endpoint="https://<account>.services.ai.azure.com/api/projects/<project>",
    credential=DefaultAzureCredential(),
)
```

## Examples

Create a voice agents client and list the voice agents in a project:

```python
from azure.ai.voiceagents import VoiceAgentsClient
from azure.ai.voiceagents.models import AgentDefinitionOptInKeys
from azure.identity import DefaultAzureCredential

client = VoiceAgentsClient(
    endpoint="https://<account>.services.ai.azure.com/api/projects/<project>",
    credential=DefaultAzureCredential(),
)

for agent in client.voice_agents.list_voice_agents(
    foundry_features=AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW
):
    print(agent.name)
```

See the [samples on GitHub](https://github.com/Azure/azure-sdk-for-python/tree/xitzhang/voice-agent-pupr/sdk/voiceagents/azure-ai-voiceagents/samples)
for management, quickstart, and realtime conversation examples.

## Key concepts

- **Voice agents** are managed in an Azure AI Foundry project through the
    `VoiceAgentsClient`.
- **Realtime sessions** connect to an agent over an asynchronous WebSocket
    connection and can stream audio input and output.
- **Persisted conversations** contain transcripts and audio when conversation
    storage is enabled for the agent.

## Troubleshooting

- Verify that `AZURE_VOICE_AGENTS_ENDPOINT` points to the Foundry project
    endpoint, not the account endpoint.
- Ensure the credential has permission to access the project and its voice
    agents.
- For realtime audio samples, install `aiohttp` and `pyaudio`, and verify that
    the operating system has an available microphone and speaker.

## Next steps

- Review the [sample collection](https://github.com/Azure/azure-sdk-for-python/tree/xitzhang/voice-agent-pupr/sdk/voiceagents/azure-ai-voiceagents/samples).
- Read the [Azure AI Foundry documentation](https://learn.microsoft.com/azure/ai-foundry/).
- See the [API reference](https://github.com/Azure/azure-sdk-for-python/blob/xitzhang/voice-agent-pupr/sdk/voiceagents/azure-ai-voiceagents/api.md).

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit <https://cla.microsoft.com>.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact <opencode@microsoft.com> with any
additional questions or comments.

<!-- LINKS -->
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
