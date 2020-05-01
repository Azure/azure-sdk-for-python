# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
from azure.core.pipeline.transport import RequestsTransport
from azure.ai.formrecognizer import FormTrainingClient, FormRecognizerClient
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer
from testcase import GlobalTrainingAccountPreparer as _GlobalTrainingAccountPreparer


GlobalTrainingAccountPreparer = functools.partial(_GlobalTrainingAccountPreparer, FormTrainingClient)


class TestManagement(FormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    def test_account_properties_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            result = client.get_account_properties()

    @GlobalFormRecognizerAccountPreparer()
    def test_get_model_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            result = client.get_custom_model("xx")

    @GlobalFormRecognizerAccountPreparer()
    def test_list_model_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            result = client.list_model_infos()
            for res in result:
                test = res

    @GlobalFormRecognizerAccountPreparer()
    def test_delete_model_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            client.delete_model("xx")

    @GlobalFormRecognizerAccountPreparer()
    def test_account_properties(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        properties = client.get_account_properties()

        self.assertIsNotNone(properties.custom_model_limit)
        self.assertIsNotNone(properties.custom_model_count)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_mgmt_model_labeled(self, client, container_sas_url):

        poller = client.begin_train_model(container_sas_url, use_labels=True)
        labeled_model_from_train = poller.result()

        labeled_model_from_get = client.get_custom_model(labeled_model_from_train.model_id)

        self.assertEqual(labeled_model_from_train.model_id, labeled_model_from_get.model_id)
        self.assertEqual(labeled_model_from_train.status, labeled_model_from_get.status)
        self.assertEqual(labeled_model_from_train.created_on, labeled_model_from_get.created_on)
        self.assertEqual(labeled_model_from_train.last_modified, labeled_model_from_get.last_modified)
        self.assertEqual(labeled_model_from_train.errors, labeled_model_from_get.errors)
        for a, b in zip(labeled_model_from_train.training_documents, labeled_model_from_get.training_documents):
            self.assertEqual(a.document_name, b.document_name)
            self.assertEqual(a.errors, b.errors)
            self.assertEqual(a.page_count, b.page_count)
            self.assertEqual(a.status, b.status)
        for a, b in zip(labeled_model_from_train.models, labeled_model_from_get.models):
            for field1, field2 in zip(a.fields.items(), b.fields.items()):
                self.assertEqual(a.fields[field1[0]].name, b.fields[field2[0]].name)
                self.assertEqual(a.fields[field1[0]].accuracy, b.fields[field2[0]].accuracy)

        models_list = client.list_model_infos()
        for model in models_list:
            self.assertIsNotNone(model.model_id)
            self.assertEqual(model.status, "ready")
            self.assertIsNotNone(model.created_on)
            self.assertIsNotNone(model.last_modified)

        client.delete_model(labeled_model_from_train.model_id)

        with self.assertRaises(ResourceNotFoundError):
            client.get_custom_model(labeled_model_from_train.model_id)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_mgmt_model_unlabeled(self, client, container_sas_url):

        poller = client.begin_train_model(container_sas_url)
        unlabeled_model_from_train = poller.result()

        unlabeled_model_from_get = client.get_custom_model(unlabeled_model_from_train.model_id)

        self.assertEqual(unlabeled_model_from_train.model_id, unlabeled_model_from_get.model_id)
        self.assertEqual(unlabeled_model_from_train.status, unlabeled_model_from_get.status)
        self.assertEqual(unlabeled_model_from_train.created_on, unlabeled_model_from_get.created_on)
        self.assertEqual(unlabeled_model_from_train.last_modified, unlabeled_model_from_get.last_modified)
        self.assertEqual(unlabeled_model_from_train.errors, unlabeled_model_from_get.errors)
        for a, b in zip(unlabeled_model_from_train.training_documents, unlabeled_model_from_get.training_documents):
            self.assertEqual(a.document_name, b.document_name)
            self.assertEqual(a.errors, b.errors)
            self.assertEqual(a.page_count, b.page_count)
            self.assertEqual(a.status, b.status)
        for a, b in zip(unlabeled_model_from_train.models, unlabeled_model_from_get.models):
            for field1, field2 in zip(a.fields.items(), b.fields.items()):
                self.assertEqual(a.fields[field1[0]].label, b.fields[field2[0]].label)

        models_list = client.list_model_infos()
        for model in models_list:
            self.assertIsNotNone(model.model_id)
            self.assertEqual(model.status, "ready")
            self.assertIsNotNone(model.created_on)
            self.assertIsNotNone(model.last_modified)

        client.delete_model(unlabeled_model_from_train.model_id)

        with self.assertRaises(ResourceNotFoundError):
            client.get_custom_model(unlabeled_model_from_train.model_id)

    @GlobalFormRecognizerAccountPreparer()
    def test_get_form_training_client(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        transport = RequestsTransport()
        frc = FormRecognizerClient(endpoint=form_recognizer_account, credential=AzureKeyCredential(form_recognizer_account_key), transport=transport)

        with frc:
            poller = frc.begin_recognize_receipts_from_url(self.receipt_url_jpg)
            result = poller.result()
            assert transport.session is not None
            with frc.get_form_training_client() as ftc:
                assert transport.session is not None
                properties = ftc.get_account_properties()
            poller = frc.begin_recognize_receipts_from_url(self.receipt_url_jpg)
            result = poller.result()
            assert transport.session is not None
