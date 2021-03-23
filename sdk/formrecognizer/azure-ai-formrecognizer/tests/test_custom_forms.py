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
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer

GlobalClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)


class TestCustomForms(FormRecognizerTest):

    @FormRecognizerPreparer()
    def test_custom_form_none_model_id(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key))
        with self.assertRaises(ValueError):
            client.begin_recognize_custom_forms(model_id=None, form=b"xx")

    @FormRecognizerPreparer()
    def test_custom_form_empty_model_id(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key))
        with self.assertRaises(ValueError):
            client.begin_recognize_custom_forms(model_id="", form=b"xx")

    @FormRecognizerPreparer()
    def test_custom_form_bad_endpoint(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(formrecognizer_test_api_key))
            poller = client.begin_recognize_custom_forms(model_id="xx", form=myfile)

    @FormRecognizerPreparer()
    def test_authentication_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            poller = client.begin_recognize_custom_forms(model_id="xx", form=b"xx", content_type="image/jpeg")

    @FormRecognizerPreparer()
    def test_passing_unsupported_url_content_type(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key))
        with self.assertRaises(TypeError):
            poller = client.begin_recognize_custom_forms(model_id="xx", form="https://badurl.jpg", content_type="application/json")

    @FormRecognizerPreparer()
    def test_auto_detect_unsupported_stream_content(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key))
        with open(self.unsupported_content_py, "rb") as fd:
            myfile = fd.read()

        with self.assertRaises(ValueError):
            poller = client.begin_recognize_custom_forms(
                model_id="xxx",
                form=myfile,
            )

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_custom_form_damaged_file(self, client, formrecognizer_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
        model = poller.result()

        with self.assertRaises(HttpResponseError):
            poller = fr_client.begin_recognize_custom_forms(
                model.model_id,
                b"\x25\x50\x44\x46\x55\x55\x55",
            )
            form = poller.result()

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_custom_form_unlabeled(self, client, formrecognizer_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
        model = poller.result()

        with open(self.form_jpg, "rb") as stream:
            poller = fr_client.begin_recognize_custom_forms(
                model.model_id,
                stream,
                content_type=FormContentType.IMAGE_JPEG
            )
        form = poller.result()

        self.assertEqual(form[0].form_type, "form-0")
        self.assertUnlabeledRecognizedFormHasValues(form[0], model)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_custom_form_multipage_unlabeled(self, client, formrecognizer_multipage_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_multipage_storage_container_sas_url, use_training_labels=False)
        model = poller.result()

        with open(self.multipage_invoice_pdf, "rb") as stream:
            poller = fr_client.begin_recognize_custom_forms(
                model.model_id,
                stream,
                content_type=FormContentType.APPLICATION_PDF
            )
        forms = poller.result()

        for form in forms:
            if form.form_type is None:
                continue  # blank page
            self.assertEqual(form.form_type, "form-0")
            self.assertUnlabeledRecognizedFormHasValues(form, model)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_custom_form_labeled(self, client, formrecognizer_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(
            formrecognizer_storage_container_sas_url,
            use_training_labels=True,
            model_name="labeled"
        )
        model = poller.result()

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        poller = fr_client.begin_recognize_custom_forms(model.model_id, myfile, content_type=FormContentType.IMAGE_JPEG)
        form = poller.result()

        self.assertEqual(form[0].form_type, "custom:labeled")
        self.assertLabeledRecognizedFormHasValues(form[0], model)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_custom_form_multipage_labeled(self, client, formrecognizer_multipage_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(
            formrecognizer_multipage_storage_container_sas_url,
            use_training_labels=True
        )
        model = poller.result()

        with open(self.multipage_invoice_pdf, "rb") as fd:
            myfile = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile,
            content_type=FormContentType.APPLICATION_PDF
        )
        forms = poller.result()

        for form in forms:
            self.assertEqual(form.form_type, "custom:"+model.model_id)
            self.assertLabeledRecognizedFormHasValues(form, model)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_custom_form_unlabeled_transform(self, client, formrecognizer_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile,
            include_field_elements=True,
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
        self.assertIsNone(recognized_form[0].form_type_confidence)
        self.assertIsNotNone(recognized_form[0].model_id)
        self.assertUnlabeledFormFieldDictTransformCorrect(recognized_form[0].fields, actual_fields, read_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_custom_form_multipage_unlabeled_transform(self, client, formrecognizer_multipage_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_multipage_storage_container_sas_url, use_training_labels=False)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.multipage_invoice_pdf, "rb") as fd:
            myfile = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile,
            include_field_elements=True,
            cls=callback
        )
        form = poller.result()
        actual = responses[0]
        recognized_form = responses[1]
        read_results = actual.analyze_result.read_results
        page_results = actual.analyze_result.page_results

        self.assertFormPagesTransformCorrect(recognized_form, read_results, page_results)

        for form, actual in zip(recognized_form, page_results):
            self.assertEqual(form.page_range.first_page_number, actual.page)
            self.assertEqual(form.page_range.last_page_number, actual.page)
            self.assertIsNone(form.form_type_confidence)
            self.assertEqual(form.model_id, model.model_id)
            self.assertUnlabeledFormFieldDictTransformCorrect(form.fields, actual.key_value_pairs, read_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_custom_form_labeled_transform(self, client, formrecognizer_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=True)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile,
            include_field_elements=True,
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
        self.assertIsNotNone(recognized_form[0].form_type_confidence)
        self.assertIsNotNone(recognized_form[0].model_id)
        self.assertFormFieldsTransformCorrect(recognized_form[0].fields, actual_fields, read_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_custom_form_multipage_labeled_transform(self, client, formrecognizer_multipage_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_multipage_storage_container_sas_url, use_training_labels=True)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.multipage_invoice_pdf, "rb") as fd:
            myfile = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile,
            include_field_elements=True,
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
            self.assertEqual(form.form_type, "custom:"+model.model_id)
            self.assertIsNotNone(form.form_type_confidence)
            self.assertEqual(form.model_id, model.model_id)
            self.assertFormFieldsTransformCorrect(form.fields, actual.fields, read_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    @pytest.mark.live_test_only
    def test_custom_form_continuation_token(self, client, formrecognizer_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
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
            None,
            continuation_token=cont_token
        )
        result = poller.result()
        self.assertIsNotNone(result)
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_custom_form_multipage_vendor_set_unlabeled_transform(self, client, formrecognizer_multipage_storage_container_sas_url_2):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_multipage_storage_container_sas_url_2, use_training_labels=False)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.multipage_vendor_pdf, "rb") as fd:
            myfile = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile,
            include_field_elements=True,
            cls=callback
        )
        form = poller.result()
        actual = responses[0]
        recognized_form = responses[1]
        read_results = actual.analyze_result.read_results
        page_results = actual.analyze_result.page_results

        self.assertFormPagesTransformCorrect(recognized_form, read_results, page_results)
        for form, actual in zip(recognized_form, page_results):
            self.assertEqual(form.page_range.first_page_number, actual.page)
            self.assertEqual(form.page_range.last_page_number, actual.page)
            self.assertIsNone(form.form_type_confidence)
            self.assertEqual(form.model_id, model.model_id)
            self.assertUnlabeledFormFieldDictTransformCorrect(form.fields, actual.key_value_pairs, read_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_custom_form_multipage_vendor_set_labeled_transform(self, client, formrecognizer_multipage_storage_container_sas_url_2):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_multipage_storage_container_sas_url_2, use_training_labels=True)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.multipage_vendor_pdf, "rb") as fd:
            myfile = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile,
            include_field_elements=True,
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
            self.assertEqual(form.form_type, "custom:"+model.model_id)
            self.assertIsNotNone(form.form_type_confidence)
            self.assertEqual(form.model_id, model.model_id)
            self.assertFormFieldsTransformCorrect(form.fields, actual.fields, read_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_custom_form_selection_mark(self, client, formrecognizer_selection_mark_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_selection_mark_storage_container_sas_url, use_training_labels=True)
        model = poller.result()

        with open(self.selection_form_pdf, "rb") as fd:
            myfile = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            myfile,
            include_field_elements=True,
            cls=callback
        )
        form = poller.result()

        actual = responses[0]
        recognized_form = responses[1]
        read_results = actual.analyze_result.read_results
        page_results = actual.analyze_result.page_results
        actual_fields = actual.analyze_result.document_results[0].fields

        self.assertFormPagesTransformCorrect(recognized_form[0].pages, read_results, page_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_pages_kwarg_specified(self, client, formrecognizer_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        training_poller = client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
        model = training_poller.result()

        poller = fr_client.begin_recognize_custom_forms(model.model_id, myfile, pages=["1"])
        assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
        result = poller.result()
        assert result
