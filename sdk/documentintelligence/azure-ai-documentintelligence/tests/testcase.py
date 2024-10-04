# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import logging
import re
from typing import Optional
from azure.core.credentials import AccessToken
from devtools_testutils import AzureRecordedTestCase

LOGGING_FORMAT = "%(asctime)s %(name)-20s %(levelname)-5s %(message)s"
ENABLE_LOGGER = os.getenv("ENABLE_LOGGER", "False")


def _get_blob_url(container_sas_url, container, file_name):
    if container_sas_url == "https://blob_sas_url":
        return container_sas_url
    url = container_sas_url.split(container)
    url[0] += container + "/" + file_name
    blob_sas_url = url[0] + url[1]
    return blob_sas_url


def adjust_value_type(value_type):
    if value_type == "array":
        value_type = "list"
    if value_type == "number":
        value_type = "float"
    if value_type == "object":
        value_type = "dictionary"
    return value_type


def adjust_confidence(score: Optional[float]) -> float:
    """Adjust confidence when not returned.

    :param float or None score: Confidence score to be adjusted.
    :return: The adjusted confidence score.
    :rtype: float
    """
    if score is None:
        return 1.0
    return score


def adjust_text_angle(text_angle: Optional[float]) -> Optional[float]:
    """Adjust to (-180, 180]

    :param float or None text_angle: The text angle to be adjusted.
    :return: The adjusted text angle.
    :rtype: float
    """
    if text_angle is not None:
        if text_angle > 180.0:
            text_angle -= 360.0
    return text_angle


def get_element_type(element_pointer):
    word_ref = re.compile(r"/readResults/\d+/lines/\d+/words/\d+")
    if re.search(word_ref, element_pointer):
        return "word"

    line_ref = re.compile(r"/readResults/\d+/lines/\d+")
    if re.search(line_ref, element_pointer):
        return "line"

    selection_mark_ref = re.compile(r"/readResults/\d+/selectionMarks/\d+")
    if re.search(selection_mark_ref, element_pointer):
        return "selectionMark"

    return None


def get_element(element_pointer, read_result):
    indices = [int(s) for s in re.findall(r"\d+", element_pointer)]
    read = indices[0]

    if get_element_type(element_pointer) == "word":
        line = indices[1]
        word = indices[2]
        ocr_word = read_result[read].lines[line].words[word]
        return "word", ocr_word, read + 1

    if get_element_type(element_pointer) == "line":
        line = indices[1]
        ocr_line = read_result[read].lines[line]
        return "line", ocr_line, read + 1

    if get_element_type(element_pointer) == "selectionMark":
        mark = indices[1]
        selection_mark = read_result[read].selection_marks[mark]
        return "selectionMark", selection_mark, read + 1

    return None, None, None


class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """

    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    def get_token(self, *args, **kwargs):
        return self.token


class DocumentIntelligenceTest(AzureRecordedTestCase):

    testing_container_sas_url = os.getenv("DOCUMENTINTELLIGENCE_TESTING_DATA_CONTAINER_SAS_URL", "https://blob_sas_url")
    barcode_url_tif = _get_blob_url(testing_container_sas_url, "testingdata", "barcode2.tif")
    receipt_url_jpg = _get_blob_url(testing_container_sas_url, "testingdata", "contoso-allinone.jpg")
    irs_classifier_document_url = _get_blob_url(testing_container_sas_url, "testingdata", "IRS-1040_2.pdf")

    # file stream samples
    invoice_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Invoice_1.pdf"))
    form_jpg = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Form_1.jpg"))
    multipage_invoice_pdf = os.path.abspath(
        os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/multipage_invoice1.pdf")
    )
    multipage_table_pdf = os.path.abspath(
        os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/multipagelayout.pdf")
    )
    irs_classifier_document = os.path.abspath(
        os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/IRS-1040.pdf")
    )
    layout_sample = os.path.abspath(
        os.path.join(os.path.abspath(__file__), "..", "./sample_forms/layout/layout-pageobject.pdf")
    )

    def get_oauth_endpoint(self):
        return os.getenv("DOCUMENTINTELLIGENCE_ENDPOINT")

    def generate_oauth_token(self):
        if self.is_live:
            from azure.identity import ClientSecretCredential

            return ClientSecretCredential(
                os.getenv("DOCUMENTINTELLIGENCE_TENANT_ID"),
                os.getenv("DOCUMENTINTELLIGENCE_CLIENT_ID"),
                os.getenv("DOCUMENTINTELLIGENCE_CLIENT_SECRET"),
            )
        return self.generate_fake_token()

    def generate_fake_token(self):
        return FakeTokenCredential()

    def configure_logging(self):
        self.enable_logging() if ENABLE_LOGGER == "True" else self.disable_logging()

    def enable_logging(self):
        self.logger = logging.getLogger("azure")
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        self.logger.handlers = [handler]
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = True
        self.logger.disabled = False

    def disable_logging(self):
        self.logger.propagate = False
        self.logger.disabled = True
        self.logger.handlers = []

    def assertBoundingBoxTransformCorrect(self, box, expected):
        if box is None and expected is None:
            return
        assert len(box) == len(expected)
        for element, expected_element in zip(box, expected):
            assert element == expected_element

    def assertBoundingPolygonTransformCorrect(self, polygon, expected):
        if polygon is None and expected is None:
            return

        assert len(polygon) == len(expected)
        for element, expected_element in zip(polygon, expected):
            assert element == expected_element

    def assertDocumentTransformCorrect(self, transformed_documents, raw_documents, **kwargs):
        if not transformed_documents and not raw_documents:
            return
        for document, expected in zip(transformed_documents, raw_documents):
            assert document.doc_type == expected.doc_type
            assert document.confidence == expected.confidence
            for span, expected_span in zip(document.spans or [], expected.spans or []):
                self.assertSpanTransformCorrect(span, expected_span)

            self.assertBoundingRegionsTransformCorrect(document.bounding_regions, expected.bounding_regions)

            self.assertDocumentFieldsTransformCorrect(document.fields, expected.fields)

    def assertDocumentKeyValuePairsTransformCorrect(self, transformed_key_value, raw_key_value, **kwargs):
        if not transformed_key_value and not raw_key_value:
            return
        for key_value, expected in zip(transformed_key_value, raw_key_value):
            self.assertDocumentKeyValueElementTransformCorrect(key_value.key, expected.key)
            self.assertDocumentKeyValueElementTransformCorrect(key_value.value, expected.value)
            assert key_value.confidence == expected.confidence

    def assertDocumentStylesTransformCorrect(self, transformed_styles, raw_styles, **kwargs):
        if not transformed_styles and not raw_styles:
            return

        for style, expected in zip(transformed_styles, raw_styles):
            assert style.is_handwritten == expected.is_handwritten
            assert style.similar_font_family == expected.similar_font_family
            assert style.font_style == expected.font_style
            assert style.font_weight == expected.font_weight
            assert style.color == expected.color
            assert style.background_color == expected.background_color
            assert style.confidence == expected.confidence

            for span, expected_span in zip(style.spans or [], expected.spans or []):
                self.assertSpanTransformCorrect(span, expected_span)

    def assertDocumentKeyValueElementTransformCorrect(self, element, expected, *kwargs):
        if not element or not expected:
            return
        assert element.content == expected.content

        for span, expected_span in zip(element.spans or [], expected.spans or []):
            self.assertSpanTransformCorrect(span, expected_span)

        self.assertBoundingRegionsTransformCorrect(element.bounding_regions, expected.bounding_regions)

    def assertDocumentTablesTransformCorrect(self, transformed_tables, raw_tables, **kwargs):
        if not transformed_tables and not raw_tables:
            return
        for table, expected in zip(transformed_tables, raw_tables):
            assert table.row_count == expected.row_count
            assert table.column_count == expected.column_count

            for cell, expected_cell in zip(table.cells, expected.cells):
                self.assertDocumentTableCellTransformCorrect(cell, expected_cell)

            for span, expected_span in zip(table.spans or [], expected.spans or []):
                self.assertSpanTransformCorrect(span, expected_span)

            self.assertBoundingRegionsTransformCorrect(table.bounding_regions, expected.bounding_regions)

    def assertDocumentTableCellTransformCorrect(self, transformed_cell, raw_cell, **kwargs):
        if raw_cell.kind:
            assert transformed_cell.kind == raw_cell.kind
        assert transformed_cell.row_index == raw_cell.row_index
        assert transformed_cell.column_index == raw_cell.column_index
        assert transformed_cell.content == raw_cell.content

        for span, expected_span in zip(transformed_cell.spans or [], raw_cell.spans or []):
            self.assertSpanTransformCorrect(span, expected_span)

        self.assertBoundingRegionsTransformCorrect(transformed_cell.bounding_regions, raw_cell.bounding_regions)

    def assertDocumentPagesTransformCorrect(self, transformed_pages, raw_pages, **kwargs):
        for page, expected_page in zip(transformed_pages, raw_pages):
            assert page.page_number == expected_page.page_number
            if page.angle:
                assert page.angle == adjust_text_angle(expected_page.angle)
            assert page.width == expected_page.width
            assert page.height == expected_page.height
            assert page.unit == expected_page.unit

            for line, expected_line in zip(page.lines or [], expected_page.lines or []):
                self.assertDocumentLineTransformCorrect(line, expected_line)

            for word, expected_word in zip(page.words or [], expected_page.words or []):
                self.assertDocumentWordTransformCorrect(word, expected_word)

            for selection_mark, expected_selection_mark in zip(
                page.selection_marks or [], expected_page.selection_marks or []
            ):
                self.assertDocumentSelectionMarkTransformCorrect(selection_mark, expected_selection_mark)

            for span, expected_span in zip(page.spans or [], expected_page.spans or []):
                self.assertSpanTransformCorrect(span, expected_span)

    def assertDocumentLineTransformCorrect(self, line, expected):
        assert line.content == expected.content
        self.assertBoundingBoxTransformCorrect(line.polygon, expected.polygon)
        for transformed_span, span in zip(line.spans or [], expected.spans or []):
            self.assertSpanTransformCorrect(transformed_span, span)

    def assertDocumentWordTransformCorrect(self, word, expected):
        assert word.content == expected.content
        self.assertBoundingPolygonTransformCorrect(word.polygon, expected.polygon)
        self.assertSpanTransformCorrect(word.span, expected.span)

    def assertSpanTransformCorrect(self, span, expected):
        if span is None and expected is None:
            return
        assert span.offset == expected.offset
        assert span.length == expected.length

    def assertDocumentSelectionMarkTransformCorrect(self, selection_mark, expected):
        assert selection_mark.confidence == adjust_confidence(expected.confidence)
        assert selection_mark.state == expected.state
        self.assertBoundingPolygonTransformCorrect(selection_mark.polygon, expected.polygon)

    def assertDocumentFieldsTransformCorrect(self, document_fields, generated_fields):
        if generated_fields is None:
            return

        for label, expected in generated_fields.items():
            if expected is None:  # None value occurs with labeled tables and empty cells
                continue
            field_type = expected.type
            assert adjust_value_type(field_type) == document_fields[label].value_type
            assert expected.confidence == document_fields[label].confidence
            # In the case of content for a signature type field we get '' in expected.content
            # vs. None for document_fields[label].content
            assert (expected.content == document_fields[label].content) or (
                expected.content == "" and not document_fields[label].content
            )
            self.assertDocumentFieldValueTransformCorrect(document_fields[label], expected)

            for span, expected_span in zip(document_fields[label].spans or [], expected.spans or []):
                self.assertSpanTransformCorrect(span, expected_span)

            self.assertBoundingRegionsTransformCorrect(
                document_fields[label].bounding_regions, expected.bounding_regions
            )

    def assertBoundingRegionsTransformCorrect(self, bounding_regions, expected):
        if not bounding_regions and not expected:
            return
        for region, expected_region in zip(bounding_regions, expected):
            assert region.page_number == expected_region.page_number
            self.assertBoundingPolygonTransformCorrect(region.polygon, expected_region.polygon)

    def assertDocumentFieldValueTransformCorrect(self, document_field, expected):
        if expected is None:
            return
        field_type = expected.type
        if field_type == "string":
            assert document_field.value == expected.value_string
        if field_type == "number":
            assert document_field.value == expected.value_number
        if field_type == "integer":
            assert document_field.value == expected.value_integer
        if field_type == "date":
            assert document_field.value == expected.value_date
        if field_type == "phoneNumber":
            assert document_field.value == expected.value_phone_number
        if field_type == "time":
            assert document_field.value == expected.value_time
        if field_type == "selectionMark":
            assert document_field.value == expected.value_selection_mark
        if field_type == "countryRegion":
            assert document_field.value == expected.value_country_region
        if field_type == "signature":
            assert document_field.value == expected.value_signature
        if field_type == "boolean":
            assert document_field.value == expected.value_boolean
        if field_type == "array":
            for i in range(len(expected.value_array)):
                self.assertDocumentFieldValueTransformCorrect(document_field.value[i], expected.value_array[i])
        if field_type == "object":
            self.assertDocumentFieldsTransformCorrect(document_field.value, expected.value_object)
