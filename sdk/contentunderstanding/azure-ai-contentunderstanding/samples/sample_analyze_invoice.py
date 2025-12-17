# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_invoice.py

DESCRIPTION:
    About extracting structured invoice fields:
    This sample demonstrates how to analyze an invoice from a URL using the prebuilt-invoice
    analyzer and extract structured fields (customer name, line items, totals, etc.) from the result.

USAGE:
    python sample_analyze_invoice.py

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
    ContentField,
    ArrayField,
    ObjectField,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()


def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    # [START analyze_invoice]
    invoice_url = (
        "https://github.com/Azure-Samples/azure-ai-content-understanding-assets/raw/refs/heads/main/docs/invoice.pdf"
    )

    print(f"Analyzing invoice with prebuilt-invoice analyzer...")
    print(f"  URL: {invoice_url}")

    poller = client.begin_analyze(
        analyzer_id="prebuilt-invoice",
        inputs=[AnalyzeInput(url=invoice_url)],
    )
    result: AnalyzeResult = poller.result()
    # [END analyze_invoice]

    # [START extract_invoice_fields]
    if not result.contents or len(result.contents) == 0:
        print("No content found in the analysis result.")
        return

    # Get the document content (invoices are documents)
    document_content: DocumentContent = result.contents[0]  # type: ignore

    # Print document unit information
    # The unit indicates the measurement system used for coordinates in the source field
    print(f"\nDocument unit: {document_content.unit or 'unknown'}")
    print(f"Pages: {document_content.start_page_number} to {document_content.end_page_number}")
    print()

    if not document_content.fields:
        print("No fields found in the analysis result.")
        return

    # Extract simple string fields
    customer_name_field = document_content.fields.get("CustomerName")
    invoice_date_field = document_content.fields.get("InvoiceDate")

    customer_name = customer_name_field.value if customer_name_field else None
    invoice_date = invoice_date_field.value if invoice_date_field else None

    print(f"Customer Name: {customer_name or '(None)'}")
    if customer_name_field:
        print(
            f"  Confidence: {customer_name_field.confidence:.2f}"
            if customer_name_field.confidence
            else "  Confidence: N/A"
        )
        # Source is an encoded identifier containing bounding box coordinates
        # Format: D(pageNumber, x1, y1, x2, y2, x3, y3, x4, y4)
        print(f"  Source: {customer_name_field.source or 'N/A'}")
        if customer_name_field.spans and len(customer_name_field.spans) > 0:
            span = customer_name_field.spans[0]
            print(f"  Position in markdown: offset={span.offset}, length={span.length}")

    print(f"Invoice Date: {invoice_date or '(None)'}")
    if invoice_date_field:
        print(
            f"  Confidence: {invoice_date_field.confidence:.2f}"
            if invoice_date_field.confidence
            else "  Confidence: N/A"
        )

    # Extract object field (TotalAmount contains Amount and CurrencyCode)
    total_amount_field = document_content.fields.get("TotalAmount")
    if total_amount_field and total_amount_field.value:
        total_amount_obj: dict[str, ContentField] = total_amount_field.value  # type: ignore
        amount_field = total_amount_obj.get("Amount")
        currency_field = total_amount_obj.get("CurrencyCode")

        amount = amount_field.value if amount_field else None
        currency = currency_field.value if currency_field else None

        print(f"\nTotal Amount: {amount} {currency}")
        if total_amount_field.confidence:
            print(f"  Confidence: {total_amount_field.confidence:.2f}")

    # Extract array field (LineItems - line items)
    # Note: The field name is "LineItems" (not "Items") to match the service response
    line_items_field = document_content.fields.get("LineItems")
    if line_items_field and isinstance(line_items_field, ArrayField) and line_items_field.value:
        items_array: list = line_items_field.value  # type: ignore
        print(f"\nLine Items ({len(items_array)}):")
        for i, item in enumerate(items_array, 1):
            # Each item in the array is a ContentField (ObjectField for line items)
            if isinstance(item, ObjectField) and item.value:
                item_dict: dict[str, ContentField] = item.value  # type: ignore
                description_field = item_dict.get("Description")
                quantity_field = item_dict.get("Quantity")
                # Try UnitPrice first, then Amount (matching .NET sample pattern)
                unit_price_field = item_dict.get("UnitPrice")
                amount_field = item_dict.get("Amount")

                description = description_field.value if description_field else "(no description)"
                quantity = quantity_field.value if quantity_field else "N/A"

                # Display price information - prefer UnitPrice if available, otherwise Amount
                # UnitPrice is an ObjectField with Amount and CurrencyCode sub-fields (like TotalAmount)
                price_info = ""
                if unit_price_field and isinstance(unit_price_field, ObjectField) and unit_price_field.value:
                    unit_price_obj: dict[str, ContentField] = unit_price_field.value  # type: ignore
                    unit_price_amount_field = unit_price_obj.get("Amount")
                    unit_price_currency_field = unit_price_obj.get("CurrencyCode")
                    if unit_price_amount_field and unit_price_amount_field.value is not None:
                        currency = unit_price_currency_field.value if unit_price_currency_field else ""
                        price_info = f"Unit Price: {unit_price_amount_field.value} {currency}".strip()
                elif amount_field and amount_field.value is not None:
                    price_info = f"Amount: {amount_field.value}"

                print(f"  {i}. {description}")
                print(f"     Quantity: {quantity}" + (f", {price_info}" if price_info else ""))
    # [END extract_invoice_fields]


if __name__ == "__main__":
    main()
