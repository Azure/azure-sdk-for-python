# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import uuid
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_bodiless_matcher
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.documentintelligence.aio import DocumentIntelligenceAdministrationClient
from azure.ai.documentintelligence.models import (
    AzureBlobContentSource,
    AzureBlobFileListContentSource,
    ClassifierDocumentTypeDetails,
    BuildDocumentClassifierRequest,
)
from asynctestcase import AsyncDocumentIntelligenceTest
from preparers import DocumentIntelligencePreparer, GlobalClientPreparerAsync as _GlobalClientPreparer

DocumentModelAdministrationClientPreparer = functools.partial(
    _GlobalClientPreparer, DocumentIntelligenceAdministrationClient
)


class TestClassifiersAsync(AsyncDocumentIntelligenceTest):
    @DocumentIntelligencePreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_build_classifier(self, client, documentintelligence_training_data_classifier_sas_url, **kwargs):
        set_bodiless_matcher()
        recorded_variables = kwargs.pop("variables", {})
        recorded_variables.setdefault("classifier_id", str(uuid.uuid4()))

        request = BuildDocumentClassifierRequest(
            classifier_id=recorded_variables.get("classifier_id"),
            description="IRS document classifier",
            doc_types={
                "IRS-1040-A": ClassifierDocumentTypeDetails(
                    azure_blob_source=AzureBlobContentSource(
                        container_url=documentintelligence_training_data_classifier_sas_url, prefix="IRS-1040-A/train"
                    )
                ),
                "IRS-1040-B": ClassifierDocumentTypeDetails(
                    azure_blob_source=AzureBlobContentSource(
                        container_url=documentintelligence_training_data_classifier_sas_url, prefix="IRS-1040-B/train"
                    )
                ),
                "IRS-1040-C": ClassifierDocumentTypeDetails(
                    azure_blob_source=AzureBlobContentSource(
                        container_url=documentintelligence_training_data_classifier_sas_url, prefix="IRS-1040-C/train"
                    )
                ),
                "IRS-1040-D": ClassifierDocumentTypeDetails(
                    azure_blob_source=AzureBlobContentSource(
                        container_url=documentintelligence_training_data_classifier_sas_url, prefix="IRS-1040-D/train"
                    )
                ),
                "IRS-1040-E": ClassifierDocumentTypeDetails(
                    azure_blob_source=AzureBlobContentSource(
                        container_url=documentintelligence_training_data_classifier_sas_url, prefix="IRS-1040-E/train"
                    )
                ),
            },
        )
        async with client:
            poller = await client.begin_build_classifier(request)
            result = await poller.result()
            assert result.api_version
            assert result.classifier_id == recorded_variables.get("classifier_id")
            assert result.created_date_time
            assert result.expiration_date_time
            assert result.description == "IRS document classifier"
            assert len(result.doc_types) == 5
            for doc_type, doc_details in result.doc_types.items():
                assert doc_type
                assert doc_details.azure_blob_source.container_url
                assert doc_details.azure_blob_source.prefix.startswith(doc_type)

            classifier = await client.get_classifier(result.classifier_id)
            assert classifier.api_version == result.api_version
            assert classifier.classifier_id == result.classifier_id
            assert classifier.created_date_time == result.created_date_time
            assert classifier.expiration_date_time == result.expiration_date_time
            assert classifier.description == result.description
            assert len(classifier.doc_types) == len(result.doc_types)
            for doc_type, doc_details in classifier.doc_types.items():
                assert doc_type in result.doc_types
                assert (
                    doc_details.azure_blob_source.container_url
                    == result.doc_types[doc_type].azure_blob_source.container_url
                )
                assert doc_details.azure_blob_source.prefix == result.doc_types[doc_type].azure_blob_source.prefix

            classifiers_list = client.list_classifiers()
            async for c in classifiers_list:
                assert c.api_version
                assert c.classifier_id
                assert c.created_date_time
                assert c.expiration_date_time
                assert c.doc_types
                await client.delete_classifier(c.classifier_id)

            with pytest.raises(ResourceNotFoundError):
                await client.get_classifier(classifier.classifier_id)

        return recorded_variables

    @DocumentIntelligencePreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_build_classifier_file_list(
        self, client, documentintelligence_training_data_classifier_sas_url, **kwargs
    ):
        set_bodiless_matcher()
        recorded_variables = kwargs.pop("variables", {})
        recorded_variables.setdefault("classifier_id", str(uuid.uuid4()))

        request = BuildDocumentClassifierRequest(
            classifier_id=recorded_variables.get("classifier_id"),
            doc_types={
                "IRS-1040-A": ClassifierDocumentTypeDetails(
                    azure_blob_file_list_source=AzureBlobFileListContentSource(
                        container_url=documentintelligence_training_data_classifier_sas_url,
                        file_list="IRS-1040-A.jsonl",
                    )
                ),
                "IRS-1040-B": ClassifierDocumentTypeDetails(
                    azure_blob_file_list_source=AzureBlobFileListContentSource(
                        container_url=documentintelligence_training_data_classifier_sas_url,
                        file_list="IRS-1040-B.jsonl",
                    )
                ),
                "IRS-1040-C": ClassifierDocumentTypeDetails(
                    azure_blob_file_list_source=AzureBlobFileListContentSource(
                        container_url=documentintelligence_training_data_classifier_sas_url,
                        file_list="IRS-1040-C.jsonl",
                    )
                ),
                "IRS-1040-D": ClassifierDocumentTypeDetails(
                    azure_blob_file_list_source=AzureBlobFileListContentSource(
                        container_url=documentintelligence_training_data_classifier_sas_url,
                        file_list="IRS-1040-D.jsonl",
                    )
                ),
                "IRS-1040-E": ClassifierDocumentTypeDetails(
                    azure_blob_file_list_source=AzureBlobFileListContentSource(
                        container_url=documentintelligence_training_data_classifier_sas_url,
                        file_list="IRS-1040-E.jsonl",
                    )
                ),
            },
        )
        async with client:
            poller = await client.begin_build_classifier(request)
            result = await poller.result()

            assert result.classifier_id == recorded_variables.get("classifier_id")
            assert result.api_version
            assert result.created_date_time
            assert result.expiration_date_time
            assert result.description is None
            assert len(result.doc_types) == 5
            for doc_type, doc_details in result.doc_types.items():
                assert doc_type
                assert doc_details.azure_blob_file_list_source.container_url
                assert doc_details.azure_blob_file_list_source.file_list.startswith(doc_type)

            classifier = await client.get_classifier(result.classifier_id)
            assert classifier.api_version == result.api_version
            assert classifier.classifier_id == result.classifier_id
            assert classifier.created_date_time == result.created_date_time
            assert classifier.expiration_date_time == result.expiration_date_time
            assert classifier.description == result.description
            assert len(classifier.doc_types) == len(result.doc_types)
            for doc_type, doc_details in classifier.doc_types.items():
                assert doc_type in result.doc_types
                assert (
                    doc_details.azure_blob_file_list_source.container_url
                    == result.doc_types[doc_type].azure_blob_file_list_source.container_url
                )
                assert (
                    doc_details.azure_blob_file_list_source.file_list
                    == result.doc_types[doc_type].azure_blob_file_list_source.file_list
                )

            classifiers_list = client.list_classifiers()
            async for c in classifiers_list:
                assert c.api_version
                assert c.classifier_id
                assert c.created_date_time
                assert c.expiration_date_time
                assert c.doc_types
                await client.delete_classifier(c.classifier_id)

            with pytest.raises(ResourceNotFoundError):
                await client.get_classifier(classifier.classifier_id)

        return recorded_variables
