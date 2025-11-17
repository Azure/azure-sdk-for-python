# pylint: disable=line-too-long,useless-suppression

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
    python analyze_url_prebuilt_invoice.py
"""

from __future__ import annotations
import asyncio
import os


from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeInput,
    AnalyzeResult,
    ContentField,
    MediaContent,
)
from sample_helper import save_json_to_file
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
    print(f"Using endpoint: {endpoint}")
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        await analyze_invoice(client)

    # Manually close DefaultAzureCredential if it was used
    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


async def analyze_invoice(client: ContentUnderstandingClient) -> None:
    """Analyze an invoice and display the extracted fields."""
    file_url = (
        "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"
    )
    print(f"Analyzing invoice from {file_url} with prebuilt-invoice analyzer...")
    poller = await client.begin_analyze(analyzer_id="prebuilt-invoice", inputs=[AnalyzeInput(url=file_url)])
    result: AnalyzeResult = await poller.result()

    # AnalyzeResult contains the full analysis result and can be used to access various properties
    print("\nInvoice Analysis Result:")
    print("=" * 50)

    # A PDF file has only one content element even if it contains multiple pages
    content: MediaContent = result.contents[0]

    if not content.fields:
        print("No fields found in the analysis result")
        return

    print("\nSample Field Extractions:")
    print("-" * 40)

    # Example 1: Simple string fields
    # Note: Use .get() to check if field exists: field = content.fields.get("FieldName")
    # Use [] when field is known to exist (cleaner code)
    customer_name = content.fields["CustomerName"].value

    # TotalAmount is an ObjectField containing Amount and CurrencyCode fields
    total_amount_obj: dict[str, ContentField] | None = content.fields["TotalAmount"].value  # type: ignore[attr-defined]
    invoice_total = total_amount_obj["Amount"].value if total_amount_obj else None  # type: ignore[union-attr]

    invoice_date = content.fields["InvoiceDate"].value

    print(f"Customer Name: {customer_name or '(None)'}")
    print(f"Invoice Total: ${invoice_total or '(None)'}")
    print(f"Invoice Date: {invoice_date or '(None)'}")

    # Example 2: Array field (Items)
    items: list[ContentField] | None = content.fields["LineItems"].value  # type: ignore[attr-defined]
    print(f"\nInvoice Items (Array):")
    if items:
        for i, item in enumerate(items):
            # item is a ContentField (ObjectField at runtime), get its value
            item_obj: dict[str, Any] | None = item.value_object  # type: ignore[attr-defined]
            if item_obj:
                print(f"  Item {i + 1}:")

                # Extract fields from line item
                # Note: For nested field access, we use value_* attributes directly
                # to avoid type checker issues with dictionary value types
                description = item_obj["Description"].value_string  # type: ignore[attr-defined]
                quantity = item_obj["Quantity"].value_number  # type: ignore[attr-defined]

                # UnitPrice and TotalAmount are ObjectFields, extract Amount from them
                # Note: Some fields might be optional in some line items
                unit_price_field = item_obj.get("UnitPrice")
                if unit_price_field and hasattr(unit_price_field, 'value_object'):
                    unit_price_obj = unit_price_field.value_object  # type: ignore[attr-defined]
                    unit_price = unit_price_obj["Amount"].value_number if unit_price_obj else None  # type: ignore[attr-defined,union-attr]
                else:
                    unit_price = None

                total_amount_field = item_obj.get("TotalAmount")
                if total_amount_field and hasattr(total_amount_field, 'value_object'):
                    total_amount_obj_inner = total_amount_field.value_object  # type: ignore[attr-defined]
                    total_amount = total_amount_obj_inner["Amount"].value_number if total_amount_obj_inner else None  # type: ignore[attr-defined,union-attr]
                else:
                    total_amount = None

                print(f"    Description: {description or 'N/A'}")
                print(f"    Quantity: {quantity or 'N/A'}")
                print(f"    Unit Price: ${unit_price or 'N/A'}")
                print(f"    Total Amount: ${total_amount or 'N/A'}")
            else:
                print(f"  Item {i + 1}: No item object found")
    else:
        print("  No items found")

    print(f"\nTotal fields extracted: {len(content.fields)}")

    # Save the full result to JSON for detailed inspection
    save_json_to_file(
        result.as_dict(),
        filename_prefix="analyze_url_prebuilt_invoice",
    )
    print("Invoice fields saved to JSON file for detailed inspection")


if __name__ == "__main__":
    asyncio.run(main())

