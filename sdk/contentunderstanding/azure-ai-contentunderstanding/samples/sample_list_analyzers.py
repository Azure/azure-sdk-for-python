# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_list_analyzers.py

DESCRIPTION:
    This sample demonstrates how to list all available analyzers in your Microsoft Foundry
    resource, including both prebuilt and custom analyzers.

    The list_analyzers method returns all analyzers in your resource, including:
    - Prebuilt analyzers: System-provided analyzers like prebuilt-documentSearch, prebuilt-invoice
    - Custom analyzers: Analyzers you've created

    This is useful for:
    - Discovery: See what analyzers are available in your resource
    - Management: Get an overview of all your custom analyzers
    - Debugging: Verify that analyzers were created successfully

USAGE:
    python sample_list_analyzers.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).
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

    # [START list_analyzers]
    print("Listing all available analyzers...")

    # List all analyzers
    analyzers = list(client.list_analyzers())

    print(f"Found {len(analyzers)} analyzer(s)")

    # Display summary
    prebuilt_count = sum(1 for a in analyzers if a.analyzer_id and a.analyzer_id.startswith("prebuilt-"))
    custom_count = len(analyzers) - prebuilt_count
    print(f"  Prebuilt analyzers: {prebuilt_count}")
    print(f"  Custom analyzers: {custom_count}")

    # Display details for each analyzer
    for analyzer in analyzers:
        print(f"  ID: {analyzer.analyzer_id}")
        print(f"  Description: {analyzer.description or '(none)'}")
        print(f"  Status: {analyzer.status}")

        if analyzer.analyzer_id and analyzer.analyzer_id.startswith("prebuilt-"):
            print("  Type: Prebuilt analyzer")
        else:
            print("  Type: Custom analyzer")

        # Show tags if available
        if analyzer.tags:
            tags_str = ", ".join(f"{k}={v}" for k, v in analyzer.tags.items())
            print(f"  Tags: {tags_str}")

        print()
    print("=" * 60)
    # [END list_analyzers]


if __name__ == "__main__":
    main()
