# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from azure.ai.formrecognizer._generated.models import Model
from azure.ai.formrecognizer._models import CustomFormModel
from azure.ai.formrecognizer.aio import FormRecognizerClient
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer, GlobalFormAndStorageAccountPreparer
from testcase import GlobalTrainingAccountPreparer as _GlobalTrainingAccountPreparer
from asynctestcase import AsyncFormRecognizerTest

GlobalTrainingAccountPreparer = functools.partial(_GlobalTrainingAccountPreparer, FormRecognizerClient)


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy==3.0.0 bug

    # records location header as a list of char instead of str
    """

    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if response.headers.get("location") and isinstance(response.headers["location"], list):
            response_dict = {header: value for header, value in response.headers.items()}
            response_dict["location"] = "".join(response.headers.get("location"))
            response.headers = CIMultiDictProxy(CIMultiDict(response_dict))
        return response


class TestTrainingAsync(AsyncFormRecognizerTest):

    @GlobalFormAndStorageAccountPreparer()
    @GlobalTrainingAccountPreparer()
    async def test_training(self, client, container_sas_url):
        training_client = client.get_form_training_client(transport=AiohttpTestTransport())
        model = await training_client.training(container_sas_url)

        self.assertIsNotNone(model.model_id)
        self.assertIsNotNone(model.created_on)
        self.assertIsNotNone(model.last_modified)
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
    async def test_training_transform(self, client, container_sas_url):
        training_client = client.get_form_training_client(transport=AiohttpTestTransport())

        raw_response = []

        def callback(response):
            raw_model = training_client._client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        model = await training_client.training(container_sas_url, cls=callback)

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model, unlabeled=True)

    @GlobalFormAndStorageAccountPreparer()
    @GlobalTrainingAccountPreparer()
    async def test_training_with_labels(self, client, container_sas_url):
        training_client = client.get_form_training_client(transport=AiohttpTestTransport())

        model = await training_client.training(container_sas_url, use_labels=True)

        self.assertIsNotNone(model.model_id)
        self.assertIsNotNone(model.created_on)
        self.assertIsNotNone(model.last_modified)
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
    async def test_training_with_labels_transform(self, client, container_sas_url):
        training_client = client.get_form_training_client(transport=AiohttpTestTransport())

        raw_response = []

        def callback(response):
            raw_model = training_client._client._deserialize(Model, response)
            custom_model = CustomFormModel._from_generated(raw_model)
            raw_response.append(raw_model)
            raw_response.append(custom_model)

        model = await training_client.training(container_sas_url, use_labels=True, cls=callback)

        raw_model = raw_response[0]
        custom_model = raw_response[1]
        self.assertModelTransformCorrect(custom_model, raw_model)

    @GlobalFormAndStorageAccountPreparer()
    @GlobalTrainingAccountPreparer()
    async def test_training_with_files_filter(self, client, container_sas_url):
        training_client = client.get_form_training_client(transport=AiohttpTestTransport())

        model = await training_client.training(container_sas_url, include_sub_folders=True)
        self.assertEqual(len(model.training_documents), 6)
        self.assertEqual(model.training_documents[-1].document_name, "subfolder/Form_6.jpg")  # we traversed subfolders

        model = await training_client.training(container_sas_url, prefix="subfolder", include_sub_folders=True)
        self.assertEqual(len(model.training_documents), 1)
        self.assertEqual(model.training_documents[0].document_name, "subfolder/Form_6.jpg")  # we filtered for only subfolders

        model = await training_client.training(container_sas_url, prefix="xxx")
        self.assertEqual(model.status, "invalid")  # prefix doesn't include any files so training fails
