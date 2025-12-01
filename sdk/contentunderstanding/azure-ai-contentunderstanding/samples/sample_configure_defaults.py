# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_configure_defaults.py

DESCRIPTION:
    This sample demonstrates how to configure and retrieve default model deployment settings
    for your Microsoft Foundry resource. This is a required one-time setup before using
    prebuilt analyzers.

    Content Understanding prebuilt analyzers require specific GPT model deployments to function:
    - GPT-4.1: Used by most prebuilt analyzers (e.g., prebuilt-invoice, prebuilt-receipt)
    - GPT-4.1-mini: Used by RAG analyzers (e.g., prebuilt-documentSearch, prebuilt-audioSearch)
    - text-embedding-3-large: Used for semantic search and embeddings

USAGE:
    python sample_configure_defaults.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).
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
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
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
        return

    # Map your deployed models to the models required by prebuilt analyzers
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
            print(f"  {model_name} -> {deployment_name}")
    # [END update_defaults]

    # [START get_defaults]
    print("\nRetrieving current model deployment settings...")
    defaults = client.get_defaults()

    print("\nCurrent model deployment mappings:")
    if defaults.model_deployments and len(defaults.model_deployments) > 0:
        for model_name, deployment_name in defaults.model_deployments.items():
            print(f"  {model_name} -> {deployment_name}")
    else:
        print("  No model deployments configured yet.")
    # [END get_defaults]


if __name__ == "__main__":
    main()
