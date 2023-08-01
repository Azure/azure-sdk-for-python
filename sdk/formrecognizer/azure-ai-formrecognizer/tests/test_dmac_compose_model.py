# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import uuid
import functools
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher
from azure.ai.formrecognizer import DocumentModelAdministrationClient, DocumentModelDetails, DocumentModelAdministrationLROPoller
from azure.ai.formrecognizer._generated.v2023_07_31.models import DocumentModelComposeOperationDetails, DocumentModelDetails as ModelDetails
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer
from conftest import skip_flaky_test


DocumentModelAdministrationClientPreparer = functools.partial(_GlobalClientPreparer, DocumentModelAdministrationClient)

class TestTraining(FormRecognizerTest):

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_compose_model(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        model_id_1 = str(uuid.uuid4())
        model_id_2 = str(uuid.uuid4())
        composed_id = str(uuid.uuid4())
        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_storage_container_sas_url, model_id=model_id_1, description="model1")
        model_1 = poller.result()

        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_storage_container_sas_url, model_id=model_id_2, description="model2")
        model_2 = poller.result()

        poller = client.begin_compose_document_model([model_1.model_id, model_2.model_id], model_id=composed_id, description="my composed model", tags={"testkey": "testvalue"})

        composed_model = poller.result()
        if self.is_live:
            assert composed_model.model_id == composed_id

        assert composed_model.model_id
        assert composed_model.description == "my composed model"
        assert composed_model.created_on
        assert composed_model.tags == {"testkey": "testvalue"}
        for name, doc_type in composed_model.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
                assert doc_type.field_confidence[key] is not None

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_compose_model_transform(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_storage_container_sas_url, description="model1")
        model_1 = poller.result()

        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_storage_container_sas_url, description="model2")
        model_2 = poller.result()

        raw_response = []

        def callback(response, _, headers):
            op_response = client._deserialize(DocumentModelComposeOperationDetails, response)
            model_info = client._deserialize(ModelDetails, op_response.result)
            document_model = DocumentModelDetails._from_generated(model_info)
            raw_response.append(model_info)
            raw_response.append(document_model)

        poller = client.begin_compose_document_model([model_1.model_id, model_2.model_id], description="my composed model", cls=callback)
        model = poller.result()

        generated = raw_response[0]
        document_model = raw_response[1]
        self.assertModelTransformCorrect(document_model, generated)

        document_model_dict = document_model.to_dict()
        document_model_from_dict = DocumentModelDetails.from_dict(document_model_dict)
        self.assertModelTransformCorrect(document_model_from_dict, generated)

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    def test_compose_continuation_token(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_storage_container_sas_url = kwargs.pop("formrecognizer_storage_container_sas_url")
        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
        model_1 = poller.result()

        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
        model_2 = poller.result()

        initial_poller = client.begin_compose_document_model([model_1.model_id, model_2.model_id])
        cont_token = initial_poller.continuation_token()

        poller = client.begin_compose_document_model(None, continuation_token=cont_token)
        result = poller.result()
        assert result

        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_poller_metadata(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
        model_1 = poller.result()

        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
        model_2 = poller.result()

        poller = client.begin_compose_document_model([model_1.model_id, model_2.model_id])
        poller.result()
        assert isinstance(poller, DocumentModelAdministrationLROPoller)
        details = poller.details
        assert details["operation_id"]
        assert details["percent_completed"] is not None
        assert details["operation_kind"] == "documentModelCompose"
        assert details["percent_completed"] == 100
        assert details["resource_location_url"]
        assert details["created_on"]
        assert details["last_updated_on"]
