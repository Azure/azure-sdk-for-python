# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

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
    @GlobalTrainingAccountPreparer(copy=True)
    def test_copy_model_successful(self, client, container_sas_url, location, resource_id):

        poller = client.begin_train_model(container_sas_url)
        model = poller.result()

        target = client.get_copy_authorization(resource_region=location, resource_id=resource_id)

        poller = client.begin_copy_model(model.model_id, target=target)
        copy = poller.result()

        copied_model = client.get_custom_model(copy.model_id)

        self.assertEqual(copy.status, "succeeded")
        self.assertIsNotNone(copy.created_on)
        self.assertIsNotNone(copy.last_modified)
        self.assertEqual(target["modelId"], copy.model_id)
        self.assertNotEqual(target["modelId"], model.model_id)
        self.assertIsNotNone(copied_model)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(copy=True)
    def test_copy_model_fail(self, client, container_sas_url, location, resource_id):

        poller = client.begin_train_model(container_sas_url)
        model = poller.result()

        # give an incorrect region
        target = client.get_copy_authorization(resource_region="eastus", resource_id=resource_id)

        with self.assertRaises(HttpResponseError):
            poller = client.begin_copy_model(model.model_id, target=target)
            copy = poller.result()

    @GlobalFormRecognizerAccountPreparer()
    @GlobalTrainingAccountPreparer(copy=True)
    def test_copy_model_transform(self, client, container_sas_url, location, resource_id):

        poller = client.begin_train_model(container_sas_url)
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
        self.assertEqual(copy.created_on, actual.created_date_time)
        self.assertEqual(copy.status, actual.status)
        self.assertEqual(copy.last_modified, actual.last_updated_date_time)
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
