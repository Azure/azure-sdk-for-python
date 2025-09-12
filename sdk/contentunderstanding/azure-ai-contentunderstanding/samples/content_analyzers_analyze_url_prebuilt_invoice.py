# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: use the prebuilt-invoice analyzer to extract invoice fields from a URL.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python content_analyzers_analyze_url_prebuilt_invoice.py
"""

from __future__ import annotations

import asyncio
import os


from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeResult,
    MediaContent,
)
from sample_helper import save_json_to_file, get_field_value
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


# ---------------------------------------------------------------------------
# Sample: Extract invoice fields from URL using begin_analyze API with prebuilt-invoice
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Analyze an invoice from a remote URL using begin_analyze with prebuilt-invoice analyzer
# 3. Save the complete analysis result to JSON file
# 4. Show examples of extracting different field types (string, number, object, array)


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    # Handle credential context manager conditionally
    if isinstance(credential, AzureKeyCredential):
        async with ContentUnderstandingClient(
            endpoint=endpoint, credential=credential
        ) as client:
            await analyze_invoice(client)
    else:
        async with ContentUnderstandingClient(
            endpoint=endpoint, credential=credential
        ) as client, credential:
            await analyze_invoice(client)


async def analyze_invoice(client: ContentUnderstandingClient) -> None:
    """Analyze an invoice and display the extracted fields."""
    file_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"
    print(f"🔍 Analyzing invoice from {file_url} with prebuilt-invoice analyzer...")
    poller = await client.content_analyzers.begin_analyze(
        analyzer_id="prebuilt-invoice", url=file_url
    )
    result: AnalyzeResult = await poller.result()

    # AnalyzeResult contains the full analysis result and can be used to access various properties
    print("\n📄 Invoice Analysis Result:")
    print("=" * 50)

    # A PDF file has only one content element even if it contains multiple pages
    content: MediaContent = result.contents[0]

    if not content.fields:
        print("No fields found in the analysis result")
        return

    print("\n📋 Sample Field Extractions:")
    print("-" * 40)

    # Example 1: Simple string fields
    customer_name = get_field_value(content.fields, "CustomerName")
    invoice_total = get_field_value(content.fields, "InvoiceTotal")
    invoice_date = get_field_value(content.fields, "InvoiceDate")

    print(f"Customer Name: {customer_name or '(None)'}")
    print(f"Invoice Total: ${invoice_total or '(None)'}")
    print(f"Invoice Date: {invoice_date or '(None)'}")

    # Example 2: Array field (Items)
    items = get_field_value(content.fields, "Items")
    print(f"\n🛒 Invoice Items (Array):")
    if items:
        for i, item in enumerate(items):
            # item is an ObjectField, extract its valueObject
            item_obj = item["valueObject"]
            if item_obj:
                print(f"  Item {i + 1}:")

                # Extract common item fields using helper function
                description = get_field_value(item_obj, "Description")
                quantity = get_field_value(item_obj, "Quantity")
                unit_price = get_field_value(item_obj, "UnitPrice")
                total_price = get_field_value(item_obj, "TotalPrice")

                print(f"    Description: {description or 'N/A'}")
                print(f"    Quantity: {quantity or 'N/A'}")
                print(f"    Unit Price: ${unit_price or 'N/A'}")
                print(f"    Total Price: ${total_price or 'N/A'}")
            else:
                print(f"  Item {i + 1}: No item object found")
    else:
        print("  No items found")

    print(f"\n📄 Total fields extracted: {len(content.fields)}")

    # Save the full result to JSON for detailed inspection
    save_json_to_file(
        result.as_dict(),
        filename_prefix="content_analyzers_analyze_url_prebuilt_invoice",
    )
    print("✅ Invoice fields saved to JSON file for detailed inspection")


if __name__ == "__main__":
    asyncio.run(main())
