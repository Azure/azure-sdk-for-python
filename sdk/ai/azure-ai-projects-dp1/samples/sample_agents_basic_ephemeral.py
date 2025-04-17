import os
from azure.ai.projects.dp1 import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=os.environ["AGENT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    run = project_client.agents.run(
        model_id="gpt-4o", instructions="You are helpful assistant", message="Tell me a joke"
    )

    for text_message in run.text_messages:
        print(text_message)
