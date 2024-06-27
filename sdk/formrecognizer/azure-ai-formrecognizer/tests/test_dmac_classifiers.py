# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import uuid
import functools
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import DocumentModelAdministrationClient, DocumentModelAdministrationLROPoller
from testcase import FormRecognizerTest
from preparers import FormRecognizerPreparer, get_sync_client
from conftest import skip_flaky_test
from azure.ai.formrecognizer import ClassifierDocumentTypeDetails, BlobSource, BlobFileListSource, DocumentClassifierDetails

get_dma_client = functools.partial(get_sync_client, DocumentModelAdministrationClient)


class TestClassifier(FormRecognizerTest):

    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_build_classifier(self, formrecognizer_training_data_classifier, **kwargs):
        client = get_dma_client()
        set_bodiless_matcher()
        poller = client.begin_build_document_classifier(
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
                ),
                "IRS-1040-D": ClassifierDocumentTypeDetails(
                    source=BlobSource(
                        container_url=formrecognizer_training_data_classifier,
                        prefix="IRS-1040-D/train"
                    )
                ),
                "IRS-1040-E": ClassifierDocumentTypeDetails(
                    source=BlobSource(
                        container_url=formrecognizer_training_data_classifier,
                        prefix="IRS-1040-E/train"
                    )
                ),
            },
            description="IRS document classifier"
        )
        result = poller.result()
        assert result.api_version
        assert result.classifier_id
        assert result.created_on
        assert result.expires_on
        assert result.description == "IRS document classifier"
        for doc_type, source in result.doc_types.items():
            assert doc_type
            assert source.source.container_url
            assert source.source.prefix

    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_build_classifier_file_list(self, formrecognizer_training_data_classifier, **kwargs):
        client = get_dma_client()
        set_bodiless_matcher()
        classifier_id = str(uuid.uuid4())
        poller = client.begin_build_document_classifier(
            doc_types={
                "IRS-1040-A": ClassifierDocumentTypeDetails(
                    source=BlobFileListSource(
                        container_url=formrecognizer_training_data_classifier,
                        file_list="IRS-1040-A.jsonl"
                    )
                ),
                "IRS-1040-B": ClassifierDocumentTypeDetails(
                    source=BlobFileListSource(
                        container_url=formrecognizer_training_data_classifier,
                        file_list="IRS-1040-B.jsonl"
                    )
                ),
                "IRS-1040-C": ClassifierDocumentTypeDetails(
                    source=BlobFileListSource(
                        container_url=formrecognizer_training_data_classifier,
                        file_list="IRS-1040-C.jsonl"
                    )
                ),
                "IRS-1040-D": ClassifierDocumentTypeDetails(
                    source=BlobFileListSource(
                        container_url=formrecognizer_training_data_classifier,
                        file_list="IRS-1040-D.jsonl"
                    )
                ),
                "IRS-1040-E": ClassifierDocumentTypeDetails(
                    source=BlobFileListSource(
                        container_url=formrecognizer_training_data_classifier,
                        file_list="IRS-1040-E.jsonl"
                    )
                ),
            },
            classifier_id=classifier_id
        )
        result = poller.result()
        if self.is_live:
            assert result.classifier_id == classifier_id

        assert result.classifier_id
        assert result.api_version
        assert result.created_on
        assert result.expires_on
        assert result.description is None
        for doc_type, source in result.doc_types.items():
            assert doc_type
            assert source.source.container_url
            assert source.source.file_list

    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_poller_metadata(self, formrecognizer_training_data_classifier, **kwargs):
        client = get_dma_client()
        set_bodiless_matcher()
        poller = client.begin_build_document_classifier(
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
                )
            },
        )
        result = poller.result()
        result_dict = result.to_dict()
        result = DocumentClassifierDetails.from_dict(result_dict)
        assert isinstance(poller, DocumentModelAdministrationLROPoller)
        details = poller.details
        assert details["operation_id"]
        assert details["operation_kind"] == "documentClassifierBuild"
        assert details["percent_completed"] == 100
        assert details["resource_location_url"]
        assert details["created_on"]
        assert details["last_updated_on"]

    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_mgmt_classifiers(self, formrecognizer_training_data_classifier, **kwargs):
        client = get_dma_client()
        set_bodiless_matcher()
        poller = client.begin_build_document_classifier(
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
                )
            },
            description="IRS document classifier"
        )
        result = poller.result()

        classifier = client.get_document_classifier(result.classifier_id)

        assert result.classifier_id == classifier.classifier_id
        assert result.description == classifier.description
        assert result.api_version == classifier.api_version
        assert result.created_on == classifier.created_on
        assert result.expires_on == classifier.expires_on
        for doc_type, source in result.doc_types.items():
            assert doc_type in classifier.doc_types
            assert source.source.container_url == classifier.doc_types[doc_type].source.container_url
            assert source.source.prefix == classifier.doc_types[doc_type].source.prefix

        classifiers_list = client.list_document_classifiers()
        for classifier in classifiers_list:
            assert classifier.classifier_id
            assert classifier.api_version
            assert classifier.created_on
            assert classifier.expires_on
            assert classifier.doc_types

        client.delete_document_classifier(classifier.classifier_id)

        with pytest.raises(ResourceNotFoundError):
            client.get_document_classifier(classifier.classifier_id)
