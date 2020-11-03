# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from azure.core.pipeline.transport import AioHttpTransport
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
from azure.ai.formrecognizer.aio import FormTrainingClient
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer
from asynctestcase import AsyncFormRecognizerTest
from testcase import GlobalClientPreparer as _GlobalClientPreparer


GlobalClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)


class TestManagementAsync(AsyncFormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    @pytest.mark.live_test_only
    async def test_active_directory_auth_async(self):
        token = self.generate_oauth_token()
        endpoint = self.get_oauth_endpoint()
        client = FormTrainingClient(endpoint, token)
        async with client:
            props = await client.get_account_properties()
        self.assertIsNotNone(props)

    @GlobalFormRecognizerAccountPreparer()
    async def test_account_properties_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                result = await client.get_account_properties()

    @GlobalFormRecognizerAccountPreparer()
    async def test_get_model_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                result = await client.get_custom_model("xx")

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_get_model_empty_model_id(self, client):
        with self.assertRaises(ValueError):
            async with client:
                result = await client.get_custom_model("")

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_get_model_none_model_id(self, client):
        with self.assertRaises(ValueError):
            async with client:
                result = await client.get_custom_model(None)

    @GlobalFormRecognizerAccountPreparer()
    async def test_list_model_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                result = client.list_custom_models()
                async for res in result:
                    test = res

    @GlobalFormRecognizerAccountPreparer()
    async def test_delete_model_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                result = await client.delete_model("xx")

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_delete_model_none_model_id(self, client):
        with self.assertRaises(ValueError):
            async with client:
                result = await client.delete_model(None)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_delete_model_empty_model_id(self, client):
        with self.assertRaises(ValueError):
            async with client:
                result = await client.delete_model("")

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_account_properties(self, client):
        async with client:
            properties = await client.get_account_properties()

        self.assertIsNotNone(properties.custom_model_limit)
        self.assertIsNotNone(properties.custom_model_count)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    async def test_mgmt_model_labeled(self, client, container_sas_url):
        async with client:
            poller = await client.begin_training(container_sas_url, use_training_labels=True)
            labeled_model_from_train = await poller.result()
            labeled_model_from_get = await client.get_custom_model(labeled_model_from_train.model_id)

            self.assertEqual(labeled_model_from_train.model_id, labeled_model_from_get.model_id)
            self.assertEqual(labeled_model_from_train.status, labeled_model_from_get.status)
            self.assertEqual(labeled_model_from_train.training_started_on, labeled_model_from_get.training_started_on)
            self.assertEqual(labeled_model_from_train.training_completed_on, labeled_model_from_get.training_completed_on)
            self.assertEqual(labeled_model_from_train.errors, labeled_model_from_get.errors)
            for a, b in zip(labeled_model_from_train.training_documents, labeled_model_from_get.training_documents):
                self.assertEqual(a.name, b.name)
                self.assertEqual(a.errors, b.errors)
                self.assertEqual(a.page_count, b.page_count)
                self.assertEqual(a.status, b.status)
            for a, b in zip(labeled_model_from_train.submodels, labeled_model_from_get.submodels):
                for field1, field2 in zip(a.fields.items(), b.fields.items()):
                    self.assertEqual(a.fields[field1[0]].name, b.fields[field2[0]].name)
                    self.assertEqual(a.fields[field1[0]].accuracy, b.fields[field2[0]].accuracy)

            models_list = client.list_custom_models()
            async for model in models_list:
                self.assertIsNotNone(model.model_id)
                self.assertIsNotNone(model.status)
                self.assertIsNotNone(model.training_started_on)
                self.assertIsNotNone(model.training_completed_on)

            await client.delete_model(labeled_model_from_train.model_id)

            with self.assertRaises(ResourceNotFoundError):
                await client.get_custom_model(labeled_model_from_train.model_id)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    async def test_mgmt_model_unlabeled(self, client, container_sas_url):
        async with client:
            poller = await client.begin_training(container_sas_url, use_training_labels=False)
            unlabeled_model_from_train = await poller.result()
            unlabeled_model_from_get = await client.get_custom_model(unlabeled_model_from_train.model_id)

            self.assertEqual(unlabeled_model_from_train.model_id, unlabeled_model_from_get.model_id)
            self.assertEqual(unlabeled_model_from_train.status, unlabeled_model_from_get.status)
            self.assertEqual(unlabeled_model_from_train.training_started_on, unlabeled_model_from_get.training_started_on)
            self.assertEqual(unlabeled_model_from_train.training_completed_on, unlabeled_model_from_get.training_completed_on)
            self.assertEqual(unlabeled_model_from_train.errors, unlabeled_model_from_get.errors)
            for a, b in zip(unlabeled_model_from_train.training_documents, unlabeled_model_from_get.training_documents):
                self.assertEqual(a.name, b.name)
                self.assertEqual(a.errors, b.errors)
                self.assertEqual(a.page_count, b.page_count)
                self.assertEqual(a.status, b.status)
            for a, b in zip(unlabeled_model_from_train.submodels, unlabeled_model_from_get.submodels):
                for field1, field2 in zip(a.fields.items(), b.fields.items()):
                    self.assertEqual(a.fields[field1[0]].label, b.fields[field2[0]].label)

            models_list = client.list_custom_models()
            async for model in models_list:
                self.assertIsNotNone(model.model_id)
                self.assertIsNotNone(model.status)
                self.assertIsNotNone(model.training_started_on)
                self.assertIsNotNone(model.training_completed_on)

            await client.delete_model(unlabeled_model_from_train.model_id)

            with self.assertRaises(ResourceNotFoundError):
                await client.get_custom_model(unlabeled_model_from_train.model_id)

    @GlobalFormRecognizerAccountPreparer()
    @pytest.mark.skip
    async def test_get_form_recognizer_client(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        transport = AioHttpTransport()
        ftc = FormTrainingClient(endpoint=form_recognizer_account, credential=AzureKeyCredential(form_recognizer_account_key), transport=transport)

        async with ftc:
            await ftc.get_account_properties()
            assert transport.session is not None
            async with ftc.get_form_recognizer_client() as frc:
                assert transport.session is not None
                await frc.begin_recognize_receipts_from_url(self.receipt_url_jpg)
            await ftc.get_account_properties()
            assert transport.session is not None
