# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils import set_bodiless_matcher
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.formrecognizer._generated.v2023_07_31.models import AnalyzeResultOperation
from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient
from azure.ai.formrecognizer import AnalyzeResult, ClassifierDocumentTypeDetails, BlobSource
from preparers import FormRecognizerPreparer, get_async_client
from asynctestcase import AsyncFormRecognizerTest
from conftest import skip_flaky_test


get_dma_client = functools.partial(get_async_client, DocumentModelAdministrationClient)


class TestDACClassifyDocumentAsync(AsyncFormRecognizerTest):

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_classify_document(self, formrecognizer_training_data_classifier, **kwargs):
        client = get_dma_client()
        set_bodiless_matcher()
        da_client = client.get_document_analysis_client()

        def callback(raw_response, _, headers):
            analyze_result = da_client._deserialize(AnalyzeResultOperation, raw_response)
            document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(document)

        async with client:
            poller = await client.begin_build_document_classifier(
                doc_types={
                    "IRS-1040-A": ClassifierDocumentTypeDetails(
                        source=BlobSource(
                            container_url=formrecognizer_training_data_classifier,
                            prefix="IRS-1040-A/train"
                        )
                    ),
                    "IRS-1040-B": ClassifierDocumentTypeDetails(
                        source=BlobSource(
                            container_url=formrecognizer_training_data_classifier,
                            prefix="IRS-1040-B/train"
                        )
                    ),
                    "IRS-1040-C": ClassifierDocumentTypeDetails(
                        source=BlobSource(
                            container_url=formrecognizer_training_data_classifier,
                            prefix="IRS-1040-C/train"
                        )
                    )
                },
            )
            classifier = await poller.result()

            responses = []

            with open(self.irs_classifier_document, "rb") as fd:
                my_file = fd.read()

            async with da_client:
                poller = await da_client.begin_classify_document(
                    classifier.classifier_id,
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

            assert len(returned_model.documents) == 2
            for doc in returned_model.documents:
                assert doc.doc_type
                assert doc.confidence is not None

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_classify_document_from_url(self, formrecognizer_training_data_classifier, **kwargs):
        client = get_dma_client()
        set_bodiless_matcher()
        da_client = client.get_document_analysis_client()

        def callback(raw_response, _, headers):
            analyze_result = da_client._deserialize(AnalyzeResultOperation, raw_response)
            document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(document)

        async with client:
            poller = await client.begin_build_document_classifier(
                doc_types={
                    "IRS-1040-A": ClassifierDocumentTypeDetails(
                        source=BlobSource(
                            container_url=formrecognizer_training_data_classifier,
                            prefix="IRS-1040-A/train"
                        )
                    ),
                    "IRS-1040-B": ClassifierDocumentTypeDetails(
                        source=BlobSource(
                            container_url=formrecognizer_training_data_classifier,
                            prefix="IRS-1040-B/train"
                        )
                    ),
                    "IRS-1040-C": ClassifierDocumentTypeDetails(
                        source=BlobSource(
                            container_url=formrecognizer_training_data_classifier,
                            prefix="IRS-1040-C/train"
                        )
                    )
                },
            )
            classifier = await poller.result()

            responses = []

            async with da_client:
                poller = await da_client.begin_classify_document_from_url(
                    classifier_id=classifier.classifier_id,
                    document_url=self.irs_classifier_document_url,
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

            assert len(returned_model.documents) == 2
            for doc in returned_model.documents:
                assert doc.doc_type
                assert doc.confidence is not None
