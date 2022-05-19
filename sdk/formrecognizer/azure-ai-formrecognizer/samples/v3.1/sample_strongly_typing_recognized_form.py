# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_strongly_typed_recognized_form.py

DESCRIPTION:
    This sample demonstrates how to use the fields in your recognized forms to create an object with
    strongly-typed fields. The pre-trained receipt method will be used to illustrate this sample, but
    note that a similar approach can be used for any custom form as long as you properly update the
    fields' names and types.

    See fields found on a receipt here:
    https://aka.ms/formrecognizer/receiptfields

USAGE:
    python sample_strongly_typed_recognized_form.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
from azure.ai.formrecognizer import FormField


class Receipt(object):
    """Creates a strongly-typed Receipt class from the fields returned in a RecognizedForm.
    If a specific field is not found on the receipt, it will return None.

    See fields found on a receipt here:
    https://aka.ms/formrecognizer/receiptfields
    """

    def __init__(self, form):
        self.receipt_type = form.fields.get("ReceiptType", FormField())
        self.merchant_name = form.fields.get("MerchantName", FormField())
        self.merchant_address = form.fields.get("MerchantAddress", FormField())
        self.merchant_phone_number = form.fields.get("MerchantPhoneNumber", FormField())
        self.receipt_items = self.convert_to_receipt_item(form.fields.get("Items", FormField()))
        self.subtotal = form.fields.get("Subtotal", FormField())
        self.tax = form.fields.get("Tax", FormField())
        self.tip = form.fields.get("Tip", FormField())
        self.total = form.fields.get("Total", FormField())
        self.transaction_date = form.fields.get("TransactionDate", FormField())
        self.transaction_time = form.fields.get("TransactionTime", FormField())

    def convert_to_receipt_item(self, items):
        """Converts Items in a receipt to a list of strongly-typed ReceiptItem
        """
        if items is None:
            return []
        return [ReceiptItem(item) for item in items.value]


class ReceiptItem(object):
    """Creates a strongly-typed ReceiptItem for every receipt item found in a RecognizedForm
    """

    def __init__(self, item):
        self.name = item.value.get("Name", FormField())
        self.quantity = item.value.get("Quantity", FormField())
        self.price = item.value.get("Price", FormField())
        self.total_price = item.value.get("TotalPrice", FormField())


class StronglyTypedRecognizedFormSample(object):

    def strongly_typed_receipt(self):
        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "./sample_forms/receipt/contoso-allinone.jpg"))

        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        with open(path_to_sample_forms, "rb") as f:
            poller = form_recognizer_client.begin_recognize_receipts(receipt=f)
        receipts = poller.result()

        for receipt in receipts:
            receipt = Receipt(receipt)
            print("Receipt Type: {} has confidence: {}".format(receipt.receipt_type.value, receipt.receipt_type.confidence))
            print("Merchant Name: {} has confidence: {}".format(receipt.merchant_name.value, receipt.merchant_name.confidence))
            print("Transaction Date: {} has confidence: {}".format(receipt.transaction_date.value, receipt.transaction_date.confidence))
            print("Receipt items:")
            for item in receipt.receipt_items:
                print("...Item Name: {} has confidence: {}".format(item.name.value, item.name.confidence))
                print("...Item Quantity: {} has confidence: {}".format(item.quantity.value, item.quantity.confidence))
                print("...Individual Item Price: {} has confidence: {}".format(item.price.value, item.price.confidence))
                print("...Total Item Price: {} has confidence: {}".format(item.total_price.value, item.total_price.confidence))
            print("Subtotal: {} has confidence: {}".format(receipt.subtotal.value, receipt.subtotal.confidence))
            print("Tax: {} has confidence: {}".format(receipt.tax.value, receipt.tax.confidence))
            print("Tip: {} has confidence: {}".format(receipt.tip.value, receipt.tip.confidence))
            print("Total: {} has confidence: {}".format(receipt.total.value, receipt.total.confidence))


if __name__ == '__main__':
    sample = StronglyTypedRecognizedFormSample()
    sample.strongly_typed_receipt()
