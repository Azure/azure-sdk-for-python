import os
from azure.ai.client import AzureAIClient
from azure.identity import DefaultAzureCredential

# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# It should have the format "<Endpoint>;<AzureSubscriptionId>;<ResourceGroup>;<WorkspaceName>"
ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(),
    connection=os.environ["AI_CLIENT_CONNECTION_STRING"],
)

# Or, you can create the Azure AI Client by giving all required parameters directly
# ai_client = AzureAIClient(
#     credential=DefaultAzureCredential(),
#     endpoint=os.environ["AI_CLIENT_ENDPOINT"],
#     subscription_id=os.environ["AI_CLIENT_SUBSCRIPTION_ID"],
#     resource_group_name=os.environ["AI_CLIENT_RESOURCE_GROUP_NAME"],
#     workspace_name=os.environ["AI_CLIENT_WORKSPACE_NAME"],
# )

# Get an authenticated OpenAI client for your default Azure OpenAI connection:
client = ai_client.inference.get_azure_openai_client()

response = client.chat.completions.create(
    model="gpt-4-0613",
    messages=[
        {
            "role": "user",
            "content": "How many feet are in a mile?",
        },
    ],
)

print(response.choices[0].message.content)


