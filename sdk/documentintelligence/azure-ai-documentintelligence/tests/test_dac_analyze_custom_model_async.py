# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import uuid
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_bodiless_matcher, get_credential
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient, DocumentIntelligenceAdministrationClient
from azure.ai.documentintelligence.models import (
    BuildDocumentModelRequest,
    AzureBlobContentSource,
    AnalyzeDocumentRequest,
)
from preparers import DocumentIntelligencePreparer
from asynctestcase import AsyncDocumentIntelligenceTest
from conftest import skip_flaky_test


class TestDACAnalyzeCustomModelAsync(AsyncDocumentIntelligenceTest):
    @DocumentIntelligencePreparer()
    @recorded_by_proxy_async
    async def test_analyze_document_none_model_id(self, **kwargs):
        documentintelligence_endpoint = kwargs.pop("documentintelligence_endpoint")
        client = DocumentIntelligenceClient(documentintelligence_endpoint, get_credential(is_async=True))
        with pytest.raises(ValueError) as e:
            async with client:
                await client.begin_analyze_document(model_id=None, body=b"xx")
        assert "No value for given attribute" in str(e.value)

    @DocumentIntelligencePreparer()
    @recorded_by_proxy_async
    async def test_analyze_document_none_model_id_from_url(self, **kwargs):
        documentintelligence_endpoint = kwargs.pop("documentintelligence_endpoint")
        client = DocumentIntelligenceClient(documentintelligence_endpoint, get_credential(is_async=True))
        with pytest.raises(ValueError) as e:
            async with client:
                await client.begin_analyze_document(
                    model_id=None, body=AnalyzeDocumentRequest(url_source="https://badurl.jpg")
                )
        assert "No value for given attribute" in str(e.value)

    @DocumentIntelligencePreparer()
    @recorded_by_proxy_async
    async def test_analyze_document_empty_model_id(self, **kwargs):
        documentintelligence_endpoint = kwargs.pop("documentintelligence_endpoint")
        client = DocumentIntelligenceClient(documentintelligence_endpoint, get_credential(is_async=True))
        with pytest.raises(ResourceNotFoundError) as e:
            async with client:
                await client.begin_analyze_document(model_id="", body=b"xx")
        assert "Resource not found" in str(e.value)

    @DocumentIntelligencePreparer()
    @recorded_by_proxy_async
    async def test_analyze_document_empty_model_id_from_url(self, **kwargs):
        documentintelligence_endpoint = kwargs.pop("documentintelligence_endpoint")
        client = DocumentIntelligenceClient(documentintelligence_endpoint, get_credential(is_async=True))
        with pytest.raises(ResourceNotFoundError) as e:
            async with client:
                await client.begin_analyze_document(
                    model_id="", body=AnalyzeDocumentRequest(url_source="https://badurl.jpg")
                )
        assert "Resource not found" in str(e.value)

    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @recorded_by_proxy_async
    async def test_custom_document_transform(self, documentintelligence_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        documentintelligence_endpoint = kwargs.pop("documentintelligence_endpoint")
        di_admin_client = DocumentIntelligenceAdministrationClient(
            documentintelligence_endpoint, get_credential(is_async=True)
        )
        di_client = DocumentIntelligenceClient(documentintelligence_endpoint, get_credential(is_async=True))

        recorded_variables = kwargs.pop("variables", {})
        recorded_variables.setdefault("model_id", str(uuid.uuid4()))
        request = BuildDocumentModelRequest(
            model_id=recorded_variables.get("model_id"),
            build_mode="template",
            azure_blob_source=AzureBlobContentSource(container_url=documentintelligence_storage_container_sas_url),
        )
        async with di_admin_client:
            build_poller = await di_admin_client.begin_build_document_model(request)
            model = await build_poller.result()
        assert model

        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()
        async with di_client:
            poller = await di_client.begin_analyze_document(model.model_id, my_file)
            document = await poller.result()
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
    @recorded_by_proxy_async
    async def test_custom_document_transform_with_continuation_token(
        self, documentintelligence_storage_container_sas_url, **kwargs
    ):
        set_bodiless_matcher()
        documentintelligence_endpoint = kwargs.pop("documentintelligence_endpoint")
        di_admin_client = DocumentIntelligenceAdministrationClient(
            documentintelligence_endpoint, get_credential(is_async=True)
        )
        di_client = DocumentIntelligenceClient(documentintelligence_endpoint, get_credential(is_async=True))

        recorded_variables = kwargs.pop("variables", {})
        recorded_variables.setdefault("model_id", str(uuid.uuid4()))
        request = BuildDocumentModelRequest(
            model_id=recorded_variables.get("model_id"),
            build_mode="template",
            azure_blob_source=AzureBlobContentSource(container_url=documentintelligence_storage_container_sas_url),
        )
        async with di_admin_client:
            build_poller = await di_admin_client.begin_build_document_model(request)
            continuation_token = build_poller.continuation_token()
            new_build_poller = await di_admin_client.begin_build_document_model(
                request, continuation_token=continuation_token
            )
            model = await new_build_poller.result()
        assert model

        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()
        async with di_client:
            poller = await di_client.begin_analyze_document(model.model_id, my_file)
            continuation_token = poller.continuation_token()

        di_client2 = DocumentIntelligenceClient(documentintelligence_endpoint, get_credential(is_async=True))
        async with di_client2:
            document = await (
                await di_client2.begin_analyze_document(None, None, continuation_token=continuation_token)
            ).result()
            assert document.model_id == model.model_id
            assert len(document.pages) == 1
            assert len(document.tables) == 2
            assert len(document.paragraphs) == 42
            assert len(document.styles) == 1
            assert document.string_index_type == "textElements"
            assert document.content_format == "text"

        return recorded_variables
