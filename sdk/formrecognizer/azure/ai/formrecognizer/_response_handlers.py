# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


from ._models import ExtractedReceipt, FieldValue, ReceiptFields, ReceiptItem, ReceiptItemField, TableCell, Table, ExtractedLayoutPage, CustomModel, LabeledCustomModel, ExtractedPage, ExtractedField, ExtractedLabel


def get_pipeline_response(pipeline_response, _, response_headers):
    return pipeline_response


def get_receipt_field_value(field):
    if field is None:
        return field
    # FIXME: refactor this
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
    pages = []

    for page in response.analyze_result.page_results:
        result_page = ExtractedLayoutPage(page_number=page.page, tables=[])
        for table in page.tables:
            my_table = [[None for x in range(table.columns)] for y in range(table.rows)]
            for cell in table.cells:
                my_table[cell.row_index][cell.column_index] = \
                    TableCell._from_generated(cell, response.analyze_result.read_results, include_raw)
            result_page.tables.append(Table(my_table))
        pages.append(result_page)
    return pages


def prepare_training_result(response):
    return CustomModel._from_generated(response)


def prepare_labeled_training_result(response):
    return LabeledCustomModel._from_generated(response)


def list_models_result(response):
    pass


def prepare_analyze_result(response, include_raw):
    pages = []

    for page in response.analyze_result.page_results:
        result_page = ExtractedPage(page_number=page.page, tables=[], fields=[], cluster_id=page.cluster_id)
        if page.tables:
            for table in page.tables:
                my_table = [[None for x in range(table.columns)] for y in range(table.rows)]
                for cell in table.cells:
                    my_table[cell.row_index][cell.column_index] = \
                        TableCell._from_generated(cell, response.analyze_result.read_results, include_raw)
                result_page.tables.append(Table(my_table))
        if page.key_value_pairs:
            for item in page.key_value_pairs:
                extracted_field = ExtractedField._from_generated(item, response.analyze_result.read_results, include_raw)
                result_page.fields.append(extracted_field)
        pages.append(result_page)
    return pages


def prepare_labeled_analyze_result(response, include_raw):
    pages = []
    read_result = response.analyze_result.read_results
    for page in response.analyze_result.page_results:
        result_page = ExtractedPage(page_number=page.page, tables=[], fields=[])
        if page.tables:
            for table in page.tables:
                my_table = [[None for x in range(table.columns)] for y in range(table.rows)]
                for cell in table.cells:
                    my_table[cell.row_index][cell.column_index] = \
                        TableCell._from_generated(cell, read_result, include_raw)
                result_page.tables.append(Table(my_table))
        pages.append(result_page)

    for idx, page in enumerate(response.analyze_result.document_results):
        if page.fields:
            pages[idx].fields = [ExtractedLabel._from_generated((label, value), read_result, include_raw) for label, value in page.fields.items()]

    return pages
