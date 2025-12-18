# Before running the sample:
#    pip install --pre azure-ai-projects>=2.0.0b1
#    pip install azure-identity

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

myEndpoint = "https://ai-account-x3pxnw7bdbexq.services.ai.azure.com/api/projects/ai-project-test-hugging-face-agent"

project_client = AIProjectClient(
    endpoint=myEndpoint,
    credential=DefaultAzureCredential(),
)

myAgent = "HuggingFace-Agent"
agent = project_client.agents.get(agent_name=myAgent)
print(f"Retrieved agent: {agent.name}")
print(f"Agent version: {agent.version if hasattr(agent, 'version') else 'N/A'}")
print(f"Agent ID: {agent.id if hasattr(agent, 'id') else 'N/A'}")



openai_client = project_client.get_openai_client()

# Reference the agent to get a streaming response
response_stream = openai_client.responses.create(
    input=[{"role": "user", "content": "What are the trending models in the OpenLLM Leaderboard?"}],
    extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    stream=True,
)

print("Streaming response:")
for chunk in response_stream:
    # if hasattr(chunk, 'output_text') and chunk.output_text:
    #     print(chunk.output_text, end='', flush=True)
    # elif hasattr(chunk, 'delta') and chunk.delta:
    #     print(chunk.delta, end='', flush=True)
    print(chunk)
print()  # New line at the end


