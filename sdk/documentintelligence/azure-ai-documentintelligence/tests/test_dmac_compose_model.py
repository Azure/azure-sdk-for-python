# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import uuid
import functools
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher
from azure.ai.documentintelligence import DocumentIntelligenceAdministrationClient
from azure.ai.documentintelligence.models import (
    AzureBlobContentSource,
    BuildDocumentModelRequest,
    BuildDocumentClassifierRequest,
    ComposeDocumentModelRequest,
    ClassifierDocumentTypeDetails,
    DocumentTypeDetails,
)
from testcase import DocumentIntelligenceTest
from conftest import skip_flaky_test
from preparers import DocumentIntelligencePreparer, GlobalClientPreparer as _GlobalClientPreparer

DocumentModelAdministrationClientPreparer = functools.partial(
    _GlobalClientPreparer, DocumentIntelligenceAdministrationClient
)


class TestTrainingAsync(DocumentIntelligenceTest):
    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_compose_model(self, client, documentintelligence_training_data_classifier_sas_url, **kwargs):
        set_bodiless_matcher()
        recorded_variables = kwargs.pop("variables", {})
        recorded_variables.setdefault("model_id1", str(uuid.uuid4()))
        recorded_variables.setdefault("model_id2", str(uuid.uuid4()))
        recorded_variables.setdefault("composed_id", str(uuid.uuid4()))

        request = BuildDocumentModelRequest(
            model_id=recorded_variables.get("model_id1"),
            description="model1",
            build_mode="template",
            azure_blob_source=AzureBlobContentSource(
                container_url=documentintelligence_training_data_classifier_sas_url
            ),
        )
        poller = client.begin_build_document_model(request)
        model_1 = poller.result()

        request = BuildDocumentModelRequest(
            model_id=recorded_variables.get("model_id2"),
            description="model2",
            build_mode="template",
            azure_blob_source=AzureBlobContentSource(
                container_url=documentintelligence_training_data_classifier_sas_url
            ),
        )
        poller = client.begin_build_document_model(request)
        model_2 = poller.result()

        request = BuildDocumentClassifierRequest(
            classifier_id=classifier.classifier_id,
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
            },
        )
        poller = client.begin_build_classifier(request)
        classifier = poller.result()
        classifier_id = classifier.classifier_id

        request = ComposeDocumentModelRequest(
            model_id=recorded_variables.get("composed_id"),
            classifier_id=classifier_id,
            description="my composed model",
            tags={"testkey": "testvalue"},
            doc_types={
                "formA": DocumentTypeDetails(model_id=model_1.model_id),
                "formA": DocumentTypeDetails(model_id=model_2.model_id),
            },
        )
        poller = client.begin_compose_model(request)
        composed_model = poller.result()
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
