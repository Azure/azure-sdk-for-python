# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.formrecognizer._generated.v2023_02_28_preview.models import AnalyzeResultOperation
from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient
from azure.ai.formrecognizer import AnalyzeResult
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from conftest import skip_flaky_test


DocumentModelAdministrationClientPreparer = functools.partial(_GlobalClientPreparer, DocumentModelAdministrationClient)


class TestDACClassifyDocumentAsync(AsyncFormRecognizerTest):

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_classify_document(self, client, formrecognizer_classifier_container_sas_url, **kwargs):
        da_client = client.get_document_analysis_client()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = da_client._deserialize(AnalyzeResultOperation, raw_response)
            document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(document)

        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()
        async with da_client:
            poller = await client.begin_build_document_classifier(blob_container_url=formrecognizer_classifier_container_sas_url)
            classifier = await poller.result()


            poller = await da_client.begin_classify_document(
                classifier.model_id,
                my_file,
                cls=callback
            )
            document = await poller.result()

        raw_analyze_result = responses[0].analyze_result
        returned_model = responses[1]

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

        assert len(document.documents) == 1
        assert document.documents[0].doc_type == "invoice"
