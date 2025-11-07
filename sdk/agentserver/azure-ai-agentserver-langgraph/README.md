# Azure AI Agent Server Adapter for LangGraph Python


## Getting started

```bash
pip install azure-ai-agentserver-langgraph
```


## Key concepts

Azure AI Agent Server wraps your LangGraph agent, and host it on the cloud.


## Examples

```python
# your existing agent
from my_langgraph_agent import my_awesome_agent

# langgraph utils
from azure.ai.agentserver.langgraph import from_langgraph

if __name__ == "__main__":
    # with this simple line, your agent will be hosted on http://localhost:8088
    from_langgraph(my_awesome_agent).run()

```

**Note**
If your langgraph agent was not using langgraph's builtin [MessageState](https://langchain-ai.github.io/langgraph/concepts/low_level/?h=messagesstate#messagesstate), you should implement your own `LanggraphStateConverter` and provide to `from_langgraph`.

Reference this [example](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-langgraph/samples/custom_state/main.py) for more details.


## Troubleshooting

First run your agent with azure-ai-agentserver-langgraph locally.

If it works on local by failed on cloud. Check your logs in the application insight connected to your Azure AI Foundry Project.


## Next steps

Please visit [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-langgraph/samples) folder. There are several samples for you to build your agent with azure-ai-agentserver-* packages


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
