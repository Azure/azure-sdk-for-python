
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import six
import logging
from azure.core.credentials import AccessToken
from azure.ai.formrecognizer._helpers import (
    adjust_value_type,
    get_element,
    adjust_confidence,
    adjust_text_angle
)
from devtools_testutils import AzureRecordedTestCase, set_custom_default_matcher

LOGGING_FORMAT = '%(asctime)s %(name)-20s %(levelname)-5s %(message)s'
ENABLE_LOGGER = os.getenv('ENABLE_LOGGER', "False")

def _get_blob_url(container_sas_url, container, file_name):
    if container_sas_url == "https://blob_sas_url":
        return container_sas_url
    url = container_sas_url.split(container)
    url[0] += container + "/" + file_name
    blob_sas_url = url[0] + url[1]
    return blob_sas_url

class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    def get_token(self, *args):
        return self.token

class FormRecognizerTest(AzureRecordedTestCase):

    testing_container_sas_url = os.getenv("FORMRECOGNIZER_TESTING_DATA_CONTAINER_SAS_URL", "https://blob_sas_url")
    receipt_url_jpg = _get_blob_url(testing_container_sas_url, "testingdata", "contoso-allinone.jpg")
    receipt_url_png = _get_blob_url(testing_container_sas_url, "testingdata", "contoso-receipt.png")
    business_card_url_jpg = _get_blob_url(testing_container_sas_url, "testingdata", "businessCard.jpg")
    business_card_url_png = _get_blob_url(testing_container_sas_url, "testingdata", "businessCard.png")
    business_card_multipage_url_pdf = _get_blob_url(testing_container_sas_url, "testingdata", "business-card-multipage.pdf")
    identity_document_url_jpg = _get_blob_url(testing_container_sas_url, "testingdata", "license.jpg")
    identity_document_url_jpg_passport = _get_blob_url(testing_container_sas_url, "testingdata", "passport_1.jpg")
    invoice_url_pdf = _get_blob_url(testing_container_sas_url, "testingdata", "Invoice_1.pdf")
    invoice_url_tiff = _get_blob_url(testing_container_sas_url, "testingdata", "Invoice_1.tiff")
    invoice_url_jpg = _get_blob_url(testing_container_sas_url, "testingdata", "sample_invoice.jpg")
    multipage_vendor_url_pdf = _get_blob_url(testing_container_sas_url, "testingdata", "multi1.pdf")
    form_url_jpg = _get_blob_url(testing_container_sas_url, "testingdata", "Form_1.jpg")
    multipage_url_pdf = _get_blob_url(testing_container_sas_url, "testingdata", "multipage_invoice1.pdf")
    multipage_table_url_pdf = _get_blob_url(testing_container_sas_url, "testingdata", "multipagelayout.pdf")
    selection_mark_url_pdf = _get_blob_url(testing_container_sas_url, "testingdata", "selection_mark_form.pdf")
    label_table_variable_row_url_pdf = _get_blob_url(testing_container_sas_url, "testingdata", "label_table_variable_rows1.pdf")
    label_table_fixed_row_url_pdf = _get_blob_url(testing_container_sas_url, "testingdata", "label_table_fixed_rows1.pdf")
    multipage_receipt_url_pdf = _get_blob_url(testing_container_sas_url, "testingdata", "multipage_receipt.pdf")
    invoice_no_sub_line_item = _get_blob_url(testing_container_sas_url, "testingdata", "ErrorImage.tiff")

    # file stream samples
    receipt_jpg = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/receipt/contoso-allinone.jpg"))
    receipt_png = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/receipt/contoso-receipt.png"))
    business_card_jpg = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/business_cards/business-card-english.jpg"))
    business_card_png = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/business_cards/business-card-english.png"))
    business_card_multipage_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/business_cards/business-card-multipage.pdf"))
    identity_document_license_jpg = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/identity_documents/license.jpg"))
    identity_document_passport_jpg = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/identity_documents/passport_1.jpg"))
    invoice_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Invoice_1.pdf"))
    invoice_tiff = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Invoice_1.tiff"))
    invoice_jpg = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/sample_invoice.jpg"))
    form_jpg = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Form_1.jpg"))
    blank_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/blank.pdf"))
    multipage_invoice_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/multipage_invoice1.pdf"))
    unsupported_content_py = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./conftest.py"))
    multipage_table_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/multipagelayout.pdf"))
    multipage_vendor_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/multi1.pdf"))
    selection_form_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/selection_mark_form.pdf"))
    multipage_receipt_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/receipt/multipage_receipt.pdf"))

    def get_oauth_endpoint(self):
        return os.getenv("FORMRECOGNIZER_TEST_ENDPOINT")

    def generate_oauth_token(self):
        if self.is_live:
            from azure.identity import ClientSecretCredential
            return ClientSecretCredential(
                os.getenv("FORMRECOGNIZER_TENANT_ID"),
                os.getenv("FORMRECOGNIZER_CLIENT_ID"),
                os.getenv("FORMRECOGNIZER_CLIENT_SECRET"),
            )
        return self.generate_fake_token()

    def generate_fake_token(self):
        return FakeTokenCredential()

    def configure_logging(self):
        self.enable_logging() if ENABLE_LOGGER == "True" else self.disable_logging()

    def enable_logging(self):
        self.logger = logging.getLogger('azure')
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

    def assertModelTransformCorrect(self, model, expected):
        assert model.model_id == expected.model_id
        assert model.created_on == expected.created_date_time
        assert model.description == expected.description

        for name, field in model.doc_types.items():
            assert name in expected.doc_types
            exp = expected.doc_types[name]
            assert field.description == exp.description
            assert field.field_confidence == exp.field_confidence
            assert field.field_schema == {name: field.serialize() for name, field in exp.field_schema.items()}

    def assertFormPagesTransformCorrect(self, form_pages, read_result, page_result=None, **kwargs):
        for page, expected_page in zip(form_pages, read_result):
            if hasattr(page, "pages"):  # this is necessary for how unlabeled forms are structured
                page = page.pages[0]
            assert page.page_number == expected_page.page
            assert page.text_angle == adjust_text_angle(expected_page.angle)
            assert page.width == expected_page.width
            assert page.height == expected_page.height
            assert page.unit == expected_page.unit

            for line, expected_line in zip(page.lines or [], expected_page.lines or []):
                self.assertFormLineTransformCorrect(line, expected_line)

            for selection_mark, expected_selection_mark in zip(page.selection_marks or [], expected_page.selection_marks or []):
                self.assertDocumentSelectionMarkTransformCorrect(selection_mark, expected_selection_mark)

        if page_result:
            for page, expected_page in zip(form_pages, page_result):
                if hasattr(page, "pages"):  # this is necessary for how unlabeled forms are structured
                    page = page.pages[0]
                if expected_page.tables:
                    self.assertTablesTransformCorrect(page.tables, expected_page.tables, read_result, **kwargs)

    def assertBoundingBoxTransformCorrect(self, box, expected):
        if box is None and expected is None:
            return
        assert box[0].x == expected[0]
        assert box[0].y == expected[1]
        assert box[1].x == expected[2]
        assert box[1].y == expected[3]
        assert box[2].x == expected[4]
        assert box[2].y == expected[5]
        assert box[3].x == expected[6]
        assert box[3].y == expected[7]

    def assertFormWordTransformCorrect(self, word, expected):
        assert word.text == expected.text
        assert word.confidence == adjust_confidence(expected.confidence)
        assert word.kind  == "word"
        self.assertBoundingBoxTransformCorrect(word.bounding_box, expected.bounding_box)

    def assertFormLineTransformCorrect(self, line, expected):
        assert line.kind == "line"
        assert line.text == expected.text
        self.assertBoundingBoxTransformCorrect(line.bounding_box, expected.bounding_box)
        if expected.appearance:
            assert line.appearance.style_name == expected.appearance.style.name
            assert line.appearance.style_confidence == expected.appearance.style.confidence
        for word, expected_word in zip(line.words, expected.words):
            self.assertFormWordTransformCorrect(word, expected_word)

    def assertFieldElementsTransFormCorrect(self, field_elements, generated_elements, read_result):
        if field_elements is None and not generated_elements:
            return
        for element, json_pointer in zip(field_elements, generated_elements):
            element_type, expected, page_number = get_element(json_pointer, read_result)
            if element_type == "word":
                self.assertFormWordTransformCorrect(element, expected)
            elif element_type == "line":
                self.assertFormLineTransformCorrect(element, expected)
            elif element_type == "selectionMark":
                self.assertDocumentSelectionMarkTransformCorrect(element, expected)

    def assertFormFieldValueTransformCorrect(self, form_field, expected, read_results=None):
        if expected is None:
            return
        field_type = expected.type
        if field_type == "string":
            assert form_field.value == expected.value_string
        if field_type == "number":
            assert form_field.value == expected.value_number
        if field_type == "integer":
            assert form_field.value == expected.value_integer
        if field_type == "date":
            assert form_field.value == expected.value_date
        if field_type == "phoneNumber":
            assert form_field.value == expected.value_phone_number
        if field_type == "time":
            assert form_field.value == expected.value_time
        if field_type == "selectionMark":
            assert form_field.value == expected.value_selection_mark
        if field_type == "countryRegion":
            assert form_field.value == expected.value_country_region
        if field_type == "array":
            for i in range(len(expected.value_array)):
                self.assertFormFieldValueTransformCorrect(form_field.value[i], expected.value_array[i], read_results)
        if field_type == "object":
            self.assertFormFieldsTransformCorrect(form_field.value, expected.value_object, read_results)

        if field_type not in ["array", "object"] and form_field.value_data:
            self.assertBoundingBoxTransformCorrect(form_field.value_data.bounding_box, expected.bounding_box)
            assert expected.text == form_field.value_data.text
            assert expected.page == form_field.value_data.page_number
            if read_results:
                self.assertFieldElementsTransFormCorrect(
                    form_field.value_data.field_elements,
                    expected.elements,
                    read_results
                )

    def assertFormFieldsTransformCorrect(self, form_fields, generated_fields, read_results=None):
        if generated_fields is None:
            return

        for label, expected in generated_fields.items():
            if expected is None:  # None value occurs with labeled tables and empty cells
                continue
            field_type = expected.type
            assert adjust_value_type(field_type) == form_fields[label].value_type
            assert label == form_fields[label].name
            assert adjust_confidence(expected.confidence) == form_fields[label].confidence
            self.assertFormFieldValueTransformCorrect(form_fields[label], expected, read_results)

    def assertUnlabeledFormFieldDictTransformCorrect(self, form_fields, generated_fields, read_results=None):
        if generated_fields is None:
            return
        for idx, expected in enumerate(generated_fields):
            assert adjust_confidence(expected.confidence) == form_fields["field-"+str(idx)].confidence
            assert expected.key.text == form_fields["field-"+str(idx)].label_data.text
            self.assertBoundingBoxTransformCorrect(form_fields["field-"+str(idx)].label_data.bounding_box, expected.key.bounding_box)
            if read_results:
                self.assertFieldElementsTransFormCorrect(
                    form_fields["field-"+str(idx)].label_data.field_elements,
                    expected.key.elements,
                    read_results
                )
            assert expected.value.text == form_fields["field-" + str(idx)].value_data.text
            self.assertBoundingBoxTransformCorrect(form_fields["field-" + str(idx)].value_data.bounding_box, expected.value.bounding_box)
            if read_results:
                self.assertFieldElementsTransFormCorrect(
                    form_fields["field-"+str(idx)].value_data.field_elements,
                    expected.value.elements,
                    read_results
                )

    def assertTablesTransformCorrect(self, layout, expected_layout, read_results=None, **kwargs):
        for table, expected_table in zip(layout, expected_layout):
            assert table.row_count == expected_table.rows
            assert table.column_count == expected_table.columns
            self.assertBoundingBoxTransformCorrect(table.bounding_box, expected_table.bounding_box)
            for cell, expected_cell in zip(table.cells, expected_table.cells):
                assert table.page_number == cell.page_number
                assert cell.text == expected_cell.text
                assert cell.row_index == expected_cell.row_index
                assert cell.column_index == expected_cell.column_index
                assert cell.row_span == expected_cell.row_span if expected_cell.row_span is not None else 1
                assert cell.column_span == expected_cell.column_span if expected_cell.column_span is not None else 1
                assert cell.confidence == adjust_confidence(expected_cell.confidence)
                assert cell.is_header == (expected_cell.is_header if expected_cell.is_header is not None else False)
                assert cell.is_footer == (expected_cell.is_footer if expected_cell.is_footer is not None else False)
                self.assertBoundingBoxTransformCorrect(cell.bounding_box, expected_cell.bounding_box)
                self.assertFieldElementsTransFormCorrect(cell.field_elements, expected_cell.elements, read_results)

    def assertReceiptItemsHasValues(self, items, page_number, include_field_elements):
        for item in items:
            assert item.value_type == "dictionary"
            self.assertBoundingBoxHasPoints(item.value.get("Name").value_data.bounding_box)
            if item.value.get("Name", None):
                assert item.value.get("Name").confidence is not None
                assert item.value.get("Name").value_data.text is not None
                assert item.value.get("Name").value_type is not None
            if item.value.get("Quantity", None):
                self.assertBoundingBoxHasPoints(item.value.get("Quantity").value_data.bounding_box)
                assert item.value.get("Quantity").confidence is not None
                assert item.value.get("Quantity").value_data.text is not None
                assert item.value.get("Quantity").value_type is not None
            if item.value.get("TotalPrice", None):
                self.assertBoundingBoxHasPoints(item.value.get("TotalPrice").value_data.bounding_box)
                assert item.value.get("TotalPrice").confidence is not None
                assert item.value.get("TotalPrice").value_data.text is not None
                assert item.value.get("TotalPrice").value_type is not None
            if item.value.get("Price", None):
                self.assertBoundingBoxHasPoints(item.value.get("Price").value_data.bounding_box)
                assert item.value.get("Price").confidence is not None
                assert item.value.get("Price").value_data.text is not None
                assert item.value.get("Price").value_type is not None

            if include_field_elements:
                if item.value.get("Name", None):
                    self.assertFieldElementsHasValues(item.value.get("Name").value_data.field_elements, page_number)
                if item.value.get("Quantity", None):
                    self.assertFieldElementsHasValues(item.value.get("Quantity").value_data.field_elements, page_number)
                if item.value.get("TotalPrice", None):
                    self.assertFieldElementsHasValues(item.value.get("TotalPrice").value_data.field_elements, page_number)
                if item.value.get("Price", None):
                    self.assertFieldElementsHasValues(item.value.get("Price").value_data.field_elements, page_number)

    def assertInvoiceItemsHasValues(self, items, page_number, include_field_elements):
        for item in items:
            assert item.value_type == "dictionary"
            if item.value.get("Amount", None):
                self.assertBoundingBoxHasPoints(item.value.get("Amount").value_data.bounding_box)
                assert item.value.get("Amount").confidence is not None
                assert item.value.get("Amount").value_data.text is not None
                assert item.value.get("Amount").value_type is not None
            if item.value.get("Quantity", None):
                self.assertBoundingBoxHasPoints(item.value.get("Quantity").value_data.bounding_box)
                assert item.value.get("Quantity").confidence is not None
                assert item.value.get("Quantity").value_data.text is not None
                assert item.value.get("Quantity").value_type is not None
            if item.value.get("Description", None):
                self.assertBoundingBoxHasPoints(item.value.get("Description").value_data.bounding_box)
                assert item.value.get("Description").confidence is not None
                assert item.value.get("Description").value_data.text is not None
                assert item.value.get("Description").value_type is not None
            if item.value.get("UnitPrice", None):
                self.assertBoundingBoxHasPoints(item.value.get("UnitPrice").value_data.bounding_box)
                assert item.value.get("UnitPrice").confidence is not None
                assert item.value.get("UnitPrice").value_data.text is not None
                assert item.value.get("UnitPrice").value_type is not None
            if item.value.get("ProductCode", None):
                self.assertBoundingBoxHasPoints(item.value.get("ProductCode").value_data.bounding_box)
                assert item.value.get("ProductCode").confidence is not None
                assert item.value.get("ProductCode").value_data.text is not None
                assert item.value.get("ProductCode").value_type is not None
            if item.value.get("Unit", None):
                self.assertBoundingBoxHasPoints(item.value.get("Unit").value_data.bounding_box)
                assert item.value.get("Unit").confidence is not None
                assert item.value.get("Unit").value_data.text is not None
                assert item.value.get("Unit").value_type is not None
            if item.value.get("Date", None):
                self.assertBoundingBoxHasPoints(item.value.get("Date").value_data.bounding_box)
                assert item.value.get("Date").confidence is not None
                assert item.value.get("Date").value_data.text is not None
                assert item.value.get("Date").value_type is not None
            if item.value.get("Tax", None):
                self.assertBoundingBoxHasPoints(item.value.get("Tax").value_data.bounding_box)
                assert item.value.get("Tax").confidence is not None
                assert item.value.get("Tax").value_data.text is not None
                assert item.value.get("Tax").value_type is not None

            if include_field_elements:
                if item.value.get("Amount", None):
                    self.assertFieldElementsHasValues(item.value.get("Amount").value_data.field_elements, page_number)
                if item.value.get("Quantity", None):
                    self.assertFieldElementsHasValues(item.value.get("Quantity").value_data.field_elements, page_number)
                if item.value.get("Description", None):
                    self.assertFieldElementsHasValues(item.value.get("Description").value_data.field_elements, page_number)
                if item.value.get("UnitPrice", None):
                    self.assertFieldElementsHasValues(item.value.get("UnitPrice").value_data.field_elements, page_number)
                if item.value.get("ProductCode", None):
                    self.assertFieldElementsHasValues(item.value.get("ProductCode").value_data.field_elements, page_number)
                if item.value.get("Unit", None):
                    self.assertFieldElementsHasValues(item.value.get("Unit").value_data.field_elements, page_number)
                if item.value.get("Date", None):
                    self.assertFieldElementsHasValues(item.value.get("Date").value_data.field_elements, page_number)
                if item.value.get("Tax", None):
                    self.assertFieldElementsHasValues(item.value.get("Tax").value_data.field_elements, page_number)

    def assertBoundingBoxHasPoints(self, box):
        if box is None:
            return
        assert box[0].x is not None
        assert box[0].y is not None
        assert box[1].x is not None
        assert box[1].y is not None
        assert box[2].x is not None
        assert box[2].y is not None
        assert box[3].x is not None
        assert box[3].y is not None

    def assertFormPagesHasValues(self, pages):
        for page in pages:
            assert page.text_angle is not None
            assert page.height is not None
            assert page.unit is not None
            assert page.width is not None
            assert page.page_number is not None
            if page.lines:
                for line in page.lines:
                    self.assertFormLineHasValues(line, page.page_number)

            if page.tables:
                for table in page.tables:
                    assert table.page_number == page.page_number
                    assert table.row_count is not None
                    if table.bounding_box:
                        self.assertBoundingBoxHasPoints(table.bounding_box)
                    assert table.column_count is not None
                    for cell in table.cells:
                        assert cell.text is not None
                        assert cell.row_index is not None
                        assert cell.column_index is not None
                        assert cell.row_span is not None
                        assert cell.column_span is not None
                        self.assertBoundingBoxHasPoints(cell.bounding_box)
                        self.assertFieldElementsHasValues(cell.field_elements, page.page_number)

            if page.selection_marks:
                for selection_mark in page.selection_marks:
                    assert selection_mark.text is None
                    assert selection_mark.page_number == page.page_number
                    self.assertBoundingBoxHasPoints(selection_mark.bounding_box)
                    assert selection_mark.confidence is not None
                    assert (selection_mark.state in ["selected", "unselected"]) == True

    def assertFormWordHasValues(self, word, page_number):
        assert word.confidence is not None
        assert word.text is not None
        self.assertBoundingBoxHasPoints(word.bounding_box)
        assert word.page_number == page_number

    def assertFormLineHasValues(self, line, page_number):
        assert line.text is not None
        self.assertBoundingBoxHasPoints(line.bounding_box)
        if line.appearance:
            assert line.appearance.style_name is not None
            assert line.appearance.style_confidence is not None
        assert line.page_number == page_number
        for word in line.words:
            self.assertFormWordHasValues(word, page_number)

    def assertFormSelectionMarkHasValues(self, selection_mark, page_number):
        assert selection_mark.confidence is not None
        assert selection_mark.state is not None
        self.assertBoundingBoxHasPoints(selection_mark.bounding_box)
        assert selection_mark.page_number == page_number

    def assertFieldElementsHasValues(self, elements, page_number):
        if elements is None:
            return
        for element in elements:
            if element.kind == "word":
                self.assertFormWordHasValues(element, page_number)
            elif element.kind == "line":
                self.assertFormLineHasValues(element, page_number)
            elif element.kind == "selectionMark":
                self.assertFormSelectionMarkHasValues(element, page_number)

    def assertComposedModelV2HasValues(self, composed, model_1, model_2):
        assert composed.model_id
        assert composed.errors == []
        assert composed.properties.is_composed_model
        assert composed.status
        assert composed.training_started_on
        assert composed.training_completed_on

        all_training_documents = model_1.training_documents + model_2.training_documents
        for doc, composed_doc in zip(all_training_documents, composed.training_documents):
            assert doc.name == composed_doc.name
            assert doc.status == composed_doc.status
            assert doc.page_count == composed_doc.page_count
            assert doc.errors == composed_doc.errors

        for model in model_1.submodels:
            composed_model = composed.submodels[0]
            if model.model_id != composed_model.model_id:  # order not guaranteed from service
                composed_model = composed.submodels[1]
            if model_1.model_name is None:
                assert model.form_type == composed_model.form_type
            assert model.accuracy == composed_model.accuracy
            assert model.model_id == composed_model.model_id
            for field, value in model.fields.items():
                assert value.name == composed_model.fields[field].name
                assert value.accuracy == composed_model.fields[field].accuracy

        for model in model_2.submodels:
            composed_model = composed.submodels[1]
            if model.model_id != composed_model.model_id:  # order not guaranteed from service
                composed_model = composed.submodels[0]
            if model_2.model_name is None:
                assert model.form_type == composed_model.form_type
            assert model.accuracy == composed_model.accuracy
            assert model.model_id == composed_model.model_id
            for field, value in model.fields.items():
                assert value.name == composed_model.fields[field].name
                assert value.accuracy == composed_model.fields[field].accuracy

    def assertUnlabeledRecognizedFormHasValues(self, form, model):
        assert form.form_type_confidence is None
        assert form.model_id == model.model_id
        self.assertFormPagesHasValues(form.pages)
        for label, field in form.fields.items():
            assert field.confidence is not None
            assert field.name is not None
            assert field.value is not None
            assert field.value_data.text is not None
            assert field.label_data.text is not None

    def assertLabeledRecognizedFormHasValues(self, form, model):
        assert form.form_type_confidence is not None
        assert form.model_id == model.model_id
        self.assertFormPagesHasValues(form.pages)
        for label, field in form.fields.items():
            assert field.confidence is not None
            assert field.name is not None
            assert field.value_data.text is not None
            assert field.value_data.bounding_box is not None

    def assertDocumentTransformCorrect(self, transformed_documents, raw_documents, **kwargs):
        if transformed_documents == [] and not raw_documents:
            return
        for document, expected in zip(transformed_documents, raw_documents):
            assert document.doc_type == expected.doc_type
            assert document.confidence == expected.confidence
            for span, expected_span in zip(document.spans or [], expected.spans or []):
                self.assertSpanTransformCorrect(span, expected_span)

            self.assertBoundingRegionsTransformCorrect(document.bounding_regions, expected.bounding_regions)

            self.assertDocumentFieldsTransformCorrect(document.fields, expected.fields)

    def assertDocumentKeyValuePairsTransformCorrect(self, transformed_key_value, raw_key_value, **kwargs):
        if transformed_key_value == [] and not raw_key_value:
            return
        for key_value, expected in zip(transformed_key_value, raw_key_value):
            self.assertDocumentKeyValueElementTransformCorrect(key_value.key, expected.key)
            self.assertDocumentKeyValueElementTransformCorrect(key_value.value, expected.value)
            assert key_value.confidence == expected.confidence

    def assertDocumentLanguagesTransformCorrect(self, transformed_languages, raw_languages, **kwargs):
        if transformed_languages == [] and not raw_languages:
            return
        for lang, expected in zip(transformed_languages, raw_languages):
            assert lang.language_code == expected.language_code
            for span, expected_span in zip(lang.spans or [], expected.spans or []):
                self.assertSpanTransformCorrect(span, expected_span)
            assert lang.confidence == expected.confidence

    def assertDocumentEntitiesTransformCorrect(self, transformed_entity, raw_entity, **kwargs):
        if transformed_entity == [] and not raw_entity:
            return
        
        for entity, expected in zip(transformed_entity, raw_entity):
            assert entity.category == expected.category
            assert entity.sub_category == expected.sub_category
            assert entity.content == expected.content
            assert entity.confidence == expected.confidence
            
            for span, expected_span in zip(entity.spans or [], expected.spans or []):
                    self.assertSpanTransformCorrect(span, expected_span)
                
            self.assertBoundingRegionsTransformCorrect(entity.bounding_regions, expected.bounding_regions)

    def assertDocumentStylesTransformCorrect(self, transformed_styles, raw_styles, **kwargs):
        if transformed_styles == [] and not raw_styles:
            return
        
        for style, expected in zip(transformed_styles, raw_styles):
            assert style.is_handwritten == expected.is_handwritten
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
        if transformed_tables == [] and not raw_tables:
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
        else:
            assert transformed_cell.kind == "content"
        assert transformed_cell.row_index == raw_cell.row_index
        assert transformed_cell.column_index == raw_cell.column_index
        if raw_cell.row_span:
            assert transformed_cell.row_span == raw_cell.row_span
        else:
            assert transformed_cell.row_span == 1
        if raw_cell.column_span:
            assert transformed_cell.column_span == raw_cell.column_span
        else:
            assert transformed_cell.column_span == 1
        assert transformed_cell.content == raw_cell.content

        for span, expected_span in zip(transformed_cell.spans or [], raw_cell.spans or []):
                self.assertSpanTransformCorrect(span, expected_span)
            
        self.assertBoundingRegionsTransformCorrect(transformed_cell.bounding_regions, raw_cell.bounding_regions)

    def assertDocumentPagesTransformCorrect(self, transformed_pages, raw_pages, **kwargs):
        for page, expected_page in zip(transformed_pages, raw_pages):
            assert page.page_number == expected_page.page_number
            assert page.angle == adjust_text_angle(expected_page.angle)
            assert page.width == expected_page.width
            assert page.height == expected_page.height
            assert page.unit == expected_page.unit

            for line, expected_line in zip(page.lines or [], expected_page.lines or []):
                self.assertDocumentLineTransformCorrect(line, expected_line)

            for word, expected_word in zip(page.words or [], expected_page.words or []):
                self.assertDocumentWordTransformCorrect(word, expected_word)

            for selection_mark, expected_selection_mark in zip(page.selection_marks or [], expected_page.selection_marks or []):
                self.assertDocumentSelectionMarkTransformCorrect(selection_mark, expected_selection_mark)

            for span, expected_span in zip(page.spans or [], expected_page.spans or []):
                self.assertSpanTransformCorrect(span, expected_span)

    def assertDocumentLineTransformCorrect(self, line, expected):
        assert line.content == expected.content
        self.assertBoundingBoxTransformCorrect(line.bounding_box, expected.bounding_box)
        for transformed_span, span in zip(line.spans or [], expected.spans or []):
            self.assertSpanTransformCorrect(transformed_span, span)

    def assertDocumentWordTransformCorrect(self, word, expected):
        assert word.kind == "word"
        assert word.content == expected.content
        self.assertBoundingBoxTransformCorrect(word.bounding_box, expected.bounding_box)
        self.assertSpanTransformCorrect(word.span, expected.span)

    def assertSpanTransformCorrect(self, span, expected):
        if span is None and expected is None:
            return
        assert span.offset == expected.offset
        assert span.length == expected.length

    def assertDocumentSelectionMarkTransformCorrect(self, selection_mark, expected):
        assert selection_mark.kind == "selectionMark"
        assert selection_mark.confidence == adjust_confidence(expected.confidence)
        assert selection_mark.state == expected.state
        self.assertBoundingBoxTransformCorrect(selection_mark.bounding_box, expected.bounding_box)

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
            assert (expected.content == document_fields[label].content) or (expected.content == '' and not document_fields[label].content)
            self.assertDocumentFieldValueTransformCorrect(document_fields[label], expected)

            for span, expected_span in zip(document_fields[label].spans or [], expected.spans or []):
                self.assertSpanTransformCorrect(span, expected_span)

            self.assertBoundingRegionsTransformCorrect(document_fields[label].bounding_regions, expected.bounding_regions)

    def assertBoundingRegionsTransformCorrect(self, bounding_regions, expected):
        if bounding_regions == [] and not expected:
            return
        for region, expected_region in zip(bounding_regions, expected):
            assert region.page_number == expected_region.page_number
            self.assertBoundingBoxTransformCorrect(region.bounding_box, expected_region.bounding_box)
            

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
        if field_type == "array":
            for i in range(len(expected.value_array)):
                self.assertDocumentFieldValueTransformCorrect(document_field.value[i], expected.value_array[i])
        if field_type == "object":
            self.assertDocumentFieldsTransformCorrect(document_field.value, expected.value_object)
