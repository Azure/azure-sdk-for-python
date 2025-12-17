# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_analyze_invoice_async.py

DESCRIPTION:
    These tests validate the sample_analyze_invoice.py sample code (async version).

USAGE:
    pytest test_sample_analyze_invoice_async.py
"""

import os
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer_async import ContentUnderstandingPreparer, ContentUnderstandingClientTestBaseAsync
from azure.ai.contentunderstanding.models import AnalyzeInput, DocumentContent


class TestSampleAnalyzeInvoiceAsync(ContentUnderstandingClientTestBaseAsync):
    """Tests for sample_analyze_invoice.py (async version)"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_analyze_invoice_async(self, azure_content_understanding_endpoint: str, **kwargs) -> None:
        """Test analyzing an invoice document with prebuilt-invoice analyzer (async version).

        This test validates:
        1. Analyzing an invoice using prebuilt-invoice analyzer
        2. Extracting invoice-specific fields (CustomerName, InvoiceDate, TotalAmount, LineItems)
        3. Field confidence scores and source locations

        03_AnalyzeInvoice.AnalyzeInvoiceAsync()
        """
        client = self.create_async_client(endpoint=azure_content_understanding_endpoint)

        # Get the invoice file path (use sample_invoice.pdf from test_data)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_data_dir = os.path.join(os.path.dirname(current_dir), "test_data")
        invoice_path = os.path.join(test_data_dir, "sample_invoice.pdf")

        # Read the invoice file as binary data
        with open(invoice_path, "rb") as f:
            invoice_data = f.read()

        # Analyze the invoice
        poller = await client.begin_analyze(analyzer_id="prebuilt-invoice", inputs=[AnalyzeInput(data=invoice_data)])

        # Wait for analysis to complete
        result = await poller.result()

        # Assertions for operation
        assert poller is not None, "Analysis operation should not be null"
        print("[PASS] Analysis operation created successfully")

        # Verify raw response using getattr with type: ignore
        raw_response = getattr(poller, "_polling_method", None)
        if raw_response:
            initial_response = getattr(raw_response, "_initial_response", None)  # type: ignore
            if initial_response:
                status = getattr(initial_response, "status_code", None)
                if status:
                    assert 200 <= status < 300, f"Response status should be successful, but was {status}"
                    print(f"[PASS] Response status: {status}")

        # Assertions for result
        assert result is not None, "Analysis result should not be null"
        print("[PASS] Analysis result received")

        assert hasattr(result, "contents"), "Result should contain contents"
        contents = getattr(result, "contents", None)
        assert contents is not None, "Result contents should not be null"
        assert len(contents) > 0, "Result should have at least one content"
        assert len(contents) == 1, "Invoice should have exactly one content element"
        print(f"[PASS] Analysis result contains {len(contents)} content(s)")

        # Get the document content
        content = contents[0]
        assert content is not None, "Content should not be null"
        assert isinstance(content, DocumentContent), "Content should be of type DocumentContent"
        print("[PASS] Content is of type DocumentContent")

        # Verify basic document properties
        document_content = content
        start_page = getattr(document_content, "start_page_number", 1)
        end_page = getattr(document_content, "end_page_number", 1)

        assert start_page >= 1, "Start page should be >= 1"
        assert end_page >= start_page, "End page should be >= start page"
        total_pages = end_page - start_page + 1
        assert total_pages > 0, "Total pages should be positive"
        print(f"[PASS] Document has {total_pages} page(s) from {start_page} to {end_page}")

        # Print document unit information
        unit = getattr(document_content, "unit", None)
        if unit:
            print(f"[INFO] Document unit: {unit}")
        else:
            print("[INFO] Document unit: unknown")

        # Extract and verify fields
        fields = getattr(document_content, "fields", {})

        # Extract CustomerName field
        customer_name_field = fields.get("CustomerName")
        if customer_name_field:
            print("[PASS] CustomerName field found")

            value = getattr(customer_name_field, "value", None)
            if value:
                assert len(str(value)) > 0, "CustomerName value should not be empty when present"
                print(f"[INFO] Customer Name: {value}")

            confidence = getattr(customer_name_field, "confidence", None)
            if confidence is not None:
                assert 0 <= confidence <= 1, f"CustomerName confidence should be between 0 and 1, but was {confidence}"
                print(f"[INFO] CustomerName confidence: {confidence:.2f}")

            source = getattr(customer_name_field, "source", None)
            if source:
                print(f"[INFO] CustomerName source: {source}")

            spans = getattr(customer_name_field, "spans", None)
            if spans and len(spans) > 0:
                span = spans[0]
                offset = getattr(span, "offset", None)
                length = getattr(span, "length", None)
                if offset is not None and length is not None:
                    print(f"[INFO] CustomerName position in markdown: offset={offset}, length={length}")
        else:
            print("[INFO] CustomerName field not found in this document")

        # Extract InvoiceDate field
        invoice_date_field = fields.get("InvoiceDate")
        if invoice_date_field:
            print("[PASS] InvoiceDate field found")

            value = getattr(invoice_date_field, "value", None)
            if value:
                print(f"[INFO] Invoice Date: {value}")

            confidence = getattr(invoice_date_field, "confidence", None)
            if confidence is not None:
                assert 0 <= confidence <= 1, f"InvoiceDate confidence should be between 0 and 1"
                print(f"[INFO] InvoiceDate confidence: {confidence:.2f}")

            source = getattr(invoice_date_field, "source", None)
            if source:
                print(f"[INFO] InvoiceDate source: {source}")
        else:
            print("[INFO] InvoiceDate field not found in this document")

        # Extract TotalAmount field (object field with nested Amount and CurrencyCode)
        total_amount_field = fields.get("TotalAmount")
        if total_amount_field:
            print("[PASS] TotalAmount field found")

            # Try to extract nested fields if it's an object
            if hasattr(total_amount_field, "value") and isinstance(total_amount_field.value, dict):
                amount_obj = total_amount_field.value
                amount = amount_obj.get("Amount")
                currency = amount_obj.get("CurrencyCode", "$")

                if amount:
                    print(
                        f"[INFO] Total: {currency}{amount:.2f}"
                        if isinstance(amount, (int, float))
                        else f"[INFO] Total: {currency}{amount}"
                    )
            else:
                value = getattr(total_amount_field, "value", None)
                if value:
                    print(f"[INFO] Total Amount: {value}")

            confidence = getattr(total_amount_field, "confidence", None)
            if confidence is not None:
                print(f"[INFO] TotalAmount confidence: {confidence:.2f}")
        else:
            print("[INFO] TotalAmount field not found in this document")

        # Extract LineItems field (array field)
        line_items_field = fields.get("LineItems")
        if line_items_field:
            print("[PASS] LineItems field found")

            # Try to extract array items
            if hasattr(line_items_field, "value") and isinstance(line_items_field.value, list):
                items = line_items_field.value
                print(f"[INFO] Line Items ({len(items)}):")

                for i, item in enumerate(items[:5]):  # Show first 5 items
                    if isinstance(item, dict):
                        description = item.get("Description", "N/A")
                        quantity = item.get("Quantity", "N/A")
                        print(f"[INFO]   Item {i + 1}: {description} (Qty: {quantity})")

                if len(items) > 5:
                    print(f"[INFO]   ... and {len(items) - 5} more items")
            else:
                print("[INFO] LineItems format not as expected")
        else:
            print("[INFO] LineItems field not found in this document")

        await client.close()
        print("\n[SUCCESS] All test_sample_analyze_invoice_async assertions passed")
