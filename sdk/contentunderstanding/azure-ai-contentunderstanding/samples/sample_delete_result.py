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

    Analysis results are stored temporarily and can be deleted using the delete_result API:
    - Immediate deletion: Results are marked for deletion and permanently removed
    - Automatic deletion: Results are automatically deleted after 24 hours if not manually deleted
    - Operation ID required: You need the operation ID from the analysis operation to delete

    Important: Once deleted, results cannot be recovered. Make sure you have saved any data
    you need before deleting.

USAGE:
    python sample_delete_result.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using prebuilt analyzers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_configure_defaults.py for setup instructions.
"""

import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeInput,
    AnalyzeResult,
    DocumentContent,
    MediaContentKind,
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
    document_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"

    print("Document Analysis Workflow")
    print("=" * 60)
    print(f"  Document URL: {document_url}")
    print(f"  Analyzer: prebuilt-invoice")
    print("=" * 60)

    # Step 1: Start the analysis operation
    print("\nStep 1: Starting document analysis...")
    poller = client.begin_analyze(
        analyzer_id="prebuilt-invoice",
        inputs=[AnalyzeInput(url=document_url)],
    )

    # Get the operation ID from the poller
    operation_id = poller.operation_id

    if not operation_id:
        print("Error: Could not extract operation ID from response")
        return

    print(f"  Operation ID: {operation_id}")

    # Wait for completion
    print("  Waiting for analysis to complete...")
    result: AnalyzeResult = poller.result()
    print("Analysis completed successfully!")

    # Display some sample results
    if result.contents and len(result.contents) > 0:
        content = result.contents[0]
        if content.kind == MediaContentKind.DOCUMENT:
            doc_content: DocumentContent = content  # type: ignore
            if doc_content.fields:
                print(f"  Total fields extracted: {len(doc_content.fields)}")
                customer_name_field = doc_content.fields.get("CustomerName")
                if customer_name_field:
                    print(f"  Customer Name: {customer_name_field.value or '(not found)'}")

    # Step 2: Delete the analysis result
    print(f"\nStep 2: Deleting analysis result (Operation ID: {operation_id})...")
    client.delete_result(operation_id=operation_id)
    print("Analysis result deleted successfully!")

    # Verify deletion by trying to get the result (should fail)
    print("\nStep 3: Verifying deletion...")
    try:
        # Try to get the result - this should fail after deletion
        client._get_result(operation_id=operation_id)  # type: ignore[attr-defined]
        print("  Warning: Result still accessible (may take time to propagate)")
    except ResourceNotFoundError:
        print("  Verified: Result is no longer accessible (404 Not Found)")
    except Exception as e:
        print(f"  Result access check: {type(e).__name__}: {e}")
    # [END analyze_and_delete_result]


if __name__ == "__main__":
    main()
