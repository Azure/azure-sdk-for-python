# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
import pytest
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
from azure.core.pipeline.transport import RequestsTransport
from azure.ai.formrecognizer import (
    DocumentModelAdministrationClient,
    DocumentAnalysisApiVersion,
    OperationDetails
)
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer
from conftest import skip_flaky_test


DocumentModelAdministrationClientPreparer = functools.partial(_GlobalClientPreparer, DocumentModelAdministrationClient)


class TestManagement(FormRecognizerTest):

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    def test_active_directory_auth(self):
        token = self.generate_oauth_token()
        endpoint = self.get_oauth_endpoint()
        client = DocumentModelAdministrationClient(endpoint, token)
        info = client.get_resource_details()
        assert info

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_dmac_auth_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key, **kwargs):
        client = DocumentModelAdministrationClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with pytest.raises(ClientAuthenticationError):
            result = client.get_resource_details()

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_get_model_empty_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError) as e:
            result = client.get_document_model("")
        assert "model_id cannot be None or empty." in str(e.value)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_get_model_none_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError) as e:
            result = client.get_document_model(None)
        assert "model_id cannot be None or empty." in str(e.value)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_delete_model_none_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError) as e:
            result = client.delete_document_model(None)
        assert "model_id cannot be None or empty." in str(e.value)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_delete_model_empty_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError) as e:
            result = client.delete_document_model("")
        assert "model_id cannot be None or empty." in str(e.value)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_account_info(self, client):
        info = client.get_resource_details()

        assert info.custom_document_models.limit
        assert info.custom_document_models.count
        assert info.custom_neural_document_model_builds.quota
        assert info.custom_neural_document_model_builds.quota_resets_on
        assert info.custom_neural_document_model_builds.used is not None

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_get_model_prebuilt(self, client, **kwargs):
        model = client.get_document_model("prebuilt-invoice")
        assert model.model_id == "prebuilt-invoice"
        assert model.description is not None
        assert model.created_on
        assert model.api_version
        assert model.tags == {}
        for name, doc_type in model.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
            assert doc_type.field_confidence == {}

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_mgmt_model(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_storage_container_sas_url, description="mgmt model")
        model = poller.result()

        model_from_get = client.get_document_model(model.model_id)

        assert model.model_id == model_from_get.model_id
        assert model.description == model_from_get.description
        assert model.created_on == model_from_get.created_on
        assert model.expires_on == model_from_get.expires_on
        for name, doc_type in model.doc_types.items():
            assert name in model_from_get.doc_types
            for key, field in doc_type.field_schema.items():
                assert key in model_from_get.doc_types[name].field_schema
                assert field["type"] == model_from_get.doc_types[name].field_schema[key]["type"]
                assert doc_type.field_confidence[key] == model_from_get.doc_types[name].field_confidence[key]

        models_list = client.list_document_models()
        for model in models_list:
            assert model.model_id
            assert model.created_on

        client.delete_document_model(model.model_id)

        with pytest.raises(ResourceNotFoundError):
            client.get_document_model(model.model_id)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_get_list_operations(self, client, **kwargs):
        operations = client.list_operations()
        successful_op = None
        failed_op = None
        for op in operations:
            assert op.operation_id
            assert op.status
            # FIXME check why some operations aren't returned with a percent_completed field
            # assert op.percent_completed is not None
            assert op.created_on
            assert op.last_updated_on
            assert op.kind
            assert op.resource_location
            if op.status == "succeeded":
                if op.kind != "documentClassifierBuild":
                    successful_op = op
                else:
                    successful_classifier_op = op
            if op.status == "failed":
                failed_op = op

        # check successful document model op
        if successful_op:
            op = client.get_operation(successful_op.operation_id)
            # TODO not seeing this returned at the operation level
            # assert op.api_version
            # assert op.tags is None
            # test to/from dict
            op_dict = op.to_dict()
            op = OperationDetails.from_dict(op_dict)
            assert op.error is None
            model = op.result
            assert model.model_id
            # operations may or may not have descriptions
            if model.description:
                assert model.description
            assert model.created_on
            for name, doc_type in model.doc_types.items():
                assert name
                for key, field in doc_type.field_schema.items():
                    assert key
                    assert field["type"]
                    if doc_type.build_mode == "neural":
                        continue  # neural models don't have field confidence
                    assert doc_type.field_confidence[key] is not None

        # check successful classifier model op
        if successful_classifier_op:
            op = client.get_operation(successful_classifier_op.operation_id)
            # test to/from dict
            op_dict = op.to_dict()
            op = OperationDetails.from_dict(op_dict)
            classifier = op.result
            assert classifier.api_version
            assert classifier.classifier_id
            assert classifier.created_on
            assert classifier.expires_on
            for doc_type, source in classifier.doc_types.items():
                assert doc_type
                assert source.azure_blob_source or source.azure_blob_file_list_source

        # check failed op
        if failed_op:
            op = client.get_operation(failed_op.operation_id)
            # test to/from dict
            op_dict = op.to_dict()
            op = OperationDetails.from_dict(op_dict)

            assert op.result is None
            error = op.error
            assert error.code
            assert error.message
            assert error.details

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_get_operation_bad_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError) as e:
            client.get_operation("")
        assert "'operation_id' cannot be None or empty." in str(e.value)
        with pytest.raises(ValueError) as e:
            client.get_operation(None)
        assert "'operation_id' cannot be None or empty." in str(e.value)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_get_document_analysis_client(self, formrecognizer_test_endpoint, formrecognizer_test_api_key, **kwargs):
        transport = RequestsTransport()
        dtc = DocumentModelAdministrationClient(endpoint=formrecognizer_test_endpoint, credential=AzureKeyCredential(formrecognizer_test_api_key), transport=transport)

        with dtc:
            dtc.get_resource_details()
            assert transport.session is not None
            with dtc.get_document_analysis_client() as dac:
                assert transport.session is not None
                dac.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg).wait()
                assert dac._api_version == DocumentAnalysisApiVersion.V2023_02_28_PREVIEW
            dtc.get_resource_details()
            assert transport.session is not None
