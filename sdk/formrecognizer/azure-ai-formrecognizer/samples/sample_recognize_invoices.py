# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_invoices.py

DESCRIPTION:
    This sample demonstrates how to recognize fields from invoices.

    See fields found on a invoice here:
    https://aka.ms/formrecognizer/invoicefields

USAGE:
    python sample_recognize_invoices.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os


class RecognizeInvoiceSample(object):

    def recognize_invoice(self):
        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                                            "..", "./sample_forms/forms/Invoice_1.pdf"))

        # [START recognize_invoices]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        with open(path_to_sample_forms, "rb") as f:
            poller = form_recognizer_client.begin_recognize_invoices(invoice=f, locale="en-US")
        invoices = poller.result()

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
        # [END recognize_invoices]

    def recognize_invoice_by_attribute(self):
        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                                            "..", "./sample_forms/forms/Invoice_1.pdf"))

        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        with open(path_to_sample_forms, "rb") as f:
            poller = form_recognizer_client.begin_recognize_invoices(invoice=f, locale="en-US")
        invoices = poller.result()

        for idx, invoice in enumerate(invoices):
            print("--------Recognizing invoice #{}--------".format(idx+1))
            print("CustomerName: {} has confidence {}".format(invoice.fields.customer_name.value, invoice.fields.customer_name.confidence))
            print("CustomerId: {} has confidence {}".format(invoice.fields.customer_id.value, invoice.fields.customer_id.confidence))
            print("PurchaseOrder: {} has confidence {}".format(invoice.fields.purchase_order.value, invoice.fields.purchase_order.confidence))
            print("InvoiceId: {} has confidence {}".format(invoice.fields.invoice_id.value, invoice.fields.invoice_id.confidence))
            print("InvoiceDate: {} has confidence {}".format(invoice.fields.invoice_date.value, invoice.fields.invoice_date.confidence))
            print("DueDate: {} has confidence {}".format(invoice.fields.due_date.value, invoice.fields.due_date.confidence))
            print("VendorName: {} has confidence {}".format(invoice.fields.vendor_name.value, invoice.fields.vendor_name.confidence))
            print("VendorAddress: {} has confidence {}".format(invoice.fields.vendor_address.value, invoice.fields.vendor_address.confidence))
            print("VendorAddressRecipient: {} has confidence {}".format(invoice.fields.vendor_address_recipient.value, invoice.fields.vendor_address_recipient.confidence))
            print("CustomerAddress: {} has confidence {}".format(invoice.fields.customer_address.value, invoice.fields.customer_address.confidence))
            print("CustomerAddressRecipient: {} has confidence {}".format(invoice.fields.customer_address_recipient.value, invoice.fields.customer_address_recipient.confidence))
            print("BillingAddress: {} has confidence {}".format(invoice.fields.billing_address.value, invoice.fields.billing_address.confidence))
            print("BillingAddressRecipient: {} has confidence {}".format(invoice.fields.billing_address_recipient.value, invoice.fields.billing_address_recipient.confidence))
            print("ShippingAddress: {} has confidence {}".format(invoice.fields.shipping_address.value, invoice.fields.shipping_address.confidence))
            print("ShippingAddressRecipient: {} has confidence {}".format(invoice.fields.shipping_address_recipient.value, invoice.fields.shipping_address_recipient.confidence))
            print("SubTotal: {} has confidence {}".format(invoice.fields.sub_total.value, invoice.fields.sub_total.confidence))
            print("TotalTax: {} has confidence {}".format(invoice.fields.total_tax.value, invoice.fields.total_tax.confidence))
            print("InvoiceTotal: {} has confidence {}".format(invoice.fields.invoice_total.value, invoice.fields.invoice_total.confidence))
            print("PreviousUnpaidBalance: {} has confidence {}".format(invoice.fields.previous_unpaid_balance.value, invoice.fields.previous_unpaid_balance.confidence))
            print("AmountDue: {} has confidence {}".format(invoice.fields.amount_due.value, invoice.fields.amount_due.confidence))
            print("ServiceStartDate: {} has confidence {}".format(invoice.fields.service_start_date.value, invoice.fields.service_start_date.confidence))
            print("ServiceEndDate: {} has confidence {}".format(invoice.fields.service_end_date.value, invoice.fields.service_end_date.confidence))
            print("ServiceAddress: {} has confidence {}".format(invoice.fields.service_address.value, invoice.fields.service_address.confidence))
            print("ServiceAddressRecipient: {} has confidence {}".format(invoice.fields.service_address_recipient.value, invoice.fields.service_address_recipient.confidence))
            print("RemittanceAddress: {} has confidence {}".format(invoice.fields.remittance_address.value, invoice.fields.remittance_address.confidence))
            print("RemittanceAddressRecipient: {} has confidence {}".format(invoice.fields.remittance_address_recipient.value, invoice.fields.remittance_address_recipient.confidence))


if __name__ == '__main__':
    sample = RecognizeInvoiceSample()
    sample.recognize_invoice()
    sample.recognize_invoice_by_attribute()
