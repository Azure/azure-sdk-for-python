
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import functools
from devtools_testutils import recorded_by_proxy
from testcase import FormRecognizerTest
from preparers import FormRecognizerPreparer
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from azure.ai.formrecognizer import (
    FormRecognizerClient,
    FormTrainingClient,
    FormRecognizerApiVersion,
    DocumentAnalysisApiVersion,
    DocumentAnalysisClient,
    DocumentModelAdministrationClient
)

FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)
FormTrainingClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)
DocumentAnalysisClientPreparer = functools.partial(_GlobalClientPreparer, DocumentAnalysisClient)


class TestMultiapi(FormRecognizerTest):

    def teardown(self):
        self.sleep(4)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_default_api_version_form_recognizer_client(self, **kwargs):
        client = kwargs.pop("client")
        assert "v2.1" in client._client._client._base_url

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    def test_default_api_version_form_training_client(self, **kwargs):
        client = kwargs.pop("client")
        assert "v2.1" in client._client._client._base_url

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_v2_0_form_recognizer_client(self, **kwargs):
        client = kwargs.pop("client")
        assert "v2.0" in client._client._client._base_url

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_v2_0_form_training_client(self, **kwargs):
        client = kwargs.pop("client")
        assert "v2.0" in client._client._client._base_url

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_1})
    def test_v2_1_form_recognizer_client(self, **kwargs):
        client = kwargs.pop("client")
        assert "v2.1" in client._client._client._base_url

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_1})
    def test_v2_1_form_training_client(self, **kwargs):
        client = kwargs.pop("client")
        assert "v2.1" in client._client._client._base_url

    @FormRecognizerPreparer()
    def test_bad_api_version_form_recognizer_client(self):
        with pytest.raises(ValueError) as excinfo:
            client = FormRecognizerClient("url", "key", api_version="9")
        assert "Unsupported API version '9'. Please select from: {}".format(
                ", ".join(v.value for v in FormRecognizerApiVersion)) == str(excinfo.value)

    @FormRecognizerPreparer()
    def test_bad_api_version_form_training_client(self):
        with pytest.raises(ValueError) as excinfo:
            client = FormTrainingClient("url", "key", api_version="9")
        assert "Unsupported API version '9'. Please select from: {}".format(
                ", ".join(v.value for v in FormRecognizerApiVersion)) == str(excinfo.value)

    @FormRecognizerPreparer()
    def test_document_api_version_form_recognizer_client(self):
        with pytest.raises(ValueError) as excinfo:
            client = FormRecognizerClient("url", "key", api_version=DocumentAnalysisApiVersion.V2022_06_30_PREVIEW)
        assert "Unsupported API version '2022-06-30-preview'. Please select from: {}\nAPI version '2022-06-30-preview' is " \
               "only available for DocumentAnalysisClient and DocumentModelAdministrationClient.".format(
            ", ".join(v.value for v in FormRecognizerApiVersion)) == str(excinfo.value)

    @FormRecognizerPreparer()
    def test_document_api_version_form_training_client(self):
        with pytest.raises(ValueError) as excinfo:
            client = FormTrainingClient("url", "key", api_version=DocumentAnalysisApiVersion.V2022_06_30_PREVIEW)
        assert "Unsupported API version '2022-06-30-preview'. Please select from: {}\nAPI version '2022-06-30-preview' is " \
               "only available for DocumentAnalysisClient and DocumentModelAdministrationClient.".format(
            ", ".join(v.value for v in FormRecognizerApiVersion)) == str(excinfo.value)

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_default_api_version_document_analysis_client(self, **kwargs):
        client = kwargs.pop("client")
        assert "2022-06-30-preview" == client._api_version

    @FormRecognizerPreparer()
    def test_bad_api_version_document_analysis_client(self):
        with pytest.raises(ValueError) as excinfo:
            client = DocumentAnalysisClient("url", "key", api_version="9")
        assert "Unsupported API version '9'. Please select from: {}".format(
                ", ".join(v.value for v in DocumentAnalysisApiVersion)) == str(excinfo.value)

    @FormRecognizerPreparer()
    def test_form_api_version_document_analysis_client(self):
        with pytest.raises(ValueError) as excinfo:
            client = DocumentModelAdministrationClient("url", "key", api_version=FormRecognizerApiVersion.V2_1)
        assert "Unsupported API version '2.1'. Please select from: {}\nAPI version '2.1' is " \
               "only available for FormRecognizerClient and FormTrainingClient.".format(
            ", ".join(v.value for v in DocumentAnalysisApiVersion)) == str(excinfo.value)

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_default_api_version_document_model_admin_client(self, **kwargs):
        client = kwargs.pop("client")
        assert "2022-06-30-preview" == client._api_version

    @FormRecognizerPreparer()
    def test_bad_api_version_document_model_admin_client(self):
        with pytest.raises(ValueError) as excinfo:
            client = DocumentModelAdministrationClient("url", "key", api_version="9")
        assert "Unsupported API version '9'. Please select from: {}".format(
                ", ".join(v.value for v in DocumentAnalysisApiVersion)) == str(excinfo.value)

    @FormRecognizerPreparer()
    def test_form_api_version_document_model_admin_client(self):
        with pytest.raises(ValueError) as excinfo:
            client = DocumentModelAdministrationClient("url", "key", api_version=FormRecognizerApiVersion.V2_1)
        assert "Unsupported API version '2.1'. Please select from: {}\nAPI version '2.1' is " \
               "only available for FormRecognizerClient and FormTrainingClient.".format(
            ", ".join(v.value for v in DocumentAnalysisApiVersion)) == str(excinfo.value)

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    @recorded_by_proxy
    def test_v2_0_compatibility(self, client, formrecognizer_storage_container_sas_url_v2, **kwargs):
        # test that the addition of new attributes in v2.1 does not break v2.0

        label_poller = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=True)
        label_result = label_poller.result()

        unlabelled_poller = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False)
        unlabelled_result = unlabelled_poller.result()

        assert label_result.properties is None
        assert label_result.model_name is None
        assert unlabelled_result.properties is None
        assert unlabelled_result.properties is None
        assert label_result.training_documents[0].model_id is None
        assert unlabelled_result.training_documents[0].model_id is None

        form_client = client.get_form_recognizer_client()
        label_poller = form_client.begin_recognize_custom_forms_from_url(label_result.model_id, self.form_url_jpg, include_field_elements=True)
        unlabelled_poller = form_client.begin_recognize_custom_forms_from_url(unlabelled_result.model_id, self.form_url_jpg, include_field_elements=True)


        label_form_result = label_poller.result()
        unlabelled_form_result = unlabelled_poller.result()

        assert unlabelled_form_result[0].form_type_confidence is None
        assert label_form_result[0].form_type_confidence is None
        assert unlabelled_form_result[0].pages[0].selection_marks is None
        assert label_form_result[0].pages[0].selection_marks is None
        assert unlabelled_form_result[0].pages[0].tables[0].bounding_box is None
        assert label_form_result[0].pages[0].tables[0].bounding_box is None
        assert unlabelled_form_result[0].pages[0].lines[0].appearance is None
        assert label_form_result[0].pages[0].lines[0].appearance is None

        models = client.list_custom_models()
        model = list(models)[0]

        assert model.model_name is None
        assert model.properties is None
