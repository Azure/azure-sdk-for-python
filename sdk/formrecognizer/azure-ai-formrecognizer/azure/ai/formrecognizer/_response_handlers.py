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
    ExtractedPage,
    ExtractedField,
    ExtractedTable,
    PageMetadata,
    ExtractedForm,
    LabelValue,
    PageRange
)
# FIXME: what if page, read, or doc result is None?
# FIXME: ExtractedWord does not have reference to Line yet


def prepare_receipt_result(response, include_ocr):
    receipts = []
    read_result = response.analyze_result.read_results

    for page in response.analyze_result.document_results:
        receipt = ExtractedReceipt(
                merchant_address=FieldValue._from_generated(
                    page.fields.pop("MerchantAddress", None),
                    read_result,
                    include_ocr
                ),
                merchant_name=FieldValue._from_generated(
                    page.fields.pop("MerchantName", None),
                    read_result,
                    include_ocr
                ),
                merchant_phone_number=FieldValue._from_generated(
                    page.fields.pop("MerchantPhoneNumber", None),
                    read_result,
                    include_ocr
                ),
                receipt_type=FieldValue._from_generated(
                    page.fields.pop("ReceiptType", None),
                    read_result,
                    include_ocr
                ),
                receipt_items=ReceiptItem._from_generated(
                    page.fields.pop("Items", None),
                    response.analyze_result.read_results,
                    include_ocr
                ),
                subtotal=FieldValue._from_generated(
                    page.fields.pop("Subtotal", None),
                    read_result,
                    include_ocr
                ),
                tax=FieldValue._from_generated(
                    page.fields.pop("Tax", None),
                    read_result,
                    include_ocr
                ),
                tip=FieldValue._from_generated(
                    page.fields.pop("Tip", None),
                    read_result,
                    include_ocr
                ),
                total=FieldValue._from_generated(
                    page.fields.pop("Total", None),
                    read_result,
                    include_ocr
                ),
                transaction_date=FieldValue._from_generated(
                    page.fields.pop("TransactionDate", None),
                    read_result,
                    include_ocr
                ),
                transaction_time=FieldValue._from_generated(
                    page.fields.pop("TransactionTime", None),
                    read_result,
                    include_ocr
                ),
                page_range=PageRange(first_page=page.page_range[0], last_page=page.page_range[1]),
                page_metadata=PageMetadata._from_generated_page_index(read_result, page.page_range[0]-1)
            )
        receipt.update(page.fields)  # for any new fields being sent
        receipts.append(receipt)
    return receipts


def prepare_tables(tables, read_result, include_ocr):
    if tables is None:
        return tables
    return [
        ExtractedTable(
            row_count=table.rows,
            column_count=table.columns,
            cells=[TableCell._from_generated(cell, read_result, include_ocr) for cell in table.cells],
        ) for table in tables
    ]


def prepare_layout_result(response, include_ocr):
    pages = []
    read_result = response.analyze_result.read_results
    for page in response.analyze_result.page_results:
        result_page = ExtractedLayoutPage(
            page_number=page.page,
            tables=prepare_tables(page.tables, read_result, include_ocr),
            page_metadata=PageMetadata._from_generated_page_index(read_result, page.page-1)
        )
        pages.append(result_page)
    return pages


def prepare_unlabeled_result(response, include_ocr):
    extracted_pages = []
    read_result = response.analyze_result.read_results

    for page in response.analyze_result.page_results:
        result_page = ExtractedPage(
            page_number=page.page,
            tables=prepare_tables(page.tables, read_result, include_ocr),
            fields=[ExtractedField._from_generated(item, read_result, include_ocr)
                    for item in page.key_value_pairs or []],
            form_type_id=page.cluster_id,
            page_metadata=PageMetadata._from_generated_page_index(read_result, page.page-1)
        )
        extracted_pages.append(result_page)

    return extracted_pages


def prepare_labeled_result(response, include_ocr):
    read_result = response.analyze_result.read_results
    document_result = response.analyze_result.document_results[0]
    return ExtractedForm(
        page_range=PageRange(first_page=document_result.page_range[0], last_page=document_result.page_range[1]),
        fields={
            label: LabelValue._from_generated(value, read_result, include_ocr)
            for label, value
            in document_result.fields.items()
        },
        pages=prepare_layout_result(response, include_ocr)
    )
