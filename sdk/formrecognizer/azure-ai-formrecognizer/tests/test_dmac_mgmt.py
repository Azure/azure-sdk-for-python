# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
import pytest
import logging
from devtools_testutils import recorded_by_proxy, set_custom_default_matcher
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
from azure.core.pipeline.transport import RequestsTransport
from azure.ai.formrecognizer import (
    DocumentModelAdministrationClient,
    DocumentAnalysisApiVersion,
    ModelOperation
)
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer
import os


DocumentModelAdministrationClientPreparer = functools.partial(_GlobalClientPreparer, DocumentModelAdministrationClient)


class TestManagement(FormRecognizerTest):

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    def test_active_directory_auth(self):
        token = self.generate_oauth_token()
        endpoint = self.get_oauth_endpoint()
        form_recognizer_endpoint_suffix = os.environ.get("FORMRECOGNIZER_ENDPOINT_SUFFIX",".cognitiveservices.azure.com")
        credential_scopes = ["https://{}/.default".format(form_recognizer_endpoint_suffix[1:])]
        client = DocumentModelAdministrationClient(endpoint, token, credential_scopes=credential_scopes)
        info = client.get_account_info()
        assert info

    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_dmac_auth_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key, **kwargs):
        client = DocumentModelAdministrationClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with pytest.raises(ClientAuthenticationError):
            result = client.get_account_info()

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_get_model_empty_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError):
            result = client.get_model("")

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_get_model_none_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError):
            result = client.get_model(None)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_delete_model_none_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError):
            result = client.delete_model(None)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_delete_model_empty_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError):
            result = client.delete_model("")

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_account_info(self, client):
        info = client.get_account_info()

        assert info.document_model_limit
        assert info.document_model_count

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_get_model_prebuilt(self, client, **kwargs):
        model = client.get_model("prebuilt-invoice")
        assert model.model_id == "prebuilt-invoice"
        assert model.description is not None
        assert model.created_on
        assert model.api_version
        assert model.tags is None
        for name, doc_type in model.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
            assert doc_type.field_confidence is None

    @pytest.mark.skip()
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_mgmt_model(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
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
                successful_op = op
            if op.status == "failed":
                failed_op = op

        # check successful op
        if successful_op:
            op = client.get_operation(successful_op.operation_id)
            # TODO not seeing this returned at the operation level
            # assert op.api_version
            # assert op.tags is None
            # test to/from dict
            op_dict = op.to_dict()
            op = ModelOperation.from_dict(op_dict)
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
            assert error.details

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_get_operation_bad_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError):
            client.get_operation("")
        with pytest.raises(ValueError):
            client.get_operation(None)

    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_get_document_analysis_client(self, formrecognizer_test_endpoint, formrecognizer_test_api_key, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )  
        transport = RequestsTransport()
        dtc = DocumentModelAdministrationClient(endpoint=formrecognizer_test_endpoint, credential=AzureKeyCredential(formrecognizer_test_api_key), transport=transport)

        with dtc:
            dtc.get_account_info()
            assert transport.session is not None
            with dtc.get_document_analysis_client() as dac:
                assert transport.session is not None
                dac.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg).wait()
                assert dac._api_version == DocumentAnalysisApiVersion.V2022_06_30_PREVIEW
            dtc.get_account_info()
            assert transport.session is not None
