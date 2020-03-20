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
    ExtractedLabeledForm,
    PageRange,
    ReceiptType
)
# FIXME: what if page, read, or doc result is None or []?


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


def prepare_receipt_result(response, include_elements):
    receipts = []
    read_result = response.analyze_result.read_results
    document_result = response.analyze_result.document_results
    elements = read_result if include_elements else None
    page_metadata = PageMetadata._from_generated(read_result)

    for page in document_result:
        receipt = ExtractedReceipt(
            merchant_address=FieldValue._from_generated(page.fields.get("MerchantAddress", None), elements),
            merchant_name=FieldValue._from_generated(page.fields.get("MerchantName", None), elements),
            merchant_phone_number=FieldValue._from_generated(page.fields.get("MerchantPhoneNumber", None), elements),
            receipt_type=ReceiptType._from_generated(page.fields.get("ReceiptType", None)),
            receipt_items=ReceiptItem._from_generated(page.fields.get("Items", None), elements),
            subtotal=FieldValue._from_generated(page.fields.get("Subtotal", None), elements),
            tax=FieldValue._from_generated(page.fields.get("Tax", None), elements),
            tip=FieldValue._from_generated(page.fields.get("Tip", None), elements),
            total=FieldValue._from_generated(page.fields.get("Total", None), elements),
            transaction_date=FieldValue._from_generated(page.fields.get("TransactionDate", None), elements),
            transaction_time=FieldValue._from_generated(page.fields.get("TransactionTime", None), elements),
            page_range=PageRange(first_page=page.page_range[0], last_page=page.page_range[1]),
            page_metadata=page_metadata
        )

        receipt.fields = {
            key: FieldValue._from_generated(value, elements)
            for key, value in page.fields.items()
            if key not in ["ReceiptType", "Items"]  # these two are not represented by FieldValue in SDK
        }
        receipts.append(receipt)
    return receipts


def prepare_tables(page, elements):
    if page.tables is None:
        return page.tables

    return [
        ExtractedTable(
            row_count=table.rows,
            column_count=table.columns,
            page_number=page.page,
            cells=[TableCell._from_generated(cell, elements) for cell in table.cells],
        ) for table in page.tables
    ]


def prepare_layout_result(response, include_elements):
    pages = []
    read_result = response.analyze_result.read_results
    elements = read_result if include_elements else None

    for page in response.analyze_result.page_results:
        result_page = ExtractedLayoutPage(
            page_number=page.page,
            tables=prepare_tables(page, elements),
            page_metadata=PageMetadata._from_generated_page_index(read_result, page.page-1)
        )
        pages.append(result_page)
    return pages


def prepare_unlabeled_result(response, include_elements):
    extracted_pages = []
    read_result = response.analyze_result.read_results
    elements = read_result if include_elements else None

    for page in response.analyze_result.page_results:
        result_page = ExtractedPage(
            page_number=page.page,
            tables=prepare_tables(page, elements),
            fields=[ExtractedField._from_generated(item, elements)
                    for item in page.key_value_pairs or []],
            form_type_id=page.cluster_id,
            page_metadata=PageMetadata._from_generated_page_index(read_result, page.page-1)
        )
        extracted_pages.append(result_page)

    return extracted_pages


def prepare_labeled_result(response, include_elements):
    read_result = response.analyze_result.read_results
    page_result = response.analyze_result.page_results
    elements = read_result if include_elements else None

    page_metadata = PageMetadata._from_generated(read_result)
    tables = [prepare_tables(page, elements) for page in page_result]

    result = []

    for document in response.analyze_result.document_results:
        form = ExtractedLabeledForm(
            page_range=PageRange(
                first_page=document.page_range[0],
                last_page=document.page_range[1]
            ),
            fields={
                label: FieldValue._from_generated(value, elements)
                for label, value
                in document.fields.items()
            },
            page_metadata=page_metadata,
            tables=tables
        )
        result.append(form)
    return result
