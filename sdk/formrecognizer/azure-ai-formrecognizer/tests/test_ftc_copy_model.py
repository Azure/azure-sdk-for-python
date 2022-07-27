# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import uuid
import functools
from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import HttpResponseError
from azure.ai.formrecognizer import FormTrainingClient
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer, is_public_cloud

FormTrainingClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)


class TestCopyModel(FormRecognizerTest):

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    @recorded_by_proxy
    def test_copy_model_successful_v2(self, client, formrecognizer_storage_container_sas_url_v2, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        
        poller = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False)
        model = poller.result()

        target = client.get_copy_authorization(resource_region=formrecognizer_region, resource_id=formrecognizer_resource_id)

        poller = client.begin_copy_model(model.model_id, target=target)
        copy = poller.result()

        copied_model = client.get_custom_model(copy.model_id)

        assert copy.status == "ready"
        assert copy.training_started_on
        assert copy.training_completed_on
        assert target["modelId"] == copy.model_id
        assert target["modelId"] != model.model_id
        assert copied_model

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy
    def test_copy_model_with_labeled_model_name_v21(self, client, formrecognizer_storage_container_sas_url_v2, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        
        poller = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=True, model_name="mymodel")
        model = poller.result()

        target = client.get_copy_authorization(resource_region=formrecognizer_region, resource_id=formrecognizer_resource_id)

        poller = client.begin_copy_model(model.model_id, target=target)
        copy = poller.result()

        copied_model = client.get_custom_model(copy.model_id)

        assert copy.status =="ready"
        assert copy.training_started_on
        assert copy.training_completed_on
        assert target["modelId"] == copy.model_id
        assert target["modelId"] != model.model_id
        assert copied_model
        assert copied_model.model_name == "mymodel"

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy
    def test_copy_model_with_unlabeled_model_name_v21(self, client, formrecognizer_storage_container_sas_url_v2, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        
        poller = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False, model_name="mymodel")
        model = poller.result()

        target = client.get_copy_authorization(resource_region=formrecognizer_region, resource_id=formrecognizer_resource_id)

        poller = client.begin_copy_model(model.model_id, target=target)
        copy = poller.result()

        copied_model = client.get_custom_model(copy.model_id)

        assert copy.status == "ready"
        assert copy.training_started_on
        assert copy.training_completed_on
        assert target["modelId"] == copy.model_id
        assert target["modelId"] != model.model_id
        assert copied_model
        assert copied_model.model_name == "mymodel"

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy
    def test_copy_model_fail_v21(self, client, formrecognizer_storage_container_sas_url_v2, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        if (not is_public_cloud() and self.is_live):
            pytest.skip("This test is skipped in usgov/china region. Follow up with service team.")

        poller = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False)
        model = poller.result()

        # give an incorrect region
        target = client.get_copy_authorization(resource_region="eastus", resource_id=formrecognizer_resource_id)

        with pytest.raises(HttpResponseError) as e:
            poller = client.begin_copy_model(model.model_id, target=target)
            copy = poller.result()
        assert e.value.error.code == "2024"
        assert e.value.error.message

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy
    def test_copy_model_case_insensitive_region_v21(self, client, formrecognizer_storage_container_sas_url_v2, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        
        poller = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False)
        model = poller.result()

        # give region all uppercase
        target = client.get_copy_authorization(resource_region=formrecognizer_region.upper(), resource_id=formrecognizer_resource_id)

        poller = client.begin_copy_model(model.model_id, target=target)
        copy = poller.result()

        assert copy.status == "ready"
        assert copy.training_started_on
        assert copy.training_completed_on
        assert target["modelId"] == copy.model_id
        assert target["modelId"] != model.model_id

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    @recorded_by_proxy
    def test_copy_authorization_v2(self, client, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        
        target = client.get_copy_authorization(resource_region="eastus", resource_id=formrecognizer_resource_id)

        assert target["modelId"]
        assert target["accessToken"]
        assert target["expirationDateTimeTicks"]
        assert target["resourceRegion"] == "eastus"
        assert target["resourceId"] == formrecognizer_resource_id

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy
    def test_copy_authorization_v21(self, client, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        
        target = client.get_copy_authorization(resource_region="eastus", resource_id=formrecognizer_resource_id)

        assert target["modelId"]
        assert target["accessToken"]
        assert target["expirationDateTimeTicks"]
        assert target["resourceRegion"] == "eastus"
        assert target["resourceId"] == formrecognizer_resource_id

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy
    def test_copy_model_with_composed_model_v21(self, client, formrecognizer_storage_container_sas_url_v2, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        
        poller_1 = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=True, model_name="model1")
        model_1 = poller_1.result()

        poller_2 = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=True, model_name="model2")
        model_2 = poller_2.result()

        composed_poller = client.begin_create_composed_model([model_1.model_id, model_2.model_id], model_name="composedmodel")
        composed_model = composed_poller.result()

        target = client.get_copy_authorization(resource_region=formrecognizer_region, resource_id=formrecognizer_resource_id)

        poller = client.begin_copy_model(composed_model.model_id, target=target)
        copy = poller.result()

        copied_model = client.get_custom_model(copy.model_id)

        assert copy.status == "ready"
        assert copy.training_started_on
        assert copy.training_completed_on
        assert target["modelId"] == copy.model_id
        assert target["modelId"] != composed_model.model_id
        assert copied_model
        assert copied_model.model_name == "composedmodel"
        for submodel in copied_model.submodels:
            assert submodel.model_id in [model_1.model_id, model_2.model_id]
