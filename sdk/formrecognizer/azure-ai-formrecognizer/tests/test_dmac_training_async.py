# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import uuid
import pytest
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_bodiless_matcher, set_custom_default_matcher
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.ai.formrecognizer._generated.v2022_06_30_preview.models import GetOperationResponse, ModelInfo
from azure.ai.formrecognizer._models import DocumentModel
from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient
from azure.ai.formrecognizer import _models
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer

DocumentModelAdministrationClientPreparer = functools.partial(_GlobalClientPreparer, DocumentModelAdministrationClient)


class TestDMACTrainingAsync(AsyncFormRecognizerTest):

    def teardown(self):
        self.sleep(4)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_build_model_polling_interval(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_storage_container_sas_url = kwargs.pop("formrecognizer_storage_container_sas_url")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        def check_poll_value(poll):
            if self.is_live:
                assert poll == 5
            else:
                assert poll == 0
        check_poll_value(client._client._config.polling_interval)
        poller = await client.begin_build_model(source=formrecognizer_storage_container_sas_url, build_mode="template", polling_interval=6)
        await poller.wait()
        assert poller._polling_method._timeout == 6
        poller2 = await client.begin_build_model(source=formrecognizer_storage_container_sas_url, build_mode="template")
        await poller2.wait()
        check_poll_value(poller2._polling_method._timeout)  # goes back to client default
        await client.close()

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_build_model_encoded_url(self, **kwargs):
        client = kwargs.pop("client")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        with pytest.raises(HttpResponseError):
            async with client:
                poller = await client.begin_build_model(
                source="https://fakeuri.com/blank%20space",
                build_mode="template",
            )
                assert "https://fakeuri.com/blank%20space" in poller._polling_method._initial_response.http_request.body
                await poller.wait()

    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_build_model_auth_bad_key(self, **kwargs):
        formrecognizer_test_endpoint = kwargs.pop("formrecognizer_test_endpoint")
        formrecognizer_test_api_key = kwargs.pop("formrecognizer_test_api_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        client = DocumentModelAdministrationClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with pytest.raises(ClientAuthenticationError):
            async with client:
                poller = await client.begin_build_model("xx", "template")
                result = await poller.result()

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_build_model(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_storage_container_sas_url = kwargs.pop("formrecognizer_storage_container_sas_url")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        model_id = str(uuid.uuid4())
        async with client:
            poller = await client.begin_build_model(
                formrecognizer_storage_container_sas_url,
                "template",
                model_id=model_id,
                description="a v3 model",
                tags={"testkey": "testvalue"}
            )
            model = await poller.result()

        if self.is_live:
            assert model.model_id == model_id

        assert model.model_id
        assert model.description == "a v3 model"
        assert model.created_on
        assert model.tags == {"testkey": "testvalue"}
        for name, doc_type in model.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
                assert doc_type.field_confidence[key] is not None

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_build_model_multipage(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_multipage_storage_container_sas_url = kwargs.pop("formrecognizer_multipage_storage_container_sas_url")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        async with client:
            poller = await client.begin_build_model(formrecognizer_multipage_storage_container_sas_url, "template")
            model = await poller.result()

        assert model.model_id
        assert model.api_version
        assert model.tags is None
        assert model.description is None
        assert model.created_on
        for name, doc_type in model.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
                assert doc_type.field_confidence[key] is not None
                assert doc_type.build_mode == "template"

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_build_model_nested_schema(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_table_variable_rows_container_sas_url = kwargs.pop("formrecognizer_table_variable_rows_container_sas_url")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        async with client:
            poller = await client.begin_build_model(formrecognizer_table_variable_rows_container_sas_url, "template")
            model = await poller.result()

        assert model.model_id
        assert model.description is None
        assert model.created_on
        for name, doc_type in model.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
                assert doc_type.field_confidence[key] is not None

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_build_model_transform(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_storage_container_sas_url = kwargs.pop("formrecognizer_storage_container_sas_url")
        
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        raw_response = []

        def callback(response, _, headers):
            op_response = client._deserialize(GetOperationResponse, response)
            model_info = client._deserialize(ModelInfo, op_response.result)
            document_model = DocumentModel._from_generated(model_info)
            raw_response.append(model_info)
            raw_response.append(document_model)

        async with client:
            poller = await client.begin_build_model(formrecognizer_storage_container_sas_url, "template", cls=callback)
            model = await poller.result()

        raw_model = raw_response[0]
        document_model = raw_response[1]
        self.assertModelTransformCorrect(document_model, raw_model)

        document_model_dict = document_model.to_dict()
        document_model_from_dict = _models.DocumentModel.from_dict(document_model_dict)
        assert document_model_from_dict.model_id == document_model.model_id
        self.assertModelTransformCorrect(document_model_from_dict, raw_model)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_build_model_multipage_transform(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_multipage_storage_container_sas_url = kwargs.pop("formrecognizer_multipage_storage_container_sas_url")
        
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        raw_response = []

        def callback(response, _, headers):
            op_response = client._deserialize(GetOperationResponse, response)
            model_info = client._deserialize(ModelInfo, op_response.result)
            document_model = DocumentModel._from_generated(model_info)
            raw_response.append(model_info)
            raw_response.append(document_model)

        async with client:
            poller = await client.begin_build_model(formrecognizer_multipage_storage_container_sas_url, "template", cls=callback)
            model = await poller.result()

        raw_model = raw_response[0]
        document_model = raw_response[1]
        self.assertModelTransformCorrect(document_model, raw_model)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_build_model_nested_schema_transform(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_table_variable_rows_container_sas_url = kwargs.pop("formrecognizer_table_variable_rows_container_sas_url")
        
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        raw_response = []

        def callback(response, _, headers):
            op_response = client._deserialize(GetOperationResponse, response)
            model_info = client._deserialize(ModelInfo, op_response.result)
            document_model = DocumentModel._from_generated(model_info)
            raw_response.append(model_info)
            raw_response.append(document_model)

        async with client:
            poller = await client.begin_build_model(formrecognizer_table_variable_rows_container_sas_url, "template", cls=callback)
            model = await poller.result()

        raw_model = raw_response[0]
        document_model = raw_response[1]
        self.assertModelTransformCorrect(document_model, raw_model)

        document_model_dict = document_model.to_dict()

        document_model_from_dict = _models.DocumentModel.from_dict(document_model_dict)
        assert document_model_from_dict.model_id == document_model.model_id
        self.assertModelTransformCorrect(document_model_from_dict, raw_model)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_build_model_azure_blob_path_filter(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_storage_container_sas_url = kwargs.pop("formrecognizer_storage_container_sas_url")
        set_bodiless_matcher()
        with pytest.raises(HttpResponseError) as e:
            async with client:
                poller = await client.begin_build_model(formrecognizer_storage_container_sas_url, "template", prefix="testfolder")
                model = await poller.result()

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_build_model_continuation_token(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_storage_container_sas_url = kwargs.pop("formrecognizer_storage_container_sas_url")
        async with client:
            initial_poller = await client.begin_build_model(formrecognizer_storage_container_sas_url, "template")
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_build_model(None, "template", continuation_token=cont_token)
            result = await poller.result()
            assert result
            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_build_model_poller_metadata(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_storage_container_sas_url = kwargs.pop("formrecognizer_storage_container_sas_url")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        async with client:
            poller = await client.begin_build_model(formrecognizer_storage_container_sas_url, "template")
            assert poller.operation_id
            assert poller.percent_completed is not None
            await poller.result()
            assert poller.operation_kind == "documentModelBuild"
            assert poller.percent_completed == 100
            assert poller.resource_location_url
            assert poller.created_on
            assert poller.last_updated_on
