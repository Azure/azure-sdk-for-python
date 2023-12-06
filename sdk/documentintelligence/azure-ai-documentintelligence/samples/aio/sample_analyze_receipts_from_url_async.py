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
    https://aka.ms/azsdk/documentintelligence/receiptfieldschema

USAGE:
    python sample_analyze_receipts_from_url_async.py

    Set the environment variables with your own values before running the sample:
    1) DOCUMENTINTELLIGENCE_ENDPOINT - the endpoint to your Document Intelligence resource.
	2) DOCUMENTINTELLIGENCE_API_KEY - your Document Intelligence API key.
"""

import os
import asyncio


def format_price(price_dict):
    return "".join([f"{p}" for p in price_dict.values()])


async def analyze_receipts_from_url():
    # [START analyze_receipts_from_url]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

    endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
    key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]

    document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/documentintelligence/azure-ai-documentintelligence/samples/sample_forms/receipt/contoso-receipt.png"
    async with document_intelligence_client:
        poller = await document_intelligence_client.begin_analyze_document(
            "prebuilt-receipt", AnalyzeDocumentRequest(url_source=url)
        )
        receipts = await poller.result()
    # [END analyze_receipts_from_url]

    for idx, receipt in enumerate(receipts.documents):
        print(f"--------Analysis of receipt #{idx + 1}--------")
        print(f"Receipt type: {receipt.doc_type if receipt.doc_type else 'N/A'}")
        merchant_name = receipt.fields.get("MerchantName")
        if merchant_name:
            print(f"Merchant Name: {merchant_name.get('valueString')} has confidence: " f"{merchant_name.confidence}")
        transaction_date = receipt.fields.get("TransactionDate")
        if transaction_date:
            print(
                f"Transaction Date: {transaction_date.get('valueDate')} has confidence: "
                f"{transaction_date.confidence}"
            )
        if receipt.fields.get("Items"):
            print("Receipt items:")
            for idx, item in enumerate(receipt.fields.get("Items").get("valueArray")):
                print(f"...Item #{idx + 1}")
                item_description = item.get("valueObject").get("Description")
                if item_description:
                    print(
                        f"......Item Description: {item_description.get('valueString')} has confidence: "
                        f"{item_description.confidence}"
                    )
                item_quantity = item.get("valueObject").get("Quantity")
                if item_quantity:
                    print(
                        f"......Item Quantity: {item_quantity.get('valueString')} has confidence: "
                        f"{item_quantity.confidence}"
                    )
                item_total_price = item.get("valueObject").get("TotalPrice")
                if item_total_price:
                    print(
                        f"......Total Item Price: {format_price(item_total_price.get('valueCurrency'))} has confidence: "
                        f"{item_total_price.confidence}"
                    )
        subtotal = receipt.fields.get("Subtotal")
        if subtotal:
            print(f"Subtotal: {format_price(subtotal.get('valueCurrency'))} has confidence: {subtotal.confidence}")
        tax = receipt.fields.get("TotalTax")
        if tax:
            print(f"Total tax: {format_price(tax.get('valueCurrency'))} has confidence: {tax.confidence}")
        tip = receipt.fields.get("Tip")
        if tip:
            print(f"Tip: {format_price(tip.get('valueCurrency'))} has confidence: {tip.confidence}")
        total = receipt.fields.get("Total")
        if total:
            print(f"Total: {format_price(total.get('valueCurrency'))} has confidence: {total.confidence}")
        print("--------------------------------------")


async def main():
    await analyze_receipts_from_url()


if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError
    from dotenv import find_dotenv, load_dotenv

    try:
        load_dotenv(find_dotenv())
        asyncio.run(main())
    except HttpResponseError as error:
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
