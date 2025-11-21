# pylint: disable=line-too-long,useless-suppression

# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: configure default model deployments for Content Understanding resource.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    GPT_4_1_DEPLOYMENT                     (required) - Your GPT-4.1 deployment name in Azure AI Foundry
    GPT_4_1_MINI_DEPLOYMENT                (required) - Your GPT-4.1-mini deployment name in Azure AI Foundry
    TEXT_EMBEDDING_3_LARGE_DEPLOYMENT      (required) - Your text-embedding-3-large deployment name in Azure AI Foundry
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python update_defaults.py
"""

from __future__ import annotations
import asyncio
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


# ---------------------------------------------------------------------------
# Sample: Update default model deployments for Content Understanding resource
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Configure default model deployment mappings for the resource
# 3. Verify the configuration was applied successfully
# 4. Display the updated model deployment mappings
#
# Note: This configuration step is required ONCE per Azure Content Understanding resource
# before using prebuilt analyzers. It maps model names to your specific deployments.


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    print(f"Using endpoint: {endpoint}")
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        await update_model_deployments(client)

    # Manually close DefaultAzureCredential if it was used
    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


async def update_model_deployments(client: ContentUnderstandingClient) -> None:
    """Configure default model deployment mappings for the Content Understanding resource."""

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
        print("\n⚠️  Error: Missing required model deployment configuration(s):")
        for deployment in missing_deployments:
            print(f"   - {deployment}")
        print("\nPrebuilt analyzers require these model deployments to function correctly.")
        print("\nPlease complete the following steps:")
        print("1. Deploy GPT-4.1, GPT-4.1-mini, and text-embedding-3-large models in Azure AI Foundry")
        print("2. Add the following to your .env file in the samples directory:")
        print("   GPT_4_1_DEPLOYMENT=<your-gpt-4.1-deployment-name>")
        print("   GPT_4_1_MINI_DEPLOYMENT=<your-gpt-4.1-mini-deployment-name>")
        print("   TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=<your-text-embedding-3-large-deployment-name>")
        print("3. Run this sample again")
        return

    print("\n📋 Configuring default model deployments...")
    print(f"   GPT-4.1 deployment: {gpt_4_1_deployment}")
    print(f"   GPT-4.1-mini deployment: {gpt_4_1_mini_deployment}")
    print(f"   text-embedding-3-large deployment: {text_embedding_3_large_deployment}")

    try:
        # Update defaults to map model names to your deployments
        # The keys are the standard model names used by Content Understanding
        # The values are your deployment names in Azure AI Foundry
        result = await client.update_defaults(
            model_deployments={
                "gpt-4.1": gpt_4_1_deployment,
                "gpt-4.1-mini": gpt_4_1_mini_deployment,
                "text-embedding-3-large": text_embedding_3_large_deployment,
            }
        )

        print("\n✅ Default model deployments configured successfully!")
        print("\nModel Mappings:")
        print("=" * 60)

        # Display the configured mappings
        if hasattr(result, "model_deployments") and result.model_deployments:
            for model, deployment in result.model_deployments.items():
                print(f"   {model:<30} → {deployment}")
        else:
            print("   No model deployments returned in response")

        print("=" * 60)
        print("\n💡 These mappings are now configured for your Content Understanding resource.")
        print("   You can now use prebuilt analyzers like 'prebuilt-invoice' and 'prebuilt-receipt'.")

    except Exception as e:
        print(f"\n❌ Failed to configure defaults: {e}")
        print("\nThis error may occur if:")
        print("   - One or more deployment names don't exist in your Azure AI Foundry project")
        print("   - The deployments exist but use different names than specified")
        print("   - You don't have permission to update defaults for this resource")
        print("\nPlease verify:")
        print("   1. All three models are deployed in Azure AI Foundry")
        print("   2. The deployment names in your .env file match exactly")
        print("   3. You have the necessary permissions on the Content Understanding resource")
        raise


if __name__ == "__main__":
    asyncio.run(main())
