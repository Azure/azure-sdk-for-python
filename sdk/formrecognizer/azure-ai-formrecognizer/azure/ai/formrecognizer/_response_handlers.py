# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from ._models import (
    FormField,
    FormPage,
    FormLine,
    FormTable,
    FormTableCell,
    FormPageRange,
    RecognizedForm,
    RecognizedReceipt
)


def prepare_receipt(response):
    receipts = []
    read_result = response.analyze_result.read_results
    document_result = response.analyze_result.document_results
    form_page = FormPage._from_generated(read_result)

    for page in document_result:
        if page.fields is None:
            receipt = RecognizedReceipt(
                page_range=FormPageRange(first_page_number=page.page_range[0], last_page_number=page.page_range[1]),
                pages=form_page[page.page_range[0]-1:page.page_range[1]],
                form_type=page.doc_type,
            )
            receipts.append(receipt)
            continue
        receipt = RecognizedReceipt(
            page_range=FormPageRange(
                first_page_number=page.page_range[0], last_page_number=page.page_range[1]
            ),
            pages=form_page[page.page_range[0]-1:page.page_range[1]],
            form_type=page.doc_type,
            fields={
                key: FormField._from_generated(key, value, read_result)
                for key, value in page.fields.items()
            }
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
            page_range=FormPageRange(
                first_page_number=page.page,
                last_page_number=page.page
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
            page_range=FormPageRange(
                first_page_number=doc.page_range[0],
                last_page_number=doc.page_range[1]
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
