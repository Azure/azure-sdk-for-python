# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._models import ExtractedReceipt

def get_pipeline_response(pipeline_response, _, response_headers):
    return pipeline_response


def get_receipt_field_value(field):
    if field is None:
        return field

    value = field.value_array or field.value_date or field.value_integer or field.value_number \
            or field.value_object or field.value_phone_number or field.value_string or field.value_time
    return value

def prepare_receipt_result(response):

    receipt = ExtractedReceipt(
        merchant_address=get_receipt_field_value(response.analyze_result.document_results[0].fields.get("MerchantAddress")),
        merchant_name=get_receipt_field_value(response.analyze_result.document_results[0].fields.get("MerchantName")),
        merchant_phone_number=get_receipt_field_value(response.analyze_result.document_results[0].fields.get("MerchantPhoneNumber")),
        receipt_type=get_receipt_field_value(response.analyze_result.document_results[0].fields.get("ReceiptType")),
        receipt_items=get_receipt_field_value(response.analyze_result.document_results[0].fields.get("Items")),
        subtotal=get_receipt_field_value(response.analyze_result.document_results[0].fields.get("Subtotal")),
        tax=get_receipt_field_value(response.analyze_result.document_results[0].fields.get("Tax")),
        tip=get_receipt_field_value(response.analyze_result.document_results[0].fields.get("Tip")),
        total=get_receipt_field_value(response.analyze_result.document_results[0].fields.get("Total")),
        transaction_date=get_receipt_field_value(response.analyze_result.document_results[0].fields.get("TransactionDate")),
        transaction_time=get_receipt_field_value(response.analyze_result.document_results[0].fields.get("TransactionTime")),
        fields=None
    )
    return receipt
