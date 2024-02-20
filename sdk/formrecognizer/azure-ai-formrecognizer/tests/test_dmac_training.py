# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import uuid
import pytest
import functools
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.ai.formrecognizer._generated.v2023_07_31.models import DocumentModelBuildOperationDetails, DocumentModelDetails as ModelDetails
from azure.ai.formrecognizer import DocumentModelAdministrationClient, DocumentModelDetails, DocumentModelAdministrationLROPoller
from testcase import FormRecognizerTest
from conftest import skip_flaky_test
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer

DocumentModelAdministrationClientPreparer = functools.partial(_GlobalClientPreparer, DocumentModelAdministrationClient)

class TestDMACTraining(FormRecognizerTest):

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_build_model_polling_interval(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        def check_poll_value(poll):
            if self.is_live:
                assert poll == 5
            else:
                assert poll == 0
        check_poll_value(client._client._config.polling_interval)
        poller = client.begin_build_document_model(blob_container_url=formrecognizer_storage_container_sas_url, build_mode="template", polling_interval=6)
        poller.wait()
        assert poller._polling_method._timeout == 6
        poller2 = client.begin_build_document_model(blob_container_url=formrecognizer_storage_container_sas_url, build_mode="template")
        poller2.wait()
        check_poll_value(poller2._polling_method._timeout)  # goes back to client default
        client.close()

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_build_model_encoded_url(self, client):
        with pytest.raises(HttpResponseError):
            poller = client.begin_build_document_model(
                blob_container_url="https://fakeuri.com/blank%20space", build_mode="template"
            )
            assert "https://fakeuri.com/blank%20space" in poller._polling_method._initial_response.http_request.body
            poller.wait()

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_build_model_auth_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key, **kwargs):
        set_bodiless_matcher()
        client = DocumentModelAdministrationClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with pytest.raises(ClientAuthenticationError):
            poller = client.begin_build_document_model(build_mode="template", blob_container_url="xx")

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_build_model(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        model_id = str(uuid.uuid4())
        poller = client.begin_build_document_model(
            build_mode="template",
            blob_container_url=formrecognizer_storage_container_sas_url,
            model_id=model_id,
            description="a v3 model",
            tags={"testkey": "testvalue"}
        )
        model = poller.result()

        if self.is_live:
            assert model.model_id == model_id

        assert model.model_id
        assert model.description == "a v3 model"
        assert model.created_on
        assert model.expires_on
        assert model.tags == {"testkey": "testvalue"}
        for name, doc_type in model.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
                assert doc_type.field_confidence[key] is not None

    @pytest.mark.skip()
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_build_model_neural(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        model_id = str(uuid.uuid4())
        poller = client.begin_build_document_model(
            "neural",
            blob_container_url=formrecognizer_storage_container_sas_url,
            model_id=model_id,
            description="a v3 model",
            tags={"testkey": "testvalue"}
        )
        model = poller.result()

        if self.is_live:
            assert model.model_id == model_id

        assert model.model_id
        assert model.description == "a v3 model"
        assert model.created_on
        assert model.expires_on
        assert model.tags == {"testkey": "testvalue"}
        for name, doc_type in model.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
                # neural not returning field confidence
                # assert doc_type.field_confidence[key] is not None

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_build_model_multipage(self, client, formrecognizer_multipage_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()

        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_multipage_storage_container_sas_url)
        model = poller.result()

        assert model.model_id
        assert model.api_version
        assert model.tags == {}
        assert model.description is None
        assert model.created_on
        assert model.expires_on
        for name, doc_type in model.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
                assert doc_type.field_confidence[key] is not None
                assert doc_type.build_mode == "template"

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_build_model_nested_schema(self, client, formrecognizer_table_variable_rows_container_sas_url, **kwargs):
        set_bodiless_matcher()

        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_table_variable_rows_container_sas_url)
        model = poller.result()

        assert model.model_id
        assert model.description is None
        assert model.created_on
        assert model.expires_on
        for name, doc_type in model.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
                assert doc_type.field_confidence[key] is not None

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_build_model_transform(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()

        raw_response = []

        def callback(response, _, headers):
            op_response = client._deserialize(DocumentModelBuildOperationDetails, response)
            model_info = client._deserialize(ModelDetails, op_response.result)
            document_model = DocumentModelDetails._from_generated(model_info)
            raw_response.append(model_info)
            raw_response.append(document_model)

        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_storage_container_sas_url, cls=callback)
        model = poller.result()

        raw_model = raw_response[0]
        document_model = raw_response[1]
        self.assertModelTransformCorrect(document_model, raw_model)

        document_model_dict = document_model.to_dict()
        document_model_from_dict = DocumentModelDetails.from_dict(document_model_dict)
        assert document_model_from_dict.model_id == document_model.model_id
        self.assertModelTransformCorrect(document_model_from_dict, raw_model)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_build_model_multipage_transform(self, client, formrecognizer_multipage_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()

        raw_response = []

        def callback(response, _, headers):
            op_response = client._deserialize(DocumentModelBuildOperationDetails, response)
            model_info = client._deserialize(ModelDetails, op_response.result)
            document_model = DocumentModelDetails._from_generated(model_info)
            raw_response.append(model_info)
            raw_response.append(document_model)

        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_multipage_storage_container_sas_url, cls=callback)
        model = poller.result()

        raw_model = raw_response[0]
        document_model = raw_response[1]
        self.assertModelTransformCorrect(document_model, raw_model)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_build_model_nested_schema_transform(self, client, formrecognizer_table_variable_rows_container_sas_url, **kwargs):
        set_bodiless_matcher()

        raw_response = []

        def callback(response, _, headers):
            op_response = client._deserialize(DocumentModelBuildOperationDetails, response)
            model_info = client._deserialize(ModelDetails, op_response.result)
            document_model = DocumentModelDetails._from_generated(model_info)
            raw_response.append(model_info)
            raw_response.append(document_model)

        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_table_variable_rows_container_sas_url, cls=callback)
        model = poller.result()

        raw_model = raw_response[0]
        document_model = raw_response[1]
        self.assertModelTransformCorrect(document_model, raw_model)

        document_model_dict = document_model.to_dict()

        document_model_from_dict = DocumentModelDetails.from_dict(document_model_dict)
        assert document_model_from_dict.model_id == document_model.model_id
        self.assertModelTransformCorrect(document_model_from_dict, raw_model)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_build_model_azure_blob_path_filter(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        with pytest.raises(HttpResponseError) as e:
            poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_storage_container_sas_url, prefix="testfolder")
            model = poller.result()

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_build_model_continuation_token(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_storage_container_sas_url = kwargs.pop("formrecognizer_storage_container_sas_url")
        initial_poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
        cont_token = initial_poller.continuation_token()
        poller = client.begin_build_document_model("template", blob_container_url=None, continuation_token=cont_token)
        result = poller.result()
        assert result
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_build_model_poller_metadata(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
        poller.result()
        assert isinstance(poller, DocumentModelAdministrationLROPoller)
        details = poller.details
        assert details["operation_id"]
        assert details["percent_completed"] is not None
        assert details["operation_kind"] == "documentModelBuild"
        assert details["percent_completed"] == 100
        assert details["resource_location_url"]
        assert details["created_on"]
        assert details["last_updated_on"]

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_build_model_file_list_source(self, client, formrecognizer_selection_mark_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        poller = client.begin_build_document_model(
            build_mode="template",
            blob_container_url=formrecognizer_selection_mark_storage_container_sas_url,
            file_list="filelist.jsonl"
        )
        model = poller.result()

        assert model.model_id
        assert model.description is None
        assert model.created_on
        for name, doc_type in model.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
                assert doc_type.field_confidence[key] is not None
