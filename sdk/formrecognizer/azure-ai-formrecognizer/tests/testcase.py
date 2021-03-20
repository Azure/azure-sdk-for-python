
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
from devtools_testutils import AzureTestCase
from azure_devtools.scenario_tests import (
    RecordingProcessor,
    ReplayableTest
)
from azure_devtools.scenario_tests.utilities import is_text_payload

LOGGING_FORMAT = '%(asctime)s %(name)-20s %(levelname)-5s %(message)s'
ENABLE_LOGGER = os.getenv('ENABLE_LOGGER', "False")


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


class OperationLocationReplacer(RecordingProcessor):
    """Replace the location/operation location uri in a request/response body."""

    def __init__(self):
        self._replacement = "https://region.api.cognitive.microsoft.com/formrecognizer/"

    def process_response(self, response):
        try:
            headers = response['headers']
            location_header = None
            if 'operation-location' in headers:
                location_header = "operation-location"
            if 'location' in headers:
                location_header = "location"
            if location_header:
                if isinstance(headers[location_header], list):
                    suffix = headers[location_header][0].split("/formrecognizer/")[1]
                    response['headers'][location_header] = [self._replacement + suffix]
                else:
                    suffix = headers[location_header].split("/formrecognizer/")[1]
                    response['headers'][location_header] = self._replacement + suffix
            url = response["url"]
            if url is not None:
                suffix = url.split("/formrecognizer/")[1]
                response['url'] = self._replacement + suffix
            return response
        except (KeyError, ValueError):
            return response


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
        self.vcr.match_on = ["path", "method", "query"]
        self.recording_processors.append(AccessTokenReplacer())
        self.recording_processors.append(RequestBodyReplacer())
        self.recording_processors.append(OperationLocationReplacer())
        self.configure_logging()

        # URL samples
        # self.receipt_url_jpg = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/receipt/contoso-allinone.jpg"
        # self.receipt_url_png = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/receipt/contoso-receipt.png"
        # self.business_card_url_jpg = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/business_cards/business-card-english.jpg"
        # self.business_card_url_png = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/business_cards/business-card-english.png"
        # self.business_card_multipage_url_pdf = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/business_cards/business-card-multipage.pdf"
        # self.invoice_url_pdf = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/Invoice_1.pdf"
        # self.invoice_url_tiff = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/Invoice_1.tiff"
        # self.multipage_vendor_url_pdf = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/multi1.pdf"
        # self.form_url_jpg = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/Form_1.jpg"
        # self.multipage_url_pdf = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/multipage_invoice1.pdf"
        # self.multipage_table_url_pdf = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/multipagelayout.pdf"
        # self.selection_mark_url_pdf = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/selection_mark_form.pdf"

        testing_container_sas_url = os.getenv("FORMRECOGNIZER_TESTING_DATA_CONTAINER_SAS_URL")
        self.receipt_url_jpg = self.get_blob_url(testing_container_sas_url, "testingdata", "contoso-allinone.jpg")
        self.receipt_url_png = self.get_blob_url(testing_container_sas_url, "testingdata", "contoso-receipt.png")
        self.business_card_url_jpg = self.get_blob_url(testing_container_sas_url, "testingdata", "businessCard.jpg")
        self.business_card_url_png = self.get_blob_url(testing_container_sas_url, "testingdata", "businessCard.png")
        self.business_card_multipage_url_pdf = self.get_blob_url(testing_container_sas_url, "testingdata", "business-card-multipage.pdf")
        self.id_document_url_jpg = self.get_blob_url(testing_container_sas_url, "testingdata", "license_2.jpg")
        self.invoice_url_pdf = self.get_blob_url(testing_container_sas_url, "testingdata", "Invoice_1.pdf")
        self.invoice_url_tiff = self.get_blob_url(testing_container_sas_url, "testingdata", "Invoice_1.tiff")
        self.multipage_vendor_url_pdf = self.get_blob_url(testing_container_sas_url, "testingdata", "multi1.pdf")
        self.form_url_jpg = self.get_blob_url(testing_container_sas_url, "testingdata", "Form_1.jpg")
        self.multipage_url_pdf = self.get_blob_url(testing_container_sas_url, "testingdata", "multipage_invoice1.pdf")
        self.multipage_table_url_pdf = self.get_blob_url(testing_container_sas_url, "testingdata", "multipagelayout.pdf")
        self.selection_mark_url_pdf = self.get_blob_url(testing_container_sas_url, "testingdata", "selection_mark_form.pdf")

        # file stream samples
        self.receipt_jpg = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/receipt/contoso-allinone.jpg"))
        self.receipt_png = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/receipt/contoso-receipt.png"))
        self.business_card_jpg = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/business_cards/business-card-english.jpg"))
        self.business_card_png = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/business_cards/business-card-english.png"))
        self.business_card_multipage_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/business_cards/business-card-multipage.pdf"))
        self.id_document_jpg = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/id_documents/license.jpg"))
        self.invoice_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Invoice_1.pdf"))
        self.invoice_tiff = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Invoice_1.tiff"))
        self.form_jpg = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Form_1.jpg"))
        self.blank_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/blank.pdf"))
        self.multipage_invoice_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/multipage_invoice1.pdf"))
        self.unsupported_content_py = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./conftest.py"))
        self.multipage_table_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/multipagelayout.pdf"))
        self.multipage_vendor_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/multi1.pdf"))
        self.selection_form_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/selection_mark_form.pdf"))

    def get_blob_url(self, container_sas_url, container, file_name):
        if self.is_live:
            url = container_sas_url.split(container)
            url[0] += container + "/" + file_name
            blob_sas_url = url[0] + url[1]
            self.scrubber.register_name_pair(
                blob_sas_url,
                "blob_sas_url"
            )
        else:
            blob_sas_url = "blob_sas_url"
        return blob_sas_url

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
                if expected_page.tables:
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

    def assertFormFieldValueTransformCorrect(self, form_field, expected, read_results=None):
        if expected is None:
            return
        field_type = expected.type
        if field_type == "string":
            self.assertEqual(form_field.value, expected.value_string)
        if field_type == "number":
            self.assertEqual(form_field.value, expected.value_number)
        if field_type == "integer":
            self.assertEqual(form_field.value, expected.value_integer)
        if field_type == "date":
            self.assertEqual(form_field.value, expected.value_date)
        if field_type == "phoneNumber":
            self.assertEqual(form_field.value, expected.value_phone_number)
        if field_type == "time":
            self.assertEqual(form_field.value, expected.value_time)
        if field_type == "array":
            for i in range(len(expected.value_array)):
                self.assertFormFieldValueTransformCorrect(form_field.value[i], expected.value_array[i], read_results)
        if field_type == "object":
            self.assertFormFieldsTransformCorrect(form_field.value, expected.value_object, read_results)

        if field_type not in ["array", "object"] and form_field.value_data:
            self.assertBoundingBoxTransformCorrect(form_field.value_data.bounding_box, expected.bounding_box)
            self.assertEqual(expected.text, form_field.value_data.text)
            self.assertEqual(expected.page, form_field.value_data.page_number)
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
            field_type = expected.type
            self.assertEqual(adjust_value_type(field_type), form_fields[label].value_type)
            self.assertEqual(label, form_fields[label].name)
            self.assertEqual(adjust_confidence(expected.confidence), form_fields[label].confidence)
            self.assertFormFieldValueTransformCorrect(form_fields[label], expected, read_results)

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
            if item.value.get("Name", None):
                self.assertIsNotNone(item.value.get("Name").confidence)
                self.assertIsNotNone(item.value.get("Name").value_data.text)
                self.assertIsNotNone(item.value.get("Name").value_type)
            if item.value.get("Quantity", None):
                self.assertBoundingBoxHasPoints(item.value.get("Quantity").value_data.bounding_box)
                self.assertIsNotNone(item.value.get("Quantity").confidence)
                self.assertIsNotNone(item.value.get("Quantity").value_data.text)
                self.assertIsNotNone(item.value.get("Quantity").value_type)
            if item.value.get("TotalPrice", None):
                self.assertBoundingBoxHasPoints(item.value.get("TotalPrice").value_data.bounding_box)
                self.assertIsNotNone(item.value.get("TotalPrice").confidence)
                self.assertIsNotNone(item.value.get("TotalPrice").value_data.text)
                self.assertIsNotNone(item.value.get("TotalPrice").value_type)
            if item.value.get("Price", None):
                self.assertBoundingBoxHasPoints(item.value.get("Price").value_data.bounding_box)
                self.assertIsNotNone(item.value.get("Price").confidence)
                self.assertIsNotNone(item.value.get("Price").value_data.text)
                self.assertIsNotNone(item.value.get("Price").value_type)

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
            self.assertEqual(item.value_type, "dictionary")
            if item.value.get("Amount", None):
                self.assertBoundingBoxHasPoints(item.value.get("Amount").value_data.bounding_box)
                self.assertIsNotNone(item.value.get("Amount").confidence)
                self.assertIsNotNone(item.value.get("Amount").value_data.text)
                self.assertIsNotNone(item.value.get("Amount").value_type)
            if item.value.get("Quantity", None):
                self.assertBoundingBoxHasPoints(item.value.get("Quantity").value_data.bounding_box)
                self.assertIsNotNone(item.value.get("Quantity").confidence)
                self.assertIsNotNone(item.value.get("Quantity").value_data.text)
                self.assertIsNotNone(item.value.get("Quantity").value_type)
            if item.value.get("Description", None):
                self.assertBoundingBoxHasPoints(item.value.get("Description").value_data.bounding_box)
                self.assertIsNotNone(item.value.get("Description").confidence)
                self.assertIsNotNone(item.value.get("Description").value_data.text)
                self.assertIsNotNone(item.value.get("Description").value_type)
            if item.value.get("UnitPrice", None):
                self.assertBoundingBoxHasPoints(item.value.get("UnitPrice").value_data.bounding_box)
                self.assertIsNotNone(item.value.get("UnitPrice").confidence)
                self.assertIsNotNone(item.value.get("UnitPrice").value_data.text)
                self.assertIsNotNone(item.value.get("UnitPrice").value_type)
            if item.value.get("ProductCode", None):
                self.assertBoundingBoxHasPoints(item.value.get("ProductCode").value_data.bounding_box)
                self.assertIsNotNone(item.value.get("ProductCode").confidence)
                self.assertIsNotNone(item.value.get("ProductCode").value_data.text)
                self.assertIsNotNone(item.value.get("ProductCode").value_type)
            if item.value.get("Unit", None):
                self.assertBoundingBoxHasPoints(item.value.get("Unit").value_data.bounding_box)
                self.assertIsNotNone(item.value.get("Unit").confidence)
                self.assertIsNotNone(item.value.get("Unit").value_data.text)
                self.assertIsNotNone(item.value.get("Unit").value_type)
            if item.value.get("Date", None):
                self.assertBoundingBoxHasPoints(item.value.get("Date").value_data.bounding_box)
                self.assertIsNotNone(item.value.get("Date").confidence)
                self.assertIsNotNone(item.value.get("Date").value_data.text)
                self.assertIsNotNone(item.value.get("Date").value_type)
            if item.value.get("Tax", None):
                self.assertBoundingBoxHasPoints(item.value.get("Tax").value_data.bounding_box)
                self.assertIsNotNone(item.value.get("Tax").confidence)
                self.assertIsNotNone(item.value.get("Tax").value_data.text)
                self.assertIsNotNone(item.value.get("Tax").value_type)

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
        self.assertIsNotNone(form.form_type_confidence)
        self.assertEqual(form.model_id, model.model_id)
        self.assertFormPagesHasValues(form.pages)
        for label, field in form.fields.items():
            self.assertIsNotNone(field.confidence)
            self.assertIsNotNone(field.name)
            self.assertIsNotNone(field.value_data.text)
            self.assertIsNotNone(field.value_data.bounding_box)
