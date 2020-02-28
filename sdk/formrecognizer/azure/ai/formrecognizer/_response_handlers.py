# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


from ._models import ExtractedReceipt, FieldValue, ReceiptFields, ReceiptItem, ReceiptItemField, TableCell, Table


def get_pipeline_response(pipeline_response, _, response_headers):
    return pipeline_response


def get_receipt_field_value(field):
    if field is None:
        return field
    value = field.value_array or field.value_date or field.value_integer or field.value_number \
            or field.value_object or field.value_phone_number or field.value_string or field.value_time
    return value


def prepare_receipt_result(response, include_raw):
    receipts = []
    for page in response.analyze_result.document_results:
        receipt = ExtractedReceipt(
            merchant_address=get_receipt_field_value(page.fields.get("MerchantAddress")),
            merchant_name=get_receipt_field_value(page.fields.get("MerchantName")),
            merchant_phone_number=get_receipt_field_value(page.fields.get("MerchantPhoneNumber")),
            receipt_type=get_receipt_field_value(page.fields.get("ReceiptType")),
            receipt_items=ReceiptItem._from_generated(page.fields.get("Items")),
            subtotal=get_receipt_field_value(page.fields.get("Subtotal")),
            tax=get_receipt_field_value(page.fields.get("Tax")),
            tip=get_receipt_field_value(page.fields.get("Tip")),
            total=get_receipt_field_value(page.fields.get("Total")),
            transaction_date=get_receipt_field_value(page.fields.get("TransactionDate")),
            transaction_time=get_receipt_field_value(page.fields.get("TransactionTime")),
            fields=ReceiptFields(
                merchant_address=FieldValue._from_generated(
                    page.fields.get("MerchantAddress"),
                    response.analyze_result.read_results,
                    include_raw
                ),
                merchant_name=FieldValue._from_generated(
                    page.fields.get("MerchantName"),
                    response.analyze_result.read_results,
                    include_raw
                ),
                merchant_phone_number=FieldValue._from_generated(
                    page.fields.get("MerchantPhoneNumber"),
                    response.analyze_result.read_results,
                    include_raw
                ),
                receipt_type=FieldValue._from_generated(
                    page.fields.get("ReceiptType"),
                    response.analyze_result.read_results,
                    include_raw
                ),
                receipt_items=ReceiptItemField._from_generated(
                    page.fields.get("Items"),
                    response.analyze_result.read_results,
                    include_raw
                ),
                subtotal=FieldValue._from_generated(
                    page.fields.get("Subtotal"),
                    response.analyze_result.read_results,
                    include_raw
                ),
                tax=FieldValue._from_generated(
                    page.fields.get("Tax"),
                    response.analyze_result.read_results,
                    include_raw
                ),
                tip=FieldValue._from_generated(
                    page.fields.get("Tip"),
                    response.analyze_result.read_results,
                    include_raw
                ),
                total=FieldValue._from_generated(
                    page.fields.get("Total"),
                    response.analyze_result.read_results,
                    include_raw
                ),
                transaction_date=FieldValue._from_generated(
                    page.fields.get("TransactionDate"),
                    response.analyze_result.read_results,
                    include_raw
                ),
                transaction_time=FieldValue._from_generated(
                    page.fields.get("TransactionTime"),
                    response.analyze_result.read_results,
                    include_raw
                ),
            )
        )
        receipts.append(receipt)
    return receipts


def prepare_layout_result(response, include_raw):
    layouts = []
    pages = []
    for page in response.analyze_result.page_results:
        for table in page.tables:
            my_table = [[None for x in range(table.columns)] for y in range(table.rows)]
            for cell in table.cells:
                my_table[cell.row_index][cell.column_index] = TableCell._from_generated(cell)
            layouts.append(Table(my_table))
        pages.append(layouts)
