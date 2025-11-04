# Azure AI Agent Server adapter for LangGraph

## Install

In current folder, run:
```bash
pip install -e .
```

## Usage

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

Reference this [example](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agentserver-langgraph/samples/custom_state/main.py) for more details.

