# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from ._helpers import adjust_text_angle, adjust_confidence
from ._models import (
    FormField,
    FormPage,
    FormLine,
    FormTable,
    FormTableCell,
    FormPageRange,
    RecognizedForm,
    FormSelectionMark,
    get_bounding_box,
)


def prepare_prebuilt_models(response):
    prebuilt_models = []
    read_result = response.analyze_result.read_results
    document_result = response.analyze_result.document_results
    form_page = prepare_content_result(response)

    for page in document_result:
        model_id = page.model_id if hasattr(page, "model_id") else None
        doc_type_confidence = (
            page.doc_type_confidence if hasattr(page, "doc_type_confidence") else None
        )
        prebuilt_model = RecognizedForm(
            page_range=FormPageRange(
                first_page_number=page.page_range[0],
                last_page_number=page.page_range[1],
            ),
            pages=form_page[page.page_range[0] - 1 : page.page_range[1]],
            form_type=page.doc_type,
            fields={
                key: FormField._from_generated(key, value, read_result)
                for key, value in page.fields.items()
            }
            if page.fields
            else None,
            form_type_confidence=doc_type_confidence,
            model_id=model_id,
        )

        prebuilt_models.append(prebuilt_model)
    return prebuilt_models


def prepare_tables(page, read_result):
    if not page.tables:
        return page.tables

    return [
        FormTable(
            row_count=table.rows,
            column_count=table.columns,
            page_number=page.page,
            cells=[
                FormTableCell._from_generated(cell, page.page, read_result)
                for cell in table.cells
            ],
            bounding_box=get_bounding_box(table)
            if hasattr(table, "bounding_box")
            else None,
        )
        for table in page.tables
    ]


def prepare_content_result(response):
    pages = []
    read_result = response.analyze_result.read_results
    page_result = response.analyze_result.page_results

    for idx, page in enumerate(read_result):
        if hasattr(page, "selection_marks"):
            selection_marks = (
                [
                    FormSelectionMark._from_generated(mark, page.page)
                    for mark in page.selection_marks
                ]
                if page.selection_marks
                else None
            )
        else:
            selection_marks = None
        form_page = FormPage(
            page_number=page.page,
            text_angle=adjust_text_angle(page.angle),
            width=page.width,
            height=page.height,
            unit=page.unit,
            lines=[
                FormLine._from_generated(line, page=page.page) for line in page.lines
            ]
            if page.lines
            else None,
            tables=prepare_tables(page_result[idx], read_result)
            if page_result
            else None,
            selection_marks=selection_marks,
        )
        pages.append(form_page)
    return pages


def prepare_form_result(response, model_id):
    document_result = response.analyze_result.document_results
    if document_result:
        return prepare_labeled_result(response, model_id)
    return prepare_unlabeled_result(response, model_id)


def prepare_unlabeled_result(response, model_id):
    result = []
    form_pages = prepare_content_result(response)
    read_result = response.analyze_result.read_results
    page_result = response.analyze_result.page_results

    for index, page in enumerate(page_result):
        unlabeled_fields = (
            [
                FormField._from_generated_unlabeled(field, idx, page.page, read_result)
                for idx, field in enumerate(page.key_value_pairs)
            ]
            if page.key_value_pairs
            else None
        )
        if unlabeled_fields:
            unlabeled_fields = {field.name: field for field in unlabeled_fields}
        form = RecognizedForm(
            page_range=FormPageRange(
                first_page_number=page.page, last_page_number=page.page
            ),
            fields=unlabeled_fields,
            form_type="form-" + str(page.cluster_id)
            if page.cluster_id is not None
            else None,
            pages=[form_pages[index]],
            model_id=model_id,
            form_type_confidence=None,
        )
        result.append(form)

    return result


def prepare_labeled_result(response, model_id):
    read_result = response.analyze_result.read_results
    form_pages = prepare_content_result(response)

    form_type = None
    if response.analyze_result.version == "2.0.0":
        form_type = "form-" + model_id

    result = []
    for doc in response.analyze_result.document_results:
        model_id = doc.model_id if hasattr(doc, "model_id") else model_id
        doc_type_confidence = (
            doc.doc_type_confidence if hasattr(doc, "doc_type_confidence") else None
        )
        if response.analyze_result.version == "2.0.0":
            form_type_confidence = None
        else:
            form_type_confidence = adjust_confidence(doc_type_confidence)
        form = RecognizedForm(
            page_range=FormPageRange(
                first_page_number=doc.page_range[0], last_page_number=doc.page_range[1]
            ),
            fields={
                label: FormField._from_generated(label, value, read_result)
                for label, value in doc.fields.items()
            },
            pages=form_pages[doc.page_range[0] - 1 : doc.page_range[1]],
            form_type=form_type if form_type else doc.doc_type,
            form_type_confidence=form_type_confidence,
            model_id=model_id,
        )
        result.append(form)
    return result
