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
    model deployments to function. The recommended models are:

    - gpt-5.2 - Completion model used by analyzers
    - text-embedding-3-large - Used for semantic search and embeddings

    Prebuilt analyzers also reference aliases. Configure these even when they map to the same
    deployments as the concrete model names:

    - prebuilt-analyzer-completion (most prebuilt analyzers, e.g. prebuilt-invoice)
    - prebuilt-analyzer-completion-mini (prebuilt-*Search analyzers)
    - prebuilt-analyzer-embedding (analyzers that require embeddings)

    This configuration is per Microsoft Foundry resource and persists across sessions.
    You only need to configure it once per Microsoft Foundry resource (or when you change
    deployment names).


    The service periodically adds support for more models, including the latest gpt-5.x models
    such as gpt-5.2, gpt-5.4-mini, gpt-5.5, and others. See the Content Understanding supported
    generative models documentation
    (https://learn.microsoft.com/azure/ai-services/content-understanding/service-limits#supported-generative-models)
    and the Foundry model retirement schedule
    (https://learn.microsoft.com/azure/foundry/openai/concepts/model-retirement-schedule)
    for current support and retirement details. For deployment guidance, see
    https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/models-deployments.

    ## Prerequisites

    To get started you'll need:

    1. An Azure subscription and a Microsoft Foundry resource. To create a Microsoft Foundry
       resource, follow the steps in the Azure Content Understanding quickstart
       (https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api?tabs=portal%2Cdocument).
       You must create your Microsoft Foundry resource in a region that supports Content Understanding.
       For available regions, see
       https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support.

    2. After creating your Microsoft Foundry resource, you must grant yourself the Cognitive Services
       User role to enable API calls for setting default model deployments. This role assignment
       is required even if you are the owner of the resource.

    3. Take note of your Microsoft Foundry resource endpoint and, if you plan to use key-based
       authentication, the API key. A typical endpoint looks like:
       https://your-foundry.services.ai.azure.com

    4. If you plan to use DefaultAzureCredential for authentication, you will need to log in to
       Azure first. Typically, you can do this by running az login (Azure CLI) or azd login
       (Azure Developer CLI) in your terminal.

    5. Deploy the following models in Microsoft Foundry
       (https://learn.microsoft.com/azure/ai-studio/how-to/deploy-models-openai):
       - gpt-5.2
       - text-embedding-3-large

    6. Take note of the deployment names used for each model. The convention is to use the model
       names (e.g., "gpt-5.2", "text-embedding-3-large"), but you can change these
       during deployment. You'll use these deployment names when configuring defaults.

USAGE:
    python sample_update_defaults.py

    Set the environment variables with your own values before running the sample:
     1) CONTENTUNDERSTANDING_ENDPOINT (required) - the endpoint to your Content Understanding resource.
       Example: https://your-foundry.services.ai.azure.com
     2) CONTENTUNDERSTANDING_KEY (optional) - your Content Understanding API key. When unset,
         DefaultAzureCredential is used. Use key-based authentication for testing only; use
       DefaultAzureCredential (recommended) for production.
     3) CU_COMPLETION_MODEL (optional) - your completion model name. Defaults to gpt-5.2.
     4) CU_COMPLETION_MODEL_MINI (optional) - your mini completion model name.
         Defaults to CU_COMPLETION_MODEL when unset.
     5) CU_COMPLETION_MODEL_DEPLOYMENT (required) - your completion model deployment name
         in Microsoft Foundry.
     6) CU_COMPLETION_MINI_DEPLOYMENT (optional) - deployment used for the mini completion model.
         Defaults to CU_COMPLETION_MODEL_DEPLOYMENT when unset.
     7) CU_EMBEDDING_MODEL (optional) - your embedding model name.
         Defaults to text-embedding-3-large.
     8) CU_EMBEDDING_DEPLOYMENT (required) - your embedding model deployment name
         in Microsoft Foundry.
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
    # Get the model name and deployment names from environment variables.
    completion_model = os.getenv("CU_COMPLETION_MODEL") or "gpt-5.2"
    mini_completion_model = os.getenv("CU_COMPLETION_MODEL_MINI") or completion_model
    embedding_model = os.getenv("CU_EMBEDDING_MODEL") or "text-embedding-3-large"
    completion_deployment = os.getenv("CU_COMPLETION_MODEL_DEPLOYMENT")
    mini_completion_deployment = os.getenv("CU_COMPLETION_MINI_DEPLOYMENT") or completion_deployment
    embedding_deployment = os.getenv("CU_EMBEDDING_DEPLOYMENT")

    missing_deployments = []
    if not completion_deployment:
        missing_deployments.append("CU_COMPLETION_MODEL_DEPLOYMENT")
    if not embedding_deployment:
        missing_deployments.append("CU_EMBEDDING_DEPLOYMENT")

    if missing_deployments:
        print("⚠️  Missing required environment variables:")
        for deployment in missing_deployments:
            print(f"   - {deployment}")
        print("\nPlease set these environment variables and try again.")
        print("The deployment names should match the models you deployed in Microsoft Foundry.")
        return

    assert completion_deployment is not None
    assert mini_completion_deployment is not None
    assert embedding_deployment is not None

    # Map concrete model names and prebuilt aliases to your deployments.
    model_deployments: dict[str, str] = {
        completion_model: completion_deployment,
        embedding_model: embedding_deployment,
        "prebuilt-analyzer-completion": completion_deployment,
        "prebuilt-analyzer-completion-mini": mini_completion_deployment,
        "prebuilt-analyzer-embedding": embedding_deployment,
    }
    if mini_completion_model != completion_model:
        model_deployments[mini_completion_model] = mini_completion_deployment

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
