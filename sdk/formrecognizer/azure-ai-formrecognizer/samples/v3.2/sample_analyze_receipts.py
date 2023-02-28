# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_receipts.py

DESCRIPTION:
    This sample demonstrates how to analyze and extract common fields from receipts,
    using a pre-trained receipt model.

    See fields found on a receipt here:
    https://aka.ms/azsdk/formrecognizer/receiptfieldschema

USAGE:
    python sample_analyze_receipts.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os


def analyze_receipts():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "..",
            "./sample_forms/receipt/contoso-allinone.jpg",
        )
    )

    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import DocumentAnalysisClient

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    with open(path_to_sample_documents, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-receipt", document=f, locale="en-US"
        )
    receipts = poller.result()

    for idx, receipt in enumerate(receipts.documents):
        print("--------Analysis of receipt #{}--------".format(idx + 1))
        print("Receipt type: {}".format(receipt.doc_type or "N/A"))
        merchant_name = receipt.fields.get("MerchantName")
        if merchant_name:
            print(
                "Merchant Name: {} has confidence: {}".format(
                    merchant_name.value, merchant_name.confidence
                )
            )
        transaction_date = receipt.fields.get("TransactionDate")
        if transaction_date:
            print(
                "Transaction Date: {} has confidence: {}".format(
                    transaction_date.value, transaction_date.confidence
                )
            )
        if receipt.fields.get("Items"):
            print("Receipt items:")
            for idx, item in enumerate(receipt.fields.get("Items").value):
                print("...Item #{}".format(idx + 1))
                item_description = item.value.get("Description")
                if item_description:
                    print(
                        "......Item Description: {} has confidence: {}".format(
                            item_description.value, item_description.confidence
                        )
                    )
                item_quantity = item.value.get("Quantity")
                if item_quantity:
                    print(
                        "......Item Quantity: {} has confidence: {}".format(
                            item_quantity.value, item_quantity.confidence
                        )
                    )
                item_price = item.value.get("Price")
                if item_price:
                    print(
                        "......Individual Item Price: {} has confidence: {}".format(
                            item_price.value, item_price.confidence
                        )
                    )
                item_total_price = item.value.get("TotalPrice")
                if item_total_price:
                    print(
                        "......Total Item Price: {} has confidence: {}".format(
                            item_total_price.value, item_total_price.confidence
                        )
                    )
        subtotal = receipt.fields.get("Subtotal")
        if subtotal:
            print(
                "Subtotal: {} has confidence: {}".format(
                    subtotal.value, subtotal.confidence
                )
            )
        tax = receipt.fields.get("TotalTax")
        if tax:
            print("Total tax: {} has confidence: {}".format(tax.value, tax.confidence))
        tip = receipt.fields.get("Tip")
        if tip:
            print("Tip: {} has confidence: {}".format(tip.value, tip.confidence))
        total = receipt.fields.get("Total")
        if total:
            print("Total: {} has confidence: {}".format(total.value, total.confidence))
        print("--------------------------------------")


if __name__ == "__main__":
    import sys
    from azure.core.exceptions import HttpResponseError
    try:
        analyze_receipts()
    except HttpResponseError as error:
        print("For more information about troubleshooting errors, see the following guide: "
              "https://aka.ms/azsdk/python/formrecognizer/troubleshooting")
        # Examples of how to check an HttpResponseError
        # Check by error code:
        if error.error is not None:
            if error.error.code == "InvalidImage":
                print(f"Received an invalid image error: {error.error}")
                sys.exit(1)
        # If the inner error is None and then it is possible to check the message to get more information:
        if "Invalid request".casefold() in error.message.casefold():
            print(f"Uh-oh! Something unexpected happened: {error}")
            sys.exit(1)
        # Print the full error content:
        print(f"Received a different error: {error}")
