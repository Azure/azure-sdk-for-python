# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_update_defaults.py

DESCRIPTION:
    This sample demonstrates how to configure and retrieve default model deployment settings
    for your Microsoft Foundry resource. This is a required one-time setup per Microsoft Foundry
    resource before using prebuilt or custom analyzers.

    ## About model deployment configuration

    Content Understanding prebuilt analyzers and custom analyzers require specific large language
    model deployments to function. Currently, Content Understanding uses OpenAI GPT models:

    - gpt-4.1 - Used by most prebuilt analyzers (e.g., prebuilt-invoice, prebuilt-receipt,
      prebuilt-idDocument)
    - gpt-4.1-mini - Used by RAG analyzers (e.g., prebuilt-documentSearch, prebuilt-imageSearch,
      prebuilt-audioSearch, prebuilt-videoSearch)
    - text-embedding-3-large - Used for semantic search and embeddings

    This configuration is per Microsoft Foundry resource and persists across sessions.
    You only need to configure it once per Microsoft Foundry resource (or when you change
    deployment names).

    ## Prerequisites

    To get started you'll need:

    1. An Azure subscription and a Microsoft Foundry resource. To create a Microsoft Foundry
       resource, follow the steps in the Azure Content Understanding quickstart.
       You must create your Microsoft Foundry resource in a region that supports Content Understanding.

    2. After creating your Microsoft Foundry resource, you must grant yourself the Cognitive Services
       User role to enable API calls for setting default model deployments. This role assignment
       is required even if you are the owner of the resource.

    3. Take note of your Microsoft Foundry resource endpoint and, if you plan to use key-based
       authentication, the API key. A typical endpoint looks like:
       https://your-foundry.services.ai.azure.com

    4. If you plan to use DefaultAzureCredential for authentication, you will need to log in to
       Azure first. Typically, you can do this by running az login (Azure CLI) or azd login
       (Azure Developer CLI) in your terminal.

    5. Deploy the following models in Microsoft Foundry:
       - gpt-4.1
       - gpt-4.1-mini
       - text-embedding-3-large

    6. Take note of the deployment names used for each model. The convention is to use the model
       names (e.g., "gpt-4.1", "gpt-4.1-mini", "text-embedding-3-large"), but you can change these
       during deployment. You'll use these deployment names when configuring defaults.

USAGE:
    python sample_update_defaults.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
       Example: https://your-foundry.services.ai.azure.com
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using
       DefaultAzureCredential). Use key-based authentication for testing only; use
       DefaultAzureCredential (recommended) for production.
    3) GPT_4_1_DEPLOYMENT - your GPT-4.1 deployment name in Microsoft Foundry.
    4) GPT_4_1_MINI_DEPLOYMENT - your GPT-4.1-mini deployment name in Microsoft Foundry.
    5) TEXT_EMBEDDING_3_LARGE_DEPLOYMENT - your text-embedding-3-large deployment name in Microsoft Foundry.
"""

import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()


def main() -> None:
    # Create a ContentUnderstandingClient
    # You can authenticate using either DefaultAzureCredential (recommended) or an API key.
    # DefaultAzureCredential will look for credentials in the following order:
    # 1. Environment variables (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)
    # 2. Managed identity (for Azure-hosted applications)
    # 3. Azure CLI (az login)
    # 4. Azure Developer CLI (azd login)
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    # [START update_defaults]
    # Get deployment names from environment variables
    gpt_4_1_deployment = os.getenv("GPT_4_1_DEPLOYMENT")
    gpt_4_1_mini_deployment = os.getenv("GPT_4_1_MINI_DEPLOYMENT")
    text_embedding_3_large_deployment = os.getenv("TEXT_EMBEDDING_3_LARGE_DEPLOYMENT")

    # Check if required deployments are configured
    missing_deployments = []
    if not gpt_4_1_deployment:
        missing_deployments.append("GPT_4_1_DEPLOYMENT")
    if not gpt_4_1_mini_deployment:
        missing_deployments.append("GPT_4_1_MINI_DEPLOYMENT")
    if not text_embedding_3_large_deployment:
        missing_deployments.append("TEXT_EMBEDDING_3_LARGE_DEPLOYMENT")

    if missing_deployments:
        print("⚠️  Missing required environment variables:")
        for deployment in missing_deployments:
            print(f"   - {deployment}")
        print("\nPlease set these environment variables and try again.")
        print("The deployment names should match the models you deployed in Microsoft Foundry.")
        return

    # Map your deployed models to the models required by prebuilt analyzers
    # The dictionary keys are the model names required by the analyzers, and the values are
    # your actual deployment names. You can use the same name for both if you prefer.
    # At this point, all deployments are guaranteed to be non-None due to the check above
    assert gpt_4_1_deployment is not None
    assert gpt_4_1_mini_deployment is not None
    assert text_embedding_3_large_deployment is not None
    model_deployments: dict[str, str] = {
        "gpt-4.1": gpt_4_1_deployment,
        "gpt-4.1-mini": gpt_4_1_mini_deployment,
        "text-embedding-3-large": text_embedding_3_large_deployment,
    }

    print("Configuring model deployments...")
    updated_defaults = client.update_defaults(model_deployments=model_deployments)

    print("Model deployments configured successfully!")
    if updated_defaults.model_deployments:
        for model_name, deployment_name in updated_defaults.model_deployments.items():
            print(f"  {model_name}: {deployment_name}")
    # [END update_defaults]

    # [START get_defaults]
    print("\nRetrieving current model deployment settings...")
    defaults = client.get_defaults()

    print("\nCurrent model deployment mappings:")
    if defaults.model_deployments and len(defaults.model_deployments) > 0:
        for model_name, deployment_name in defaults.model_deployments.items():
            print(f"  {model_name}: {deployment_name}")
    else:
        print("  No model deployments configured yet.")
    # [END get_defaults]


if __name__ == "__main__":
    main()
