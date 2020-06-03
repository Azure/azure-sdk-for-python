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
    def test_get_model_empty_model_id(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with self.assertRaises(ValueError):
            result = client.get_custom_model("")

    @GlobalFormRecognizerAccountPreparer()
    def test_get_model_none_model_id(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with self.assertRaises(ValueError):
            result = client.get_custom_model(None)

    @GlobalFormRecognizerAccountPreparer()
    def test_list_model_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            result = client.list_custom_models()
            for res in result:
                test = res

    @GlobalFormRecognizerAccountPreparer()
    def test_delete_model_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            client.delete_model("xx")

    @GlobalFormRecognizerAccountPreparer()
    def test_delete_model_none_model_id(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with self.assertRaises(ValueError):
            result = client.delete_model(None)

    @GlobalFormRecognizerAccountPreparer()
    def test_delete_model_empty_model_id(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with self.assertRaises(ValueError):
            result = client.delete_model("")

    @GlobalFormRecognizerAccountPreparer()
    def test_account_properties(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        properties = client.get_account_properties()

        self.assertIsNotNone(properties.custom_model_limit)
        self.assertIsNotNone(properties.custom_model_count)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_mgmt_model_labeled(self, client, container_sas_url):

        poller = client.begin_training(container_sas_url, use_training_labels=True)
        labeled_model_from_train = poller.result()

        labeled_model_from_get = client.get_custom_model(labeled_model_from_train.model_id)

        self.assertEqual(labeled_model_from_train.model_id, labeled_model_from_get.model_id)
        self.assertEqual(labeled_model_from_train.status, labeled_model_from_get.status)
        self.assertEqual(labeled_model_from_train.requested_on, labeled_model_from_get.requested_on)
        self.assertEqual(labeled_model_from_train.completed_on, labeled_model_from_get.completed_on)
        self.assertEqual(labeled_model_from_train.errors, labeled_model_from_get.errors)
        for a, b in zip(labeled_model_from_train.training_documents, labeled_model_from_get.training_documents):
            self.assertEqual(a.document_name, b.document_name)
            self.assertEqual(a.errors, b.errors)
            self.assertEqual(a.page_count, b.page_count)
            self.assertEqual(a.status, b.status)
        for a, b in zip(labeled_model_from_train.submodels, labeled_model_from_get.submodels):
            for field1, field2 in zip(a.fields.items(), b.fields.items()):
                self.assertEqual(a.fields[field1[0]].name, b.fields[field2[0]].name)
                self.assertEqual(a.fields[field1[0]].accuracy, b.fields[field2[0]].accuracy)

        models_list = client.list_custom_models()
        for model in models_list:
            self.assertIsNotNone(model.model_id)
            self.assertIsNotNone(model.status)
            self.assertIsNotNone(model.requested_on)
            self.assertIsNotNone(model.completed_on)

        client.delete_model(labeled_model_from_train.model_id)

        with self.assertRaises(ResourceNotFoundError):
            client.get_custom_model(labeled_model_from_train.model_id)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_mgmt_model_unlabeled(self, client, container_sas_url):

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        unlabeled_model_from_train = poller.result()

        unlabeled_model_from_get = client.get_custom_model(unlabeled_model_from_train.model_id)

        self.assertEqual(unlabeled_model_from_train.model_id, unlabeled_model_from_get.model_id)
        self.assertEqual(unlabeled_model_from_train.status, unlabeled_model_from_get.status)
        self.assertEqual(unlabeled_model_from_train.requested_on, unlabeled_model_from_get.requested_on)
        self.assertEqual(unlabeled_model_from_train.completed_on, unlabeled_model_from_get.completed_on)
        self.assertEqual(unlabeled_model_from_train.errors, unlabeled_model_from_get.errors)
        for a, b in zip(unlabeled_model_from_train.training_documents, unlabeled_model_from_get.training_documents):
            self.assertEqual(a.document_name, b.document_name)
            self.assertEqual(a.errors, b.errors)
            self.assertEqual(a.page_count, b.page_count)
            self.assertEqual(a.status, b.status)
        for a, b in zip(unlabeled_model_from_train.submodels, unlabeled_model_from_get.submodels):
            for field1, field2 in zip(a.fields.items(), b.fields.items()):
                self.assertEqual(a.fields[field1[0]].label, b.fields[field2[0]].label)

        models_list = client.list_custom_models()
        for model in models_list:
            self.assertIsNotNone(model.model_id)
            self.assertIsNotNone(model.status)
            self.assertIsNotNone(model.requested_on)
            self.assertIsNotNone(model.completed_on)

        client.delete_model(unlabeled_model_from_train.model_id)

        with self.assertRaises(ResourceNotFoundError):
            client.get_custom_model(unlabeled_model_from_train.model_id)

    @GlobalFormRecognizerAccountPreparer()
    def test_get_form_recognizer_client(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        transport = RequestsTransport()
        ftc = FormTrainingClient(endpoint=form_recognizer_account, credential=AzureKeyCredential(form_recognizer_account_key), transport=transport)

        with ftc:
            ftc.get_account_properties()
            assert transport.session is not None
            with ftc.get_form_recognizer_client() as frc:
                assert transport.session is not None
                frc.begin_recognize_receipts_from_url(self.receipt_url_jpg).wait()
            ftc.get_account_properties()
            assert transport.session is not None
