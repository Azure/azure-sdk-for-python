# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ServiceRequestError, ClientAuthenticationError
from azure.ai.formrecognizer import FormRecognizerClient, FormTrainingClient
from azure.ai.formrecognizer._generated.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_form_result
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer
from testcase import GlobalClientPreparer as _GlobalClientPreparer


GlobalClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)


class TestCustomFormsFromUrl(FormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    def test_custom_forms_encoded_url(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        try:
            poller = client.begin_recognize_custom_forms_from_url(
                model_id="00000000-0000-0000-0000-000000000000",
                form_url="https://fakeuri.com/blank%20space"
            )
        except HttpResponseError as e:
            self.assertIn("https://fakeuri.com/blank%20space", e.response.request.body)

    @GlobalFormRecognizerAccountPreparer()
    def test_custom_form_none_model_id(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with self.assertRaises(ValueError):
            client.begin_recognize_custom_forms_from_url(model_id=None, form_url="https://badurl.jpg")

    @GlobalFormRecognizerAccountPreparer()
    def test_custom_form_empty_model_id(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with self.assertRaises(ValueError):
            client.begin_recognize_custom_forms_from_url(model_id="", form_url="https://badurl.jpg")

    @GlobalFormRecognizerAccountPreparer()
    def test_custom_form_url_bad_endpoint(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(form_recognizer_account_key))
            result = client.begin_recognize_custom_forms_from_url(model_id="xx", form_url=self.form_url_jpg)

    @GlobalFormRecognizerAccountPreparer()
    def test_url_authentication_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            result = client.begin_recognize_custom_forms_from_url(model_id="xx", form_url=self.form_url_jpg)

    @GlobalFormRecognizerAccountPreparer()
    def test_passing_bad_url(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with self.assertRaises(HttpResponseError):
            poller = client.begin_recognize_custom_forms_from_url(model_id="xx", form_url="https://badurl.jpg")

    @GlobalFormRecognizerAccountPreparer()
    def test_pass_stream_into_url(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with open(self.unsupported_content_py, "rb") as fd:
            with self.assertRaises(HttpResponseError):
                poller = client.begin_recognize_custom_forms_from_url(
                    model_id="xxx",
                    form_url=fd,
                )

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    def test_custom_form_bad_url(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=True)
        model = poller.result()

        with pytest.raises(HttpResponseError) as e:
            poller = fr_client.begin_recognize_custom_forms_from_url(
                model.model_id,
                form_url="https://badurl.jpg"
            )
            form = poller.result()
        self.assertEqual(e.value.error.code, "2003")
        self.assertIsNotNone(e.value.error.message)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    def test_custom_form_unlabeled(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = poller.result()

        poller = fr_client.begin_recognize_custom_forms_from_url(model.model_id, self.form_url_jpg)
        form = poller.result()

        self.assertEqual(form[0].form_type, "form-0")
        self.assertUnlabeledRecognizedFormHasValues(form[0], model)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, multipage=True, blob_sas_url=True)
    def test_form_multipage_unlabeled(self, client, container_sas_url, blob_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = poller.result()

        poller = fr_client.begin_recognize_custom_forms_from_url(
            model.model_id,
            blob_sas_url
        )
        forms = poller.result()

        for form in forms:
            if form.form_type is None:
                continue  # blank page
            self.assertEqual(form.form_type, "form-0")
            self.assertUnlabeledRecognizedFormHasValues(form, model)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    def test_custom_form_labeled(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=True, model_name="labeled")
        model = poller.result()

        poller = fr_client.begin_recognize_custom_forms_from_url(model.model_id, self.form_url_jpg)
        form = poller.result()

        self.assertEqual(form[0].form_type, "custom:labeled")
        self.assertLabeledRecognizedFormHasValues(form[0], model)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, multipage=True, blob_sas_url=True)
    def test_form_multipage_labeled(self, client, container_sas_url, blob_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(
            container_sas_url,
            use_training_labels=True
        )
        model = poller.result()

        poller = fr_client.begin_recognize_custom_forms_from_url(
            model.model_id,
            blob_sas_url
        )
        forms = poller.result()

        for form in forms:
            self.assertEqual(form.form_type, "custom:"+model.model_id)
            self.assertLabeledRecognizedFormHasValues(form, model)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    def test_custom_form_unlabeled_transform(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        poller = fr_client.begin_recognize_custom_forms_from_url(
            model.model_id,
            self.form_url_jpg,
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

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, multipage=True, blob_sas_url=True)
    def test_custom_form_multipage_unlabeled_transform(self, client, container_sas_url, blob_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        poller = fr_client.begin_recognize_custom_forms_from_url(
            model.model_id,
            blob_sas_url,
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


    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    def test_form_labeled_transform(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=True)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        poller = fr_client.begin_recognize_custom_forms_from_url(
            model.model_id,
            self.form_url_jpg,
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
        self.assertEqual(recognized_form[0].form_type_confidence, 1.0)
        self.assertIsNotNone(recognized_form[0].model_id)
        self.assertFormFieldsTransformCorrect(recognized_form[0].fields, actual_fields, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, multipage=True, blob_sas_url=True)
    def test_custom_form_multipage_labeled_transform(self, client, container_sas_url, blob_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=True)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        poller = fr_client.begin_recognize_custom_forms_from_url(
            model.model_id,
            blob_sas_url,
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
            self.assertEqual(form.form_type_confidence, 1.0)
            self.assertEqual(form.model_id, model.model_id)
            self.assertFormFieldsTransformCorrect(form.fields, actual.fields, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    @pytest.mark.live_test_only
    def test_custom_form_continuation_token(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        training_poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = training_poller.result()

        initial_poller = fr_client.begin_recognize_custom_forms_from_url(
            model.model_id,
            self.form_url_jpg
        )

        cont_token = initial_poller.continuation_token()
        poller = fr_client.begin_recognize_custom_forms_from_url(
            model.model_id,
            None,
            continuation_token=cont_token
        )
        result = poller.result()
        self.assertIsNotNone(result)
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, multipage2=True, blob_sas_url=True)
    def test_custom_form_multipage_vendor_set_unlabeled_transform(self, client, container_sas_url, blob_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        poller = fr_client.begin_recognize_custom_forms_from_url(
            model.model_id,
            blob_sas_url,
            include_field_elements=True,
            cls=callback
        )
        form = poller.result()
        actual = responses[0]
        recognized_form = responses[1]
        read_results = actual.analyze_result.read_results
        page_results = actual.analyze_result.page_results
        page_results = actual.analyze_result.page_results

        self.assertFormPagesTransformCorrect(recognized_form, read_results, page_results)
        for form, actual in zip(recognized_form, page_results):
            self.assertEqual(form.page_range.first_page_number, actual.page)
            self.assertEqual(form.page_range.last_page_number, actual.page)
            self.assertIsNone(form.form_type_confidence)
            self.assertEqual(form.model_id, model.model_id)
            self.assertUnlabeledFormFieldDictTransformCorrect(form.fields, actual.key_value_pairs, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, multipage2=True, blob_sas_url=True)
    def test_custom_form_multipage_vendor_set_labeled_transform(self, client, container_sas_url, blob_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=True)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        poller = fr_client.begin_recognize_custom_forms_from_url(
            model.model_id,
            blob_sas_url,
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
            self.assertEqual(form.form_type_confidence, 1.0)
            self.assertEqual(form.model_id, model.model_id)
            self.assertFormFieldsTransformCorrect(form.fields, actual.fields, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, selection_marks=True)
    def test_custom_form_selection_mark(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(container_sas_url, use_training_labels=True)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        poller = fr_client.begin_recognize_custom_forms_from_url(
            model_id=model.model_id,
            form_url=self.selection_mark_url_pdf,
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
