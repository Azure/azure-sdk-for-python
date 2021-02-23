# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.ai.formrecognizer import FormTrainingClient
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer


GlobalClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)

class TestTraining(FormRecognizerTest):

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_compose_model_with_model_name(self, client, formrecognizer_storage_container_sas_url):

        poller = client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=True)
        model_1 = poller.result()

        poller = client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=True, model_name="second-labeled-model")
        model_2 = poller.result()

        poller = client.begin_create_composed_model([model_1.model_id, model_2.model_id], model_name="my composed model")

        composed_model = poller.result()
        self.assertEqual(composed_model.model_name, "my composed model")
        self.assertComposedModelHasValues(composed_model, model_1, model_2)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_compose_model_no_model_name(self, client, formrecognizer_storage_container_sas_url):

        poller = client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=True)
        model_1 = poller.result()

        poller = client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=True)
        model_2 = poller.result()

        poller = client.begin_create_composed_model([model_1.model_id, model_2.model_id])

        composed_model = poller.result()
        self.assertIsNone(composed_model.model_name)
        self.assertComposedModelHasValues(composed_model, model_1, model_2)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_compose_model_invalid_unlabeled_models(self, client, formrecognizer_storage_container_sas_url):

        poller = client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
        model_1 = poller.result()

        poller = client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
        model_2 = poller.result()

        with pytest.raises(HttpResponseError) as e:
            poller = client.begin_create_composed_model([model_1.model_id, model_2.model_id])
            composed_model = poller.result()
        self.assertEqual(e.value.error.code, "1001")
        self.assertIsNotNone(e.value.error.message)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    @pytest.mark.live_test_only
    def test_compose_continuation_token(self, client, formrecognizer_storage_container_sas_url):

        poller = client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=True)
        model_1 = poller.result()

        poller = client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=True)
        model_2 = poller.result()

        initial_poller = client.begin_create_composed_model([model_1.model_id, model_2.model_id])
        cont_token = initial_poller.continuation_token()

        poller = client.begin_create_composed_model(None, continuation_token=cont_token)
        result = poller.result()
        self.assertIsNotNone(result)

        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @GlobalClientPreparer(client_kwargs={"api_version": "2.0"})
    def test_compose_model_bad_api_version(self, client, formrecognizer_storage_container_sas_url):
        with pytest.raises(ValueError) as excinfo:
            poller = client.begin_create_composed_model(["00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000"])
            result = poller.result()
        assert "Method 'begin_create_composed_model' is only available for API version V2_1_PREVIEW and up" in str(excinfo.value)
