import os
from azure.ai.projects.dp1.models import Run, TextContent, ChatMessage
from azure.ai.projects.dp1 import AIProjectClient
from azure.identity import DefaultAzureCredential
from typing import List

project_client = AIProjectClient(
    endpoint=os.environ["AGENT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    agent = project_client.agents.create_agent(
        model_id="gpt-4o", display_name="SampleAgent", instructions="You are helpful assistant"
    )

    run = project_client.agents.run(agent_id=agent.agent_id, message="Tell me a joke")
    for text_message in run.text_messages:
        print(text_message)
