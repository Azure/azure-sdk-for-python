# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ServiceRequestError, ClientAuthenticationError, HttpResponseError
from azure.ai.formrecognizer import FormRecognizerClient, FormContentType, FormTrainingClient
from azure.ai.formrecognizer._generated.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_form_result
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer
from testcase import GlobalTrainingAccountPreparer as _GlobalTrainingAccountPreparer


GlobalTrainingAccountPreparer = functools.partial(_GlobalTrainingAccountPreparer, FormTrainingClient)


class TestCustomForms(FormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    def test_custom_form_none_model_id(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with self.assertRaises(ValueError):
            client.begin_recognize_custom_forms(model_id=None, form=b"xx")

    @GlobalFormRecognizerAccountPreparer()
    def test_custom_form_empty_model_id(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with self.assertRaises(ValueError):
            client.begin_recognize_custom_forms(model_id="", form=b"xx")

    @GlobalFormRecognizerAccountPreparer()
    def test_custom_form_bad_endpoint(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(form_recognizer_account_key))
            poller = client.begin_recognize_custom_forms(model_id="xx", form=myfile)

    @GlobalFormRecognizerAccountPreparer()
    def test_authentication_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            poller = client.begin_recognize_custom_forms(model_id="xx", form=b"xx", content_type="image/jpeg")

    @GlobalFormRecognizerAccountPreparer()
    def test_passing_unsupported_url_content_type(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with self.assertRaises(TypeError):
            poller = client.begin_recognize_custom_forms(model_id="xx", form="https://badurl.jpg", content_type="application/json")

    @GlobalFormRecognizerAccountPreparer()
    def test_auto_detect_unsupported_stream_content(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with open(self.unsupported_content_py, "rb") as fd:
            myfile = fd.read()

        with self.assertRaises(ValueError):
            poller = client.begin_recognize_custom_forms(
                model_id="xxx",
                form=myfile,
            )

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_custom_form_damaged_file(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = poller.result()

        with self.assertRaises(HttpResponseError):
            poller = fr_client.begin_recognize_custom_forms(
                model.model_id,
                b"\x25\x50\x44\x46\x55\x55\x55",
            )
            form = poller.result()

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_custom_form_unlabeled(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = poller.result()

        with open(self.form_jpg, "rb") as stream:
            poller = fr_client.begin_recognize_custom_forms(
                model.model_id,
                stream,
                content_type=FormContentType.image_jpeg
            )
        form = poller.result()

        self.assertEqual(form[0].form_type, "form-0")
        self.assertFormPagesHasValues(form[0].pages)
        for label, field in form[0].fields.items():
            self.assertIsNotNone(field.confidence)
            self.assertIsNotNone(field.name)
            self.assertIsNotNone(field.value)
            self.assertIsNotNone(field.value_data.text)
            self.assertIsNotNone(field.label_data.text)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(multipage=True)
    def test_custom_form_multipage_unlabeled(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = poller.result()

        with open(self.multipage_invoice_pdf, "rb") as stream:
            poller = fr_client.begin_recognize_custom_forms(
                model.model_id,
                stream,
                content_type=FormContentType.application_pdf
            )
        forms = poller.result()

        for form in forms:
            if form.form_type is None:
                continue  # blank page
            self.assertEqual(form.form_type, "form-0")
            self.assertFormPagesHasValues(form.pages)
            for label, field in form.fields.items():
                self.assertIsNotNone(field.confidence)
                self.assertIsNotNone(field.name)
                self.assertIsNotNone(field.value)
                self.assertIsNotNone(field.value_data.text)
                self.assertIsNotNone(field.label_data.text)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_custom_form_labeled(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(
            container_sas_url,
            use_training_labels=True
        )
        model = poller.result()

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        poller = fr_client.begin_recognize_custom_forms(model.model_id, myfile, content_type=FormContentType.image_jpeg)
        form = poller.result()

        self.assertEqual(form[0].form_type, "form-"+model.model_id)
        self.assertFormPagesHasValues(form[0].pages)
        for label, field in form[0].fields.items():
            self.assertIsNotNone(field.confidence)
            self.assertIsNotNone(field.name)
            self.assertIsNotNone(field.value_data.text)
            self.assertIsNotNone(field.value_data.bounding_box)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(multipage=True)
    def test_custom_form_multipage_labeled(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(
            container_sas_url,
            use_training_labels=True
        )
        model = poller.result()

        with open(self.multipage_invoice_pdf, "rb") as fd:
            myfile = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile,
            content_type=FormContentType.application_pdf
        )
        forms = poller.result()

        for form in forms:
            self.assertEqual(form.form_type, "form-"+model.model_id)
            self.assertFormPagesHasValues(form.pages)
            for label, field in form.fields.items():
                self.assertIsNotNone(field.confidence)
                self.assertIsNotNone(field.name)
                self.assertIsNotNone(field.value_data.text)
                self.assertIsNotNone(field.value_data.bounding_box)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_custom_form_unlabeled_transform(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile,
            include_text_content=True,
            cls=callback
        )
        form = poller.result()
        actual = responses[0]
        recognized_form = responses[1]
        read_results = actual.analyze_result.read_results
        page_results = actual.analyze_result.page_results
        actual_fields = actual.analyze_result.page_results[0].key_value_pairs

        self.assertFormPagesTransformCorrect(recognized_form[0].pages, read_results, page_results)
        self.assertEqual(recognized_form[0].page_range.first_page_number, page_results[0].page)
        self.assertEqual(recognized_form[0].page_range.last_page_number, page_results[0].page)
        self.assertUnlabeledFormFieldDictTransformCorrect(recognized_form[0].fields, actual_fields, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(multipage=True)
    def test_custom_form_multipage_unlabeled_transform(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.multipage_invoice_pdf, "rb") as fd:
            myfile = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile,
            include_text_content=True,
            cls=callback
        )
        form = poller.result()
        actual = responses[0]
        recognized_form = responses[1]
        read_results = actual.analyze_result.read_results
        page_results = actual.analyze_result.page_results

        self.assertFormPagesTransformCorrect(recognized_form, read_results, page_results, bug_skip_text_content=True)

        for form, actual in zip(recognized_form, page_results):
            self.assertEqual(form.page_range.first_page_number, actual.page)
            self.assertEqual(form.page_range.last_page_number, actual.page)
            self.assertUnlabeledFormFieldDictTransformCorrect(form.fields, actual.key_value_pairs, read_results, bug_skip_text_content=True)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_custom_form_labeled_transform(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=True)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile,
            include_text_content=True,
            cls=callback
        )
        form = poller.result()
        actual = responses[0]
        recognized_form = responses[1]
        read_results = actual.analyze_result.read_results
        page_results = actual.analyze_result.page_results
        actual_fields = actual.analyze_result.document_results[0].fields

        self.assertFormPagesTransformCorrect(recognized_form[0].pages, read_results, page_results)
        self.assertEqual(recognized_form[0].page_range.first_page_number, page_results[0].page)
        self.assertEqual(recognized_form[0].page_range.last_page_number, page_results[0].page)
        self.assertLabeledFormFieldDictTransformCorrect(recognized_form[0].fields, actual_fields, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(multipage=True)
    def test_custom_form_multipage_labeled_transform(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=True)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.multipage_invoice_pdf, "rb") as fd:
            myfile = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile,
            include_text_content=True,
            cls=callback
        )
        form = poller.result()
        actual = responses[0]
        recognized_form = responses[1]
        read_results = actual.analyze_result.read_results
        page_results = actual.analyze_result.page_results
        document_results = actual.analyze_result.document_results

        self.assertFormPagesTransformCorrect(recognized_form, read_results, page_results)
        for form, actual in zip(recognized_form, document_results):
            self.assertEqual(form.page_range.first_page_number, actual.page_range[0])
            self.assertEqual(form.page_range.last_page_number, actual.page_range[1])
            self.assertEqual(form.form_type, "form-"+model.model_id)
            self.assertLabeledFormFieldDictTransformCorrect(form.fields, actual.fields, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    @pytest.mark.live_test_only
    def test_custom_form_continuation_token(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = poller.result()

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()
        initial_poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile
        )
        cont_token = initial_poller.continuation_token()
        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile,
            continuation_token=cont_token
        )
        result = poller.result()
        self.assertIsNotNone(result)
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(multipage2=True)
    def test_custom_form_multipage_vendor_set_unlabeled_transform(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.multipage_vendor_pdf, "rb") as fd:
            myfile = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile,
            include_text_content=True,
            cls=callback
        )
        form = poller.result()
        actual = responses[0]
        recognized_form = responses[1]
        read_results = actual.analyze_result.read_results
        page_results = actual.analyze_result.page_results
        document_results = actual.analyze_result.document_results

        self.assertFormPagesTransformCorrect(recognized_form, read_results, page_results)
        for form, actual in zip(recognized_form, document_results):
            self.assertEqual(form.page_range.first_page_number, actual.page_range[0])
            self.assertEqual(form.page_range.last_page_number, actual.page_range[1])
            self.assertEqual(form.form_type, "form-"+model.model_id)
            self.assertLabeledFormFieldDictTransformCorrect(form.fields, actual.fields, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(multipage2=True)
    def test_custom_form_multipage_vendor_set_labeled_transform(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=True)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.multipage_vendor_pdf, "rb") as fd:
            myfile = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile,
            include_text_content=True,
            cls=callback
        )
        form = poller.result()
        actual = responses[0]
        recognized_form = responses[1]
        read_results = actual.analyze_result.read_results
        page_results = actual.analyze_result.page_results
        document_results = actual.analyze_result.document_results

        self.assertFormPagesTransformCorrect(recognized_form, read_results, page_results)
        for form, actual in zip(recognized_form, document_results):
            self.assertEqual(form.page_range.first_page_number, actual.page_range[0])
            self.assertEqual(form.page_range.last_page_number, actual.page_range[1])
            self.assertEqual(form.form_type, "form-"+model.model_id)
            self.assertLabeledFormFieldDictTransformCorrect(form.fields, actual.fields, read_results)
