
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


import os
import time
import pytest
import re
from azure.core.credentials import AzureKeyCredential, AccessToken
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

        # URL samples
        self.receipt_url_jpg = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/receipt/contoso-allinone.jpg"
        self.receipt_url_png = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/receipt/contoso-receipt.png"
        self.invoice_url_pdf = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/Invoice_1.pdf"
        self.form_url_jpg = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/Form_1.jpg"
        self.multipage_url_pdf = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/multipage_invoice1.pdf"
        self.multipage_table_url_pdf = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/multipagelayout.pdf"

        # file stream samples
        self.receipt_jpg = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/receipt/contoso-allinone.jpg"))
        self.receipt_png = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/receipt/contoso-receipt.png"))
        self.invoice_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Invoice_1.pdf"))
        self.invoice_tiff = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Invoice_1.tiff"))
        self.form_jpg = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Form_1.jpg"))
        self.blank_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/blank.pdf"))
        self.multipage_invoice_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/multipage_invoice1.pdf"))
        self.unsupported_content_py = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./conftest.py"))
        self.multipage_table_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/multipagelayout.pdf"))
        self.multipage_vendor_pdf = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/multi1.pdf"))

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

    def assertModelTransformCorrect(self, model, actual, unlabeled=False):
        self.assertEqual(model.model_id, actual.model_info.model_id)
        self.assertEqual(model.requested_on, actual.model_info.created_date_time)
        self.assertEqual(model.completed_on, actual.model_info.last_updated_date_time)
        self.assertEqual(model.status, actual.model_info.status)
        self.assertEqual(model.errors, actual.train_result.errors)
        for m, a in zip(model.training_documents, actual.train_result.training_documents):
            self.assertEqual(m.document_name, a.document_name)
            if m.errors and a.errors:
                self.assertEqual(m.errors, a.errors)
            self.assertEqual(m.page_count, a.pages)
            self.assertEqual(m.status, a.status)

        if unlabeled:
            if actual.keys.clusters:
                for cluster_id, fields in actual.keys.clusters.items():
                    self.assertEqual(cluster_id, model.submodels[int(cluster_id)].form_type[-1])
                    for field_idx, model_field in model.submodels[int(cluster_id)].fields.items():
                        self.assertIn(model_field.label, fields)

        else:
            if actual.train_result:
                if actual.train_result.fields:
                    for a in actual.train_result.fields:
                        self.assertEqual(model.submodels[0].fields[a.field_name].name, a.field_name)
                        self.assertEqual(model.submodels[0].fields[a.field_name].accuracy, a.accuracy)
                    self.assertEqual(model.submodels[0].form_type, "form-"+model.model_id)
                    self.assertEqual(model.submodels[0].accuracy, actual.train_result.average_model_accuracy)

    def assertFormPagesTransformCorrect(self, pages, actual_read, page_result=None, **kwargs):
        for page, actual_page in zip(pages, actual_read):
            if hasattr(page, "pages"):  # this is necessary for how unlabeled forms are structured
                page = page.pages[0]
            self.assertEqual(page.page_number, actual_page.page)
            self.assertEqual(page.text_angle, actual_page.angle)
            self.assertEqual(page.width, actual_page.width)
            self.assertEqual(page.height, actual_page.height)
            self.assertEqual(page.unit, actual_page.unit)

            if not page.lines and not actual_page.lines:
                continue
            for p, a in zip(page.lines, actual_page.lines):
                self.assertEqual(p.text, a.text)
                self.assertBoundingBoxTransformCorrect(p.bounding_box, a.bounding_box)
                for wp, wa, in zip(p.words, a.words):
                    self.assertEqual(wp.text, wa.text)
                    self.assertEqual(wp.confidence, wa.confidence if wa.confidence is not None else 1.0)
                    self.assertBoundingBoxTransformCorrect(wp.bounding_box, wa.bounding_box)

        if page_result:
            for page, actual_page in zip(pages, page_result):
                if hasattr(page, "pages"):  # this is necessary for how unlabeled forms are structured
                    page = page.pages[0]
                self.assertTablesTransformCorrect(page.tables, actual_page.tables, actual_read, **kwargs)

    def assertBoundingBoxTransformCorrect(self, box, actual):
        if box is None and actual is None:
            return
        self.assertEqual(box[0].x, actual[0])
        self.assertEqual(box[0].y, actual[1])
        self.assertEqual(box[1].x, actual[2])
        self.assertEqual(box[1].y, actual[3])
        self.assertEqual(box[2].x, actual[4])
        self.assertEqual(box[2].y, actual[5])
        self.assertEqual(box[3].x, actual[6])
        self.assertEqual(box[3].y, actual[7])

    def assertTextContentTransformCorrect(self, field_elements, actual_elements, read_result):
        if field_elements is None and actual_elements is None:
            return
        for receipt, actual in zip(field_elements, actual_elements):
            nums = [int(s) for s in re.findall(r'\d+', actual)]
            read, line, word = nums[0:3]
            text_element = read_result[read].lines[line].words[word]
            self.assertEqual(receipt.text, text_element.text)
            self.assertEqual(receipt.confidence, text_element.confidence if text_element.confidence is not None else 1.0)
            self.assertBoundingBoxTransformCorrect(receipt.bounding_box, text_element.bounding_box)

    def assertLabeledFormFieldDictTransformCorrect(self, form_fields, actual_fields, read_results=None):
        if actual_fields is None:
            return

        b = form_fields
        for label, a in actual_fields.items():
            self.assertEqual(label, b[label].name)
            self.assertEqual(a.confidence, b[label].confidence if a.confidence is not None else 1.0)
            self.assertBoundingBoxTransformCorrect(b[label].value_data.bounding_box, a.bounding_box)
            self.assertEqual(a.text, b[label].value_data.text)
            field_type = a.type
            if field_type == "string":
                self.assertEqual(b[label].value, a.value_string)
            if field_type == "number":
                self.assertEqual(b[label].value, a.value_number)
            if field_type == "integer":
                self.assertEqual(b[label].value, a.value_integer)
            if field_type == "date":
                self.assertEqual(b[label].value, a.value_date)
            if field_type == "phoneNumber":
                self.assertEqual(b[label].value, a.value_phone_number)
            if field_type == "time":
                self.assertEqual(b[label].value, a.value_time)
            if read_results:
                self.assertTextContentTransformCorrect(
                    b[label].value_data.text_content,
                    a.elements,
                    read_results
                )

    def assertUnlabeledFormFieldDictTransformCorrect(self, form_fields, actual_fields, read_results=None, **kwargs):
        if actual_fields is None:
            return
        for idx, a in enumerate(actual_fields):
            self.assertEqual(a.confidence, form_fields["field-"+str(idx)].confidence if a.confidence is not None else 1.0)
            self.assertEqual(a.key.text, form_fields["field-"+str(idx)].label_data.text)
            self.assertBoundingBoxTransformCorrect(form_fields["field-"+str(idx)].label_data.bounding_box, a.key.bounding_box)
            if read_results and not kwargs.get("bug_skip_text_content", False):
                self.assertTextContentTransformCorrect(
                    form_fields["field-"+str(idx)].label_data.text_content,
                    a.key.elements,
                    read_results
                )
            self.assertEqual(a.value.text, form_fields["field-" + str(idx)].value_data.text)
            self.assertBoundingBoxTransformCorrect(form_fields["field-" + str(idx)].value_data.bounding_box, a.value.bounding_box)
            if read_results and not kwargs.get("bug_skip_text_content", False):
                self.assertTextContentTransformCorrect(
                    form_fields["field-"+str(idx)].value_data.text_content,
                    a.value.elements,
                    read_results
                )

    def assertFormFieldTransformCorrect(self, receipt_field, actual_field, read_results=None):
        if actual_field is None:
            return
        field_type = actual_field.type
        if field_type == "string":
            self.assertEqual(receipt_field.value, actual_field.value_string)
        if field_type == "number":
            self.assertEqual(receipt_field.value, actual_field.value_number)
        if field_type == "integer":
            self.assertEqual(receipt_field.value, actual_field.value_integer)
        if field_type == "date":
            self.assertEqual(receipt_field.value, actual_field.value_date)
        if field_type == "phoneNumber":
            self.assertEqual(receipt_field.value, actual_field.value_phone_number)
        if field_type == "time":
            self.assertEqual(receipt_field.value, actual_field.value_time)

        self.assertBoundingBoxTransformCorrect(receipt_field.value_data.bounding_box, actual_field.bounding_box)
        self.assertEqual(receipt_field.value_data.text, actual_field.text)
        self.assertEqual(receipt_field.confidence, actual_field.confidence if actual_field.confidence is not None else 1.0)
        if read_results:
            self.assertTextContentTransformCorrect(
                receipt_field.value_data.text_content,
                actual_field.elements,
                read_results
            )

    def assertReceiptItemsTransformCorrect(self, items, actual_items, read_results=None):
        actual = actual_items.value_array

        for r, a in zip(items, actual):
            self.assertFormFieldTransformCorrect(r.value.get("Name"), a.value_object.get("Name"), read_results)
            self.assertFormFieldTransformCorrect(r.value.get("Quantity"), a.value_object.get("Quantity"), read_results)
            self.assertFormFieldTransformCorrect(r.value.get("TotalPrice"), a.value_object.get("TotalPrice"), read_results)
            self.assertFormFieldTransformCorrect(r.value.get("Price"), a.value_object.get("Price"), read_results)

    def assertTablesTransformCorrect(self, layout, actual_layout, read_results=None, **kwargs):
        for table, actual_table in zip(layout, actual_layout):
            self.assertEqual(table.row_count, actual_table.rows)
            self.assertEqual(table.column_count, actual_table.columns)
            for cell, actual_cell in zip(table.cells, actual_table.cells):
                self.assertEqual(table.page_number, cell.page_number)
                self.assertEqual(cell.text, actual_cell.text)
                self.assertEqual(cell.row_index, actual_cell.row_index)
                self.assertEqual(cell.column_index, actual_cell.column_index)
                self.assertEqual(cell.row_span, actual_cell.row_span if actual_cell.row_span is not None else 1)
                self.assertEqual(cell.column_span, actual_cell.column_span if actual_cell.column_span is not None else 1)
                self.assertEqual(cell.confidence, actual_cell.confidence if actual_cell.confidence is not None else 1.0)
                self.assertEqual(cell.is_header, actual_cell.is_header if actual_cell.is_header is not None else False)
                self.assertEqual(cell.is_footer, actual_cell.is_footer if actual_cell.is_footer is not None else False)
                self.assertBoundingBoxTransformCorrect(cell.bounding_box, actual_cell.bounding_box)
                if not kwargs.get("bug_skip_text_content", False):
                    self.assertTextContentTransformCorrect(cell.text_content, actual_cell.elements, read_results)

    def assertReceiptItemsHasValues(self, items, page_number, include_text_content):
        for item in items:
            self.assertBoundingBoxHasPoints(item.value.get("Name").value_data.bounding_box)
            self.assertIsNotNone(item.value.get("Name").confidence)
            self.assertIsNotNone(item.value.get("Name").value_data.text)
            self.assertBoundingBoxHasPoints(item.value.get("Quantity").value_data.bounding_box)
            self.assertIsNotNone(item.value.get("Quantity").confidence)
            self.assertIsNotNone(item.value.get("Quantity").value_data.text)
            self.assertBoundingBoxHasPoints(item.value.get("TotalPrice").value_data.bounding_box)
            self.assertIsNotNone(item.value.get("TotalPrice").confidence)
            self.assertIsNotNone(item.value.get("TotalPrice").value_data.text)

            if include_text_content:
                self.assertTextContentHasValues(item.value.get("Name").value_data.text_content, page_number)
                self.assertTextContentHasValues(item.value.get("Name").value_data.text_content, page_number)
                self.assertTextContentHasValues(item.value.get("Name").value_data.text_content, page_number)
            else:
                self.assertIsNone(item.value.get("Name").value_data.text_content)
                self.assertIsNone(item.value.get("Name").value_data.text_content)
                self.assertIsNone(item.value.get("Name").value_data.text_content)

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
                    self.assertIsNotNone(line.text)
                    self.assertIsNotNone(line.page_number)
                    self.assertBoundingBoxHasPoints(line.bounding_box)
                    for word in line.words:
                        self.assertFormWordHasValues(word, page.page_number)

            if page.tables:
                for table in page.tables:
                    self.assertEqual(table.page_number, page.page_number)
                    self.assertIsNotNone(table.row_count)
                    self.assertIsNotNone(table.column_count)
                    for cell in table.cells:
                        self.assertIsNotNone(cell.text)
                        self.assertIsNotNone(cell.row_index)
                        self.assertIsNotNone(cell.column_index)
                        self.assertIsNotNone(cell.row_span)
                        self.assertIsNotNone(cell.column_span)
                        self.assertBoundingBoxHasPoints(cell.bounding_box)
                        self.assertTextContentHasValues(cell.text_content, page.page_number)

    def assertFormWordHasValues(self, word, page_number):
        self.assertIsNotNone(word.confidence)
        self.assertIsNotNone(word.text)
        self.assertBoundingBoxHasPoints(word.bounding_box)
        self.assertEqual(word.page_number, page_number)

    def assertTextContentHasValues(self, elements, page_number):
        if elements is None:
            return
        for word in elements:
            self.assertFormWordHasValues(word, page_number)


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
            'location': 'westcentralus',
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
            'location': 'westcentralus',
            'resource_group': FormRecognizerTest._RESOURCE_GROUP,
            'form_recognizer_account': form_recognizer_account,
            'form_recognizer_account_key': FormRecognizerTest._FORM_RECOGNIZER_KEY
        }


class GlobalTrainingAccountPreparer(AzureMgmtPreparer):
    def __init__(self, client_cls, client_kwargs={}, **kwargs):
        super(GlobalTrainingAccountPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )
        self.client_kwargs = client_kwargs
        self.client_cls = client_cls
        self.multipage_test = kwargs.get("multipage", False)
        self.multipage_test_2 = kwargs.get("multipage2", False)
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

    def create_resource(self, name, **kwargs):
        client, container_sas_url, blob_sas_url = self.create_form_client_and_container_sas_url(**kwargs)

        if self.need_blob_sas_url:
            return {"client": client,
                    "container_sas_url": container_sas_url,
                    "blob_sas_url": blob_sas_url}
        if self.copy:
            if self.is_live:
                resource_group = kwargs.get("resource_group")
                subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
                form_recognizer_name = FormRecognizerTest._FORM_RECOGNIZER_NAME

                resource_id = "/subscriptions/" + subscription_id + "/resourceGroups/" + resource_group.name + \
                              "/providers/Microsoft.CognitiveServices/accounts/" + form_recognizer_name
                resource_location = "westcentralus"
                self.test_class_instance.scrubber.register_name_pair(
                    resource_id,
                    "resource_id"
                )
            else:
                resource_location = "westcentralus"
                resource_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rgname/providers/Microsoft.CognitiveServices/accounts/frname"

            return {
                "client": client,
                "container_sas_url": container_sas_url,
                "location": resource_location,
                "resource_id": resource_id
            }

        else:
            return {"client": client,
                    "container_sas_url": container_sas_url}

    def create_form_client_and_container_sas_url(self, **kwargs):
        form_recognizer_account = self.client_kwargs.pop("form_recognizer_account", None)
        if form_recognizer_account is None:
            form_recognizer_account = kwargs.pop("form_recognizer_account")

        form_recognizer_account_key = self.client_kwargs.pop("form_recognizer_account_key", None)
        if form_recognizer_account_key is None:
            form_recognizer_account_key = kwargs.pop("form_recognizer_account_key")

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

        return self.client_cls(
            form_recognizer_account,
            AzureKeyCredential(form_recognizer_account_key),
            **self.client_kwargs
        ), container_sas_url, blob_sas_url


@pytest.fixture(scope="session")
def form_recognizer_account():
    test_case = AzureTestCase("__init__")
    rg_preparer = ResourceGroupPreparer(random_name_enabled=True, name_prefix='pycog', location="westcentralus")
    form_recognizer_preparer = CognitiveServicesAccountPreparer(
        random_name_enabled=True,
        kind="formrecognizer",
        name_prefix='pycog',
        location="westcentralus"
    )
    time.sleep(60)  # current ask until race condition bug fixed

    try:
        rg_name, rg_kwargs = rg_preparer._prepare_create_resource(test_case)
        FormRecognizerTest._RESOURCE_GROUP = rg_kwargs['resource_group']
        try:
            form_recognizer_name, form_recognizer_kwargs = form_recognizer_preparer._prepare_create_resource(
                test_case, **rg_kwargs)
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
