"""Minimal test agent — proves the azure-ai-agentserver-github package works end-to-end."""

from dotenv import load_dotenv
load_dotenv(override=False)

from azure.ai.agentserver.github import GitHubCopilotAdapter

adapter = GitHubCopilotAdapter.from_project(".")
adapter.run()
