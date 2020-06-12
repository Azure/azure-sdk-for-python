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
from azure.ai.formrecognizer import FormTrainingClient
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer
from testcase import GlobalTrainingAccountPreparer as _GlobalTrainingAccountPreparer

GlobalTrainingAccountPreparer = functools.partial(_GlobalTrainingAccountPreparer, FormTrainingClient)


class TestCopyModel(FormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_copy_model_none_model_id(self, client, container_sas_url):
        with self.assertRaises(ValueError):
            client.begin_copy_model(model_id=None, target={})

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_copy_model_empty_model_id(self, client, container_sas_url):
        with self.assertRaises(ValueError):
            client.begin_copy_model(model_id="", target={})

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(copy=True)
    def test_copy_model_successful(self, client, container_sas_url, location, resource_id):

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = poller.result()

        target = client.get_copy_authorization(resource_region=location, resource_id=resource_id)

        poller = client.begin_copy_model(model.model_id, target=target)
        copy = poller.result()

        copied_model = client.get_custom_model(copy.model_id)

        self.assertEqual(copy.status, "ready")
        self.assertIsNotNone(copy.requested_on)
        self.assertIsNotNone(copy.completed_on)
        self.assertEqual(target["modelId"], copy.model_id)
        self.assertNotEqual(target["modelId"], model.model_id)
        self.assertIsNotNone(copied_model)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(copy=True)
    def test_copy_model_fail(self, client, container_sas_url, location, resource_id):

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = poller.result()

        # give an incorrect region
        target = client.get_copy_authorization(resource_region="eastus", resource_id=resource_id)

        with self.assertRaises(HttpResponseError):
            poller = client.begin_copy_model(model.model_id, target=target)
            copy = poller.result()

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(copy=True)
    def test_copy_model_transform(self, client, container_sas_url, location, resource_id):

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = poller.result()

        target = client.get_copy_authorization(resource_region=location, resource_id=resource_id)

        raw_response = []

        def callback(response, _, headers):
            copy_result = client._client._deserialize(CopyOperationResult, response)
            model_info = CustomFormModelInfo._from_generated(copy_result, target["modelId"])
            raw_response.append(copy_result)
            raw_response.append(model_info)

        poller = client.begin_copy_model(model.model_id, target=target, cls=callback)
        copy = poller.result()

        actual = raw_response[0]
        copy = raw_response[1]
        self.assertEqual(copy.requested_on, actual.created_date_time)
        self.assertEqual(copy.status, actual.status)
        self.assertEqual(copy.completed_on, actual.last_updated_date_time)
        self.assertEqual(copy.model_id, target["modelId"])

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(copy=True)
    def test_copy_authorization(self, client, container_sas_url, location, resource_id):

        target = client.get_copy_authorization(resource_region="eastus", resource_id=resource_id)

        self.assertIsNotNone(target["modelId"])
        self.assertIsNotNone(target["accessToken"])
        self.assertIsNotNone(target["expirationDateTimeTicks"])
        self.assertEqual(target["resourceRegion"], "eastus")
        self.assertEqual(target["resourceId"], resource_id)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(copy=True)
    @pytest.mark.live_test_only
    def test_copy_continuation_token(self, client, container_sas_url, location, resource_id):

        poller = client.begin_training(container_sas_url, use_training_labels=False)
        model = poller.result()

        target = client.get_copy_authorization(resource_region=location, resource_id=resource_id)
        initial_poller = client.begin_copy_model(model.model_id, target=target)
        cont_token = initial_poller.continuation_token()

        poller = client.begin_copy_model(model.model_id, target=target, continuation_token=cont_token)
        result = poller.result()
        self.assertIsNotNone(result)

        copied_model = client.get_custom_model(result.model_id)
        self.assertIsNotNone(copied_model)
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error
