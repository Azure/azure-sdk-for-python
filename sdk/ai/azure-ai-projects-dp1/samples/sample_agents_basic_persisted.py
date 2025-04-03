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
        model_id="gpt-4o", name="SampleAgent", instructions_str="You are helpful assistant"
    )

    # If create_agent returns None (and does not throw an error), it means the agent already exists.
    # In that case, you can retrieve the agent using get_agent method.
    if agent is None:
        agent = project_client.agents.get_agent(agent_name="SampleAgent")

    run: Run = project_client.agents.run(agent_id=agent.agent_id, input_message="Tell me a joke")
    messages = run.run_outputs.messages
    for text_message in messages.text_messages:
        print(text_message)
