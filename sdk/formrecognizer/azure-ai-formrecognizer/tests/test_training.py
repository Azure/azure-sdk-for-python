# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.ai.formrecognizer._generated.models import Model
from azure.ai.formrecognizer._models import CustomFormModel
from azure.ai.formrecognizer import FormTrainingClient
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer
from testcase import GlobalTrainingAccountPreparer as _GlobalTrainingAccountPreparer


GlobalTrainingAccountPreparer = functools.partial(_GlobalTrainingAccountPreparer, FormTrainingClient)


class TestTraining(FormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    def test_training_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            poller = client.begin_train_model("xx")

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_training(self, client, container_sas_url):

        poller = client.begin_train_model(training_files_url=container_sas_url)
        model = poller.result()

        self.assertIsNotNone(model.model_id)
        self.assertIsNotNone(model.created_on)
        self.assertIsNotNone(model.last_modified)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.status, "ready")
        for doc in model.training_documents:
            self.assertIsNotNone(doc.document_name)
            self.assertIsNotNone(doc.page_count)
            self.assertEqual(doc.status, "succeeded")
            self.assertEqual(doc.errors, [])
        for sub in model.models:
            self.assertIsNotNone(sub.form_type)
            for key, field in sub.fields.items():
                self.assertIsNotNone(field.label)
                self.assertIsNotNone(field.name)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(multipage=True)
    def test_training_multipage(self, client, container_sas_url):

        poller = client.begin_train_model(container_sas_url)
        model = poller.result()

        self.assertIsNotNone(model.model_id)
        self.assertIsNotNone(model.created_on)
        self.assertIsNotNone(model.last_modified)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.status, "ready")
        for doc in model.training_documents:
            self.assertIsNotNone(doc.document_name)
            self.assertIsNotNone(doc.page_count)
            self.assertEqual(doc.status, "succeeded")
            self.assertEqual(doc.errors, [])
        for sub in model.models:
            self.assertIsNotNone(sub.form_type)
            for key, field in sub.fields.items():
                self.assertIsNotNone(field.label)
                self.assertIsNotNone(field.name)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_training_transform(self, client, container_sas_url):

        raw_response = []

        def callback(response):
            raw_model = client._client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        poller = client.begin_train_model(training_files_url=container_sas_url, cls=callback)
        model = poller.result()

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model, unlabeled=True)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(multipage=True)
    def test_training_multipage_transform(self, client, container_sas_url):

        raw_response = []

        def callback(response):
            raw_model = client._client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        poller = client.begin_train_model(container_sas_url, cls=callback)
        model = poller.result()

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model, unlabeled=True)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_training_with_labels(self, client, container_sas_url):

        poller = client.begin_train_model(training_files_url=container_sas_url, use_training_labels=True)
        model = poller.result()

        self.assertIsNotNone(model.model_id)
        self.assertIsNotNone(model.created_on)
        self.assertIsNotNone(model.last_modified)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.status, "ready")
        for doc in model.training_documents:
            self.assertIsNotNone(doc.document_name)
            self.assertIsNotNone(doc.page_count)
            self.assertEqual(doc.status, "succeeded")
            self.assertEqual(doc.errors, [])
        for sub in model.models:
            self.assertIsNotNone(sub.form_type)
            self.assertIsNotNone(sub.accuracy)
            for key, field in sub.fields.items():
                self.assertIsNotNone(field.accuracy)
                self.assertIsNotNone(field.name)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(multipage=True)
    def test_training_multipage_with_labels(self, client, container_sas_url):

        poller = client.begin_train_model(container_sas_url, use_training_labels=True)
        model = poller.result()

        self.assertIsNotNone(model.model_id)
        self.assertIsNotNone(model.created_on)
        self.assertIsNotNone(model.last_modified)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.status, "ready")
        for doc in model.training_documents:
            self.assertIsNotNone(doc.document_name)
            self.assertIsNotNone(doc.page_count)
            self.assertEqual(doc.status, "succeeded")
            self.assertEqual(doc.errors, [])
        for sub in model.models:
            self.assertIsNotNone(sub.form_type)
            self.assertIsNotNone(sub.accuracy)
            for key, field in sub.fields.items():
                self.assertIsNotNone(field.accuracy)
                self.assertIsNotNone(field.name)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_training_with_labels_transform(self, client, container_sas_url):

        raw_response = []

        def callback(response):
            raw_model = client._client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        poller = client.begin_train_model(training_files_url=container_sas_url, use_training_labels=True, cls=callback)
        model = poller.result()

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(multipage=True)
    def test_train_multipage_w_labels_transform(self, client, container_sas_url):

        raw_response = []

        def callback(response):
            raw_model = client._client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        poller = client.begin_train_model(container_sas_url, use_training_labels=True, cls=callback)
        model = poller.result()

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_training_with_files_filter(self, client, container_sas_url):

        poller = client.begin_train_model(training_files_url=container_sas_url, include_sub_folders=True)
        model = poller.result()
        self.assertEqual(len(model.training_documents), 6)
        self.assertEqual(model.training_documents[-1].document_name, "subfolder/Form_6.jpg")  # we traversed subfolders

        poller = client.begin_train_model(container_sas_url, prefix="subfolder", include_sub_folders=True)
        model = poller.result()
        self.assertEqual(len(model.training_documents), 1)
        self.assertEqual(model.training_documents[0].document_name, "subfolder/Form_6.jpg")  # we filtered for only subfolders

        with self.assertRaises(HttpResponseError):
            poller = client.begin_train_model(training_files_url=container_sas_url, prefix="xxx")
            model = poller.result()
