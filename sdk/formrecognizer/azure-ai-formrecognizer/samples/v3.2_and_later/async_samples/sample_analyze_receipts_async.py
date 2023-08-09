# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_receipts_async.py

DESCRIPTION:
    This sample demonstrates how to analyze and extract common fields from receipts,
    using a pre-trained receipt model.

    See fields found on a receipt here:
    https://aka.ms/azsdk/formrecognizer/receiptfieldschema

USAGE:
    python sample_analyze_receipts_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
import asyncio


async def analyze_receipts_async():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "..",
            "..",
            "./sample_forms/receipt/contoso-allinone.jpg",
        )
    )

    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer.aio import DocumentAnalysisClient

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    async with document_analysis_client:
        with open(path_to_sample_documents, "rb") as f:
            poller = await document_analysis_client.begin_analyze_document(
                "prebuilt-receipt", document=f, locale="en-US"
            )
        receipts = await poller.result()

    for idx, receipt in enumerate(receipts.documents):
        print(f"--------Analysis of receipt #{idx + 1}--------")
        print(f"Receipt type: {receipt.doc_type if receipt.doc_type else 'N/A'}")
        merchant_name = receipt.fields.get("MerchantName")
        if merchant_name:
            print(
                f"Merchant Name: {merchant_name.value} has confidence: "
                f"{merchant_name.confidence}"
            )
        transaction_date = receipt.fields.get("TransactionDate")
        if transaction_date:
            print(
                f"Transaction Date: {transaction_date.value} has confidence: "
                f"{transaction_date.confidence}"
            )
        if receipt.fields.get("Items"):
            print("Receipt items:")
            for idx, item in enumerate(receipt.fields.get("Items").value):
                print(f"...Item #{idx + 1}")
                item_description = item.value.get("Description")
                if item_description:
                    print(
                        f"......Item Description: {item_description.value} has confidence: "
                        f"{item_description.confidence}"
                    )
                item_quantity = item.value.get("Quantity")
                if item_quantity:
                    print(
                        f"......Item Quantity: {item_quantity.value} has confidence: "
                        f"{item_quantity.confidence}"
                    )
                item_price = item.value.get("Price")
                if item_price:
                    print(
                        f"......Individual Item Price: {item_price.value} has confidence: "
                        f"{item_price.confidence}"
                    )
                item_total_price = item.value.get("TotalPrice")
                if item_total_price:
                    print(
                        f"......Total Item Price: {item_total_price.value} has confidence: "
                        f"{item_total_price.confidence}"
                    )
        subtotal = receipt.fields.get("Subtotal")
        if subtotal:
            print(f"Subtotal: {subtotal.value} has confidence: {subtotal.confidence}")
        tax = receipt.fields.get("TotalTax")
        if tax:
            print(f"Total tax: {tax.value} has confidence: {tax.confidence}")
        tip = receipt.fields.get("Tip")
        if tip:
            print(f"Tip: {tip.value} has confidence: {tip.confidence}")
        total = receipt.fields.get("Total")
        if total:
            print(f"Total: {total.value} has confidence: {total.confidence}")
        print("--------------------------------------")


async def main():
    await analyze_receipts_async()


if __name__ == "__main__":
    import sys
    from azure.core.exceptions import HttpResponseError

    try:
        asyncio.run(main())
    except HttpResponseError as error:
        print(
            "For more information about troubleshooting errors, see the following guide: "
            "https://aka.ms/azsdk/python/formrecognizer/troubleshooting"
        )
        # Examples of how to check an HttpResponseError
        # Check by error code:
        if error.error is not None:
            if error.error.code == "InvalidImage":
                print(f"Received an invalid image error: {error.error}")
            if error.error.code == "InvalidRequest":
                print(f"Received an invalid request error: {error.error}")
            # Raise the error again after printing it
            raise
        # If the inner error is None and then it is possible to check the message to get more information:
        if "Invalid request".casefold() in error.message.casefold():
            print(f"Uh-oh! Seems there was an invalid request: {error}")
        # Raise the error again
        raise
