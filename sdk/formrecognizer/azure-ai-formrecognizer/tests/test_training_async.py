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
from asynctestcase import AsyncFormRecognizerTest
from testcase import GlobalClientPreparer as _GlobalClientPreparer


GlobalClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)


class TestTrainingAsync(AsyncFormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    async def test_polling_interval(self, client, container_sas_url):
        def check_poll_value(poll):
            if self.is_live:
                self.assertEqual(poll, 5)
            else:
                self.assertEqual(poll, 0)
        check_poll_value(client._client._config.polling_interval)
        poller = await client.begin_training(training_files_url=container_sas_url, use_training_labels=False, polling_interval=6)
        await poller.wait()
        self.assertEqual(poller._polling_method._timeout, 6)
        poller2 = await client.begin_training(training_files_url=container_sas_url, use_training_labels=False)
        await poller2.wait()
        check_poll_value(poller2._polling_method._timeout)  # goes back to client default
        await client.close()

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_training_encoded_url(self, client):
        with self.assertRaises(HttpResponseError):
            async with client:
                poller = await client.begin_training(
                    training_files_url="https://fakeuri.com/blank%20space",
                    use_training_labels=False
                )
                self.assertIn("https://fakeuri.com/blank%20space", poller._polling_method._initial_response.http_request.body)
                await poller.wait()

    @GlobalFormRecognizerAccountPreparer()
    async def test_training_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                poller = await client.begin_training("xx", use_training_labels=False)
                result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    async def test_training(self, client, container_sas_url):

        async with client:
            poller = await client.begin_training(
                training_files_url=container_sas_url,
                use_training_labels=False,
                model_name="my unlabeled model")
            model = await poller.result()

        self.assertIsNotNone(model.model_id)
        # self.assertEqual(model.model_name, "my unlabeled model")  # FIXME: bug in service
        self.assertIsNotNone(model.training_started_on)
        self.assertIsNotNone(model.training_completed_on)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.status, "ready")
        for doc in model.training_documents:
            self.assertIsNotNone(doc.name)
            self.assertIsNotNone(doc.page_count)
            self.assertIsNotNone(doc.status)
            self.assertEqual(doc.errors, [])
        for sub in model.submodels:
            self.assertIsNotNone(sub.form_type)
            for key, field in sub.fields.items():
                self.assertIsNotNone(field.label)
                self.assertIsNotNone(field.name)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, multipage=True)
    async def test_training_multipage(self, client, container_sas_url):
        async with client:
            poller = await client.begin_training(container_sas_url, use_training_labels=False)
            model = await poller.result()

        self.assertIsNotNone(model.model_id)
        self.assertIsNotNone(model.training_started_on)
        self.assertIsNotNone(model.training_completed_on)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.status, "ready")
        for doc in model.training_documents:
            self.assertIsNotNone(doc.name)
            self.assertIsNotNone(doc.page_count)
            self.assertIsNotNone(doc.status)
            self.assertEqual(doc.errors, [])
        for sub in model.submodels:
            self.assertIsNotNone(sub.form_type)
            for key, field in sub.fields.items():
                self.assertIsNotNone(field.label)
                self.assertIsNotNone(field.name)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    async def test_training_transform(self, client, container_sas_url):

        raw_response = []

        def callback(response, _, headers):
            raw_model = client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model, client.api_version)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        async with client:
            poller = await client.begin_training(
                training_files_url=container_sas_url,
                use_training_labels=False,
                cls=callback)
            model = await poller.result()

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model, unlabeled=True)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, multipage=True)
    async def test_training_multipage_transform(self, client, container_sas_url):

        raw_response = []

        def callback(response, _, headers):
            raw_model = client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model, client.api_version)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        async with client:
            poller = await client.begin_training(container_sas_url, use_training_labels=False, cls=callback)
            model = await poller.result()

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model, unlabeled=True)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    async def test_training_with_labels(self, client, container_sas_url):
        async with client:
            poller = await client.begin_training(training_files_url=container_sas_url, use_training_labels=True, model_name="my labeled model")
            model = await poller.result()

        self.assertIsNotNone(model.model_id)
        self.assertEqual(model.model_name, "my labeled model")
        self.assertIsNotNone(model.training_started_on)
        self.assertIsNotNone(model.training_completed_on)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.status, "ready")
        for doc in model.training_documents:
            self.assertIsNotNone(doc.name)
            self.assertIsNotNone(doc.page_count)
            self.assertIsNotNone(doc.status)
            self.assertEqual(doc.errors, [])
        for sub in model.submodels:
            self.assertIsNotNone(sub.form_type)
            for key, field in sub.fields.items():
                self.assertIsNotNone(field.accuracy)
                self.assertIsNotNone(field.name)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, multipage=True)
    async def test_training_multipage_with_labels(self, client, container_sas_url):
        async with client:
            poller = await client.begin_training(container_sas_url, use_training_labels=True)
            model = await poller.result()

        self.assertIsNotNone(model.model_id)
        self.assertIsNotNone(model.training_started_on)
        self.assertIsNotNone(model.training_completed_on)
        self.assertEqual(model.errors, [])
        self.assertEqual(model.status, "ready")
        for doc in model.training_documents:
            self.assertIsNotNone(doc.name)
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
    @GlobalClientPreparer(training=True)
    async def test_training_with_labels_transform(self, client, container_sas_url):

        raw_response = []

        def callback(response, _, headers):
            raw_model = client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model, client.api_version)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        async with client:
            poller = await client.begin_training(training_files_url=container_sas_url, use_training_labels=True, cls=callback)
            model = await poller.result()

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, multipage=True)
    async def test_train_multipage_w_lbls_trnsfrm(self, client, container_sas_url):

        raw_response = []

        def callback(response, _, headers):
            raw_model = client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model, client.api_version)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        async with client:
            poller = await client.begin_training(container_sas_url, use_training_labels=True, cls=callback)
            model = await poller.result()

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    async def test_training_with_files_filter(self, client, container_sas_url):
        async with client:
            poller = await client.begin_training(training_files_url=container_sas_url, use_training_labels=False, include_subfolders=True)
            model = await poller.result()
            self.assertEqual(len(model.training_documents), 6)
            self.assertEqual(model.training_documents[-1].name, "subfolder/Form_6.jpg")  # we traversed subfolders

            poller = await client.begin_training(container_sas_url, use_training_labels=False, prefix="subfolder", include_subfolders=True)
            model = await poller.result()
            self.assertEqual(len(model.training_documents), 1)
            self.assertEqual(model.training_documents[0].name, "subfolder/Form_6.jpg")  # we filtered for only subfolders

            with pytest.raises(HttpResponseError) as e:
                poller = await client.begin_training(training_files_url=container_sas_url, use_training_labels=False, prefix="xxx")
                model = await poller.result()
            self.assertIsNotNone(e.value.error.code)
            self.assertIsNotNone(e.value.error.message)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    @pytest.mark.live_test_only
    async def test_training_continuation_token(self, client, container_sas_url):
        async with client:
            initial_poller = await client.begin_training(training_files_url=container_sas_url, use_training_labels=False)
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_training(None, None, continuation_token=cont_token)
            result = await poller.result()
            self.assertIsNotNone(result)
            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, client_kwargs={"api_version": "2.0"})
    async def test_training_with_model_name_bad_api_version(self, client, container_sas_url):
        with pytest.raises(ValueError) as excinfo:
            poller = await client.begin_training(training_files_url="url", use_training_labels=True, model_name="not supported in v2.0")
            result = await poller.result()
        assert "'model_name' is only available for API version V2_1_PREVIEW and up" in str(excinfo.value)
