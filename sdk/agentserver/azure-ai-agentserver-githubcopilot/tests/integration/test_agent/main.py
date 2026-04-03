"""Minimal test agent — proves the azure-ai-agentserver-githubcopilot package works end-to-end."""

import logging
import os

from dotenv import load_dotenv
load_dotenv(override=False)

logging.basicConfig(level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO))

from azure.ai.agentserver.githubcopilot import GitHubCopilotAdapter

adapter = GitHubCopilotAdapter.from_project(".")
adapter.run()
