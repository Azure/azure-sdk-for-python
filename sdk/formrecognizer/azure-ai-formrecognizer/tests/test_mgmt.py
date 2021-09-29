# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
import pytest
import logging
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
from azure.core.pipeline.transport import RequestsTransport
from azure.ai.formrecognizer import (
    FormTrainingClient,
    DocumentModelAdministrationClient,
    FormRecognizerApiVersion,
    DocumentAnalysisApiVersion,
    ModelOperation
)
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer

FormTrainingClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)
DocumentModelAdministrationClientPreparer = functools.partial(_GlobalClientPreparer, DocumentModelAdministrationClient)


class TestManagement(FormRecognizerTest):

    @pytest.mark.skip("aad not working in canary")
    @FormRecognizerPreparer()
    @pytest.mark.live_test_only
    def test_active_directory_auth(self):
        token = self.generate_oauth_token()
        endpoint = self.get_oauth_endpoint()
        client = DocumentModelAdministrationClient(endpoint, token)
        info = client.get_account_info()
        assert info

    @FormRecognizerPreparer()
    def test_dmac_auth_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = DocumentModelAdministrationClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with pytest.raises(ClientAuthenticationError):
            result = client.get_account_info()

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_get_model_empty_model_id(self, client):
        with pytest.raises(ValueError):
            result = client.get_model("")

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_get_model_none_model_id(self, client):
        with pytest.raises(ValueError):
            result = client.get_model(None)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_delete_model_none_model_id(self, client):
        with pytest.raises(ValueError):
            result = client.delete_model(None)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_delete_model_empty_model_id(self, client):
        with pytest.raises(ValueError):
            result = client.delete_model("")

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_account_info(self, client):
        info = client.get_account_info()

        assert info.model_limit
        assert info.model_count

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_get_model_prebuilt(self, client):
        model = client.get_model("prebuilt-invoice")
        assert model.model_id == "prebuilt-invoice"
        assert model.description is not None
        assert model.created_on
        for name, doc_type in model.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
            assert doc_type.field_confidence is None

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_mgmt_model(self, client, formrecognizer_storage_container_sas_url):

        poller = client.begin_build_model(formrecognizer_storage_container_sas_url, description="mgmt model")
        model = poller.result()

        model_from_get = client.get_model(model.model_id)

        assert model.model_id == model_from_get.model_id
        assert model.description == model_from_get.description
        assert model.created_on == model_from_get.created_on
        for name, doc_type in model.doc_types.items():
            assert name in model_from_get.doc_types
            for key, field in doc_type.field_schema.items():
                assert key in model_from_get.doc_types[name].field_schema
                assert field["type"] == model_from_get.doc_types[name].field_schema[key]["type"]
                assert doc_type.field_confidence[key] == model_from_get.doc_types[name].field_confidence[key]

        models_list = client.list_models()
        for model in models_list:
            assert model.model_id
            assert model.created_on

        client.delete_model(model.model_id)

        with pytest.raises(ResourceNotFoundError):
            client.get_model(model.model_id)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_get_list_operations(self, client):
        operations = client.list_operations()
        successful_op = None
        failed_op = None
        for op in operations:
            assert op.operation_id
            assert op.status
            assert op.percent_completed is not None
            assert op.created_on
            assert op.last_updated_on
            assert op.kind
            assert op.resource_location
            if op.status == "succeeded":
                successful_op = op
            if op.status == "failed":
                failed_op = op

        # check successful op
        if successful_op:
            op = client.get_operation(successful_op.operation_id)
            # test to/from dict
            op_dict = op.to_dict()
            op = ModelOperation.from_dict(op_dict)

            assert op.error is None
            model = op.result
            assert model.model_id
            assert model.description is None
            assert model.created_on
            for name, doc_type in model.doc_types.items():
                assert name
                for key, field in doc_type.field_schema.items():
                    assert key
                    assert field["type"]
                    assert doc_type.field_confidence[key] is not None

        # check failed op
        if failed_op:
            op = client.get_operation(failed_op.operation_id)
            # test to/from dict
            op_dict = op.to_dict()
            op = ModelOperation.from_dict(op_dict)

            assert op.result is None
            error = op.error
            assert error.code
            assert error.message

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_get_operation_bad_model_id(self, client):
        with pytest.raises(ValueError):
            client.get_operation("")
        with pytest.raises(ValueError):
            client.get_operation(None)

    @FormRecognizerPreparer()
    def test_get_document_analysis_client(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        transport = RequestsTransport()
        dtc = DocumentModelAdministrationClient(endpoint=formrecognizer_test_endpoint, credential=AzureKeyCredential(formrecognizer_test_api_key), transport=transport)

        with dtc:
            dtc.get_account_info()
            assert transport.session is not None
            with dtc.get_document_analysis_client() as dac:
                assert transport.session is not None
                dac.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg).wait()
                assert dac._api_version == DocumentAnalysisApiVersion.V2021_09_30_PREVIEW
            dtc.get_account_info()
            assert transport.session is not None

    # --------------------------------------- BACK COMPATABILITY TESTS ---------------------------------------

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    def test_account_properties_v2(self, client):
        properties = client.get_account_properties()

        assert properties.custom_model_limit
        assert properties.custom_model_count

    @pytest.mark.skip("service is returning null for some models")
    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    def test_mgmt_model_labeled_v2(self, client, formrecognizer_storage_container_sas_url_v2):

        poller = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=True)
        labeled_model_from_train = poller.result()

        labeled_model_from_get = client.get_custom_model(labeled_model_from_train.model_id)

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
        for model in models_list:
            assert model.model_id
            assert model.status
            assert model.training_started_on
            assert model.training_completed_on

        client.delete_model(labeled_model_from_train.model_id)

        with pytest.raises(ResourceNotFoundError):
            client.get_custom_model(labeled_model_from_train.model_id)

    @pytest.mark.skip("service is returning null for some models")
    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    def test_mgmt_model_unlabeled_v2(self, client, formrecognizer_storage_container_sas_url_v2):

        poller = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False)
        unlabeled_model_from_train = poller.result()

        unlabeled_model_from_get = client.get_custom_model(unlabeled_model_from_train.model_id)

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
        for model in models_list:
            assert model.model_id
            assert model.status
            assert model.training_started_on
            assert model.training_completed_on

        client.delete_model(unlabeled_model_from_train.model_id)

        with pytest.raises(ResourceNotFoundError):
            client.get_custom_model(unlabeled_model_from_train.model_id)

    @FormRecognizerPreparer()
    def test_get_form_recognizer_client_v2(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        transport = RequestsTransport()
        ftc = FormTrainingClient(endpoint=formrecognizer_test_endpoint, credential=AzureKeyCredential(formrecognizer_test_api_key), transport=transport, api_version="2.1")

        with ftc:
            ftc.get_account_properties()
            assert transport.session is not None
            with ftc.get_form_recognizer_client() as frc:
                assert transport.session is not None
                frc.begin_recognize_receipts_from_url(self.receipt_url_jpg).wait()
                assert frc._api_version == FormRecognizerApiVersion.V2_1
            ftc.get_account_properties()
            assert transport.session is not None
