# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from azure.ai.formrecognizer._generated.models import Model
from azure.ai.formrecognizer._models import CustomFormModel
from azure.ai.formrecognizer import FormTrainingClient
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer, GlobalFormAndStorageAccountPreparer
from testcase import GlobalTrainingAccountPreparer as _GlobalTrainingAccountPreparer


GlobalTrainingAccountPreparer = functools.partial(_GlobalTrainingAccountPreparer, FormTrainingClient)


class TestTraining(FormRecognizerTest):

    @GlobalFormAndStorageAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_training(self, training_client, container_sas_url):

        poller = training_client.begin_training(container_sas_url)
        model = poller.result()

        self.assertIsNotNone(model.model_id)
        self.assertIsNotNone(model.created_on)
        self.assertIsNotNone(model.last_updated_on)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.status, "ready")
        for doc in model.training_documents:
            self.assertIsNotNone(doc.document_name)
            self.assertEqual(doc.page_count, 1)
            self.assertEqual(doc.status, "succeeded")
            self.assertEqual(doc.errors, [])
        for sub in model.models:
            self.assertIsNotNone(sub.form_type)
            for key, field in sub.fields.items():
                self.assertIsNotNone(field.label)
                self.assertIsNotNone(field.name)

    @GlobalFormAndStorageAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_training_transform(self, training_client, container_sas_url):

        raw_response = []

        def callback(response):
            raw_model = training_client._client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        poller = training_client.begin_training(container_sas_url, cls=callback)
        model = poller.result()

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model, unlabeled=True)

    @GlobalFormAndStorageAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_training_with_labels(self, training_client, container_sas_url):

        poller = training_client.begin_training(container_sas_url, use_labels=True)
        model = poller.result()

        self.assertIsNotNone(model.model_id)
        self.assertIsNotNone(model.created_on)
        self.assertIsNotNone(model.last_updated_on)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.status, "ready")
        for doc in model.training_documents:
            self.assertIsNotNone(doc.document_name)
            self.assertEqual(doc.page_count, 1)
            self.assertEqual(doc.status, "succeeded")
            self.assertEqual(doc.errors, [])
        for sub in model.models:
            self.assertIsNotNone(sub.form_type)
            for key, field in sub.fields.items():
                self.assertIsNotNone(field.accuracy)
                self.assertIsNotNone(field.name)

    @GlobalFormAndStorageAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_training_with_labels_transform(self, training_client, container_sas_url):

        raw_response = []

        def callback(response):
            raw_model = training_client._client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        poller = training_client.begin_training(container_sas_url, use_labels=True, cls=callback)
        model = poller.result()

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model)

    @GlobalFormAndStorageAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_training_with_files_filter(self, training_client, container_sas_url):

        poller = training_client.begin_training(container_sas_url, include_sub_folders=True)
        model = poller.result()

        self.assertIsNotNone(model.model_id)
        self.assertIsNotNone(model.created_on)
        self.assertIsNotNone(model.last_updated_on)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.status, "ready")
        for doc in model.training_documents:
            self.assertIsNotNone(doc.document_name)
            self.assertEqual(doc.page_count, 1)
            self.assertEqual(doc.status, "succeeded")
            self.assertEqual(doc.errors, [])
        self.assertEqual(model.training_documents[-1].document_name, "subfolder/Form_6.jpg")  # we traversed subfolders
        for sub in model.models:
            self.assertIsNotNone(sub.form_type)
            for key, field in sub.fields.items():
                self.assertIsNotNone(field.label)
                self.assertIsNotNone(field.name)
