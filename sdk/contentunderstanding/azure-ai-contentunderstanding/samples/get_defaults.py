# pylint: disable=line-too-long,useless-suppression

# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: retrieve default model deployment settings for Content Understanding resource.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python get_defaults.py
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
# Sample: Retrieve default model deployment settings
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Retrieve the current default model deployment mappings
# 3. Display configured model deployments
# 4. Show which prebuilt analyzers are ready to use
#
# Note: Default model deployments must be configured using update_defaults
# before prebuilt analyzers can be used. See update_defaults.py sample.


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    print(f"Using endpoint: {endpoint}")
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        await get_deployment_settings(client)

    # Manually close DefaultAzureCredential if it was used
    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


async def get_deployment_settings(client: ContentUnderstandingClient) -> None:
    """Retrieve and display default model deployment settings."""

    print("\n📋 Retrieving default model deployment settings...")

    try:
        # Get the current default settings
        defaults = await client.get_defaults()

        print("\n✅ Successfully retrieved default settings")
        print("\nModel Deployment Mappings:")
        print("=" * 60)

        # Check if model deployments are configured
        if hasattr(defaults, "model_deployments") and defaults.model_deployments:
            # Display each model deployment mapping
            for model_name, deployment_name in defaults.model_deployments.items():
                print(f"   {model_name:<30} → {deployment_name}")

            print("=" * 60)

            # Provide context about what these models are used for
            print("\n💡 Model Usage:")
            if "gpt-4.1" in defaults.model_deployments:
                print("   • GPT-4.1: Used by most prebuilt analyzers")
                print("     (prebuilt-invoice, prebuilt-receipt, prebuilt-idDocument, etc.)")

            if "gpt-4.1-mini" in defaults.model_deployments:
                print("   • GPT-4.1-mini: Used by RAG analyzers")
                print("     (prebuilt-documentSearch, prebuilt-audioSearch, prebuilt-videoSearch)")

            if "text-embedding-3-large" in defaults.model_deployments:
                print("   • text-embedding-3-large: Used for semantic search and embeddings")

            print("\n✨ Your Content Understanding resource is configured!")
            print("   You can now use prebuilt analyzers that depend on these models.")

        else:
            print("   No model deployments configured")
            print("=" * 60)
            print("\n⚠️  Model deployments have not been configured yet.")
            print("\n   To use prebuilt analyzers, you need to:")
            print("   1. Deploy GPT-4.1, GPT-4.1-mini, and text-embedding-3-large in Azure AI Foundry")
            print("   2. Run the update_defaults.py sample to configure the mappings")
            print("   3. Run this sample again to verify the configuration")

    except Exception as e:
        print(f"\n❌ Error retrieving defaults: {e}")
        print("\nThis error may occur if:")
        print("   - The Content Understanding resource is not properly configured")
        print("   - You don't have permission to read resource settings")
        print("   - The endpoint URL is incorrect")
        print("\nTroubleshooting steps:")
        print("   1. Verify AZURE_CONTENT_UNDERSTANDING_ENDPOINT is correct")
        print("   2. Check your authentication credentials")
        print("   3. Ensure you have read permissions on the resource")
        raise


if __name__ == "__main__":
    asyncio.run(main())
