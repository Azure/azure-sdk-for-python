# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils import recorded_by_proxy, set_custom_default_matcher
from azure.core.exceptions import HttpResponseError
from azure.ai.formrecognizer._models import CustomFormModel
from azure.ai.formrecognizer import FormTrainingClient
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer

FormTrainingClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)

class TestTraining(FormRecognizerTest):

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    @recorded_by_proxy
    def test_training_with_labels_v2(self, client, formrecognizer_storage_container_sas_url_v2, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        poller = client.begin_training(training_files_url=formrecognizer_storage_container_sas_url_v2, use_training_labels=True)
        model = poller.result()

        model_dict = model.to_dict()
        model = CustomFormModel.from_dict(model_dict)

        assert model.model_id
        assert model.training_started_on
        assert model.training_completed_on
        assert model.errors == []
        assert model.status == "ready"
        for doc in model.training_documents:
            assert doc.name
            assert doc.page_count
            assert doc.status
            assert doc.errors == []
        for sub in model.submodels:
            assert sub.form_type
            assert sub.accuracy is not None
            for key, field in sub.fields.items():
                assert field.accuracy is not None
                assert field.name

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    @recorded_by_proxy
    def test_training_multipage_with_labels_v2(self, client, formrecognizer_multipage_storage_container_sas_url_v2, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        poller = client.begin_training(formrecognizer_multipage_storage_container_sas_url_v2, use_training_labels=True)
        model = poller.result()

        assert model.model_id
        assert model.training_started_on
        assert model.training_completed_on
        assert model.errors == []
        assert model.status == "ready"
        for doc in model.training_documents:
            assert doc.name
            assert doc.page_count
            assert doc.status
            assert doc.errors == []
        for sub in model.submodels:
            assert sub.form_type
            assert sub.accuracy is not None
            for key, field in sub.fields.items():
                assert field.accuracy is not None
                assert field.name


    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    @recorded_by_proxy
    def test_training_without_labels_v2(self, client, formrecognizer_storage_container_sas_url_v2, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        poller = client.begin_training(training_files_url=formrecognizer_storage_container_sas_url_v2, use_training_labels=True)
        model = poller.result()

        model_dict = model.to_dict()
        model = CustomFormModel.from_dict(model_dict)

        assert model.model_id
        assert model.training_started_on
        assert model.training_completed_on
        assert model.errors == []
        assert model.status == "ready"
        for doc in model.training_documents:
            assert doc.name
            assert doc.page_count
            assert doc.status
            assert doc.errors == []
        for sub in model.submodels:
            assert sub.form_type
            assert sub.accuracy is not None
            for key, field in sub.fields.items():
                assert field.accuracy is not None
                assert field.name

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    @recorded_by_proxy
    def test_training_multipage_without_labels_v2(self, client, formrecognizer_multipage_storage_container_sas_url_v2, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        poller = client.begin_training(formrecognizer_multipage_storage_container_sas_url_v2, use_training_labels=True)
        model = poller.result()

        assert model.model_id
        assert model.training_started_on
        assert model.training_completed_on
        assert model.errors == []
        assert model.status == "ready"
        for doc in model.training_documents:
            assert doc.name
            assert doc.page_count
            assert doc.status
            assert doc.errors == []
        for sub in model.submodels:
            assert sub.form_type
            assert sub.accuracy is not None
            for key, field in sub.fields.items():
                assert field.accuracy is not None
                assert field.name

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    @recorded_by_proxy
    def test_training_with_files_filter_v2(self, client, formrecognizer_storage_container_sas_url_v2, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        poller = client.begin_training(training_files_url=formrecognizer_storage_container_sas_url_v2, use_training_labels=False, include_subfolders=True)
        model = poller.result()
        assert len(model.training_documents) == 6
        assert model.training_documents[-1].name == "subfolder/Form_6.jpg"  # we traversed subfolders

        poller = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False, prefix="subfolder", include_subfolders=True)
        model = poller.result()
        assert len(model.training_documents) == 1
        assert model.training_documents[0].name == "subfolder/Form_6.jpg"  # we filtered for only subfolders

        with pytest.raises(HttpResponseError) as e:
            poller = client.begin_training(training_files_url=formrecognizer_storage_container_sas_url_v2, use_training_labels=False, prefix="xxx")
            model = poller.result()
        assert e.value.error.code
        assert e.value.error.message

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy
    def test_training_with_labels_v21(self, client, formrecognizer_storage_container_sas_url_v2, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        poller = client.begin_training(training_files_url=formrecognizer_storage_container_sas_url_v2, use_training_labels=True, model_name="my labeled model")
        model = poller.result()

        model_dict = model.to_dict()
        model = CustomFormModel.from_dict(model_dict)

        assert model.model_id
        assert model.model_name == "my labeled model"
        assert model.training_started_on
        assert model.training_completed_on
        assert model.errors == []
        assert model.status == "ready"
        for doc in model.training_documents:
            assert doc.name
            assert doc.page_count
            assert doc.status
            assert doc.errors == []
        for sub in model.submodels:
            assert sub.form_type
            assert sub.accuracy is not None
            for key, field in sub.fields.items():
                assert field.accuracy is not None
                assert field.name

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy
    def test_training_multipage_with_labels_v21(self, client, formrecognizer_multipage_storage_container_sas_url_v2, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        poller = client.begin_training(formrecognizer_multipage_storage_container_sas_url_v2, use_training_labels=True)
        model = poller.result()

        assert model.model_id
        assert model.training_started_on
        assert model.training_completed_on
        assert model.errors == []
        assert model.status == "ready"
        for doc in model.training_documents:
            assert doc.name
            assert doc.page_count
            assert doc.status
            assert doc.errors == []
        for sub in model.submodels:
            assert sub.form_type
            assert sub.accuracy is not None
            for key, field in sub.fields.items():
                assert field.accuracy is not None
                assert field.name

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy
    def test_training_without_labels_v21(self, client, formrecognizer_storage_container_sas_url_v2, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        poller = client.begin_training(training_files_url=formrecognizer_storage_container_sas_url_v2, use_training_labels=True, model_name="my labeled model")
        model = poller.result()

        model_dict = model.to_dict()
        model = CustomFormModel.from_dict(model_dict)

        assert model.model_id
        assert model.model_name == "my labeled model"
        assert model.training_started_on
        assert model.training_completed_on
        assert model.errors == []
        assert model.status == "ready"
        for doc in model.training_documents:
            assert doc.name
            assert doc.page_count
            assert doc.status
            assert doc.errors == []
        for sub in model.submodels:
            assert sub.form_type
            assert sub.accuracy is not None
            for key, field in sub.fields.items():
                assert field.accuracy is not None
                assert field.name

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy
    def test_training_multipage_without_labels_v21(self, client, formrecognizer_multipage_storage_container_sas_url_v2, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        poller = client.begin_training(formrecognizer_multipage_storage_container_sas_url_v2, use_training_labels=True)
        model = poller.result()

        assert model.model_id
        assert model.training_started_on
        assert model.training_completed_on
        assert model.errors == []
        assert model.status == "ready"
        for doc in model.training_documents:
            assert doc.name
            assert doc.page_count
            assert doc.status
            assert doc.errors == []
        for sub in model.submodels:
            assert sub.form_type
            assert sub.accuracy is not None
            for key, field in sub.fields.items():
                assert field.accuracy is not None
                assert field.name

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy
    def test_training_with_files_filter_v21(self, client, formrecognizer_storage_container_sas_url_v2, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        poller = client.begin_training(training_files_url=formrecognizer_storage_container_sas_url_v2, use_training_labels=False, include_subfolders=True)
        model = poller.result()
        assert len(model.training_documents) == 6
        assert model.training_documents[-1].name == "subfolder/Form_6.jpg"  # we traversed subfolders

        poller = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False, prefix="subfolder", include_subfolders=True)
        model = poller.result()
        assert len(model.training_documents) == 1
        assert model.training_documents[0].name == "subfolder/Form_6.jpg"  # we filtered for only subfolders

        with pytest.raises(HttpResponseError) as e:
            poller = client.begin_training(training_files_url=formrecognizer_storage_container_sas_url_v2, use_training_labels=False, prefix="xxx")
            model = poller.result()
        assert e.value.error.code
        assert e.value.error.message

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    def test_training_with_model_name_bad_api_version(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError) as excinfo:
            poller = client.begin_training(training_files_url="url", use_training_labels=True, model_name="not supported in v2.0")
            result = poller.result()
        assert "'model_name' is only available for API version V2_1 and up" in str(excinfo.value)
