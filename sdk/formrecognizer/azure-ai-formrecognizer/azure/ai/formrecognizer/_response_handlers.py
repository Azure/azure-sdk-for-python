# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from ._models import (
    USReceipt,
    USReceiptType,
    FormField,
    USReceiptItem,
    FormPage,
    TableCell,
    ExtractedLayoutPage,
    ExtractedPage,
    ExtractedField,
    ExtractedTable,
    PageMetadata,
    ExtractedLabeledForm,
    PageRange,
)


def create_us_receipt(response):
    receipts = []
    read_result = response.analyze_result.read_results
    document_result = response.analyze_result.document_results
    form_page = FormPage._from_generated_receipt(read_result)

    for page in document_result:
        if page.fields is None:
            receipt = USReceipt(
                page_range=PageRange(first_page=page.page_range[0], last_page=page.page_range[1]),
                pages=form_page,
                form_type=page.doc_type,
            )
            receipts.append(receipt)
            continue
        receipt = USReceipt(
            merchant_address=FormField._from_generated(
                "MerchantAddress", page.fields.get("MerchantAddress"), read_result
            ),
            merchant_name=FormField._from_generated(
                "MerchantName", page.fields.get("MerchantName"), read_result
            ),
            merchant_phone_number=FormField._from_generated(
                "MerchantPhoneNumber",
                page.fields.get("MerchantPhoneNumber"),
                read_result,
            ),
            receipt_type=USReceiptType._from_generated(page.fields.get("ReceiptType")),
            receipt_items=USReceiptItem._from_generated(
                page.fields.get("Items"), read_result
            ),
            subtotal=FormField._from_generated(
                "Subtotal", page.fields.get("Subtotal"), read_result
            ),
            tax=FormField._from_generated("Tax", page.fields.get("Tax"), read_result),
            tip=FormField._from_generated("Tip", page.fields.get("Tip"), read_result),
            total=FormField._from_generated(
                "Total", page.fields.get("Total"), read_result
            ),
            transaction_date=FormField._from_generated(
                "TransactionDate", page.fields.get("TransactionDate"), read_result
            ),
            transaction_time=FormField._from_generated(
                "TransactionTime", page.fields.get("TransactionTime"), read_result
            ),
            page_range=PageRange(
                first_page=page.page_range[0], last_page=page.page_range[1]
            ),
            pages=form_page,
            form_type=page.doc_type,
            fields={
                key: FormField._from_generated(key, value, read_result)
                for key, value in page.fields.items()
                if key not in ["ReceiptType", "Items"]  # these two are not represented by FormField in SDK
            },
        )

        receipts.append(receipt)
    return receipts


def prepare_receipt_result(response, receipt_locale):
    if receipt_locale.lower() == "en-us":
        return create_us_receipt(response)
    raise ValueError("The receipt locale '{}' is not supported.".format(receipt_locale))


def prepare_tables(page, read_result):
    if not page.tables:
        return page.tables

    return [
        ExtractedTable(
            row_count=table.rows,
            column_count=table.columns,
            page_number=page.page,
            cells=[TableCell._from_generated(cell, read_result) for cell in table.cells],
        ) for table in page.tables
    ]


def prepare_layout_result(response):
    pages = []
    read_result = response.analyze_result.read_results

    for page in response.analyze_result.page_results:
        result_page = ExtractedLayoutPage(
            page_number=page.page,
            tables=prepare_tables(page, read_result),
            page_metadata=PageMetadata._from_generated_page_index(read_result, page.page-1)
        )
        pages.append(result_page)
    return pages


def prepare_unlabeled_result(response):
    extracted_pages = []
    read_result = response.analyze_result.read_results

    for page in response.analyze_result.page_results:
        result_page = ExtractedPage(
            page_number=page.page,
            tables=prepare_tables(page, read_result),
            fields=[ExtractedField._from_generated(item, read_result)
                    for item in page.key_value_pairs] if page.key_value_pairs else None,
            form_type_id=page.cluster_id,
            page_metadata=PageMetadata._from_generated_page_index(read_result, page.page-1)
        )
        extracted_pages.append(result_page)

    return extracted_pages


def prepare_labeled_result(response):
    read_result = response.analyze_result.read_results
    page_result = response.analyze_result.page_results
    page_metadata = PageMetadata._from_generated(read_result)
    tables = [prepare_tables(page, read_result) for page in page_result]

    result = []

    for document in response.analyze_result.document_results:
        form = ExtractedLabeledForm(
            page_range=PageRange(
                first_page=document.page_range[0],
                last_page=document.page_range[1]
            ),
            fields={
                label: FormField._from_generated(label, value, read_result)
                for label, value in document.fields.items()
            },
            page_metadata=page_metadata,
            tables=tables
        )
        result.append(form)
    return result
