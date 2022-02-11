# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_bodiless_matcher
from azure.core.pipeline.transport import AioHttpTransport
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
from azure.ai.formrecognizer import (
    DocumentModelAdministrationClient,
    DocumentAnalysisApiVersion,
    ModelOperation
)
from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer


DocumentModelAdministrationClientPreparer = functools.partial(_GlobalClientPreparer, DocumentModelAdministrationClient)


class TestManagementAsync(AsyncFormRecognizerTest):

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    async def test_active_directory_auth_async(self):
        token = self.generate_oauth_token()
        endpoint = self.get_oauth_endpoint()
        client = DocumentModelAdministrationClient(endpoint, token)
        async with client:
            info = await client.get_account_info()
        assert info

    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_dmac_auth_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key, **kwargs):
        client = DocumentModelAdministrationClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with pytest.raises(ClientAuthenticationError):
            async with client:
                result = await client.get_account_info()

        return {}

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_get_model_empty_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError):
            async with client:
                result = await client.get_model("")

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_get_model_none_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError):
            async with client:
                result = await client.get_model(None)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_delete_model_none_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError):
            async with client:
                result = await client.delete_model(None)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_delete_model_empty_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError):
            async with client:
                result = await client.delete_model("")

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_account_info(self, client):
        async with client:
            info = await client.get_account_info()

        assert info.model_limit
        assert info.model_count

        return {}

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_get_model_prebuilt(self, client):
        async with client:
            model = await client.get_model("prebuilt-invoice")
            assert model.model_id == "prebuilt-invoice"
            assert model.description is not None
            assert model.created_on
            for name, doc_type in model.doc_types.items():
                assert name
                for key, field in doc_type.field_schema.items():
                    assert key
                    assert field["type"]
                assert doc_type.field_confidence is None

        return {}

    @pytest.mark.skip()
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_mgmt_model(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()  
        
        async with client:
            poller = await client.begin_build_model(formrecognizer_storage_container_sas_url, "template", description="mgmt model")
            model = await poller.result()

            model_from_get = await client.get_model(model.model_id)

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
            async for model in models_list:
                assert model.model_id
                assert model.created_on

            await client.delete_model(model.model_id)

            with pytest.raises(ResourceNotFoundError):
                await client.get_model(model.model_id)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_get_list_operations(self, client):
        async with client:
            operations = client.list_operations()
            successful_op = None
            failed_op = None
            async for op in operations:
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
                op = await client.get_operation(successful_op.operation_id)
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
                op = await client.get_operation(failed_op.operation_id)
                # test to/from dict
                op_dict = op.to_dict()
                op = ModelOperation.from_dict(op_dict)

                error = op.error
                assert op.result is None
                assert error.code
                assert error.message
                assert error.details

        return {}

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_get_operation_bad_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError):
            await client.get_operation("")
        with pytest.raises(ValueError):
            await client.get_operation(None)

    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_get_document_analysis_client(self, formrecognizer_test_endpoint, formrecognizer_test_api_key, **kwargs):
        set_bodiless_matcher()  
        transport = AioHttpTransport()
        dtc = DocumentModelAdministrationClient(endpoint=formrecognizer_test_endpoint, credential=AzureKeyCredential(formrecognizer_test_api_key), transport=transport)

        async with dtc:
            await dtc.get_account_info()
            assert transport.session is not None
            async with dtc.get_document_analysis_client() as dac:
                assert transport.session is not None
                await (await dac.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg)).wait()
                assert dac._api_version == DocumentAnalysisApiVersion.V2022_01_30_PREVIEW
            await dtc.get_account_info()
            assert transport.session is not None

        return {}
