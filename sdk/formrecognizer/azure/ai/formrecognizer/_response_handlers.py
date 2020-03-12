# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


from ._models import (
    ExtractedReceipt,
    FieldValue,
    ReceiptItem,
    TableCell,
    ExtractedLayoutPage,
    CustomModel,
    LabeledCustomModel,
    ExtractedPage,
    ExtractedField,
    ExtractedTable,
    PageMetadata,
    ExtractedForm,
    ExtractedLabel
)


def prepare_receipt_result(response, include_raw):
    receipts = []
    read_result = response.analyze_result.read_results

    for page in response.analyze_result.document_results:
        receipt = ExtractedReceipt(
                merchant_address=FieldValue._from_generated(
                    page.fields.pop("MerchantAddress", None),
                    read_result,
                    include_raw
                ),
                merchant_name=FieldValue._from_generated(
                    page.fields.pop("MerchantName", None),
                    read_result,
                    include_raw
                ),
                merchant_phone_number=FieldValue._from_generated(
                    page.fields.pop("MerchantPhoneNumber", None),
                    read_result,
                    include_raw
                ),
                receipt_type=FieldValue._from_generated(
                    page.fields.pop("ReceiptType", None),
                    read_result,
                    include_raw
                ),
                receipt_items=ReceiptItem._from_generated(
                    page.fields.pop("Items", None),
                    response.analyze_result.read_results,
                    include_raw
                ),
                subtotal=FieldValue._from_generated(
                    page.fields.pop("Subtotal", None),
                    read_result,
                    include_raw
                ),
                tax=FieldValue._from_generated(
                    page.fields.pop("Tax", None),
                    read_result,
                    include_raw
                ),
                tip=FieldValue._from_generated(
                    page.fields.pop("Tip", None),
                    read_result,
                    include_raw
                ),
                total=FieldValue._from_generated(
                    page.fields.pop("Total", None),
                    read_result,
                    include_raw
                ),
                transaction_date=FieldValue._from_generated(
                    page.fields.pop("TransactionDate", None),
                    read_result,
                    include_raw
                ),
                transaction_time=FieldValue._from_generated(
                    page.fields.pop("TransactionTime", None),
                    read_result,
                    include_raw
                ),
                page_range=page.page_range,
                page_metadata=PageMetadata._from_generated(read_result, page.page_range[0]-1)
            )
        receipt.update(page.fields)  # for any new fields being sent
        receipts.append(receipt)
    return receipts


def prepare_tables(page, read_result, include_raw):
    if page.tables is None:
        return page.tables
    return [
        ExtractedTable(
            row_count=table.rows,
            column_count=table.columns,
            cells=[TableCell._from_generated(cell, read_result, include_raw) for cell in table.cells],
            page_number=page.page,
        ) for table in page.tables
    ]


def prepare_layout_result(response, include_raw):
    pages = []
    read_result = response.analyze_result.read_results
    for page in response.analyze_result.page_results:
        result_page = ExtractedLayoutPage(
            page_number=page.page,
            tables=prepare_tables(page, read_result, include_raw),
            page_metadata=PageMetadata._from_generated(read_result, page.page-1)
        )
        pages.append(result_page)
    return pages


def prepare_training_result(response):
    return CustomModel._from_generated(response)


def prepare_labeled_training_result(response):
    return LabeledCustomModel._from_generated(response)


def prepare_unlabeled_result(response, include_raw):
    # FIXME: refactor this function, fix tables
    # FIXME: rename include_raw to include_ocr
    extracted_pages = []
    read_result = response.analyze_result.read_results

    for page in response.analyze_result.page_results:
        result_page = ExtractedPage(page_number=page.page, tables=[], fields=[], form_type_id=page.cluster_id)
        if page.tables:
            result_page.tables = prepare_tables(page, read_result, include_raw)
        if page.key_value_pairs:
            result_page.fields = [ExtractedField._from_generated(item, read_result, include_raw)
                                  for item in page.key_value_pairs]
        extracted_pages.append(result_page)

    return extracted_pages


def prepare_labeled_result(response, include_raw):
    read_result = response.analyze_result.read_results
    page_result = response.analyze_result.page_results
    document_result = response.analyze_result.document_results[0]
    return ExtractedForm(
        page_range=document_result.page_range,
        page_metadata=PageMetadata._all_pages(read_result),
        fields=[
            ExtractedLabel._from_generated((label, value), read_result, include_raw)
            for label, value
            in document_result.fields.items()
        ],
        tables=[prepare_tables(page, read_result, include_raw) for page in page_result]
    )

