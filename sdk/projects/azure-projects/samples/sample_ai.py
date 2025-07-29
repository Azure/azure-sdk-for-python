# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_ai.py

DESCRIPTION:
    This sample demonstrates using the AzureApp and AzureInfrastructure components
    to build and run various AI scenarios.

    This sample includes provisioning the following Azure resources which may incur charges:
    - Azure Resource Group
    - Azure User-Assigned Managed Identity
    - Azure App Configuration (SKU: Free)
    - Azure Foundry
    - Azure AI Project
    - Azure AI Chat model (SKU:)
    - Azure AI Embeddings model (SKU:)

    See pricing: https://azure.microsoft.com/pricing/.

USAGE:
    python sample_ai.py

    Running the samples requires that Azure Developer CLI be installed and authenticated:
    For more information: https://learn.microsoft.com/azure/developer/azure-developer-cli/
"""
import asyncio
import time

from azure.projects import deprovision

unique_suffix = int(time.time())


async def main():
    # Creating a chat client and provisioning the model behind it can be achieved in a few lines.
    from azure.projects import AzureApp
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import AssistantMessage, UserMessage

    class ChatApp(AzureApp):
        chat: ChatCompletionsClient

    with ChatApp.provision() as app:
        response = app.chat.complete(
            messages=[  # type: ignore[arg-type]
                UserMessage("How many feet are in a mile?"),
            ],
        )

        print(response.choices[0].message.content)
        print(f"\nToken usage: {response.usage}")

    # The Chat model resource is already parameterized with the following parameters that you
    # can use to modify the deployment:
    # - aiChatModel, default value is 'o1-mini'
    # - aiChatModelFormat, default value is 'OpenAI'
    # - aiChatModelVersion, default value is '2024-09-12'
    # - aiChatModelSku, default value is 'GlobalStandard'
    # - aiChatModelCapacity, default value is 1
    parameters = {
        "aiChatModel": "DeepSeek-V3",
        "aiChatModelFormat": "DeepSeek",
        "aiChatModelVersion": "1",
    }
    with ChatApp.provision(parameters=parameters) as app:
        response = app.chat.complete(
            messages=[  # type: ignore[arg-type]
                UserMessage("How many feet are in a mile?"),
            ]
        )

        print(response.choices[0].message.content)
        print(f"\nToken usage: {response.usage}")

    # If you want to change the default model deployment, including defining your own parameters,
    # you can update the AIChat resource
    from azure.projects import Parameter
    from azure.projects.resources.ai.deployment import AIChat

    AIChat.DEFAULTS = {
        "name": "Phi-4",
        "properties": {
            "model": {
                "name": "Phi-4",
                "version": Parameter("Phi4Version"),
                "format": "Microsoft",
            },
            "raiPolicyName": "Microsoft.DefaultV2",
        },
        "sku": {"name": "GlobalStandard", "capacity": 1},
    }

    with ChatApp.provision(parameters={"Phi4Version": "7"}) as app:
        response = app.chat.complete(
            messages=[  # type: ignore[arg-type]
                UserMessage("How many feet are in a mile?"),
            ]
        )

        print(response.choices[0].message.content)
        print(f"\nToken usage: {response.usage}")

        deprovision(app, purge=True)

    # If we want to have more control over the deployed resources, including adding other resources or
    # multiple models, we can create an AzureInfrastructure definition.
    from azure.projects import AzureInfrastructure
    from azure.projects.resources.storage.blobs.container import BlobContainer

    class ChatInfra(AzureInfrastructure):
        phi_4: AIChat = AIChat(model="Phi-4", version="7", format="Microsoft")
        open_ai: AIChat = AIChat(model="o1-mini", version="2024-09-12", format="OpenAI")
        deepseek: AIChat = AIChat(model="DeepSeek-V3", version="1", format="DeepSeek")
        data: BlobContainer = BlobContainer()

    infra = ChatInfra()

    from openai import AzureOpenAI
    from azure.storage.blob import ContainerClient

    class MultiChatApp(AzureApp):
        chat_a: AzureOpenAI  # We can also use the OpenAI SDK
        chat_b: ChatCompletionsClient
        outputs: ContainerClient

    # Our custom infra definition has multiple chat models defined, so we will need to provide
    # a mapping to specify which resources should be used with which clients.
    resource_map = {"chat_a": "open_ai", "chat_b": "phi_4"}

    with MultiChatApp.provision(infra, attr_map=resource_map) as multi_chat_app:
        question = "How many feet are in a mile?"
        print(f"Question: {question}")
        openai_response = multi_chat_app.chat_a.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": question,
                },
            ],
            model="o1-mini",
        )
        print(f"OpenAI says: {openai_response.choices[0].message.content}")
        phi_response = multi_chat_app.chat_b.complete(
            messages=[
                UserMessage(question),
                AssistantMessage(openai_response.choices[0].message.content),
                UserMessage("Do you agree?"),
            ]
        )
        print(f"Phi says: {phi_response.choices[0].message.content}")

        deprovision(multi_chat_app, purge=True)

    # You can also provision models as part of complete Azure Foundry deployment, which could
    # use a combination of new or existing resources
    from azure.projects.resources.foundry import AIHub, AIProject
    from azure.projects.resources.keyvault import KeyVault
    from azure.projects.resources.storage.blobs import BlobStorage
    from azure.projects.resources.search import SearchService
    from azure.ai.projects import AIProjectClient

    # When using the AIProject and AIHub resources, Connections will automatically be created
    # with other applicable resources within the Infrastructure definition.
    class FoundryInfra(AzureInfrastructure):
        phi_4: AIChat = AIChat(model="Phi-4", version="7", format="Microsoft")
        open_ai: AIChat = AIChat(model="o1-mini", version="2024-09-12", format="OpenAI")
        deepseek: AIChat = AIChat(model="DeepSeek-V3", version="1", format="DeepSeek")
        vault: KeyVault = KeyVault()
        datastore: BlobStorage = BlobStorage()
        search: SearchService = SearchService()
        hub: AIHub = AIHub()
        project: AIProject = AIProject()

    my_foundry = FoundryInfra()

    class AIProjectApp(AzureApp):
        admin: AIProjectClient

    with AIProjectApp.provision(my_foundry) as foundry_app:
        for connection in foundry_app.admin.connections.list():
            print(f"Connection: {connection.name}, {connection.connection_type}, {connection.authentication_type}")

        deprovision(foundry_app, purge=True)


if __name__ == "__main__":
    asyncio.run(main())
