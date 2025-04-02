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
        model="gpt-4o", name="SampleAgent", instruction="You are helpful assistant"
    )
    run = project_client.agents.run(agent_id=agent.agent_id, input_message="Tell me a joke")
    messages = run.run_outputs.messages
    for text_message in messages.text_messages:
        print(text_message)