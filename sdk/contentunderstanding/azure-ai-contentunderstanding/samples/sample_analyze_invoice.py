# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_invoice.py

DESCRIPTION:
    This sample demonstrates how to analyze an invoice from a URL using the prebuilt-invoice
    analyzer and extract structured fields from the result.

    Content Understanding provides 70+ production-ready prebuilt analyzers that are ready to use
    without any training or configuration. The prebuilt-invoice analyzer automatically extracts:
    - Customer/Vendor information: Name, address, contact details
    - Invoice metadata: Invoice number, date, due date, purchase order number
    - Line items: Description, quantity, unit price, total for each item
    - Financial totals: Subtotal, tax amount, shipping charges, total amount
    - Payment information: Payment terms, payment method, remittance address

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
    MediaContentKind,
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
    invoice_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"

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

    content = result.contents[0]

    # Get the document content (invoices are documents)
    if content.kind == MediaContentKind.DOCUMENT:
        document_content: DocumentContent = content  # type: ignore

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
            print(f"  Confidence: {customer_name_field.confidence:.2f}" if customer_name_field.confidence else "  Confidence: N/A")
            # Source is an encoded identifier containing bounding box coordinates
            # Format: D(pageNumber, x1, y1, x2, y2, x3, y3, x4, y4)
            print(f"  Source: {customer_name_field.source or 'N/A'}")
            if customer_name_field.spans and len(customer_name_field.spans) > 0:
                span = customer_name_field.spans[0]
                print(f"  Position in markdown: offset={span.offset}, length={span.length}")

        print(f"Invoice Date: {invoice_date or '(None)'}")
        if invoice_date_field:
            print(f"  Confidence: {invoice_date_field.confidence:.2f}" if invoice_date_field.confidence else "  Confidence: N/A")

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

        # Extract array field (Items - line items)
        items_field = document_content.fields.get("Items")
        if items_field and items_field.value:
            items_array: list = items_field.value  # type: ignore
            print(f"\nLine Items ({len(items_array)}):")
            for i, item in enumerate(items_array, 1):
                if isinstance(item, dict):
                    description_field = item.get("Description")
                    quantity_field = item.get("Quantity")
                    amount_field = item.get("Amount")

                    description = description_field.value if description_field else "(no description)"
                    quantity = quantity_field.value if quantity_field else "N/A"
                    amount = amount_field.value if amount_field else "N/A"

                    print(f"  {i}. {description}")
                    print(f"     Quantity: {quantity}, Amount: {amount}")
    # [END extract_invoice_fields]


if __name__ == "__main__":
    main()
