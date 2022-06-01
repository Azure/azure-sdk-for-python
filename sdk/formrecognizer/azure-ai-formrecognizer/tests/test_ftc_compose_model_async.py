# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_custom_default_matcher
from azure.core.exceptions import HttpResponseError
from azure.ai.formrecognizer.aio import FormTrainingClient
from azure.ai.formrecognizer import CustomFormModel
from preparers import FormRecognizerPreparer
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from asynctestcase import AsyncFormRecognizerTest


FormTrainingClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)


class TestTrainingAsync(AsyncFormRecognizerTest):

    def teardown(self):
        self.sleep(4)

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy_async
    async def test_compose_model_v21(self, client, formrecognizer_storage_container_sas_url_v2, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        async with client:
            poller = await client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=True)
            model_1 = await poller.result()

            poller = await client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=True, model_name="second-labeled-model")
            model_2 = await poller.result()

            poller = await client.begin_create_composed_model([model_1.model_id, model_2.model_id], model_name="my composed model")

            composed_model = await poller.result()

        composed_model_dict = composed_model.to_dict()
        composed_model = CustomFormModel.from_dict(composed_model_dict)
        self.assertComposedModelV2HasValues(composed_model, model_1, model_2)

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy_async
    async def test_compose_model_invalid_unlabeled_models_v21(self, client, formrecognizer_storage_container_sas_url_v2, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        async with client:
            poller = await client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False)
            model_1 = await poller.result()

            poller = await client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False)
            model_2 = await poller.result()

            with pytest.raises(HttpResponseError) as e:
                poller = await client.begin_create_composed_model([model_1.model_id, model_2.model_id])
                composed_model = await poller.result()
            assert e.value.error.code == "1001"
            assert e.value.error.message

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    async def test_compose_model_bad_api_version(self, **kwargs):
        client = kwargs.pop("client")
        async with client:
            with pytest.raises(ValueError) as excinfo:
                poller = await client.begin_create_composed_model(["00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000"])
                result = await poller.result()
            assert "Method 'begin_create_composed_model' is only available for API version V2_1 and up" in str(excinfo.value)
