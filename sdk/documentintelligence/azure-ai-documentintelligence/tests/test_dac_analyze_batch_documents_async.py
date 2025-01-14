# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import uuid
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_bodiless_matcher
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    AnalyzeBatchDocumentsRequest,
    AzureBlobContentSource,
)
from preparers import DocumentIntelligencePreparer, GlobalClientPreparerAsync as _GlobalClientPreparer
from asynctestcase import AsyncDocumentIntelligenceTest


DocumentIntelligenceClientPreparer = functools.partial(_GlobalClientPreparer, DocumentIntelligenceClient)


class TestDACAnalyzeBatchAsync(AsyncDocumentIntelligenceTest):
    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy_async
    async def test_doc_batch_analysis(
        self,
        client: DocumentIntelligenceClient,
        documentintelligence_batch_training_data_container_sas_url,
        documentintelligence_batch_training_async_result_data_container_sas_url,
        **kwargs
    ):
        set_bodiless_matcher()
        recorded_variables = kwargs.pop("variables", {})
        recorded_variables.setdefault("model_id", str(uuid.uuid4()))
        request = AnalyzeBatchDocumentsRequest(
            result_container_url=documentintelligence_batch_training_async_result_data_container_sas_url,
            azure_blob_source=AzureBlobContentSource(
                container_url=documentintelligence_batch_training_data_container_sas_url
            ),
        )
        poller = await client.begin_analyze_batch_documents(
            model_id="prebuilt-layout",
            body=request,
        )
        response = await poller.result()
        # FIXME: The training data container isn't being cleaned up, tracking issue: https://github.com/Azure/azure-sdk-for-python/issues/38881
        # assert response.succeeded_count == 6
        assert response.failed_count == 0
        assert response.skipped_count == 0
        return recorded_variables
