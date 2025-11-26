# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_delete_analyzer.py

DESCRIPTION:
    This sample demonstrates how to delete a custom analyzer.

    The delete_analyzer method permanently removes a custom analyzer from your resource.
    This operation cannot be undone.

    Important notes:
    - Only custom analyzers can be deleted. Prebuilt analyzers cannot be deleted.
    - Deleting an analyzer does not delete analysis results that were created using that analyzer.
    - Once deleted, the analyzer ID cannot be reused immediately.

USAGE:
    python sample_delete_analyzer.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).
"""

import os
import time

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()


def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    # [START create_simple_analyzer]
    # Generate a unique analyzer ID
    analyzer_id = f"my_analyzer_{int(time.time())}"

    print(f"Creating analyzer '{analyzer_id}'...")

    # Create a simple analyzer
    analyzer = ContentAnalyzer(
        base_analyzer_id="prebuilt-document",
        description="Simple analyzer for deletion example",
        config=ContentAnalyzerConfig(return_details=True),
        models={"completion": "gpt-4.1"},
    )

    poller = client.begin_create_analyzer(
        analyzer_id=analyzer_id,
        resource=analyzer,
    )
    poller.result()
    print(f"Analyzer '{analyzer_id}' created successfully.")
    # [END create_simple_analyzer]

    # [START delete_analyzer]
    print(f"Deleting analyzer '{analyzer_id}'...")
    client.delete_analyzer(analyzer_id=analyzer_id)
    print(f"Analyzer '{analyzer_id}' deleted successfully.")
    # [END delete_analyzer]


if __name__ == "__main__":
    main()
