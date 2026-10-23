# Samples for azure-ai-agentserver-ghcopilot

## Quick start

For hosted Python deployments, set `PYTHONNOUSERSITE` to `"1"` in the agent
definition's `environment_variables` map, or add `ENV PYTHONNOUSERSITE=1` to its
Dockerfile. This disables Python user-site package loading. Install dependencies
in a virtual environment or image, not with `pip install --user`. See
[Configure hosted agent environment variables](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/configure-hosted-agent-env-variables)
for deployment configuration.

```python
from azure.ai.agentserver.githubcopilot import GitHubCopilotAdapter

adapter = GitHubCopilotAdapter.from_project(".")
adapter.run()
```

See the [package README](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-ghcopilot) for environment variable configuration.
