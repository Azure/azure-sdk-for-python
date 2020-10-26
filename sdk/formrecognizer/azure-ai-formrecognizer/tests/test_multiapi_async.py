
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from testcase import GlobalFormRecognizerAccountPreparer
from testcase import GlobalClientPreparer as _GlobalClientPreparer
from asynctestcase import AsyncFormRecognizerTest
from azure.ai.formrecognizer.aio import FormRecognizerClient, FormTrainingClient
from azure.ai.formrecognizer import FormRecognizerApiVersion

FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)
FormTrainingClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)

class TestMultiapi(AsyncFormRecognizerTest):
    @GlobalFormRecognizerAccountPreparer()
    @FormRecognizerClientPreparer()
    def test_default_api_version_form_recognizer_client(self, client):
        assert "v2.1-preview.1" in client._client._client._base_url

    @GlobalFormRecognizerAccountPreparer()
    @FormTrainingClientPreparer()
    def test_default_api_version_form_training_client(self, client):
        assert "v2.1-preview.1" in client._client._client._base_url

    @GlobalFormRecognizerAccountPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_v2_0_form_recognizer_client(self, client):
        assert "v2.0" in client._client._client._base_url

    @GlobalFormRecognizerAccountPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_v2_0_form_training_client(self, client):
        assert "v2.0" in client._client._client._base_url

    @GlobalFormRecognizerAccountPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_1_PREVIEW})
    def test_v2_1_preview_1_form_recognizer_client(self, client):
        assert "v2.1-preview.1" in client._client._client._base_url

    @GlobalFormRecognizerAccountPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_1_PREVIEW})
    def test_v2_1_preview_1_form_training_client(self, client):
        assert "v2.1-preview.1" in client._client._client._base_url

    @GlobalFormRecognizerAccountPreparer()
    @FormTrainingClientPreparer(training=True, client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    async def test_v2_0_compatibility(self, client, container_sas_url):
        # test that the addition of new attributes in v2.1 does not break v2.0
        async with client:
            label_poller = await client.begin_training(container_sas_url, use_training_labels=True)
            label_result = await label_poller.result()

            unlabel_poller = await client.begin_training(container_sas_url, use_training_labels=False)
            unlabel_result = await unlabel_poller.result()

            assert label_result.properties is None
            assert label_result.model_name is None
            assert unlabel_result.properties is None
            assert unlabel_result.properties is None
            assert label_result.training_documents[0].model_id is None
            assert unlabel_result.training_documents[0].model_id is None

            form_client = client.get_form_recognizer_client()
            async with form_client:
                label_poller = await form_client.begin_recognize_custom_forms_from_url(label_result.model_id, self.form_url_jpg)
                unlabel_poller = await form_client.begin_recognize_custom_forms_from_url(unlabel_result.model_id, self.form_url_jpg)

                label_form_result = await label_poller.result()
                unlabel_form_result = await unlabel_poller.result()

            assert unlabel_form_result[0].form_type_confidence is None
            assert label_form_result[0].form_type_confidence is None
            assert unlabel_form_result[0].pages[0].selection_marks is None
            assert label_form_result[0].pages[0].selection_marks is None

            models = client.list_custom_models()
            first_model = await models.__anext__()

            assert first_model.model_name is None
            assert first_model.properties is None
