# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import uuid
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.documentintelligence import DocumentIntelligenceClient, DocumentIntelligenceAdministrationClient
from azure.ai.documentintelligence.models import (
    BuildDocumentModelRequest,
    AzureBlobContentSource,
    AnalyzeDocumentRequest,
)
from testcase import DocumentIntelligenceTest
from preparers import DocumentIntelligencePreparer
from conftest import skip_flaky_test


class TestDACAnalyzeCustomModel(DocumentIntelligenceTest):
    @DocumentIntelligencePreparer()
    def test_analyze_document_none_model_id(self, **kwargs):
        documentintelligence_endpoint = kwargs.pop("documentintelligence_endpoint")
        documentintelligence_api_key = kwargs.pop("documentintelligence_api_key")
        client = DocumentIntelligenceClient(
            documentintelligence_endpoint, AzureKeyCredential(documentintelligence_api_key)
        )
        with pytest.raises(ValueError) as e:
            client.begin_analyze_document(model_id=None, analyze_request=b"xx")
        assert "No value for given attribute" in str(e.value)

    @DocumentIntelligencePreparer()
    def test_analyze_document_none_model_id_from_url(self, **kwargs):
        documentintelligence_endpoint = kwargs.pop("documentintelligence_endpoint")
        documentintelligence_api_key = kwargs.pop("documentintelligence_api_key")
        client = DocumentIntelligenceClient(
            documentintelligence_endpoint, AzureKeyCredential(documentintelligence_api_key)
        )
        with pytest.raises(ValueError) as e:
            client.begin_analyze_document(
                model_id=None, analyze_request=AnalyzeDocumentRequest(url_source="https://badurl.jpg")
            )
        assert "No value for given attribute" in str(e.value)

    @DocumentIntelligencePreparer()
    @recorded_by_proxy
    def test_analyze_document_empty_model_id(self, **kwargs):
        documentintelligence_endpoint = kwargs.pop("documentintelligence_endpoint")
        documentintelligence_api_key = kwargs.pop("documentintelligence_api_key")
        client = DocumentIntelligenceClient(
            documentintelligence_endpoint, AzureKeyCredential(documentintelligence_api_key)
        )
        with pytest.raises(ResourceNotFoundError) as e:
            client.begin_analyze_document(model_id="", analyze_request=b"xx")
        assert "Resource not found" in str(e.value)

    @DocumentIntelligencePreparer()
    @recorded_by_proxy
    def test_analyze_document_empty_model_id_from_url(self, **kwargs):
        documentintelligence_endpoint = kwargs.pop("documentintelligence_endpoint")
        documentintelligence_api_key = kwargs.pop("documentintelligence_api_key")
        client = DocumentIntelligenceClient(
            documentintelligence_endpoint, AzureKeyCredential(documentintelligence_api_key)
        )
        with pytest.raises(ResourceNotFoundError) as e:
            client.begin_analyze_document(
                model_id="", analyze_request=AnalyzeDocumentRequest(url_source="https://badurl.jpg")
            )
        assert "Resource not found" in str(e.value)

    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @recorded_by_proxy
    def test_custom_document_transform(self, documentintelligence_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        documentintelligence_endpoint = kwargs.pop("documentintelligence_endpoint")
        documentintelligence_api_key = kwargs.pop("documentintelligence_api_key")
        di_admin_client = DocumentIntelligenceAdministrationClient(
            documentintelligence_endpoint, AzureKeyCredential(documentintelligence_api_key)
        )
        di_client = DocumentIntelligenceClient(
            documentintelligence_endpoint, AzureKeyCredential(documentintelligence_api_key)
        )

        recorded_variables = kwargs.pop("variables", {})
        recorded_variables.setdefault("model_id", str(uuid.uuid4()))
        request = BuildDocumentModelRequest(
            model_id=recorded_variables.get("model_id"),
            build_mode="template",
            azure_blob_source=AzureBlobContentSource(container_url=documentintelligence_storage_container_sas_url),
        )
        poller = di_admin_client.begin_build_document_model(request)
        model = poller.result()
        assert model

        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()
        poller = di_client.begin_analyze_document(model.model_id, my_file, content_type="application/octet-stream")
        document = poller.result()
        assert document.model_id == model.model_id
        assert len(document.pages) == 1
        assert len(document.tables) == 2
        assert document.paragraphs is None
        assert len(document.styles) == 1
        assert document.string_index_type == "textElements"
        assert document.content_format == "text"

        return recorded_variables
