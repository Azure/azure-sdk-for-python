# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates the FoundryProject endpoint with "_default" project name.

    The OpenAI compatible Responses call in this sample is made using the OpenAI client from the
    `openai` package. See https://platform.openai.com/docs/api-reference for more information.

USAGE:
    python sample_agent_with_default_endpoint.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
     1) FOUNDRY_ACCOUNT_NAME - Your Foundry account name (used to construct the project endpoint).
     2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
         the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

foundry_account_name = os.environ["FOUNDRY_ACCOUNT_NAME"]

# [START default_endpoint]
endpoint = f"https://{foundry_account_name}.services.ai.azure.com/api/projects/_default"
# [END default_endpoint]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    with project_client.get_openai_client() as openai_client:
        agent = project_client.agents.create_version(
            agent_name="MyAgent",
            definition=PromptAgentDefinition(
                model=os.environ["FOUNDRY_MODEL_NAME"],
                instructions="You are a helpful assistant that answers general questions",
            ),
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

        response = openai_client.responses.create(
            extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
            input="What is the size of France in square miles?",
        )
        print(f"Response output: {response.output_text}")

    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
