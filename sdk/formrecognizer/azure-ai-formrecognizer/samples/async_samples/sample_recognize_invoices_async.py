# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_invoices_async.py

DESCRIPTION:
    This sample demonstrates how to recognize fields from invoices.

    See fields found on a invoice here:
    https://aka.ms/formrecognizer/invoicefields

USAGE:
    python sample_recognize_invoices_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
import asyncio


class RecognizeInvoiceSampleAsync(object):

    async def recognize_invoice(self):
        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                                            "..",  "..", "./sample_forms/forms/Invoice_1.pdf"))

        # [START recognize_invoices_async]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        async with FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        ) as form_recognizer_client:
            with open(path_to_sample_forms, "rb") as f:
                poller = await form_recognizer_client.begin_recognize_invoices(invoice=f, locale="en-US")
            invoices = await poller.result()

            for idx, invoice in enumerate(invoices):
                print("--------Recognizing invoice #{}--------".format(idx+1))
                vendor_name = invoice.fields.get("VendorName")
                if vendor_name:
                    print("Vendor Name: {} has confidence: {}".format(vendor_name.value, vendor_name.confidence))
                vendor_address = invoice.fields.get("VendorAddress")
                if vendor_address:
                    print("Vendor Address: {} has confidence: {}".format(vendor_address.value, vendor_address.confidence))
                customer_name = invoice.fields.get("CustomerName")
                if customer_name:
                    print("Customer Name: {} has confidence: {}".format(customer_name.value, customer_name.confidence))
                customer_address = invoice.fields.get("CustomerAddress")
                if customer_address:
                    print("Customer Address: {} has confidence: {}".format(customer_address.value, customer_address.confidence))
                customer_address_recipient = invoice.fields.get("CustomerAddressRecipient")
                if customer_address_recipient:
                    print("Customer Address Recipient: {} has confidence: {}".format(customer_address_recipient.value, customer_address_recipient.confidence))
                invoice_id = invoice.fields.get("InvoiceId")
                if invoice_id:
                    print("Invoice Id: {} has confidence: {}".format(invoice_id.value, invoice_id.confidence))
                invoice_date = invoice.fields.get("InvoiceDate")
                if invoice_date:
                    print("Invoice Date: {} has confidence: {}".format(invoice_date.value, invoice_date.confidence))
                invoice_total = invoice.fields.get("InvoiceTotal")
                if invoice_total:
                    print("Invoice Total: {} has confidence: {}".format(invoice_total.value, invoice_total.confidence))
                due_date = invoice.fields.get("DueDate")
                if due_date:
                    print("Due Date: {} has confidence: {}".format(due_date.value, due_date.confidence))
        # [END recognize_invoices_async]

async def main():
    sample = RecognizeInvoiceSampleAsync()
    await sample.recognize_invoice()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
