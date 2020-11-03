
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


import os
import time
import six
import pytest
import logging
from azure.core.credentials import AzureKeyCredential, AccessToken
from azure.ai.formrecognizer._helpers import (
    adjust_value_type,
    get_element,
    adjust_confidence,
    adjust_text_angle
)
from devtools_testutils import (
    AzureTestCase,
    AzureMgmtPreparer,
    FakeResource,
    ResourceGroupPreparer,
)
from devtools_testutils.cognitiveservices_testcase import CognitiveServicesAccountPreparer
from azure_devtools.scenario_tests import (
    RecordingProcessor,
    ReplayableTest
)
from azure_devtools.scenario_tests.utilities import is_text_payload

LOGGING_FORMAT = '%(asctime)s %(name)-20s %(levelname)-5s %(message)s'
ENABLE_LOGGER = os.getenv('ENABLE_LOGGER', "False")
REGION = os.getenv('REGION', 'centraluseuap')


class RequestBodyReplacer(RecordingProcessor):
    """Replace request body when a file is read."""

    def __init__(self, max_request_body=128):
        self._max_request_body = max_request_body

    def process_request(self, request):
        try:
            if request.body and six.binary_type(request.body) and len(request.body) > self._max_request_body * 1024:
                request.body = '!!! The request body has been omitted from the recording because its ' \
                               'size {} is larger than {}KB. !!!'.format(len(request.body),
                                                                         self._max_request_body)
        except TypeError:
            pass
        return request


class AccessTokenReplacer(RecordingProcessor):
    """Replace the access token in a request/response body."""

    def __init__(self, replacement='redacted'):

        self._replacement = replacement

    def process_request(self, request):
        import re
        if is_text_payload(request) and request.body:
            body = str(request.body)
            body = re.sub(r'"accessToken": "([0-9a-f-]{36})"', r'"accessToken": 00000000-0000-0000-0000-000000000000', body)
            request.body = body
        return request

    def process_response(self, response):
        import json
        try:
            body = json.loads(response['body']['string'])
            if 'accessToken' in body:
                body['accessToken'] = self._replacement
            response['body']['string'] = json.dumps(body)
            return response
        except (KeyError, ValueError):
            return response


class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    def get_token(self, *args):
        return self.token


class FormRecognizerTest(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['Ocp-Apim-Subscription-Key']

    def __init__(self, method_name):
        super(FormRecognizerTest, self).__init__(method_name)
        self.recording_processors.append(AccessTokenReplacer())
        self.recording_processors.append(RequestBodyReplacer())
        self.configure_logging()

        # URL samples
        self.receipt_url_jpg = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/receipt/contoso-allinone.jpg"
        self.receipt_url_png = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/receipt/contoso-receipt.png"
        self.business_card_url_jpg = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/business_cards/business-card-english.jpg"
        self.business_card_url_png = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/business_cards/business-card-english.png"
        self.business_card_multipage_url_pdf = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/business_cards/business-card-multipage.pdf"
        self.invoice_url_pdf = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/Invoice_1.pdf"
        self.invoice_url_tiff = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/Invoice_1.tiff"
        self.form_url_jpg = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/Form_1.jpg"
        self.multipage_url_pdf = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/multipage_invoice1.pdf"
        self.multipage_table_url_pdf = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/multipagelayout.pdf"
        self.selection_mark_url_pdf = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/selection_mark_form.pdf"

        # file stream samples
        self.receipt_jpg = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/receipt/contoso-allinone.jpg"))
        self.receipt_png = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/receipt/contoso-receipt.png"))
        self.business_card_jpg = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/business_cards/business-card-english.jpg"))
        self.business_card_png = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/business_cards/business-card-english.png"))
        self.business_card_multipage_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/business_cards/business-card-multipage.pdf"))
        self.invoice_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Invoice_1.pdf"))
        self.invoice_tiff = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Invoice_1.tiff"))
        self.form_jpg = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Form_1.jpg"))
        self.blank_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/blank.pdf"))
        self.multipage_invoice_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/multipage_invoice1.pdf"))
        self.unsupported_content_py = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./conftest.py"))
        self.multipage_table_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/multipagelayout.pdf"))
        self.multipage_vendor_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/multi1.pdf"))
        self.selection_form_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/selection_mark_form.pdf"))

    def get_oauth_endpoint(self):
        return self.get_settings_value("FORM_RECOGNIZER_AAD_ENDPOINT")

    def generate_oauth_token(self):
        if self.is_live:
            from azure.identity import ClientSecretCredential
            return ClientSecretCredential(
                self.get_settings_value("TENANT_ID"),
                self.get_settings_value("CLIENT_ID"),
                self.get_settings_value("CLIENT_SECRET"),
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

    def assertModelTransformCorrect(self, model, expected, unlabeled=False):
        self.assertEqual(model.model_id, expected.model_info.model_id)
        self.assertEqual(model.training_started_on, expected.model_info.created_date_time)
        self.assertEqual(model.training_completed_on, expected.model_info.last_updated_date_time)
        self.assertEqual(model.status, expected.model_info.status)
        self.assertEqual(model.errors, expected.train_result.errors)
        for m, a in zip(model.training_documents, expected.train_result.training_documents):
            self.assertEqual(m.name, a.document_name)
            if m.errors and a.errors:
                self.assertEqual(m.errors, a.errors)
            self.assertEqual(m.page_count, a.pages)
            self.assertEqual(m.status, a.status)

        if unlabeled:
            if expected.keys.clusters:
                for cluster_id, fields in expected.keys.clusters.items():
                    self.assertEqual(cluster_id, model.submodels[int(cluster_id)].form_type[-1])
                    for field_idx, model_field in model.submodels[int(cluster_id)].fields.items():
                        self.assertIn(model_field.label, fields)

        else:
            if expected.train_result:
                if expected.train_result.fields:
                    for a in expected.train_result.fields:
                        self.assertEqual(model.submodels[0].fields[a.field_name].name, a.field_name)
                        self.assertEqual(model.submodels[0].fields[a.field_name].accuracy, a.accuracy)
                    self.assertEqual(model.submodels[0].form_type, "custom:"+model.model_id)
                    self.assertEqual(model.submodels[0].accuracy, expected.train_result.average_model_accuracy)

    def assertFormPagesTransformCorrect(self, form_pages, read_result, page_result=None, **kwargs):
        for page, expected_page in zip(form_pages, read_result):
            if hasattr(page, "pages"):  # this is necessary for how unlabeled forms are structured
                page = page.pages[0]
            self.assertEqual(page.page_number, expected_page.page)
            self.assertEqual(page.text_angle, adjust_text_angle(expected_page.angle))
            self.assertEqual(page.width, expected_page.width)
            self.assertEqual(page.height, expected_page.height)
            self.assertEqual(page.unit, expected_page.unit)

            for line, expected_line in zip(page.lines or [], expected_page.lines or []):
                self.assertFormLineTransformCorrect(line, expected_line)

            for selection_mark, expected_selection_mark in zip(page.selection_marks or [], expected_page.selection_marks or []):
                self.assertFormSelectionMarkTransformCorrect(selection_mark, expected_selection_mark)

        if page_result:
            for page, expected_page in zip(form_pages, page_result):
                if hasattr(page, "pages"):  # this is necessary for how unlabeled forms are structured
                    page = page.pages[0]
                self.assertTablesTransformCorrect(page.tables, expected_page.tables, read_result, **kwargs)

    def assertBoundingBoxTransformCorrect(self, box, expected):
        if box is None and expected is None:
            return
        self.assertEqual(box[0].x, expected[0])
        self.assertEqual(box[0].y, expected[1])
        self.assertEqual(box[1].x, expected[2])
        self.assertEqual(box[1].y, expected[3])
        self.assertEqual(box[2].x, expected[4])
        self.assertEqual(box[2].y, expected[5])
        self.assertEqual(box[3].x, expected[6])
        self.assertEqual(box[3].y, expected[7])

    def assertFormWordTransformCorrect(self, word, expected):
        self.assertEqual(word.text, expected.text)
        self.assertEqual(word.confidence, adjust_confidence(expected.confidence))
        self.assertEqual(word.kind, "word")
        self.assertBoundingBoxTransformCorrect(word.bounding_box, expected.bounding_box)

    def assertFormLineTransformCorrect(self, line, expected):
        self.assertEqual(line.kind, "line")
        self.assertEqual(line.text, expected.text)
        self.assertBoundingBoxTransformCorrect(line.bounding_box, expected.bounding_box)
        if expected.appearance:
            self.assertEqual(line.appearance.style.name, expected.appearance.style.name)
            self.assertEqual(line.appearance.style.confidence, expected.appearance.style.confidence)
        for word, expected_word in zip(line.words, expected.words):
            self.assertFormWordTransformCorrect(word, expected_word)

    def assertFormSelectionMarkTransformCorrect(self, selection_mark, expected):
        self.assertEqual(selection_mark.kind, "selectionMark")
        self.assertEqual(selection_mark.confidence, adjust_confidence(expected.confidence))
        self.assertEqual(selection_mark.state, expected.state)
        self.assertBoundingBoxTransformCorrect(selection_mark.bounding_box, expected.bounding_box)

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
                self.assertFormSelectionMarkTransformCorrect(element, expected)

    def assertLabeledFormFieldDictTransformCorrect(self, form_fields, generated_fields, read_results=None):
        if generated_fields is None:
            return

        for label, expected in generated_fields.items():
            self.assertEqual(label, form_fields[label].name)
            self.assertEqual(adjust_confidence(expected.confidence), form_fields[label].confidence)
            self.assertBoundingBoxTransformCorrect(form_fields[label].value_data.bounding_box, expected.bounding_box)
            self.assertEqual(expected.text, form_fields[label].value_data.text)
            field_type = expected.type
            self.assertEqual(adjust_value_type(field_type), form_fields[label].value_type)
            if field_type == "string":
                self.assertEqual(form_fields[label].value, expected.value_string)
            if field_type == "number":
                self.assertEqual(form_fields[label].value, expected.value_number)
            if field_type == "integer":
                self.assertEqual(form_fields[label].value, expected.value_integer)
            if field_type == "date":
                self.assertEqual(form_fields[label].value, expected.value_date)
            if field_type == "phoneNumber":
                self.assertEqual(form_fields[label].value, expected.value_phone_number)
            if field_type == "time":
                self.assertEqual(form_fields[label].value, expected.value_time)
            if read_results:
                self.assertFieldElementsTransFormCorrect(
                    form_fields[label].value_data.field_elements,
                    expected.elements,
                    read_results
                )

    def assertUnlabeledFormFieldDictTransformCorrect(self, form_fields, generated_fields, read_results=None):
        if generated_fields is None:
            return
        for idx, expected in enumerate(generated_fields):
            self.assertEqual(adjust_confidence(expected.confidence), form_fields["field-"+str(idx)].confidence)
            self.assertEqual(expected.key.text, form_fields["field-"+str(idx)].label_data.text)
            self.assertBoundingBoxTransformCorrect(form_fields["field-"+str(idx)].label_data.bounding_box, expected.key.bounding_box)
            if read_results:
                self.assertFieldElementsTransFormCorrect(
                    form_fields["field-"+str(idx)].label_data.field_elements,
                    expected.key.elements,
                    read_results
                )
            self.assertEqual(expected.value.text, form_fields["field-" + str(idx)].value_data.text)
            self.assertBoundingBoxTransformCorrect(form_fields["field-" + str(idx)].value_data.bounding_box, expected.value.bounding_box)
            if read_results:
                self.assertFieldElementsTransFormCorrect(
                    form_fields["field-"+str(idx)].value_data.field_elements,
                    expected.value.elements,
                    read_results
                )

    def _assertFormFieldTransformCorrectHelper(self, receipt_field, generated_field, read_results=None):
        field_type = generated_field.type
        self.assertEqual(adjust_value_type(field_type), receipt_field.value_type)
        if field_type == "string":
            self.assertEqual(receipt_field.value, generated_field.value_string)
        elif field_type == "number":
            self.assertEqual(receipt_field.value, generated_field.value_number)
        elif field_type == "integer":
            self.assertEqual(receipt_field.value, generated_field.value_integer)
        elif field_type == "date":
            self.assertEqual(receipt_field.value, generated_field.value_date)
        elif field_type == "phoneNumber":
            self.assertEqual(receipt_field.value, generated_field.value_phone_number)
        elif field_type == "time":
            self.assertEqual(receipt_field.value, generated_field.value_time)
        elif field_type == "object":
            self.assertLabeledFormFieldDictTransformCorrect(receipt_field.value, generated_field.value_object)
        else:
            raise ValueError('field type {} not valid'.format(field_type))


        self.assertBoundingBoxTransformCorrect(receipt_field.value_data.bounding_box, generated_field.bounding_box)
        self.assertEqual(receipt_field.value_data.text, generated_field.text)
        self.assertEqual(receipt_field.confidence, adjust_confidence(generated_field.confidence))
        if read_results:
            self.assertFieldElementsTransFormCorrect(
                receipt_field.value_data.field_elements,
                generated_field.elements,
                read_results
            )

    def assertFormFieldTransformCorrect(self, receipt_field, generated_field, read_results=None):
        if generated_field is None:
            return
        field_type = generated_field.type
        if field_type == "array":
            for i in range(len(generated_field.value_array)):
                self._assertFormFieldTransformCorrectHelper(receipt_field.value[i], generated_field.value_array[i], read_results)
        else:
            self._assertFormFieldTransformCorrectHelper(receipt_field, generated_field, read_results)


    def assertReceiptItemsTransformCorrect(self, items, generated_items, read_results=None):
        expected_items = generated_items.value_array

        for r, expected in zip(items, expected_items):
            self.assertFormFieldTransformCorrect(r.value.get("Name"), expected.value_object.get("Name"), read_results)
            self.assertFormFieldTransformCorrect(r.value.get("Quantity"), expected.value_object.get("Quantity"), read_results)
            self.assertFormFieldTransformCorrect(r.value.get("TotalPrice"), expected.value_object.get("TotalPrice"), read_results)
            self.assertFormFieldTransformCorrect(r.value.get("Price"), expected.value_object.get("Price"), read_results)

    def assertBusinessCardTransformCorrect(self, business_card, expected, read_results=None):
        self.assertFormFieldTransformCorrect(business_card.fields.get("ContactNames"), expected.get("ContactNames"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("JobTitles"), expected.get("JobTitles"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("Departments"), expected.get("Departments"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("Emails"), expected.get("Emails"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("Websites"), expected.get("Websites"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("MobilePhones"), expected.get("MobilePhones"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("OtherPhones"), expected.get("OtherPhones"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("Faxes"), expected.get("Faxes"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("Addresses"), expected.get("Addresses"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("CompanyNames"), expected.get("CompanyNames"), read_results)

    def assertInvoiceTransformCorrect(self, invoice, expected, read_results=None):
        self.assertFormFieldTransformCorrect(invoice.fields.get("VendorName"), expected.get("VendorName"), read_results)
        self.assertFormFieldTransformCorrect(invoice.fields.get("VendorAddress"), expected.get("VendorAddress"), read_results)
        self.assertFormFieldTransformCorrect(invoice.fields.get("CustomerAddressRecipient"), expected.get("CustomerAddressRecipient"), read_results)
        self.assertFormFieldTransformCorrect(invoice.fields.get("CustomerAddress"), expected.get("CustomerAddress"), read_results)
        self.assertFormFieldTransformCorrect(invoice.fields.get("CustomerName"), expected.get("CustomerName"), read_results)
        self.assertFormFieldTransformCorrect(invoice.fields.get("InvoiceId"), expected.get("InvoiceId"), read_results)
        self.assertFormFieldTransformCorrect(invoice.fields.get("InvoiceDate"), expected.get("InvoiceDate"), read_results)
        self.assertFormFieldTransformCorrect(invoice.fields.get("InvoiceTotal"), expected.get("InvoiceTotal"), read_results)
        self.assertFormFieldTransformCorrect(invoice.fields.get("DueDate"), expected.get("DueDate"), read_results)

    def assertTablesTransformCorrect(self, layout, expected_layout, read_results=None, **kwargs):
        for table, expected_table in zip(layout, expected_layout):
            self.assertEqual(table.row_count, expected_table.rows)
            self.assertEqual(table.column_count, expected_table.columns)
            self.assertBoundingBoxTransformCorrect(table.bounding_box, expected_table.bounding_box)
            for cell, expected_cell in zip(table.cells, expected_table.cells):
                self.assertEqual(table.page_number, cell.page_number)
                self.assertEqual(cell.text, expected_cell.text)
                self.assertEqual(cell.row_index, expected_cell.row_index)
                self.assertEqual(cell.column_index, expected_cell.column_index)
                self.assertEqual(cell.row_span, expected_cell.row_span if expected_cell.row_span is not None else 1)
                self.assertEqual(cell.column_span, expected_cell.column_span if expected_cell.column_span is not None else 1)
                self.assertEqual(cell.confidence, adjust_confidence(expected_cell.confidence))
                self.assertEqual(cell.is_header, expected_cell.is_header if expected_cell.is_header is not None else False)
                self.assertEqual(cell.is_footer, expected_cell.is_footer if expected_cell.is_footer is not None else False)
                self.assertBoundingBoxTransformCorrect(cell.bounding_box, expected_cell.bounding_box)
                self.assertFieldElementsTransFormCorrect(cell.field_elements, expected_cell.elements, read_results)

    def assertReceiptItemsHasValues(self, items, page_number, include_field_elements):
        for item in items:
            self.assertEqual(item.value_type, "dictionary")
            self.assertBoundingBoxHasPoints(item.value.get("Name").value_data.bounding_box)
            self.assertIsNotNone(item.value.get("Name").confidence)
            self.assertIsNotNone(item.value.get("Name").value_data.text)
            self.assertIsNotNone(item.value.get("Name").value_type)
            self.assertBoundingBoxHasPoints(item.value.get("Quantity").value_data.bounding_box)
            self.assertIsNotNone(item.value.get("Quantity").confidence)
            self.assertIsNotNone(item.value.get("Quantity").value_data.text)
            self.assertIsNotNone(item.value.get("Quantity").value_type)
            self.assertBoundingBoxHasPoints(item.value.get("TotalPrice").value_data.bounding_box)
            self.assertIsNotNone(item.value.get("TotalPrice").confidence)
            self.assertIsNotNone(item.value.get("TotalPrice").value_data.text)
            self.assertIsNotNone(item.value.get("TotalPrice").value_type)

            if include_field_elements:
                self.assertFieldElementsHasValues(item.value.get("Name").value_data.field_elements, page_number)
                self.assertFieldElementsHasValues(item.value.get("Quantity").value_data.field_elements, page_number)
                self.assertFieldElementsHasValues(item.value.get("TotalPrice").value_data.field_elements, page_number)
            else:
                self.assertIsNone(item.value.get("Name").value_data.field_elements)
                self.assertIsNone(item.value.get("Quantity").value_data.field_elements)
                self.assertIsNone(item.value.get("TotalPrice").value_data.field_elements)

    def assertBoundingBoxHasPoints(self, box):
        if box is None:
            return
        self.assertIsNotNone(box[0].x)
        self.assertIsNotNone(box[0].y)
        self.assertIsNotNone(box[1].x)
        self.assertIsNotNone(box[1].y)
        self.assertIsNotNone(box[2].x)
        self.assertIsNotNone(box[2].y)
        self.assertIsNotNone(box[3].x)
        self.assertIsNotNone(box[3].y)

    def assertFormPagesHasValues(self, pages):
        for page in pages:
            self.assertIsNotNone(page.text_angle)
            self.assertIsNotNone(page.height)
            self.assertIsNotNone(page.unit)
            self.assertIsNotNone(page.width)
            self.assertIsNotNone(page.page_number)
            if page.lines:
                for line in page.lines:
                    self.assertFormLineHasValues(line, page.page_number)

            if page.tables:
                for table in page.tables:
                    self.assertEqual(table.page_number, page.page_number)
                    self.assertIsNotNone(table.row_count)
                    if table.bounding_box:
                        self.assertBoundingBoxHasPoints(table.bounding_box)
                    self.assertIsNotNone(table.column_count)
                    for cell in table.cells:
                        self.assertIsNotNone(cell.text)
                        self.assertIsNotNone(cell.row_index)
                        self.assertIsNotNone(cell.column_index)
                        self.assertIsNotNone(cell.row_span)
                        self.assertIsNotNone(cell.column_span)
                        self.assertBoundingBoxHasPoints(cell.bounding_box)
                        self.assertFieldElementsHasValues(cell.field_elements, page.page_number)

            if page.selection_marks:
                for selection_mark in page.selection_marks:
                    self.assertIsNone(selection_mark.text)
                    self.assertEqual(selection_mark.page_number, page.page_number)
                    self.assertBoundingBoxHasPoints(selection_mark.bounding_box)
                    self.assertIsNotNone(selection_mark.confidence)
                    self.assertTrue(selection_mark.state in ["selected", "unselected"])

    def assertFormWordHasValues(self, word, page_number):
        self.assertIsNotNone(word.confidence)
        self.assertIsNotNone(word.text)
        self.assertBoundingBoxHasPoints(word.bounding_box)
        self.assertEqual(word.page_number, page_number)

    def assertFormLineHasValues(self, line, page_number):
        self.assertIsNotNone(line.text)
        self.assertBoundingBoxHasPoints(line.bounding_box)
        if line.appearance:
            self.assertIsNotNone(line.appearance.style.name)
            self.assertIsNotNone(line.appearance.style.confidence)
        self.assertEqual(line.page_number, page_number)
        for word in line.words:
            self.assertFormWordHasValues(word, page_number)

    def assertFormSelectionMarkHasValues(self, selection_mark, page_number):
        self.assertIsNotNone(selection_mark.confidence)
        self.assertIsNotNone(selection_mark.state)
        self.assertBoundingBoxHasPoints(selection_mark.bounding_box)
        self.assertEqual(selection_mark.page_number, page_number)

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

    def assertComposedModelHasValues(self, composed, model_1, model_2):
        self.assertIsNotNone(composed.model_id)
        self.assertIsNone(composed.errors)
        self.assertTrue(composed.properties.is_composed_model)
        self.assertIsNotNone(composed.status)
        self.assertIsNotNone(composed.training_started_on)
        self.assertIsNotNone(composed.training_completed_on)

        all_training_documents = model_1.training_documents + model_2.training_documents
        for doc, composed_doc in zip(all_training_documents, composed.training_documents):
            self.assertEqual(doc.name, composed_doc.name)
            self.assertEqual(doc.status, composed_doc.status)
            self.assertEqual(doc.page_count, composed_doc.page_count)
            self.assertEqual(doc.errors, composed_doc.errors)

        for model in model_1.submodels:
            composed_model = composed.submodels[0]
            if model.model_id != composed_model.model_id:  # order not guaranteed from service
                composed_model = composed.submodels[1]
            if model_1.model_name is None:
                self.assertEqual(model.form_type, composed_model.form_type)
            self.assertEqual(model.accuracy, composed_model.accuracy)
            self.assertEqual(model.model_id, composed_model.model_id)
            for field, value in model.fields.items():
                self.assertEqual(value.name, composed_model.fields[field].name)
                self.assertEqual(value.accuracy, composed_model.fields[field].accuracy)

        for model in model_2.submodels:
            composed_model = composed.submodels[1]
            if model.model_id != composed_model.model_id:  # order not guaranteed from service
                composed_model = composed.submodels[0]
            if model_2.model_name is None:
                self.assertEqual(model.form_type, composed_model.form_type)
            self.assertEqual(model.accuracy, composed_model.accuracy)
            self.assertEqual(model.model_id, composed_model.model_id)
            for field, value in model.fields.items():
                self.assertEqual(value.name, composed_model.fields[field].name)
                self.assertEqual(value.accuracy, composed_model.fields[field].accuracy)

    def assertUnlabeledRecognizedFormHasValues(self, form, model):
        self.assertIsNone(form.form_type_confidence)
        self.assertEqual(form.model_id, model.model_id)
        self.assertFormPagesHasValues(form.pages)
        for label, field in form.fields.items():
            self.assertIsNotNone(field.confidence)
            self.assertIsNotNone(field.name)
            self.assertIsNotNone(field.value)
            self.assertIsNotNone(field.value_data.text)
            self.assertIsNotNone(field.label_data.text)

    def assertLabeledRecognizedFormHasValues(self, form, model):
        self.assertEqual(form.form_type_confidence, 1.0)
        self.assertEqual(form.model_id, model.model_id)
        self.assertFormPagesHasValues(form.pages)
        for label, field in form.fields.items():
            self.assertIsNotNone(field.confidence)
            self.assertIsNotNone(field.name)
            self.assertIsNotNone(field.value_data.text)
            self.assertIsNotNone(field.value_data.bounding_box)


class GlobalResourceGroupPreparer(AzureMgmtPreparer):
    def __init__(self):
        super(GlobalResourceGroupPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )

    def create_resource(self, name, **kwargs):
        rg = FormRecognizerTest._RESOURCE_GROUP
        if self.is_live:
            self.test_class_instance.scrubber.register_name_pair(
                rg.name,
                "rgname"
            )
        else:
            rg = FakeResource(
                name="rgname",
                id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rgname"
            )

        return {
            'location': REGION,
            'resource_group': rg,
        }


class GlobalFormRecognizerAccountPreparer(AzureMgmtPreparer):
    def __init__(self):
        super(GlobalFormRecognizerAccountPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )

    def create_resource(self, name, **kwargs):
        form_recognizer_account = FormRecognizerTest._FORM_RECOGNIZER_ACCOUNT
        return {
            'location': REGION,
            'resource_group': FormRecognizerTest._RESOURCE_GROUP,
            'form_recognizer_account': form_recognizer_account,
            'form_recognizer_account_key': FormRecognizerTest._FORM_RECOGNIZER_KEY
        }


class GlobalClientPreparer(AzureMgmtPreparer):
    def __init__(self, client_cls, client_kwargs={}, **kwargs):
        super(GlobalClientPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )
        self.client_kwargs = client_kwargs
        self.client_cls = client_cls
        self.training = kwargs.get("training", False)
        self.multipage_test = kwargs.get("multipage", False)
        self.multipage_test_2 = kwargs.get("multipage2", False)
        self.selection_marks = kwargs.get("selection_marks", False)
        self.need_blob_sas_url = kwargs.get("blob_sas_url", False)
        self.copy = kwargs.get("copy", False)

    def _load_settings(self):
        try:
            from devtools_testutils import mgmt_settings_real as real_settings
            return real_settings
        except ImportError:
            return False

    def get_settings_value(self, key):
        key_value = os.environ.get("AZURE_"+key, None)
        self._real_settings = self._load_settings()

        if key_value and self._real_settings and getattr(self._real_settings, key) != key_value:
            raise ValueError(
                "You have both AZURE_{key} env variable and mgmt_settings_real.py for {key} to difference values"
                .format(key=key))

        if not key_value:
            try:
                key_value = getattr(self._real_settings, key)
            except Exception:
                print("Could not get {}".format(key))
                raise
        return key_value

    def get_training_parameters(self, client):
        if self.is_live:
            if self.multipage_test:
                container_sas_url = self.get_settings_value("FORM_RECOGNIZER_MULTIPAGE_STORAGE_CONTAINER_SAS_URL")
                url = container_sas_url.split("multipage-training-data")
                url[0] += "multipage-training-data/multipage_invoice1.pdf"
                blob_sas_url = url[0] + url[1]
                self.test_class_instance.scrubber.register_name_pair(
                    blob_sas_url,
                    "blob_sas_url"
                )
            elif self.multipage_test_2:
                container_sas_url = self.get_settings_value("FORM_RECOGNIZER_MULTIPAGE_STORAGE_CONTAINER_SAS_URL_2")
                url = container_sas_url.split("multipage-vendor-forms")
                url[0] += "multipage-vendor-forms/multi1.pdf"
                blob_sas_url = url[0] + url[1]
                self.test_class_instance.scrubber.register_name_pair(
                    blob_sas_url,
                    "blob_sas_url"
                )
            elif self.selection_marks:
                container_sas_url = self.get_settings_value("FORM_RECOGNIZER_SELECTION_MARK_STORAGE_CONTAINER_SAS_URL")
                blob_sas_url = None
            else:
                container_sas_url = self.get_settings_value("FORM_RECOGNIZER_STORAGE_CONTAINER_SAS_URL")
                blob_sas_url = None

            self.test_class_instance.scrubber.register_name_pair(
                container_sas_url,
                "containersasurl"
            )
        else:
            container_sas_url = "containersasurl"
            blob_sas_url = "blob_sas_url"

        if self.need_blob_sas_url:
            return {"client": client,
                    "container_sas_url": container_sas_url,
                    "blob_sas_url": blob_sas_url}
        else:
            return {"client": client,
                    "container_sas_url": container_sas_url}

    def get_copy_parameters(self, training_params, client, **kwargs):
        if self.is_live:
            resource_group = kwargs.get("resource_group")
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            form_recognizer_name = FormRecognizerTest._FORM_RECOGNIZER_NAME

            resource_id = "/subscriptions/" + subscription_id + "/resourceGroups/" + resource_group.name + \
                          "/providers/Microsoft.CognitiveServices/accounts/" + form_recognizer_name
            resource_location = REGION
            self.test_class_instance.scrubber.register_name_pair(
                resource_id,
                "resource_id"
            )
        else:
            resource_location = REGION
            resource_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rgname/providers/Microsoft.CognitiveServices/accounts/frname"

        return {
            "client": client,
            "container_sas_url": training_params["container_sas_url"],
            "location": resource_location,
            "resource_id": resource_id
        }

    def create_resource(self, name, **kwargs):
        client = self.create_form_client(**kwargs)

        if not self.training:
            return {"client": client}

        training_params = self.get_training_parameters(client)

        if self.copy:
            return self.get_copy_parameters(training_params, client, **kwargs)

        return training_params

    def create_form_client(self, **kwargs):
        form_recognizer_account = self.client_kwargs.pop("form_recognizer_account", None)
        if form_recognizer_account is None:
            form_recognizer_account = kwargs.pop("form_recognizer_account")

        form_recognizer_account_key = self.client_kwargs.pop("form_recognizer_account_key", None)
        if form_recognizer_account_key is None:
            form_recognizer_account_key = kwargs.pop("form_recognizer_account_key")

        if self.is_live:
            polling_interval = 5
        else:
            polling_interval = 0

        return self.client_cls(
            form_recognizer_account,
            AzureKeyCredential(form_recognizer_account_key),
            polling_interval=polling_interval,
            logging_enable=True if ENABLE_LOGGER == "True" else False,
            **self.client_kwargs
        )


@pytest.fixture(scope="session")
def form_recognizer_account():
    test_case = AzureTestCase("__init__")
    rg_preparer = ResourceGroupPreparer(random_name_enabled=True, name_prefix='pycog', location=REGION)
    form_recognizer_preparer = CognitiveServicesAccountPreparer(
        random_name_enabled=True,
        kind="formrecognizer",
        name_prefix='pycog',
        location=REGION
    )

    try:
        rg_name, rg_kwargs = rg_preparer._prepare_create_resource(test_case)
        FormRecognizerTest._RESOURCE_GROUP = rg_kwargs['resource_group']
        try:
            form_recognizer_name, form_recognizer_kwargs = form_recognizer_preparer._prepare_create_resource(
                test_case, **rg_kwargs)
            if test_case.is_live:
                time.sleep(60)  # current ask until race condition bug fixed
            FormRecognizerTest._FORM_RECOGNIZER_ACCOUNT = form_recognizer_kwargs['cognitiveservices_account']
            FormRecognizerTest._FORM_RECOGNIZER_KEY = form_recognizer_kwargs['cognitiveservices_account_key']
            FormRecognizerTest._FORM_RECOGNIZER_NAME = form_recognizer_name
            yield
        finally:
            form_recognizer_preparer.remove_resource(
                form_recognizer_name,
                resource_group=rg_kwargs['resource_group']
            )
            FormRecognizerTest._FORM_RECOGNIZER_ACCOUNT = None
            FormRecognizerTest._FORM_RECOGNIZER_KEY = None

    finally:
        rg_preparer.remove_resource(rg_name)
        FormRecognizerTest._RESOURCE_GROUP = None
