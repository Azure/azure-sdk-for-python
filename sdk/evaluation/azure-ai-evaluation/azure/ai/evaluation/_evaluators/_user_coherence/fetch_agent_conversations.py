"""
Fetch conversations from Azure AI Foundry agents and save to JSON files.

Usage:
    python fetch_agent_conversations.py

Prerequisites:
    - pip install azure-ai-projects azure-identity
    - Azure credentials configured (e.g., `az login`)

Environment variables:
    PROJECT_ENDPOINT: Your Azure AI Foundry project endpoint
        e.g., "https://<account>-resource.services.ai.azure.com/api/projects/<project>"
    AGENTS: Comma-separated list of agent names to fetch (optional).
    MAX_CONVERSATIONS: Max conversations per agent (default: 30).
"""

import json
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.core.rest import HttpRequest


# Configuration
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT", "")
AGENTS = os.environ.get("AGENTS", "legal-contract-review-sim,airline-customer-service-sim").split(",")
MAX_CONVERSATIONS_PER_AGENT = int(os.environ.get("MAX_CONVERSATIONS", "30"))
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def fetch_all_conversation_ids(project):
    """Fetch all conversation IDs from the project, paginating if needed.

    :param project: AIProjectClient instance.
    :return: List of conversation ID strings.
    """
    all_ids = []
    after = None
    while True:
        url = "/openai/v1/conversations?limit=100"
        if after:
            url += f"&after={after}"
        resp = project.send_request(HttpRequest(method="GET", url=url))
        page = json.loads(resp.content.decode("utf-8", errors="replace"))
        convs = page.get("data", [])
        all_ids.extend(c["id"] for c in convs)
        if not page.get("has_more", False) or not convs:
            break
        after = convs[-1]["id"]
    return all_ids


def get_agent_name_from_messages(messages):
    """Extract the agent name from conversation messages.

    Looks at the ``created_by.agent.name`` field on assistant messages.

    :param messages: List of message dicts (as returned by model_dump).
    :return: Agent name string, or None if not found.
    """
    for msg in messages:
        created_by = msg.get("created_by", {})
        if isinstance(created_by, dict):
            agent = created_by.get("agent", {})
            if isinstance(agent, dict) and agent.get("name"):
                return agent["name"]
    return None


def fetch_conversations(project_endpoint, agents, max_per_agent):
    """Fetch conversations from Foundry, grouped by agent.

    The Foundry ``conversations.items.list()`` API returns messages in **reverse
    chronological order** (newest first). This function reverses them back to
    chronological order before returning.

    :param project_endpoint: The Azure AI Foundry project endpoint URL.
    :param agents: List of agent names to collect.
    :param max_per_agent: Max conversations per agent.
    :return: Dict mapping agent_name -> list of conversation dicts.
    """
    project = AIProjectClient(endpoint=project_endpoint, credential=DefaultAzureCredential())
    openai_client = project.get_openai_client()

    # Get all conversation IDs
    conv_ids = fetch_all_conversation_ids(project)
    print(f"Total conversations in project: {len(conv_ids)}")

    needed = {a: max_per_agent for a in agents}
    result = {a: [] for a in agents}

    for i, conv_id in enumerate(conv_ids):
        # Stop early if we have enough for every agent
        if all(n <= 0 for n in needed.values()):
            print(f"Got enough conversations for all agents. Stopping at {i}/{len(conv_ids)}.")
            break

        # Retrieve conversation metadata
        conv = openai_client.conversations.retrieve(conv_id)

        # Get messages (returned newest-first by the API)
        items = list(openai_client.conversations.items.list(conversation_id=conv_id))
        messages = [item.model_dump() if hasattr(item, "model_dump") else item for item in items]

        # Identify agent
        agent_name = get_agent_name_from_messages(messages)

        if agent_name not in needed or needed[agent_name] <= 0:
            continue

        # Reverse to chronological order (oldest first)
        messages.reverse()

        result[agent_name].append({
            "conversation_id": conv_id,
            "created_at": conv.created_at if hasattr(conv, "created_at") else None,
            "metadata": conv.metadata if hasattr(conv, "metadata") else {},
            "agent_name": agent_name,
            "messages": messages,
        })
        needed[agent_name] -= 1
        print(f"  [{i+1}/{len(conv_ids)}] {conv_id[:30]}... -> {agent_name} ({len(messages)} msgs) [need {needed[agent_name]} more]")

    project.close()
    return result


def main():
    if not PROJECT_ENDPOINT:
        print("ERROR: Set the PROJECT_ENDPOINT environment variable.")
        print("  e.g., set PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>")
        return

    agent_conversations = fetch_conversations(PROJECT_ENDPOINT, AGENTS, MAX_CONVERSATIONS_PER_AGENT)

    for agent_name, convs in agent_conversations.items():
        total_msgs = sum(len(c["messages"]) for c in convs)
        output_path = os.path.join(OUTPUT_DIR, f"{agent_name}_conversations.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(convs, f, indent=2, default=str)
        print(f"\n{agent_name}: {len(convs)} conversations ({total_msgs} messages) -> {output_path}")

    print("\nDone!")


if __name__ == "__main__":
    main()
