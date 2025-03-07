# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import uuid
import pytest
import functools
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.documentintelligence import DocumentIntelligenceAdministrationClient
from azure.ai.documentintelligence.models import (
    BuildDocumentClassifierRequest,
    AzureBlobContentSource,
    AuthorizeClassifierCopyRequest,
    ClassifierDocumentTypeDetails,
)
from testcase import DocumentIntelligenceTest
from preparers import DocumentIntelligencePreparer, GlobalClientPreparer as _GlobalClientPreparer

DocumentModelAdministrationClientPreparer = functools.partial(
    _GlobalClientPreparer, DocumentIntelligenceAdministrationClient
)


class TestCopyClassifier(DocumentIntelligenceTest):
    @DocumentIntelligencePreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_copy_classifier_none_classifier_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError) as e:
            client.begin_copy_classifier_to(classifier_id=None, body={})
        assert "No value for given attribute" in str(e.value)

    @DocumentIntelligencePreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_copy_classifier_empty_classifier_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ResourceNotFoundError):
            client.begin_copy_classifier_to(classifier_id="", body={})

    @DocumentIntelligencePreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_copy_classifier_successful(self, client, documentintelligence_training_data_classifier_sas_url, **kwargs):
        set_bodiless_matcher()
        recorded_variables = kwargs.pop("variables", {})
        recorded_variables.setdefault("classifier_id", str(uuid.uuid4()))
        recorded_variables.setdefault("classifier_id_copy", str(uuid.uuid4()))

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
        poller = client.begin_build_classifier(request)
        classifier = poller.result()

        copy_auth = client.authorize_classifier_copy(
            AuthorizeClassifierCopyRequest(
                classifier_id=recorded_variables.get("classifier_id_copy"),
                tags={"testkey": "testvalue"},
            )
        )
        poller = client.begin_copy_classifier_to(classifier.classifier_id, body=copy_auth)
        copy = poller.result()

        assert copy.api_version == classifier.api_version
        assert copy.classifier_id != classifier.classifier_id
        assert copy.classifier_id == copy_auth["targetClassifierId"]
        assert copy.base_classifier_id == classifier.base_classifier_id
        assert copy.base_classifier_id is None
        assert copy.description == classifier.description

        return recorded_variables
