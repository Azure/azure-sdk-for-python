# Azure AI Agent Server adapter for Agent-framework

## Install

In current folder, run:
```bash
pip install -e .
```

## Usage

```python
# your existing agent
from my_framework_agent import my_awesome_agent

# agent framework utils
from azure.ai.agentserver.agentframework import from_agent_framework

if __name__ == "__main__":
    # with this simple line, your agent will be hosted on http://localhost:8088
    from_agent_framework(my_awesome_agent).run()

```
