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


class RecognizeReceiptsSampleAsync(object):

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    async def recognize_receipts(self):
        # TODO: this can be used as examples in sphinx
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormRecognizerClient
        form_recognizer_client = FormRecognizerClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key))
        with open("../sample_forms/receipt/contoso-allinone.jpg", "rb") as f:
            receipts = await form_recognizer_client.begin_recognize_receipts(stream=f.read())

        for idx, receipt in enumerate(receipts):
            print("--------Recognizing receipt #{}--------".format(idx))
            print("Total: {} with a confidence score of {})".format(
                receipt.total.value,
                receipt.total.confidence
            ))
            print("Merchant: {} with a confidence score of {})".format(
                receipt.merchant_name.value,
                receipt.merchant_name.confidence
            ))
            print("Transaction date: {} with a confidence score of {}".format(
                receipt.transaction_date.value,
                receipt.transaction_date.confidence
            ))
            print("--------------------------------------")
        await form_recognizer_client.close()


async def main():
    sample = RecognizeReceiptsSampleAsync()
    await sample.recognize_receipts()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
