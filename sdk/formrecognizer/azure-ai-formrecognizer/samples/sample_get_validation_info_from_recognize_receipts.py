# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_validation_info_from_recognize_receipts.py

DESCRIPTION:
    This sample demonstrates how to output the information that will help with manually
    validating your output from recognize receipts.

USAGE:
    python sample_get_validation_info_from_recognize_receipts.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer subscription key
"""

import os


class GetValidationInfoFromRecognizeReceiptsSample(object):

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    def get_validation_info_from_recognize_receipts(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient
        form_recognizer_client = FormRecognizerClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key))
        with open("sample_forms/receipt/contoso-allinone.jpg", "rb") as f:
            poller = form_recognizer_client.begin_recognize_receipts(stream=f.read())
        receipts = poller.result()

        for idx, receipt in enumerate(receipts):
            print("--------Recognizing receipt #{}--------".format(idx))
            print("Total: {} (Confidence score of {}, based on text value '{}', with bounding box {})".format(
                receipt.total.value,
                receipt.total.confidence,
                receipt.total.value_data.text,
                ", ".join(["[{}, {}]".format(p.x, p.y) for p in receipt.total.value_data.bounding_box]),
            ))
            print("Merchant: {} (Confidence score of {}, based on text value '{}', with bounding box {})".format(
                receipt.merchant_name.value,
                receipt.merchant_name.confidence,
                receipt.merchant_name.value_data.text,
                ", ".join(["[{}, {}]".format(p.x, p.y) for p in receipt.merchant_name.value_data.bounding_box]),
            ))
            print("Transaction date: {} (Confidence score of {}, based on text value '{}', with bounding box {})".format(
                receipt.transaction_date.value,
                receipt.transaction_date.confidence,
                receipt.transaction_date.value_data.text,
                ", ".join(["[{}, {}]".format(p.x, p.y) for p in receipt.transaction_date.value_data.bounding_box]),
            ))
            print("--------------------------------------")


if __name__ == '__main__':
    sample = GetValidationInfoFromRecognizeReceiptsSample()
    sample.get_validation_info_from_recognize_receipts()
