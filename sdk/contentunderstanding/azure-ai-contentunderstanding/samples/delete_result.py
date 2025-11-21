# pylint: disable=line-too-long,useless-suppression

# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: analyze a document with prebuilt-invoice and delete the result.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python delete_result.py
"""

from __future__ import annotations
import asyncio
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalyzeInput
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


# ---------------------------------------------------------------------------
# Sample: Analyze document and delete the result
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Analyze an invoice document using prebuilt-invoice analyzer
# 3. Extract the operation ID from the analysis operation
# 4. Get the analysis result using the operation ID and verify accessibility
# 5. Delete the analysis result to free up storage
# 6. Verify deletion by confirming the result is no longer accessible (404 error)
#
# Note: Deleting results is useful for managing storage and cleaning up
# temporary analysis results that are no longer needed.


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    print(f"Using endpoint: {endpoint}")
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        await analyze_and_delete_result(client)

    # Manually close DefaultAzureCredential if it was used
    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


async def analyze_and_delete_result(client: ContentUnderstandingClient) -> None:
    """Analyze a document and demonstrate result deletion."""

    # Use a sample invoice document from GitHub
    file_url = (
        "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"
    )

    print("\n📄 Document Analysis Workflow")
    print("=" * 60)
    print(f"   Document URL: {file_url}")
    print(f"   Analyzer: prebuilt-invoice")
    print("=" * 60)

    try:
        # Step 1: Start the analysis operation
        print(f"\n🔍 Step 1: Starting document analysis...")
        poller = await client.begin_analyze(
            analyzer_id="prebuilt-invoice",
            inputs=[AnalyzeInput(url=file_url)],
        )

        # Extract the operation ID from the poller
        # The operation ID is used to track and manage the analysis operation
        operation_id = poller.operation_id

        if not operation_id:
            print("❌ Error: Could not extract operation ID from response")
            return

        print(f"✅ Analysis operation started")
        print(f"   Operation ID: {operation_id}")

        # Step 2: Wait for analysis to complete
        print(f"\n⏳ Step 2: Waiting for analysis to complete...")
        result = await poller.result()
        print(f"✅ Analysis completed successfully!")

        # Verify we can access the result before deletion (this is for demonstration only)
        print(f"\n🔍 Step 2.5: Verifying result accessibility before deletion...")
        try:
            status_before = await client._get_result(operation_id=operation_id)  # type: ignore[attr-defined]
            print(f"✅ Result accessible before deletion (status: {status_before.status})")
        except Exception as e:
            print(f"⚠️  Unexpected error accessing result before deletion: {e}")

        # Step 3: Display sample results from the analysis
        print(f"\n📊 Step 3: Analysis Results Summary")
        print("=" * 60)

        if result.contents and len(result.contents) > 0:
            content = result.contents[0]
            if content.fields:
                # Display a few key fields from the invoice
                fields_to_show = ["CustomerName", "InvoiceId", "InvoiceDate", "TotalAmount"]
                print("   Sample Fields:")
                for field_name in fields_to_show:
                    if field_name in content.fields:
                        field = content.fields[field_name]
                        if field_name == "TotalAmount" and hasattr(field, "value") and isinstance(field.value, dict):
                            # TotalAmount is an ObjectField with Amount and CurrencyCode
                            amount = field.value.get("Amount")
                            if amount and hasattr(amount, "value"):
                                print(f"   • {field_name}: {amount.value}")
                        elif hasattr(field, "value"):
                            print(f"   • {field_name}: {field.value}")

                print(f"   Total fields extracted: {len(content.fields)}")
            else:
                print("   No fields found in analysis result")
        else:
            print("   No content found in analysis result")

        print("=" * 60)

        # Step 4: Delete the analysis result
        print(f"\n🗑️  Step 4: Deleting analysis result...")
        print(f"   Operation ID: {operation_id}")

        await client.delete_result(operation_id=operation_id)
        print(f"✅ Analysis result deleted successfully!")

        # Step 5: Verify deletion by attempting to get the result again
        print(f"\n🔍 Step 5: Verifying deletion...")
        print(f"   Attempting to access the deleted result...")
        try:
            # Try to get the operation status after deletion (this is for demonstration only)
            deleted_status = await client._get_result(operation_id=operation_id)  # type: ignore[attr-defined]
            print("❌ Unexpected: Result still exists after deletion!")
        except Exception as delete_error:
            if isinstance(delete_error, ResourceNotFoundError):
                print(f"✅ Verification successful: Result properly deleted")
                print(f"   Error type: {type(delete_error).__name__}")
                if hasattr(delete_error, 'error') and delete_error.error:
                    print(f"   Code: {delete_error.error.code}")
                    print(f"   Message: {delete_error.error.message}")
                print(f"   ✓ Confirmed: Result is no longer accessible as expected")
            else:
                print(f"❌ Unexpected error type: {type(delete_error).__name__}")
                print(f"   Error details: {delete_error}")
                print(f"   Expected ResourceNotFoundError for deleted result")

        print("\n💡 Why delete results?")
        print("   • Free up storage space in your Content Understanding resource")
        print("   • Remove temporary or sensitive analysis results")
        print("   • Manage resource quotas and limits")
        print("   • Clean up test or development analysis operations")

        print("\n📋 Note: Deleting a result marks it for deletion.")
        print("   The result data will be permanently removed and cannot be recovered.")

    except Exception as e:
        print(f"\n❌ Error during analysis or deletion: {e}")
        print("\nThis error may occur if:")
        print("   - Default model deployments are not configured (run update_defaults.py)")
        print("   - The prebuilt-invoice analyzer is not available")
        print("   - The document URL is not accessible")
        print("   - You don't have permission to delete results")
        print("\nTroubleshooting steps:")
        print("   1. Run get_defaults.py to verify model deployments are configured")
        print("   2. Check that the document URL is accessible")
        print("   3. Verify you have permissions to analyze and delete results")
        print("   4. Ensure the endpoint and credentials are correct")
        raise


if __name__ == "__main__":
    asyncio.run(main())
