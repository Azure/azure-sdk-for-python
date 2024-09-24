# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: assistants_v2_aoai_quickstart.py

DESCRIPTION:
    This sample demonstrates how to get started with Assistants (v2) using the official OpenAI library for Python.

USAGE:
    python assistants_v2_aoai_quickstart.py

    Before running the sample:

    pip install openai
    pip install azure-identity

    Set the environment variables with your own values:
    1) AZURE_OPENAI_ENDPOINT - the endpoint to your Azure OpenAI resource.
    2) AZURE_OPENAI_DEPLOYMENT - the deployment name you chose when deploying your model.
"""

# These lines are intentionally excluded from the sample code, we use them to configure any vars
# or to tweak usage in ways that keep samples looking consistent when rendered in docs and tools
import os
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZ_OPENAI_ENDPOINT")
os.environ["AZURE_OPENAI_DEPLOYMENT"] = "gpt-4-1106-preview"

def assistants_v2_aoai_quickstart() -> None:
  #[START assistant_setup]
  import os
  from azure.identity import DefaultAzureCredential, get_bearer_token_provider
  from openai import AzureOpenAI

  token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

  client = AzureOpenAI(
      azure_ad_token_provider=token_provider,
      api_version=os.getenv("GA"),
      azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
      )

  assistant = client.beta.assistants.create(
      instructions="You are an AI assistant that can write code to help answer math questions.",
      model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
      tools=[{"type":"code_interpreter"}]
      )
  #[END assistant_setup]

  #[START run_assistant]
  # Create a thread
  thread = client.beta.threads.create()

  # Add a user question to the thread
  message = client.beta.threads.messages.create(
      thread_id=thread.id,
      role="user",
      content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
  )

  # Run the thread and poll for the result
  run = client.beta.threads.runs.create_and_poll(
      thread_id=thread.id,
      assistant_id=assistant.id,
      instructions="Please address the user as Jane Doe. The user has a premium account.",
  )

  print("Run completed with status: " + run.status)

  if run.status == "completed":
      messages = client.beta.threads.messages.list(thread_id=thread.id)
      print(messages.to_json(indent=2))
  #[END run_assistant]

if __name__ == "__main__":
  assistants_v2_aoai_quickstart()
