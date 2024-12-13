# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import uuid
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher, get_credential
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
        client = DocumentIntelligenceClient(documentintelligence_endpoint, get_credential())
        with pytest.raises(ValueError) as e:
            client.begin_analyze_document(model_id=None, body=b"xx")
        assert "No value for given attribute" in str(e.value)

    @DocumentIntelligencePreparer()
    def test_analyze_document_none_model_id_from_url(self, **kwargs):
        documentintelligence_endpoint = kwargs.pop("documentintelligence_endpoint")
        client = DocumentIntelligenceClient(documentintelligence_endpoint, get_credential())
        with pytest.raises(ValueError) as e:
            client.begin_analyze_document(model_id=None, body=AnalyzeDocumentRequest(url_source="https://badurl.jpg"))
        assert "No value for given attribute" in str(e.value)

    @DocumentIntelligencePreparer()
    @recorded_by_proxy
    def test_analyze_document_empty_model_id(self, **kwargs):
        documentintelligence_endpoint = kwargs.pop("documentintelligence_endpoint")
        client = DocumentIntelligenceClient(documentintelligence_endpoint, get_credential())
        with pytest.raises(ResourceNotFoundError) as e:
            client.begin_analyze_document(model_id="", body=b"xx")
        assert "Resource not found" in str(e.value)

    @DocumentIntelligencePreparer()
    @recorded_by_proxy
    def test_analyze_document_empty_model_id_from_url(self, **kwargs):
        documentintelligence_endpoint = kwargs.pop("documentintelligence_endpoint")
        client = DocumentIntelligenceClient(documentintelligence_endpoint, get_credential())
        with pytest.raises(ResourceNotFoundError) as e:
            client.begin_analyze_document(model_id="", body=AnalyzeDocumentRequest(url_source="https://badurl.jpg"))
        assert "Resource not found" in str(e.value)

    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @recorded_by_proxy
    def test_custom_document_transform(self, documentintelligence_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        documentintelligence_endpoint = kwargs.pop("documentintelligence_endpoint")
        di_admin_client = DocumentIntelligenceAdministrationClient(documentintelligence_endpoint, get_credential())
        di_client = DocumentIntelligenceClient(documentintelligence_endpoint, get_credential())

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
        poller = di_client.begin_analyze_document(model.model_id, my_file)
        document = poller.result()
        assert document.model_id == model.model_id
        assert len(document.pages) == 1
        assert len(document.tables) == 2
        assert len(document.paragraphs) == 42
        assert len(document.styles) == 1
        assert document.string_index_type == "textElements"
        assert document.content_format == "text"

        return recorded_variables

    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @recorded_by_proxy
    def test_custom_document_transform_with_continuation_token(
        self, documentintelligence_storage_container_sas_url, **kwargs
    ):
        set_bodiless_matcher()
        documentintelligence_endpoint = kwargs.pop("documentintelligence_endpoint")
        di_admin_client = DocumentIntelligenceAdministrationClient(documentintelligence_endpoint, get_credential())
        di_client = DocumentIntelligenceClient(documentintelligence_endpoint, get_credential())

        recorded_variables = kwargs.pop("variables", {})
        recorded_variables.setdefault("model_id", str(uuid.uuid4()))
        request = BuildDocumentModelRequest(
            model_id=recorded_variables.get("model_id"),
            build_mode="template",
            azure_blob_source=AzureBlobContentSource(container_url=documentintelligence_storage_container_sas_url),
        )
        poller = di_admin_client.begin_build_document_model(request)
        continuation_token = poller.continuation_token()
        poller2 = di_admin_client.begin_build_document_model(request, continuation_token=continuation_token)
        model = poller2.result()
        assert model

        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()
        poller = di_client.begin_analyze_document(model.model_id, my_file)
        continuation_token = poller.continuation_token()
        di_client2 = DocumentIntelligenceClient(documentintelligence_endpoint, get_credential())
        poller2 = di_client2.begin_analyze_document(None, None, continuation_token=continuation_token)
        document = poller2.result()
        assert document.model_id == model.model_id
        assert len(document.pages) == 1
        assert len(document.tables) == 2
        assert len(document.paragraphs) == 42
        assert len(document.styles) == 1
        assert document.string_index_type == "textElements"
        assert document.content_format == "text"

        return recorded_variables
