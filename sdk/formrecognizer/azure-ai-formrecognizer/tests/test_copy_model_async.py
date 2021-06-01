# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from azure.core.exceptions import HttpResponseError
from azure.ai.formrecognizer._generated.models import CopyOperationResult
from azure.ai.formrecognizer import CustomFormModelInfo
from azure.ai.formrecognizer.aio import FormTrainingClient
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer


GlobalClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)


class TestCopyModelAsync(AsyncFormRecognizerTest):

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_copy_model_none_model_id(self, client, formrecognizer_storage_container_sas_url):
        with self.assertRaises(ValueError):
            async with client:
                await client.begin_copy_model(model_id=None, target={})

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_copy_model_empty_model_id(self, client, formrecognizer_storage_container_sas_url):
        with self.assertRaises(ValueError):
            async with client:
                await client.begin_copy_model(model_id="", target={})

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_copy_model_successful(self, client, formrecognizer_storage_container_sas_url, formrecognizer_region, formrecognizer_resource_id):
        async with client:
            training_poller = await client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
            model = await training_poller.result()

            target = await client.get_copy_authorization(resource_region=formrecognizer_region, resource_id=formrecognizer_resource_id)

            copy_poller = await client.begin_copy_model(model.model_id, target=target)
            copy = await copy_poller.result()

            copied_model = await client.get_custom_model(copy.model_id)

        self.assertEqual(copy.status, "ready")
        self.assertIsNotNone(copy.training_started_on)
        self.assertIsNotNone(copy.training_completed_on)
        self.assertEqual(target["modelId"], copy.model_id)
        self.assertNotEqual(target["modelId"], model.model_id)
        self.assertIsNotNone(copied_model)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_copy_model_fail(self, client, formrecognizer_storage_container_sas_url, formrecognizer_region, formrecognizer_resource_id):
        async with client:
            training_poller = await client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
            model = await training_poller.result()

            # give an incorrect region
            target = await client.get_copy_authorization(resource_region="eastus", resource_id=formrecognizer_resource_id)

            with pytest.raises(HttpResponseError) as e:
                poller = await client.begin_copy_model(model.model_id, target=target)
                copy = await poller.result()
            self.assertIsNotNone(e.value.error.code)
            self.assertIsNotNone(e.value.error.message)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_copy_model_case_insensitive_region(self, client, formrecognizer_storage_container_sas_url, formrecognizer_region, formrecognizer_resource_id):
        async with client:
            poller = await client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
            model = await poller.result()

            # give region all uppercase
            target = await client.get_copy_authorization(resource_region=formrecognizer_region.upper(), resource_id=formrecognizer_resource_id)

            poller = await client.begin_copy_model(model.model_id, target=target)
            copy = await poller.result()

        self.assertEqual(copy.status, "ready")
        self.assertIsNotNone(copy.training_started_on)
        self.assertIsNotNone(copy.training_completed_on)
        self.assertEqual(target["modelId"], copy.model_id)
        self.assertNotEqual(target["modelId"], model.model_id)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_copy_model_fail_bad_model_id(self, client, formrecognizer_storage_container_sas_url, formrecognizer_region, formrecognizer_resource_id):

        async with client:
            poller = await client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
            model = await poller.result()

            target = await client.get_copy_authorization(resource_region=formrecognizer_region, resource_id=formrecognizer_resource_id)

            with self.assertRaises(HttpResponseError):
                # give bad model_id
                poller = await client.begin_copy_model("00000000-0000-0000-0000-000000000000", target=target)
                copy = await poller.result()

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_copy_model_transform(self, client, formrecognizer_storage_container_sas_url, formrecognizer_region, formrecognizer_resource_id):
        def callback(response, _, headers):
            copy_result = client._deserialize(CopyOperationResult, response)
            model_info = CustomFormModelInfo._from_generated(copy_result, target["modelId"])
            raw_response.append(copy_result)
            raw_response.append(model_info)

        async with client:
            training_poller = await client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
            model = await training_poller.result()

            target = await client.get_copy_authorization(resource_region=formrecognizer_region, resource_id=formrecognizer_resource_id)

            raw_response = []

            poller = await client.begin_copy_model(model.model_id, target=target, cls=callback)
            copy = await poller.result()

        actual = raw_response[0]
        copy = raw_response[1]
        self.assertEqual(copy.training_started_on, actual.created_date_time)
        self.assertEqual(copy.status, actual.status)
        self.assertEqual(copy.training_completed_on, actual.last_updated_date_time)
        self.assertEqual(copy.model_id, target["modelId"])

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_copy_authorization(self, client, formrecognizer_storage_container_sas_url, formrecognizer_region, formrecognizer_resource_id):
        async with client:
            target = await client.get_copy_authorization(resource_region="eastus", resource_id=formrecognizer_resource_id)

        self.assertIsNotNone(target["modelId"])
        self.assertIsNotNone(target["accessToken"])
        self.assertIsNotNone(target["expirationDateTimeTicks"])
        self.assertEqual(target["resourceRegion"], "eastus")
        self.assertEqual(target["resourceId"], formrecognizer_resource_id)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    @pytest.mark.live_test_only
    async def test_copy_continuation_token(self, client, formrecognizer_storage_container_sas_url, formrecognizer_region, formrecognizer_resource_id):
        async with client:
            poller = await client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
            model = await poller.result()

            target = await client.get_copy_authorization(resource_region=formrecognizer_region, resource_id=formrecognizer_resource_id)

            initial_poller = await client.begin_copy_model(model.model_id, target=target)
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_copy_model(model.model_id, None, continuation_token=cont_token)
            result = await poller.result()
            self.assertIsNotNone(result)

            copied_model = await client.get_custom_model(result.model_id)
            self.assertIsNotNone(copied_model)
            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_copy_model_with_labeled_model_name(self, client, formrecognizer_storage_container_sas_url, formrecognizer_region, formrecognizer_resource_id):
        async with client:
            poller = await client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=True, model_name="mymodel")
            model = await poller.result()

            target = await client.get_copy_authorization(resource_region=formrecognizer_region, resource_id=formrecognizer_resource_id)

            poller = await client.begin_copy_model(model.model_id, target=target)
            copy = await poller.result()

            copied_model = await client.get_custom_model(copy.model_id)

        self.assertEqual(copy.status, "ready")
        self.assertIsNotNone(copy.training_started_on)
        self.assertIsNotNone(copy.training_completed_on)
        self.assertEqual(target["modelId"], copy.model_id)
        self.assertNotEqual(target["modelId"], model.model_id)
        self.assertIsNotNone(copied_model)
        self.assertEqual(copied_model.model_name, "mymodel")

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_copy_model_with_unlabeled_model_name(self, client, formrecognizer_storage_container_sas_url, formrecognizer_region, formrecognizer_resource_id):
        async with client:
            poller = await client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False, model_name="mymodel")
            model = await poller.result()

            target = await client.get_copy_authorization(resource_region=formrecognizer_region, resource_id=formrecognizer_resource_id)

            poller = await client.begin_copy_model(model.model_id, target=target)
            copy = await poller.result()

            copied_model = await client.get_custom_model(copy.model_id)

        self.assertEqual(copy.status, "ready")
        self.assertIsNotNone(copy.training_started_on)
        self.assertIsNotNone(copy.training_completed_on)
        self.assertEqual(target["modelId"], copy.model_id)
        self.assertNotEqual(target["modelId"], model.model_id)
        self.assertIsNotNone(copied_model)
        self.assertEqual(copied_model.model_name, "mymodel")

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_copy_model_with_composed_model(self, client, formrecognizer_storage_container_sas_url, formrecognizer_region, formrecognizer_resource_id):
        async with client:
            poller_1 = await client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=True, model_name="model1")
            model_1 = await poller_1.result()

            poller_2 = await client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=True, model_name="model2")
            model_2 = await poller_2.result()

            composed_poller = await client.begin_create_composed_model([model_1.model_id, model_2.model_id], model_name="composedmodel")
            composed_model = await composed_poller.result()

            target = await client.get_copy_authorization(resource_region=formrecognizer_region, resource_id=formrecognizer_resource_id)

            poller = await client.begin_copy_model(composed_model.model_id, target=target)
            copy = await poller.result()

            copied_model = await client.get_custom_model(copy.model_id)

        self.assertEqual(copy.status, "ready")
        self.assertIsNotNone(copy.training_started_on)
        self.assertIsNotNone(copy.training_completed_on)
        self.assertEqual(target["modelId"], copy.model_id)
        self.assertNotEqual(target["modelId"], composed_model.model_id)
        self.assertIsNotNone(copied_model)
        self.assertEqual(copied_model.model_name, "composedmodel")
        for submodel in copied_model.submodels:
            assert submodel.model_id in [model_1.model_id, model_2.model_id]
