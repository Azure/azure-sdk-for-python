# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_custom_default_matcher
from azure.core.pipeline.transport import AioHttpTransport
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import FormTrainingClient
from azure.ai.formrecognizer.aio import FormTrainingClient
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer


FormTrainingClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)


class TestManagementAsync(AsyncFormRecognizerTest):

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy_async
    async def test_account_properties_v2(self, client):
        async with client:
            properties = await client.get_account_properties()

            assert properties.custom_model_limit
            assert properties.custom_model_count

    @pytest.mark.skip("service is returning null for some models")
    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy_async
    async def test_mgmt_model_labeled_v2(self, client, formrecognizer_storage_container_sas_url_v2, **kwargs):
        async with client:
            poller = await client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=True)
            labeled_model_from_train = await poller.result()

            labeled_model_from_get = await client.get_custom_model(labeled_model_from_train.model_id)

            assert labeled_model_from_train.model_id == labeled_model_from_get.model_id
            assert labeled_model_from_train.status == labeled_model_from_get.status
            assert labeled_model_from_train.training_started_on == labeled_model_from_get.training_started_on
            assert labeled_model_from_train.training_completed_on == labeled_model_from_get.training_completed_on
            assert labeled_model_from_train.errors == labeled_model_from_get.errors
            for a, b in zip(labeled_model_from_train.training_documents, labeled_model_from_get.training_documents):
                assert a.name == b.name
                assert a.errors == b.errors
                assert a.page_count == b.page_count
                assert a.status == b.status
            for a, b in zip(labeled_model_from_train.submodels, labeled_model_from_get.submodels):
                for field1, field2 in zip(a.fields.items(), b.fields.items()):
                    assert a.fields[field1[0]].name == b.fields[field2[0]].name
                    assert a.fields[field1[0]].accuracy == b.fields[field2[0]].accuracy

            models_list = client.list_custom_models()
            async for model in models_list:
                assert model.model_id
                assert model.status
                assert model.training_started_on
                assert model.training_completed_on

            await client.delete_model(labeled_model_from_train.model_id)

            with pytest.raises(ResourceNotFoundError):
                await client.get_custom_model(labeled_model_from_train.model_id)

    @pytest.mark.skip("service is returning null for some models")
    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy_async
    async def test_mgmt_model_unlabeled_v2(self, client, formrecognizer_storage_container_sas_url_v2, **kwargs):
        async with client:
            poller = await client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False)
            unlabeled_model_from_train = await poller.result()

            unlabeled_model_from_get = await client.get_custom_model(unlabeled_model_from_train.model_id)

            assert unlabeled_model_from_train.model_id == unlabeled_model_from_get.model_id
            assert unlabeled_model_from_train.status == unlabeled_model_from_get.status
            assert unlabeled_model_from_train.training_started_on == unlabeled_model_from_get.training_started_on
            assert unlabeled_model_from_train.training_completed_on == unlabeled_model_from_get.training_completed_on
            assert unlabeled_model_from_train.errors == unlabeled_model_from_get.errors
            for a, b in zip(unlabeled_model_from_train.training_documents, unlabeled_model_from_get.training_documents):
                assert a.name == b.name
                assert a.errors == b.errors
                assert a.page_count == b.page_count
                assert a.status == b.status
            for a, b in zip(unlabeled_model_from_train.submodels, unlabeled_model_from_get.submodels):
                for field1, field2 in zip(a.fields.items(), b.fields.items()):
                    assert a.fields[field1[0]].label == b.fields[field2[0]].label

            models_list = client.list_custom_models()
            async for model in models_list:
                assert model.model_id
                assert model.status
                assert model.training_started_on
                assert model.training_completed_on

            await client.delete_model(unlabeled_model_from_train.model_id)

            with pytest.raises(ResourceNotFoundError):
                await client.get_custom_model(unlabeled_model_from_train.model_id)

    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_get_form_recognizer_client(self, formrecognizer_test_endpoint, formrecognizer_test_api_key, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )  
        transport = AioHttpTransport()
        ftc = FormTrainingClient(endpoint=formrecognizer_test_endpoint, credential=AzureKeyCredential(formrecognizer_test_api_key), transport=transport, api_version="2.1")

        async with ftc:
            await ftc.get_account_properties()
            assert transport.session is not None
            async with ftc.get_form_recognizer_client() as frc:
                assert transport.session is not None
                await (await frc.begin_recognize_receipts_from_url(self.receipt_url_jpg)).wait()
            await ftc.get_account_properties()
            assert transport.session is not None
