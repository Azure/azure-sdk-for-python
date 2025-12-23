# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_invoice_async.py

DESCRIPTION:
    This sample demonstrates how to analyze an invoice from a URL using the prebuilt-invoice analyzer
    and extract structured fields from the result.

    ## About analyzing invoices

    Content Understanding provides a rich set of prebuilt analyzers that are ready to use without any
    configuration. These analyzers are powered by knowledge bases of thousands of real-world document
    examples, enabling them to understand document structure and adapt to variations in format and
    content.

    Prebuilt analyzers are ideal for:
    - Content ingestion in search and retrieval-augmented generation (RAG) workflows
    - Intelligent document processing (IDP) to extract structured data from common document types
    - Agentic flows as tools for extracting structured representations from input files

    ### The prebuilt-invoice analyzer

    The prebuilt-invoice analyzer is a domain-specific analyzer optimized for processing invoices,
    utility bills, sales orders, and purchase orders. It automatically extracts structured fields
    including:

    - Customer/Vendor information: Name, address, contact details
    - Invoice metadata: Invoice number, date, due date, purchase order number
    - Line items: Description, quantity, unit price, total for each item
    - Financial totals: Subtotal, tax amount, shipping charges, total amount
    - Payment information: Payment terms, payment method, remittance address

    The analyzer works out of the box with various invoice formats and requires no configuration.
    It's part of the financial documents category of prebuilt analyzers, which also includes:
    - prebuilt-receipt - Sales receipts from retail and dining establishments
    - prebuilt-creditCard - Credit card statements
    - prebuilt-bankStatement.us - US bank statements
    - prebuilt-check.us - US bank checks
    - prebuilt-creditMemo - Credit memos and refund documents

USAGE:
    python sample_analyze_invoice_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using prebuilt analyzers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_update_defaults.py for setup instructions.
"""

import asyncio
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeInput,
    AnalyzeResult,
    DocumentContent,
    ContentField,
    ArrayField,
    ObjectField,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        # [START analyze_invoice]
        # You can replace this URL with your own invoice file URL
        invoice_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/invoice.pdf"

        print("Analyzing invoice with prebuilt-invoice analyzer...")
        print(f"  URL: {invoice_url}\n")

        poller = await client.begin_analyze(
            analyzer_id="prebuilt-invoice",
            inputs=[AnalyzeInput(url=invoice_url)],
        )
        result: AnalyzeResult = await poller.result()
        # [END analyze_invoice]

        # [START extract_invoice_fields]
        if not result.contents or len(result.contents) == 0:
            print("No content found in the analysis result.")
            return

        # Get the document content (invoices are documents)
        document_content: DocumentContent = result.contents[0]  # type: ignore

        # Print document unit information
        # The unit indicates the measurement system used for coordinates in the source field
        print(f"Document unit: {document_content.unit or 'unknown'}")
        print(f"Pages: {document_content.start_page_number} to {document_content.end_page_number}")

        # Print page dimensions if available
        if document_content.pages and len(document_content.pages) > 0:
            page = document_content.pages[0]
            unit = document_content.unit or "units"
            print(f"Page dimensions: {page.width} x {page.height} {unit}")
        print()

        if not document_content.fields:
            print("No fields found in the analysis result.")
            return

        # Extract simple string fields
        customer_name_field = document_content.fields.get("CustomerName")
        print(f"Customer Name: {customer_name_field.value or '(None)' if customer_name_field else '(None)'}")
        if customer_name_field:
            print(f"  Confidence: {customer_name_field.confidence:.2f}" if customer_name_field.confidence else "  Confidence: N/A")
            print(f"  Source: {customer_name_field.source or 'N/A'}")
            if customer_name_field.spans and len(customer_name_field.spans) > 0:
                span = customer_name_field.spans[0]
                print(f"  Position in markdown: offset={span.offset}, length={span.length}")

        # Extract simple date field
        invoice_date_field = document_content.fields.get("InvoiceDate")
        print(f"Invoice Date: {invoice_date_field.value or '(None)' if invoice_date_field else '(None)'}")
        if invoice_date_field:
            print(f"  Confidence: {invoice_date_field.confidence:.2f}" if invoice_date_field.confidence else "  Confidence: N/A")
            print(f"  Source: {invoice_date_field.source or 'N/A'}")
            if invoice_date_field.spans and len(invoice_date_field.spans) > 0:
                span = invoice_date_field.spans[0]
                print(f"  Position in markdown: offset={span.offset}, length={span.length}")

        # Extract object fields (nested structures)
        total_amount_field = document_content.fields.get("TotalAmount")
        if isinstance(total_amount_field, ObjectField) and total_amount_field.value:
            amount_field = total_amount_field.value.get("Amount")
            currency_field = total_amount_field.value.get("CurrencyCode")
            amount = amount_field.value if amount_field else None
            currency = currency_field.value if currency_field else "$"
            print(f"\nTotal: {currency}{amount:.2f}" if isinstance(amount, (int, float)) else f"\nTotal: {currency}{amount}")
            print(f"  Confidence: {total_amount_field.confidence:.2f}" if total_amount_field.confidence else "  Confidence: N/A")  # type: ignore
            print(f"  Source: {total_amount_field.source or 'N/A'}")  # type: ignore

        # Extract array fields (collections like line items)
        line_items_field = document_content.fields.get("LineItems")
        if isinstance(line_items_field, ArrayField) and line_items_field.value:
            print(f"\nLine Items ({len(line_items_field.value)}):")
            for i, item in enumerate(line_items_field.value, 1):
                if isinstance(item, ObjectField) and item.value:
                    description_field = item.value.get("Description")
                    quantity_field = item.value.get("Quantity")
                    description = description_field.value if description_field else "N/A"
                    quantity = quantity_field.value if quantity_field else "N/A"
                    print(f"  Item {i}: {description} (Qty: {quantity})")
                    print(f"    Confidence: {item.confidence:.2f}" if item.confidence else "    Confidence: N/A")  # type: ignore
        # [END extract_invoice_fields]

        if not isinstance(credential, AzureKeyCredential):
            await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
