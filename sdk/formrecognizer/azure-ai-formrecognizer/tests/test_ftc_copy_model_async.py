# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
import uuid
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import HttpResponseError
from azure.ai.formrecognizer.aio import FormTrainingClient
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from conftest import skip_flaky_test


FormTrainingClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)


class TestCopyModelAsync(AsyncFormRecognizerTest):

    @skip_flaky_test
    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    @recorded_by_proxy_async
    async def test_copy_model_successful_v2(self, client, formrecognizer_storage_container_sas_url_v2, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        async with client:
            poller = await client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False)
            model = await poller.result()

            target = await client.get_copy_authorization(resource_region=formrecognizer_region, resource_id=formrecognizer_resource_id)

            poller = await client.begin_copy_model(model.model_id, target=target)
            copy = await poller.result()

            copied_model = await client.get_custom_model(copy.model_id)

            assert copy.status == "ready"
            assert copy.training_started_on
            assert copy.training_completed_on
            assert target["modelId"] == copy.model_id
            assert target["modelId"] != model.model_id
            assert copied_model

    @skip_flaky_test
    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy_async
    async def test_copy_model_with_labeled_model_name_v21(self, client, formrecognizer_storage_container_sas_url_v2, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        async with client:
            poller = await client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=True, model_name="mymodel")
            model = await poller.result()

            target = await client.get_copy_authorization(resource_region=formrecognizer_region, resource_id=formrecognizer_resource_id)

            poller = await client.begin_copy_model(model.model_id, target=target)
            copy = await poller.result()

            copied_model = await client.get_custom_model(copy.model_id)

            assert copy.status =="ready"
            assert copy.training_started_on
            assert copy.training_completed_on
            assert target["modelId"] == copy.model_id
            assert target["modelId"] != model.model_id
            assert copied_model
            assert copied_model.model_name == "mymodel"

    @skip_flaky_test
    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy_async
    async def test_copy_model_with_unlabeled_model_name_v21(self, client, formrecognizer_storage_container_sas_url_v2, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        async with client:
            poller = await client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False, model_name="mymodel")
            model = await poller.result()

            target = await client.get_copy_authorization(resource_region=formrecognizer_region, resource_id=formrecognizer_resource_id)

            poller = await client.begin_copy_model(model.model_id, target=target)
            copy = await poller.result()

            copied_model = await client.get_custom_model(copy.model_id)

            assert copy.status == "ready"
            assert copy.training_started_on
            assert copy.training_completed_on
            assert target["modelId"] == copy.model_id
            assert target["modelId"] != model.model_id
            assert copied_model
            assert copied_model.model_name == "mymodel"

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy_async
    async def test_copy_model_fail_v21(self, client, formrecognizer_storage_container_sas_url_v2, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        async with client:
            poller = await client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False)
            model = await poller.result()

            # give an incorrect region
            target = await client.get_copy_authorization(resource_region="eastus2", resource_id=formrecognizer_resource_id)

            with pytest.raises(HttpResponseError) as e:
                poller = await client.begin_copy_model(model.model_id, target=target)
                copy = await poller.result()
            assert e.value.error.code == "2024"
            assert e.value.error.message

    @skip_flaky_test
    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy_async
    async def test_copy_model_case_insensitive_region_v21(self, client, formrecognizer_storage_container_sas_url_v2, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        async with client:
            poller = await client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False)
            model = await poller.result()

            # give region all uppercase
            target = await client.get_copy_authorization(resource_region=formrecognizer_region.upper(), resource_id=formrecognizer_resource_id)

            poller = await client.begin_copy_model(model.model_id, target=target)
            copy = await poller.result()

            assert copy.status == "ready"
            assert copy.training_started_on
            assert copy.training_completed_on
            assert target["modelId"] == copy.model_id
            assert target["modelId"] != model.model_id

    @skip_flaky_test
    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    @recorded_by_proxy_async
    async def test_copy_authorization_v2(self, client, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        async with client:
            target = await client.get_copy_authorization(resource_region="eastus", resource_id=formrecognizer_resource_id)

            assert target["modelId"]
            assert target["accessToken"]
            assert target["expirationDateTimeTicks"]
            assert target["resourceRegion"] == "eastus"
            assert target["resourceId"] == formrecognizer_resource_id

    @skip_flaky_test
    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy_async
    async def test_copy_authorization_v21(self, client, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        async with client:
            target = await client.get_copy_authorization(resource_region="eastus", resource_id=formrecognizer_resource_id)

            assert target["modelId"]
            assert target["accessToken"]
            assert target["expirationDateTimeTicks"]
            assert target["resourceRegion"] == "eastus"
            assert target["resourceId"] == formrecognizer_resource_id

    @skip_flaky_test
    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy_async
    async def test_copy_model_with_composed_model_v21(self, client, formrecognizer_storage_container_sas_url_v2, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        async with client:
            poller_1 = await client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=True, model_name="model1")
            model_1 = await poller_1.result()

            poller_2 = await client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=True, model_name="model2")
            model_2 = await poller_2.result()

            composed_poller = await client.begin_create_composed_model([model_1.model_id, model_2.model_id], model_name="composedmodel")
            composed_model = await composed_poller.result()

            target = await client.get_copy_authorization(resource_region=formrecognizer_region, resource_id=formrecognizer_resource_id)

            poller = await client.begin_copy_model(composed_model.model_id, target=target)
            copy = await poller.result()

            copied_model = await client.get_custom_model(copy.model_id)

            assert copy.status == "ready"
            assert copy.training_started_on
            assert copy.training_completed_on
            assert target["modelId"] == copy.model_id
            assert target["modelId"] != composed_model.model_id
            assert copied_model
            assert copied_model.model_name == "composedmodel"
            for submodel in copied_model.submodels:
                assert submodel.model_id in [model_1.model_id, model_2.model_id]
