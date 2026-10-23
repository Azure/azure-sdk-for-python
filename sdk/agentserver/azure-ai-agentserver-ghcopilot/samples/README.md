# Samples for azure-ai-agentserver-ghcopilot

## Quick start

For hosted deployments, configure `PYTHONNOUSERSITE` as `"1"` in the
remote agent definition's environment or the Python Dockerfile, as described in the
[Python startup guide](../../../ai/azure-ai-projects/samples/hosted_agents/README.md#python-startup-configuration).
Install dependencies in the virtual environment or image, not with `pip install --user`.

```python
from azure.ai.agentserver.githubcopilot import GitHubCopilotAdapter

adapter = GitHubCopilotAdapter.from_project(".")
adapter.run()
```

See the [package README](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-ghcopilot) for environment variable configuration.
