# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import uuid
import functools
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    AnalyzeBatchDocumentsRequest,
    AzureBlobContentSource,
)
from testcase import DocumentIntelligenceTest
from preparers import DocumentIntelligencePreparer, GlobalClientPreparer as _GlobalClientPreparer


DocumentIntelligenceClientPreparer = functools.partial(_GlobalClientPreparer, DocumentIntelligenceClient)


class TestDACAnalyzeBatch(DocumentIntelligenceTest):
    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy
    def test_doc_batch_analysis(
        self,
        client,
        documentintelligence_batch_training_data_container_sas_url,
        documentintelligence_batch_training_result_data_container_sas_url,
        **kwargs
    ):
        set_bodiless_matcher()
        recorded_variables = kwargs.pop("variables", {})
        recorded_variables.setdefault("model_id", str(uuid.uuid4()))
        request = AnalyzeBatchDocumentsRequest(
            result_container_url=documentintelligence_batch_training_result_data_container_sas_url,
            azure_blob_source=AzureBlobContentSource(
                container_url=documentintelligence_batch_training_data_container_sas_url
            ),
        )
        poller = client.begin_analyze_batch_documents(
            model_id="prebuilt-layout",
            body=request,
        )
        response = poller.result()
        # FIXME: The training data container isn't being cleaned up, tracking issue: https://github.com/Azure/azure-sdk-for-python/issues/38881
        # assert response.succeeded_count == 6
        assert response.failed_count == 0
        assert response.skipped_count == 0
        return recorded_variables
