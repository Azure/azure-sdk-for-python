# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
import uuid
from devtools_testutils import set_bodiless_matcher
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import HttpResponseError
from azure.ai.formrecognizer._generated.v2022_06_30_preview.models import GetOperationResponse, ModelInfo
from azure.ai.formrecognizer import DocumentModelDetails
from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient, AsyncDocumentModelAdministrationLROPoller
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer


DocumentModelAdministrationClientPreparer = functools.partial(_GlobalClientPreparer, DocumentModelAdministrationClient)


class TestCopyModelAsync(AsyncFormRecognizerTest):

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_copy_model_none_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError):
            async with client:
                await client.begin_copy_model_to(model_id=None, target={})

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_copy_model_empty_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError):
            async with client:
                await client.begin_copy_model_to(model_id="", target={})

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_copy_model_successful(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        async with client:
            training_poller = await client.begin_build_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
            model = await training_poller.result()

            target = await client.get_copy_authorization(tags={"testkey": "testvalue"})

            copy_poller = await client.begin_copy_model_to(model.model_id, target=target)
            copy = await copy_poller.result()

            assert copy.model_id == target["targetModelId"]
            assert copy.description is None
            assert copy.created_on
            assert copy.tags == {"testkey": "testvalue"}
            for name, doc_type in copy.doc_types.items():
                # FIXME: tracking issue #24916
                # assert name == target["targetModelId"]
                for key, field in doc_type.field_schema.items():
                    assert key
                    assert field["type"]
                    assert doc_type.field_confidence[key] is not None

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_copy_model_with_model_id_and_desc(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        async with client:
            poller = await client.begin_build_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
            model = await poller.result()

            model_id = str(uuid.uuid4())
            description = "this is my copied model"
            target = await client.get_copy_authorization(model_id=model_id, description=description)

            poller = await client.begin_copy_model_to(model.model_id, target=target)
            copy = await poller.result()
            if self.is_live:
                assert copy.model_id == model_id
            assert copy.model_id
            assert copy.description == "this is my copied model"
            assert copy.created_on
            for name, doc_type in copy.doc_types.items():
                # if self.is_live:
                    # FIXME: tracking issue #24916
                    # assert name == target["targetModelId"]
                for key, field in doc_type.field_schema.items():
                    assert key
                    assert field["type"]
                    assert doc_type.field_confidence[key] is not None

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_copy_model_fail_bad_model_id(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        async with client:
            poller = await client.begin_build_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
            model = await poller.result()

            target = await client.get_copy_authorization()

            with pytest.raises(HttpResponseError):
                # give bad model_id
                poller = await client.begin_copy_model_to("00000000-0000-0000-0000-000000000000", target=target)
                copy = await poller.result()

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_copy_model_transform(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        raw_response = []

        def callback(response, _, headers):
            op_response = client._deserialize(GetOperationResponse, response)
            model_info = client._deserialize(ModelInfo, op_response.result)
            document_model = DocumentModelDetails._from_generated(model_info)
            raw_response.append(model_info)
            raw_response.append(document_model)

        async with client:
            training_poller = await client.begin_build_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
            model = await training_poller.result()

            target = await client.get_copy_authorization()
            poller = await client.begin_copy_model_to(model.model_id, target=target, cls=callback)
            copy = await poller.result()

            generated = raw_response[0]
            copy = raw_response[1]
            self.assertModelTransformCorrect(copy, generated)

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_copy_authorization(self, client, formrecognizer_region, formrecognizer_resource_id, **kwargs):
        async with client:
            target = await client.get_copy_authorization()

            assert target["targetResourceId"] == formrecognizer_resource_id
            assert target["targetResourceRegion"] == formrecognizer_region
            assert target["targetModelId"]
            assert target["accessToken"]
            assert target["expirationDateTime"]
            assert target["targetModelLocation"]

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_copy_model_with_composed_model(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        async with client:
            poller_1 = await client.begin_build_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
            model_1 = await poller_1.result()

            poller_2 = await client.begin_build_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
            model_2 = await poller_2.result()

            composed_poller = await client.begin_compose_model([model_1.model_id, model_2.model_id])
            composed_model = await composed_poller.result()

            target = await client.get_copy_authorization()

            poller = await client.begin_copy_model_to(composed_model.model_id, target=target)
            copy = await poller.result()

            assert target["targetModelId"] == copy.model_id
            assert target["targetModelId"] != composed_model.model_id
            assert copy.model_id
            assert copy.description is None
            assert copy.created_on
            for name, doc_type in copy.doc_types.items():
                assert name in [model_1.model_id, model_2.model_id]
                for key, field in doc_type.field_schema.items():
                    assert key
                    assert field["type"]
                    assert doc_type.field_confidence[key] is not None

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_copy_continuation_token(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_storage_container_sas_url = kwargs.pop("formrecognizer_storage_container_sas_url")
        async with client:
            poller = await client.begin_build_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
            model = await poller.result()

            target = await client.get_copy_authorization()

            initial_poller = await client.begin_copy_model_to(model.model_id, target=target)
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_copy_model_to(model.model_id, None, continuation_token=cont_token)
            result = await poller.result()
            assert result

            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_poller_metadata(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        async with client:
            poller = await client.begin_build_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
            model = await poller.result()

            target = await client.get_copy_authorization()

            poller = await client.begin_copy_model_to(model.model_id, target=target)
            await poller.result()
            assert isinstance(poller, AsyncDocumentModelAdministrationLROPoller)
            details = poller.details
            assert details["operation_id"]
            assert details["percent_completed"] is not None
            assert details["operation_kind"] == "documentModelCopyTo"
            assert details["percent_completed"] == 100
            assert details["resource_location_url"]
            assert details["created_on"]
            assert details["last_updated_on"]
