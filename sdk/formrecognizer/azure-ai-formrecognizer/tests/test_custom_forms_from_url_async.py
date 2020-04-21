# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ServiceRequestError, ClientAuthenticationError
from azure.ai.formrecognizer.aio import FormRecognizerClient
from azure.ai.formrecognizer._generated.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_form_result
from testcase import GlobalFormRecognizerAccountPreparer, GlobalFormAndStorageAccountPreparer
from testcase import GlobalTrainingAccountPreparer as _GlobalTrainingAccountPreparer
from asynctestcase import AsyncFormRecognizerTest

GlobalTrainingAccountPreparer = functools.partial(_GlobalTrainingAccountPreparer, FormRecognizerClient)


class TestCustomFormsFromUrlAsync(AsyncFormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    async def test_custom_form_url_bad_endpoint(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(form_recognizer_account_key))
            result = await client.recognize_custom_forms_from_url(model_id="xx", url=self.form_url_jpg)

    @GlobalFormRecognizerAccountPreparer()
    async def test_url_authentication_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            result = await client.recognize_custom_forms_from_url(model_id="xx", url=self.form_url_jpg)

    @GlobalFormRecognizerAccountPreparer()
    async def test_passing_bad_url(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with self.assertRaises(HttpResponseError):
            result = await client.recognize_custom_forms_from_url(model_id="xx", url="https://badurl.jpg")

    @GlobalFormRecognizerAccountPreparer()
    async def test_pass_stream_into_url(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with open(self.unsupported_content_py, "rb") as fd:
            with self.assertRaises(HttpResponseError):
                result = await client.recognize_custom_forms_from_url(
                    model_id="xxx",
                    url=fd,
                )

    @GlobalFormAndStorageAccountPreparer()
    @GlobalTrainingAccountPreparer()
    async def test_form_unlabeled(self, client, container_sas_url):
        training_client = client.get_form_training_client()

        model = await training_client.train_model(container_sas_url)

        form = await client.recognize_custom_forms_from_url(model.model_id, self.form_url_jpg)

        self.assertEqual(form[0].form_type, "form-0")
        self.assertFormPagesHasValues(form[0].pages)
        for label, field in form[0].fields.items():
            self.assertIsNotNone(field.confidence)
            self.assertIsNotNone(field.name)
            self.assertIsNotNone(field.page_number)
            self.assertIsNotNone(field.value)
            self.assertIsNotNone(field.value_data.text)
            self.assertIsNotNone(field.label_data.text)

    @GlobalFormAndStorageAccountPreparer()
    @GlobalTrainingAccountPreparer()
    async def test_form_labeled(self, client, container_sas_url):
        training_client = client.get_form_training_client()

        model = await training_client.train_model(container_sas_url, use_labels=True)

        form = await client.recognize_custom_forms_from_url(model.model_id, self.form_url_jpg)

        self.assertEqual(form[0].form_type, "form-"+model.model_id)
        self.assertFormPagesHasValues(form[0].pages)
        for label, field in form[0].fields.items():
            self.assertIsNotNone(field.confidence)
            self.assertIsNotNone(field.name)
            self.assertIsNotNone(field.page_number)
            self.assertIsNotNone(field.value_data.text)
            self.assertIsNotNone(field.value_data.bounding_box)

    @GlobalFormAndStorageAccountPreparer()
    @GlobalTrainingAccountPreparer()
    async def test_fr_unlbld_trnsfrm(self, client, container_sas_url):
        training_client = client.get_form_training_client()

        model = await training_client.train_model(container_sas_url)

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        form = await client.recognize_custom_forms_from_url(
            model.model_id,
            self.form_url_jpg,
            include_text_content=True,
            cls=callback
        )

        actual = responses[0]
        recognized_form = responses[1]
        read_results = actual.analyze_result.read_results
        page_results = actual.analyze_result.page_results
        actual_fields = actual.analyze_result.page_results[0].key_value_pairs

        self.assertFormPagesTransformCorrect(recognized_form[0].pages, read_results, page_results)
        self.assertEqual(recognized_form[0].page_range.first_page, page_results[0].page)
        self.assertEqual(recognized_form[0].page_range.last_page, page_results[0].page)
        self.assertUnlabeledFormFieldDictTransformCorrect(recognized_form[0].fields, actual_fields, read_results)

    @GlobalFormAndStorageAccountPreparer()
    @GlobalTrainingAccountPreparer()
    async def test_fr_lbld_transform(self, client, container_sas_url):
        training_client = client.get_form_training_client()

        model = await training_client.train_model(container_sas_url, use_labels=True)

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        form = await client.recognize_custom_forms_from_url(
            model.model_id,
            self.form_url_jpg,
            include_text_content=True,
            cls=callback
        )

        actual = responses[0]
        recognized_form = responses[1]
        read_results = actual.analyze_result.read_results
        page_results = actual.analyze_result.page_results
        actual_fields = actual.analyze_result.document_results[0].fields

        self.assertFormPagesTransformCorrect(recognized_form[0].pages, read_results, page_results)
        self.assertEqual(recognized_form[0].page_range.first_page, page_results[0].page)
        self.assertEqual(recognized_form[0].page_range.last_page, page_results[0].page)
        self.assertLabeledFormFieldDictTransformCorrect(recognized_form[0].fields, actual_fields, read_results)
