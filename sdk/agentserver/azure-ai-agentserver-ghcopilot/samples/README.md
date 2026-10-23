# Samples for azure-ai-agentserver-ghcopilot

## Quick start

Before starting Python, activate a virtual environment with the sample's
dependencies installed and configure the launching shell:

```bash
export PYTHONNOUSERSITE=1
```

In PowerShell use `$env:PYTHONNOUSERSITE = "1"`. Do not set this only inside
Python or a `.env` file loaded by the application. For hosted deployments,
also configure the remote agent definition as described in the
[Python startup guide](../../../ai/azure-ai-projects/samples/hosted_agents/README.md#python-startup-configuration).
Install dependencies in the virtual environment or image, not with `pip install --user`.

```python
from azure.ai.agentserver.githubcopilot import GitHubCopilotAdapter

adapter = GitHubCopilotAdapter.from_project(".")
adapter.run()
```

See the [package README](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-ghcopilot) for environment variable configuration.
