# Azure AI Agent Server Adapter for Python


## Getting started

```bash
pip install azure-ai-agentserver-core
```

## Key concepts

This is the core package for Azure AI Agent server. It hosts your agent as a container on the cloud.

You can talk to your agent using azure-ai-project sdk.


## Examples

If your agent is not built using a supported framework such as LangGraph and Agent-framework, you can still make it compatible with Microsoft AI Foundry by manually implementing the predefined interface.

```python
import datetime

from azure.ai.agentserver.core import FoundryCBAgent
from azure.ai.agentserver.core.models import (
    CreateResponse, 
    Response as OpenAIResponse,
)
from azure.ai.agentserver.core.models.projects import (
    ItemContentOutputText,
    ResponsesAssistantMessageItemResource,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
)


def stream_events(text: str):
    assembled = ""
    for i, token in enumerate(text.split(" ")):
        piece = token if i == len(text.split(" ")) - 1 else token + " "
        assembled += piece
        yield ResponseTextDeltaEvent(delta=piece)
    # Done with text
    yield ResponseTextDoneEvent(text=assembled)


async def agent_run(request_body: CreateResponse):
    agent = request_body.agent
    print(f"agent:{agent}")

    if request_body.stream:
        return stream_events("I am mock agent with no intelligence in stream mode.")

    # Build assistant output content
    output_content = [
        ItemContentOutputText(
            text="I am mock agent with no intelligence.",
            annotations=[],
        )
    ]

    response = OpenAIResponse(
        metadata={},
        temperature=0.0,
        top_p=0.0,
        user="me",
        id="id",
        created_at=datetime.datetime.now(),
        output=[
            ResponsesAssistantMessageItemResource(
                status="completed",
                content=output_content,
            )
        ],
    )
    return response


my_agent = FoundryCBAgent()
my_agent.agent_run = agent_run

if __name__ == "__main__":
    my_agent.run()

```

## Troubleshooting

First run your agent with azure-ai-agentserver-core locally.

If it works on local by failed on cloud. Check your logs in the application insight connected to your Azure AI Foundry Project.


### Reporting issues

To report an issue with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues). Mention the package name "azure-ai-agents" in the title or content.


## Next steps

Please visit [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-core/samples) folder. There are several cases for you to build your agent with azure-ai-agentserver


## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.
