# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from datetime import datetime, timedelta
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.models import Model
from azure.ai.formrecognizer._models import CustomFormModel
from azure.ai.formrecognizer import FormTrainingClient
from azure.storage.blob import ContainerSasPermissions, generate_container_sas
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer


class TestTraining(FormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    def test_training(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        self.get_credentials()
        train_client = FormTrainingClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        sas_token = generate_container_sas(
            self.storage_account_name,
            "form-recognizer-testing-forms",
            self.storage_key,
            permission=ContainerSasPermissions.from_string("rl"),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        container_sas_url = self.storage_endpoint + "form-recognizer-testing-forms?" + sas_token

        poller = train_client.begin_training(container_sas_url)
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

    @GlobalFormRecognizerAccountPreparer()
    def test_training_transform(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        self.get_credentials()
        train_client = FormTrainingClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        sas_token = generate_container_sas(
            self.storage_account_name,
            "form-recognizer-testing-forms",
            self.storage_key,
            permission=ContainerSasPermissions.from_string("rl"),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        container_sas_url = self.storage_endpoint + "form-recognizer-testing-forms?" + sas_token

        raw_response = []

        def callback(response):
            raw_model = train_client._client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        poller = train_client.begin_training(container_sas_url, cls=callback)
        model = poller.result()

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model)

    @GlobalFormRecognizerAccountPreparer()
    def test_training_with_labels(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        self.get_credentials()
        train_client = FormTrainingClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        sas_token = generate_container_sas(
            self.storage_account_name,
            "form-recognizer-testing-forms",
            self.storage_key,
            permission=ContainerSasPermissions.from_string("rl"),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        container_sas_url = self.storage_endpoint + "form-recognizer-testing-forms?" + sas_token

        poller = train_client.begin_training(container_sas_url, use_labels=True)
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

    @GlobalFormRecognizerAccountPreparer()
    def test_training_with_labels_transform(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        self.get_credentials()
        train_client = FormTrainingClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        sas_token = generate_container_sas(
            self.storage_account_name,
            "form-recognizer-testing-forms",
            self.storage_key,
            permission=ContainerSasPermissions.from_string("rl"),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        container_sas_url = self.storage_endpoint + "form-recognizer-testing-forms?" + sas_token

        raw_response = []

        def callback(response):
            raw_model = train_client._client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        poller = train_client.begin_training(container_sas_url, use_labels=True, cls=callback)
        model = poller.result()

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model)

    @GlobalFormRecognizerAccountPreparer()
    def test_training_with_files_filter(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        self.get_credentials()
        train_client = FormTrainingClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        sas_token = generate_container_sas(
            self.storage_account_name,
            "form-recognizer-testing-forms",
            self.storage_key,
            permission=ContainerSasPermissions.from_string("rl"),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        container_sas_url = self.storage_endpoint + "form-recognizer-testing-forms?" + sas_token

        poller = train_client.begin_training(container_sas_url, files_prefix="subfolder", include_sub_folders=True)
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
