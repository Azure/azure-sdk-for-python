# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_delete_result.py

DESCRIPTION:
    This sample demonstrates how to delete analysis results using the delete_result API.
    This is useful for removing temporary or sensitive analysis results immediately, rather
    than waiting for automatic deletion after 24 hours.

    About deleting results:
    Analysis results from analyze or begin_analyze are automatically deleted after 24 hours.
    However, you may want to delete results earlier in certain cases:
    - Remove sensitive data immediately: Ensure sensitive information is not retained longer than necessary
    - Comply with data retention policies: Meet requirements for data deletion

    To delete results earlier than the 24-hour automatic deletion, use delete_result.
    This method requires the operation ID from the analysis operation.

    Important: Once deleted, results cannot be recovered. Make sure you have saved any data
    you need before deleting.

USAGE:
    python sample_delete_result.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using prebuilt analyzers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_update_defaults.py for setup instructions.
"""

import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeInput,
    AnalyzeResult,
    DocumentContent,
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

load_dotenv()


def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    # [START analyze_and_delete_result]
    # You can replace this URL with your own invoice file URL
    document_url = (
        "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/invoice.pdf"
    )

    # Step 1: Analyze and wait for completion
    analyze_operation = client.begin_analyze(
        analyzer_id="prebuilt-invoice",
        inputs=[AnalyzeInput(url=document_url)],
    )

    # Get the operation ID - this is needed to delete the result later
    operation_id = analyze_operation.operation_id
    print(f"Operation ID: {operation_id}")
    result: AnalyzeResult = analyze_operation.result()
    print("Analysis completed successfully!")

    # Display some sample results
    if result.contents and len(result.contents) > 0:
        document_content: DocumentContent = result.contents[0]  # type: ignore
        if document_content.fields:
            print(f"Total fields extracted: {len(document_content.fields)}")

    # Step 2: Delete the analysis result
    print(f"Deleting analysis result (Operation ID: {operation_id})...")
    client.delete_result(operation_id=operation_id)
    print("Analysis result deleted successfully!")

    # [END analyze_and_delete_result]


if __name__ == "__main__":
    main()
