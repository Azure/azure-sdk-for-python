# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import uuid
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_bodiless_matcher
from azure.ai.documentintelligence.aio import DocumentIntelligenceAdministrationClient
from azure.ai.documentintelligence.models import (
    BuildDocumentModelRequest,
    AzureBlobContentSource,
    ComposeDocumentModelRequest,
    ComponentDocumentModelDetails,
)
from asynctestcase import AsyncDocumentIntelligenceTest
from conftest import skip_flaky_test
from preparers import DocumentIntelligencePreparer, GlobalClientPreparer as _GlobalClientPreparer

DocumentModelAdministrationClientPreparer = functools.partial(
    _GlobalClientPreparer, DocumentIntelligenceAdministrationClient
)


class TestTrainingAsync(AsyncDocumentIntelligenceTest):
    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_compose_model(self, client, documentintelligence_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        recorded_variables = kwargs.pop("variables", {})
        recorded_variables.setdefault("model_id1", str(uuid.uuid4()))
        recorded_variables.setdefault("model_id2", str(uuid.uuid4()))
        recorded_variables.setdefault("composed_id", str(uuid.uuid4()))
        async with client:
            request = BuildDocumentModelRequest(
                model_id=recorded_variables.get("model_id1"),
                description="model1",
                build_mode="template",
                azure_blob_source=AzureBlobContentSource(container_url=documentintelligence_storage_container_sas_url),
            )
            poller = await client.begin_build_document_model(request)
            model_1 = await poller.result()

            request = BuildDocumentModelRequest(
                model_id=recorded_variables.get("model_id2"),
                description="model2",
                build_mode="template",
                azure_blob_source=AzureBlobContentSource(container_url=documentintelligence_storage_container_sas_url),
            )
            poller = await client.begin_build_document_model(request)
            model_2 = await poller.result()

            request = ComposeDocumentModelRequest(
                model_id=recorded_variables.get("composed_id"),
                description="my composed model",
                tags={"testkey": "testvalue"},
                component_models=[
                    ComponentDocumentModelDetails(model_id=model_1.model_id),
                    ComponentDocumentModelDetails(model_id=model_2.model_id),
                ],
            )
            poller = await client.begin_compose_model(request)
            composed_model = await poller.result()
            assert composed_model.api_version
            assert composed_model.model_id == recorded_variables.get("composed_id")
            assert composed_model.description == "my composed model"
            assert composed_model.created_date_time
            assert composed_model.expiration_date_time
            assert composed_model.tags == {"testkey": "testvalue"}
            for name, doc_details in composed_model.doc_types.items():
                assert name
                for key, field in doc_details.field_schema.items():
                    assert key
                    assert field["type"]
                    assert doc_details.field_confidence[key] is not None

        return recorded_variables
