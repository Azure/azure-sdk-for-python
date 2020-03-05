# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


from ._models import (
    ExtractedReceipt,
    FieldValue,
    ReceiptFields,
    ReceiptItem,
    ReceiptItemField,
    TableCell,
    Table,
    ExtractedLayoutPage,
    CustomModel,
    LabeledCustomModel,
    ExtractedPage,
    ExtractedField,
)
from ._helpers import get_receipt_field_value


def prepare_receipt_result(response, include_raw):
    receipts = []
    read_result = response.analyze_result.read_results

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
                    read_result,
                    include_raw
                ),
                merchant_name=FieldValue._from_generated(
                    page.fields.get("MerchantName"),
                    read_result,
                    include_raw
                ),
                merchant_phone_number=FieldValue._from_generated(
                    page.fields.get("MerchantPhoneNumber"),
                    read_result,
                    include_raw
                ),
                receipt_type=FieldValue._from_generated(
                    page.fields.get("ReceiptType"),
                    read_result,
                    include_raw
                ),
                receipt_items=ReceiptItemField._from_generated(
                    page.fields.get("Items"),
                    response.analyze_result.read_results,
                    include_raw
                ),
                subtotal=FieldValue._from_generated(
                    page.fields.get("Subtotal"),
                    read_result,
                    include_raw
                ),
                tax=FieldValue._from_generated(
                    page.fields.get("Tax"),
                    read_result,
                    include_raw
                ),
                tip=FieldValue._from_generated(
                    page.fields.get("Tip"),
                    read_result,
                    include_raw
                ),
                total=FieldValue._from_generated(
                    page.fields.get("Total"),
                    read_result,
                    include_raw
                ),
                transaction_date=FieldValue._from_generated(
                    page.fields.get("TransactionDate"),
                    read_result,
                    include_raw
                ),
                transaction_time=FieldValue._from_generated(
                    page.fields.get("TransactionTime"),
                    read_result,
                    include_raw
                ),
            )
        )
        receipts.append(receipt)
    return receipts


def prepare_layout_result(response, include_raw):
    pages = []
    read_result = response.analyze_result.read_results

    for page in response.analyze_result.page_results:
        result_page = ExtractedLayoutPage(page_number=page.page, tables=[])
        for table in page.tables:
            my_table = [[None for x in range(table.columns)] for y in range(table.rows)]
            for cell in table.cells:
                my_table[cell.row_index][cell.column_index] = \
                    TableCell._from_generated(cell, read_result, include_raw)
            result_page.tables.append(Table(my_table))
        pages.append(result_page)
    return pages


def prepare_training_result(response):
    return CustomModel._from_generated(response)


def prepare_labeled_training_result(response):
    return LabeledCustomModel._from_generated(response)


def prepare_analyze_result(response, include_raw):
    pages = []
    read_result = response.analyze_result.read_results

    for page in response.analyze_result.page_results:
        try:
            result_page = ExtractedPage(page_number=page.page, tables=[], fields=[], form_type_id=page.cluster_id)
        except AttributeError:
            result_page = ExtractedPage(page_number=page.page, tables=[], fields=[])
        if page.tables:
            for table in page.tables:
                my_table = [[None for x in range(table.columns)] for y in range(table.rows)]
                for cell in table.cells:
                    my_table[cell.row_index][cell.column_index] = \
                        TableCell._from_generated(cell, read_result, include_raw)
                result_page.tables.append(Table(my_table))
        try:
            if page.key_value_pairs:
                for item in page.key_value_pairs:
                    extracted_field = ExtractedField._from_generated(item, read_result, include_raw)
                    result_page.fields.append(extracted_field)
            pages.append(result_page)
        except AttributeError:
            pass

    try:
        for idx, page in enumerate(response.analyze_result.document_results):
            if page.fields:
                pages[idx].fields = [
                    ExtractedField._from_labeled_generated((label, value), read_result, include_raw)
                    for label, value
                    in page.fields.items()
                ]
    except AttributeError:
        pass
    return pages
