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
    BuildDocumentModelRequest,
    AzureBlobContentSource,
    AuthorizeCopyRequest,
)
from testcase import DocumentIntelligenceTest
from conftest import skip_flaky_test
from preparers import DocumentIntelligencePreparer, GlobalClientPreparer as _GlobalClientPreparer

DocumentModelAdministrationClientPreparer = functools.partial(
    _GlobalClientPreparer, DocumentIntelligenceAdministrationClient
)


class TestCopyModelAsync(DocumentIntelligenceTest):
    @DocumentIntelligencePreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_copy_model_none_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError) as e:
            client.begin_copy_model_to(model_id=None, copy_to_request={})
        assert "No value for given attribute" in str(e.value)

    @DocumentIntelligencePreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_copy_model_empty_model_id(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ResourceNotFoundError):
            client.begin_copy_model_to(model_id="", copy_to_request={})

    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_copy_model_successful(self, client, documentintelligence_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        recorded_variables = kwargs.pop("variables", {})
        recorded_variables.setdefault("model_id", str(uuid.uuid4()))
        recorded_variables.setdefault("model_id_copy", str(uuid.uuid4()))

        request = BuildDocumentModelRequest(
            model_id=recorded_variables.get("model_id"),
            build_mode="template",
            azure_blob_source=AzureBlobContentSource(container_url=documentintelligence_storage_container_sas_url),
        )
        poller = client.begin_build_document_model(request)
        model = poller.result()

        copy_auth = client.authorize_model_copy(
            AuthorizeCopyRequest(model_id=recorded_variables.get("model_id_copy"), tags={"testkey": "testvalue"})
        )
        poller = client.begin_copy_model_to(model.model_id, copy_to_request=copy_auth)
        copy = poller.result()

        assert copy.api_version == model.api_version
        assert copy.model_id != model.model_id
        assert copy.description == model.description
        assert copy.created_date_time == model.created_date_time
        assert copy.expiration_date_time == model.expiration_date_time
        assert copy.tags == {"testkey": "testvalue"}
        assert model.tags is None
        for name, doc_type in copy.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
                assert doc_type.field_confidence[key] is not None

        return recorded_variables
