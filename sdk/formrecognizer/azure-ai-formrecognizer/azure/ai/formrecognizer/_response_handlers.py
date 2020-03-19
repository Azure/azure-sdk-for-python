# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.exceptions import HttpResponseError
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
    PageRange,
    ReceiptType
)
# FIXME: what if page, read, or doc result is None or []?
# FIXME: ExtractedWord does not have reference to Line yet


def get_content_type(form):
    if len(form) > 3 and form[0] == 0x25 and form[1] == 0x50 and form[2] == 0x44 and form[3] == 0x46:
        return "application/pdf"
    if len(form) > 2 and form[0] == 0xFF and form[1] == 0xD8 and form[2] == 0xFF:
        return "image/jpeg"
    if len(form) > 3 and form[0] == 0x89 and form[1] == 0x50 and form[2] == 0x4E and form[3] == 0x47:
        return "image/png"
    if len(form) > 3 and ((form[0] == 0x49 and form[1] == 0x49 and form[2] == 0x2A and form[3] == 0x0)  # little-endian
            or (form[0] == 0x4D and form[1] == 0x4D and form[2] == 0x0 and form[3] == 0x2A)):  # big-endian
        return "image/tiff"
    raise HttpResponseError("Content type could not be auto-detected. Please pass the content_type keyword argument.")


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
                receipt_type=ReceiptType._from_generated(
                    page.fields.pop("ReceiptType", None)
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
            label: FieldValue._from_generated(value, read_result, include_ocr)
            for label, value
            in document_result.fields.items()
        },
        pages=prepare_layout_result(response, include_ocr)
    )
