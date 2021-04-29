
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import functools
from testcase import FormRecognizerTest
from preparers import FormRecognizerPreparer
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from azure.ai.formrecognizer import FormRecognizerClient, FormTrainingClient, FormRecognizerApiVersion

FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)
FormTrainingClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)

class TestMultiapi(FormRecognizerTest):
    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_default_api_version_form_recognizer_client(self, client):
        assert "v2.1-preview.3" in client._client._client._base_url

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    def test_default_api_version_form_training_client(self, client):
        assert "v2.1-preview.3" in client._client._client._base_url

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_v2_0_form_recognizer_client(self, client):
        assert "v2.0" in client._client._client._base_url

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_v2_0_form_training_client(self, client):
        assert "v2.0" in client._client._client._base_url

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_1_PREVIEW})
    def test_v2_1_preview_3_form_recognizer_client(self, client):
        assert "v2.1-preview.3" in client._client._client._base_url

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_1_PREVIEW})
    def test_v2_1_preview_3_form_training_client(self, client):
        assert "v2.1-preview.3" in client._client._client._base_url

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_v2_0_compatibility(self, client, formrecognizer_storage_container_sas_url):
        # test that the addition of new attributes in v2.1 does not break v2.0

        label_poller = client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=True)
        label_result = label_poller.result()

        unlabel_poller = client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
        unlabel_result = unlabel_poller.result()

        assert label_result.properties is None
        assert label_result.model_name is None
        assert unlabel_result.properties is None
        assert unlabel_result.properties is None
        assert label_result.training_documents[0].model_id is None
        assert unlabel_result.training_documents[0].model_id is None

        form_client = client.get_form_recognizer_client()
        label_poller = form_client.begin_recognize_custom_forms_from_url(label_result.model_id, self.form_url_jpg, include_field_elements=True)
        unlabel_poller = form_client.begin_recognize_custom_forms_from_url(unlabel_result.model_id, self.form_url_jpg, include_field_elements=True)


        label_form_result = label_poller.result()
        unlabel_form_result = unlabel_poller.result()

        assert unlabel_form_result[0].form_type_confidence is None
        assert label_form_result[0].form_type_confidence is None
        assert unlabel_form_result[0].pages[0].selection_marks is None
        assert label_form_result[0].pages[0].selection_marks is None
        assert unlabel_form_result[0].pages[0].tables[0].bounding_box is None
        assert label_form_result[0].pages[0].tables[0].bounding_box is None
        assert unlabel_form_result[0].pages[0].lines[0].appearance is None
        assert label_form_result[0].pages[0].lines[0].appearance is None

        models = client.list_custom_models()
        model = list(models)[0]

        assert model.model_name is None
        assert model.properties is None
