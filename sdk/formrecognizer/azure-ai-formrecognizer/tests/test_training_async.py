# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.ai.formrecognizer._generated.models import Model
from azure.ai.formrecognizer._models import CustomFormModel
from azure.ai.formrecognizer.aio import FormTrainingClient
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer
from testcase import GlobalTrainingAccountPreparer as _GlobalTrainingAccountPreparer
from asynctestcase import AsyncFormRecognizerTest

GlobalTrainingAccountPreparer = functools.partial(_GlobalTrainingAccountPreparer, FormTrainingClient)


class TestTrainingAsync(AsyncFormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    async def test_training_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            poller = await client.begin_training("xx", use_training_labels=False)
            result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    async def test_training(self, client, container_sas_url):

        poller = await client.begin_training(
            training_files_url=container_sas_url,
            use_training_labels=False)
        model = await poller.result()

        self.assertIsNotNone(model.model_id)
        self.assertIsNotNone(model.requested_on)
        self.assertIsNotNone(model.completed_on)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.status, "ready")
        for doc in model.training_documents:
            self.assertIsNotNone(doc.document_name)
            self.assertIsNotNone(doc.page_count)
            self.assertIsNotNone(doc.status)
            self.assertEqual(doc.errors, [])
        for sub in model.submodels:
            self.assertIsNotNone(sub.form_type)
            for key, field in sub.fields.items():
                self.assertIsNotNone(field.label)
                self.assertIsNotNone(field.name)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(multipage=True)
    async def test_training_multipage(self, client, container_sas_url):

        poller = await client.begin_training(container_sas_url, use_training_labels=False)
        model = await poller.result()

        self.assertIsNotNone(model.model_id)
        self.assertIsNotNone(model.requested_on)
        self.assertIsNotNone(model.completed_on)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.status, "ready")
        for doc in model.training_documents:
            self.assertIsNotNone(doc.document_name)
            self.assertIsNotNone(doc.page_count)
            self.assertIsNotNone(doc.status)
            self.assertEqual(doc.errors, [])
        for sub in model.submodels:
            self.assertIsNotNone(sub.form_type)
            for key, field in sub.fields.items():
                self.assertIsNotNone(field.label)
                self.assertIsNotNone(field.name)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    async def test_training_transform(self, client, container_sas_url):

        raw_response = []

        def callback(response):
            raw_model = client._client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        poller = await client.begin_training(
            training_files_url=container_sas_url,
            use_training_labels=False,
            cls=callback)
        model = await poller.result()

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model, unlabeled=True)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(multipage=True)
    async def test_training_multipage_transform(self, client, container_sas_url):

        raw_response = []

        def callback(response):
            raw_model = client._client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        poller = await client.begin_training(container_sas_url, use_training_labels=False, cls=callback)
        model = await poller.result()

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model, unlabeled=True)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    async def test_training_with_labels(self, client, container_sas_url):

        poller = await client.begin_training(training_files_url=container_sas_url, use_training_labels=True)
        model = await poller.result()

        self.assertIsNotNone(model.model_id)
        self.assertIsNotNone(model.requested_on)
        self.assertIsNotNone(model.completed_on)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.status, "ready")
        for doc in model.training_documents:
            self.assertIsNotNone(doc.document_name)
            self.assertIsNotNone(doc.page_count)
            self.assertIsNotNone(doc.status)
            self.assertEqual(doc.errors, [])
        for sub in model.submodels:
            self.assertIsNotNone(sub.form_type)
            for key, field in sub.fields.items():
                self.assertIsNotNone(field.accuracy)
                self.assertIsNotNone(field.name)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(multipage=True)
    async def test_training_multipage_with_labels(self, client, container_sas_url):

        poller = await client.begin_training(container_sas_url, use_training_labels=True)
        model = await poller.result()

        self.assertIsNotNone(model.model_id)
        self.assertIsNotNone(model.requested_on)
        self.assertIsNotNone(model.completed_on)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.status, "ready")
        for doc in model.training_documents:
            self.assertIsNotNone(doc.document_name)
            self.assertIsNotNone(doc.page_count)
            self.assertIsNotNone(doc.status)
            self.assertEqual(doc.errors, [])
        for sub in model.submodels:
            self.assertIsNotNone(sub.form_type)
            self.assertIsNotNone(sub.accuracy)
            for key, field in sub.fields.items():
                self.assertIsNotNone(field.accuracy)
                self.assertIsNotNone(field.name)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    async def test_training_with_labels_transform(self, client, container_sas_url):

        raw_response = []

        def callback(response):
            raw_model = client._client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        poller = await client.begin_training(training_files_url=container_sas_url, use_training_labels=True, cls=callback)
        model = await poller.result()

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(multipage=True)
    async def test_train_multipage_w_lbls_trnsfrm(self, client, container_sas_url):

        raw_response = []

        def callback(response):
            raw_model = client._client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        poller = await client.begin_training(container_sas_url, use_training_labels=True, cls=callback)
        model = await poller.result()

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    async def test_training_with_files_filter(self, client, container_sas_url):

        poller = await client.begin_training(training_files_url=container_sas_url, use_training_labels=False, include_sub_folders=True)
        model = await poller.result()
        self.assertEqual(len(model.training_documents), 6)
        self.assertEqual(model.training_documents[-1].document_name, "subfolder/Form_6.jpg")  # we traversed subfolders

        poller = await client.begin_training(container_sas_url, use_training_labels=False, prefix="subfolder", include_sub_folders=True)
        model = await poller.result()
        self.assertEqual(len(model.training_documents), 1)
        self.assertEqual(model.training_documents[0].document_name, "subfolder/Form_6.jpg")  # we filtered for only subfolders

        with self.assertRaises(HttpResponseError):
            poller = await client.begin_training(training_files_url=container_sas_url, use_training_labels=False, prefix="xxx")
            model = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    @pytest.mark.live_test_only
    async def test_training_continuation_token(self, client, container_sas_url):

        initial_poller = await client.begin_training(training_files_url=container_sas_url, use_training_labels=False)
        cont_token = initial_poller.continuation_token()
        poller = await client.begin_training(training_files_url=container_sas_url, use_training_labels=False, continuation_token=cont_token)
        result = await poller.result()
        self.assertIsNotNone(result)
        await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error
