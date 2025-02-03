# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import uuid
import pytest
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_bodiless_matcher
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.documentintelligence.aio import DocumentIntelligenceAdministrationClient
from azure.ai.documentintelligence.models import (
    BuildDocumentModelRequest,
    AzureBlobContentSource,
    AuthorizeCopyRequest,
)
from asynctestcase import AsyncDocumentIntelligenceTest
from conftest import skip_flaky_test
from preparers import DocumentIntelligencePreparer, GlobalClientPreparerAsync as _GlobalClientPreparer

DocumentModelAdministrationClientPreparer = functools.partial(
    _GlobalClientPreparer, DocumentIntelligenceAdministrationClient
)


class TestCopyModelAsync(AsyncDocumentIntelligenceTest):
    @DocumentIntelligencePreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_copy_model_none_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError) as e:
            async with client:
                await client.begin_copy_model_to(model_id=None, body={})
        assert "No value for given attribute" in str(e.value)

    @DocumentIntelligencePreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_copy_model_empty_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ResourceNotFoundError):
            async with client:
                await client.begin_copy_model_to(model_id="", body={})

    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_copy_model_successful(self, client, documentintelligence_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        recorded_variables = kwargs.pop("variables", {})
        recorded_variables.setdefault("model_id", str(uuid.uuid4()))
        recorded_variables.setdefault("model_id_copy", str(uuid.uuid4()))

        async with client:
            request = BuildDocumentModelRequest(
                model_id=recorded_variables.get("model_id"),
                build_mode="template",
                azure_blob_source=AzureBlobContentSource(container_url=documentintelligence_storage_container_sas_url),
            )
            poller = await client.begin_build_document_model(request)
            model = await poller.result()

            copy_auth = await client.authorize_model_copy(
                AuthorizeCopyRequest(model_id=recorded_variables.get("model_id_copy"), tags={"testkey": "testvalue"})
            )
            poller = await client.begin_copy_model_to(model.model_id, body=copy_auth)
            copy = await poller.result()

            assert copy.api_version == model.api_version
            assert copy.model_id != model.model_id
            assert copy.model_id == copy_auth["targetModelId"]
            assert copy.description == model.description
            assert copy.tags == {"testkey": "testvalue"}
            assert model.tags is None
            for name, doc_type in copy.doc_types.items():
                assert name == copy_auth["targetModelId"]
                for key, field in doc_type.field_schema.items():
                    assert key
                    assert field["type"]
                    assert doc_type.field_confidence[key] is not None

        return recorded_variables
