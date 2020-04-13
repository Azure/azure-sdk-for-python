# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_receipts_async.py

DESCRIPTION:
    This sample demonstrates how to analyze receipts from a file.

USAGE:
    python sample_recognize_receipts_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer subscription key
"""

import os
import asyncio
from pathlib import Path


class RecognizeReceiptsSampleAsync(object):

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    async def recognize_receipts(self):
        # the sample forms are located in this file's parent's parent's files.
        path_to_sample_forms = Path(__file__).parent.parent.absolute() / Path("sample_forms/receipt/contoso-allinone.jpg")
        # TODO: this can be used as examples in sphinx
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormRecognizerClient
        async with FormRecognizerClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key)) as form_recognizer_client:

            with open(path_to_sample_forms, "rb") as f:
                receipts = await form_recognizer_client.recognize_receipts(stream=f.read())

            for idx, receipt in enumerate(receipts):
                print("--------Recognizing receipt #{}--------".format(idx))
                print("Receipt Type: {}\nconfidence: {}\n".format(receipt.receipt_type.type, receipt.receipt_type.confidence))
                print("Merchant Name: {}\nconfidence: {}\n".format(receipt.merchant_name.value, receipt.merchant_name.confidence))
                print("Transaction Date: {}\nconfidence: {}\n".format(receipt.transaction_date.value, receipt.transaction_date.confidence))
                print("Receipt items:")
                for item in receipt.receipt_items:
                    print("Item Name: {}\nconfidence: {}".format(item.name.value, item.name.confidence))
                    print("Item Quantity: {}\nconfidence: {}".format(item.quantity.value, item.quantity.confidence))
                    print("Total Price: {}\nconfidence: {}\n".format(item.total_price.value, item.total_price.confidence))
                print("Subtotal: {}\nconfidence: {}\n".format(receipt.subtotal.value, receipt.subtotal.confidence))
                print("Tax: {}\nconfidence: {}\n".format(receipt.tax.value, receipt.tax.confidence))
                print("Tip: {}\nconfidence: {}\n".format(receipt.tip.value, receipt.tip.confidence))
                print("Total: {}\nconfidence: {}\n".format(receipt.total.value, receipt.total.confidence))
                print("--------------------------------------")


async def main():
    sample = RecognizeReceiptsSampleAsync()
    await sample.recognize_receipts()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
