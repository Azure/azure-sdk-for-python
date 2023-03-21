# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_receipts_from_url_async.py

DESCRIPTION:
    This sample demonstrates how to analyze and extract common fields from a receipt URL,
    using a pre-trained receipt model.

    See fields found on a receipt here:
    https://aka.ms/azsdk/formrecognizer/receiptfieldschema

USAGE:
    python sample_analyze_receipts_from_url_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
import asyncio


async def analyze_receipts_from_url_async():
    # [START analyze_receipts_from_url_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer.aio import DocumentAnalysisClient
    from azure.core.exceptions import HttpResponseError

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    async with document_analysis_client:
        url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/receipt/contoso-receipt.png"
        
        # The test is unstable in China cloud, we try to set the number of retries in the code to increase stability
        retry_times = 0
        while retry_times != 5 :
            try:
                # Begin analyze document from url, this sample test is unstable in China cloud.(We are testing sovereign cloud test)
                # Increasing the number of retries in the code until there is a better solution
                poller = await document_analysis_client.begin_analyze_document_from_url(
                    "prebuilt-receipt", document_url=url
                )
            except HttpResponseError as e:
                retry_times += 1
                # Print the known unstable errors
                print(e.message)
                continue
            else:
                break
        print("--------Retry times: {}--------".format(retry_times))
        receipts = await poller.result()

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
    # [END analyze_receipts_from_url_async]


async def main():
    await analyze_receipts_from_url_async()


if __name__ == "__main__":
    import sys
    from azure.core.exceptions import HttpResponseError
    try:
        asyncio.run(main())
    except HttpResponseError as error:
        print("For more information about troubleshooting errors, see the following guide: "
              "https://aka.ms/azsdk/python/formrecognizer/troubleshooting")
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
