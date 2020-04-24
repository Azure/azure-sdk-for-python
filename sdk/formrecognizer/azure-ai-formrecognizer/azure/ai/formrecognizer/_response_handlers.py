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
    FormLine,
    FormTable,
    FormTableCell,
    PageRange,
    RecognizedForm
)


def prepare_us_receipt(response):
    receipts = []
    read_result = response.analyze_result.read_results
    document_result = response.analyze_result.document_results
    form_page = FormPage._from_generated(read_result)

    for page in document_result:
        if page.fields is None:
            receipt = USReceipt(
                page_range=PageRange(first_page=page.page_range[0], last_page=page.page_range[1]),
                pages=form_page[page.page_range[0]-1:page.page_range[1]],
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
            pages=form_page[page.page_range[0]-1:page.page_range[1]],
            form_type=page.doc_type,
            fields={
                key: FormField._from_generated(key, value, read_result)
                for key, value in page.fields.items()
            },
        )

        receipts.append(receipt)
    return receipts


def prepare_tables(page, read_result):
    if not page.tables:
        return page.tables

    return [
        FormTable(
            row_count=table.rows,
            column_count=table.columns,
            page_number=page.page,
            cells=[FormTableCell._from_generated(cell, page.page, read_result) for cell in table.cells],
        ) for table in page.tables
    ]


def prepare_content_result(response):
    pages = []
    read_result = response.analyze_result.read_results
    page_result = response.analyze_result.page_results

    for idx, page in enumerate(read_result):
        form_page = FormPage(
            page_number=page.page,
            text_angle=page.angle,
            width=page.width,
            height=page.height,
            unit=page.unit,
            lines=[FormLine._from_generated(line, page=page.page) for line in page.lines] if page.lines else None,
            tables=prepare_tables(page_result[idx], read_result),
        )
        pages.append(form_page)
    return pages


def prepare_form_result(response, model_id):
    document_result = response.analyze_result.document_results
    if document_result:
        return prepare_labeled_result(response, model_id)
    return prepare_unlabeled_result(response)


def prepare_unlabeled_result(response):
    result = []
    form_pages = prepare_content_result(response)
    read_result = response.analyze_result.read_results
    page_result = response.analyze_result.page_results

    for index, page in enumerate(page_result):
        unlabeled_fields = [FormField._from_generated_unlabeled(field, idx, page.page, read_result)
                            for idx, field in enumerate(page.key_value_pairs)] if page.key_value_pairs else None
        if unlabeled_fields:
            unlabeled_fields = {field.name: field for field in unlabeled_fields}
        form = RecognizedForm(
            page_range=PageRange(
                first_page=page.page,
                last_page=page.page
            ),
            fields=unlabeled_fields,
            form_type="form-" + str(page.cluster_id) if page.cluster_id is not None else None,
            pages=[form_pages[index]]
        )
        result.append(form)

    return result


def prepare_labeled_result(response, model_id):
    read_result = response.analyze_result.read_results
    form_pages = prepare_content_result(response)

    result = []
    for doc in response.analyze_result.document_results:
        form = RecognizedForm(
            page_range=PageRange(
                first_page=doc.page_range[0],
                last_page=doc.page_range[1]
            ),
            fields={
                label: FormField._from_generated(label, value, read_result)
                for label, value in doc.fields.items()
            },
            pages=form_pages[doc.page_range[0]-1:doc.page_range[1]],
            form_type="form-" + model_id,
        )
        result.append(form)
    return result
