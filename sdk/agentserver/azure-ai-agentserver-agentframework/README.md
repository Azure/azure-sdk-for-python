# Azure AI Agent Server Adapter for Agent-framework Python



## Getting started

```bash
pip install azure-ai-agentserver-agentframework
```


## Key concepts

Azure AI Agent Server wraps your Agent-framework agent, and host it on the cloud.


## Examples

```python
# your existing agent
from my_framework_agent import my_awesome_agent

# agent framework utils
from azure.ai.agentserver.agentframework import from_agent_framework

if __name__ == "__main__":
    # with this simple line, your agent will be hosted on http://localhost:8088
    from_agent_framework(my_awesome_agent).run()

```

## Troubleshooting

First run your agent with azure-ai-agentserver-agentframework locally.

If it works on local but failed on cloud. Check your logs in the application insight connected to your Azure AI Foundry Project.


## Next steps

Please visit [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-agentframework/samples) folder. There are several samples for you to build your agent with azure-ai-agentserver


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
