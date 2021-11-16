# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import asyncio
import uuid
import warnings
import logging
import pytest
import functools
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.ai.formrecognizer._generated.v2021_09_30_preview.models import GetOperationResponse, ModelInfo
from azure.ai.formrecognizer._models import CustomFormModel, DocumentModel
from azure.ai.formrecognizer.aio import FormTrainingClient, DocumentModelAdministrationClient
from azure.ai.formrecognizer import _models
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer


FormTrainingClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)
DocumentModelAdministrationClientPreparer = functools.partial(_GlobalClientPreparer, DocumentModelAdministrationClient)


class TestTrainingAsync(AsyncFormRecognizerTest):

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_build_model_polling_interval(self, client, formrecognizer_storage_container_sas_url):
        def check_poll_value(poll):
            if self.is_live:
                assert poll == 5
            else:
                assert poll == 0
        check_poll_value(client._client._config.polling_interval)
        poller = await client.begin_build_model(source=formrecognizer_storage_container_sas_url, polling_interval=6)
        await poller.wait()
        assert poller._polling_method._timeout == 6
        poller2 = await client.begin_build_model(source=formrecognizer_storage_container_sas_url)
        await poller2.wait()
        check_poll_value(poller2._polling_method._timeout)  # goes back to client default
        await client.close()

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_build_model_encoded_url(self, client):
        with pytest.raises(HttpResponseError):
            async with client:
                poller = await client.begin_build_model(
                source="https://fakeuri.com/blank%20space"
            )
                assert "https://fakeuri.com/blank%20space" in poller._polling_method._initial_response.http_request.body
                await poller.wait()

    @FormRecognizerPreparer()
    async def test_build_model_auth_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = DocumentModelAdministrationClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with pytest.raises(ClientAuthenticationError):
            async with client:
                poller = await client.begin_build_model("xx")
                result = await poller.result()

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_build_model(self, client, formrecognizer_storage_container_sas_url):
        model_id = str(uuid.uuid4())
        async with client:
            poller = await client.begin_build_model(
                formrecognizer_storage_container_sas_url,
                model_id=model_id,
                description="a v3 model"
            )
            model = await poller.result()

        if self.is_live:
            assert model.model_id == model_id

        assert model.model_id
        assert model.description == "a v3 model"
        assert model.created_on
        for name, doc_type in model.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
                assert doc_type.field_confidence[key] is not None

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_build_model_multipage(self, client, formrecognizer_multipage_storage_container_sas_url):
        async with client:
            poller = await client.begin_build_model(formrecognizer_multipage_storage_container_sas_url)
            model = await poller.result()

        assert model.model_id
        assert model.description is None
        assert model.created_on
        for name, doc_type in model.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
                assert doc_type.field_confidence[key] is not None

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_build_model_nested_schema(self, client, formrecognizer_table_variable_rows_container_sas_url):
        async with client:
            poller = await client.begin_build_model(formrecognizer_table_variable_rows_container_sas_url)
            model = await poller.result()

        assert model.model_id
        assert model.description is None
        assert model.created_on
        for name, doc_type in model.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
                assert doc_type.field_confidence[key] is not None

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_build_model_transform(self, client, formrecognizer_storage_container_sas_url):

        raw_response = []

        def callback(response, _, headers):
            op_response = client._deserialize(GetOperationResponse, response)
            model_info = client._deserialize(ModelInfo, op_response.result)
            document_model = DocumentModel._from_generated(model_info)
            raw_response.append(model_info)
            raw_response.append(document_model)

        async with client:
            poller = await client.begin_build_model(formrecognizer_storage_container_sas_url, cls=callback)
            model = await poller.result()

        raw_model = raw_response[0]
        document_model = raw_response[1]
        self.assertModelTransformCorrect(document_model, raw_model)

        document_model_dict = document_model.to_dict()
        document_model_from_dict = _models.DocumentModel.from_dict(document_model_dict)
        assert document_model_from_dict.model_id == document_model.model_id
        self.assertModelTransformCorrect(document_model_from_dict, raw_model)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_build_model_multipage_transform(self, client, formrecognizer_multipage_storage_container_sas_url):

        raw_response = []

        def callback(response, _, headers):
            op_response = client._deserialize(GetOperationResponse, response)
            model_info = client._deserialize(ModelInfo, op_response.result)
            document_model = DocumentModel._from_generated(model_info)
            raw_response.append(model_info)
            raw_response.append(document_model)

        async with client:
            poller = await client.begin_build_model(formrecognizer_multipage_storage_container_sas_url, cls=callback)
            model = await poller.result()

        raw_model = raw_response[0]
        document_model = raw_response[1]
        self.assertModelTransformCorrect(document_model, raw_model)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_build_model_nested_schema_transform(self, client, formrecognizer_table_variable_rows_container_sas_url):

        raw_response = []

        def callback(response, _, headers):
            op_response = client._deserialize(GetOperationResponse, response)
            model_info = client._deserialize(ModelInfo, op_response.result)
            document_model = DocumentModel._from_generated(model_info)
            raw_response.append(model_info)
            raw_response.append(document_model)

        async with client:
            poller = await client.begin_build_model(formrecognizer_table_variable_rows_container_sas_url, cls=callback)
            model = await poller.result()

        raw_model = raw_response[0]
        document_model = raw_response[1]
        self.assertModelTransformCorrect(document_model, raw_model)

        document_model_dict = document_model.to_dict()

        document_model_from_dict = _models.DocumentModel.from_dict(document_model_dict)
        assert document_model_from_dict.model_id == document_model.model_id
        self.assertModelTransformCorrect(document_model_from_dict, raw_model)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_build_model_azure_blob_path_filter(self, client, formrecognizer_storage_container_sas_url):
        with pytest.raises(HttpResponseError) as e:
            async with client:
                poller = await client.begin_build_model(formrecognizer_storage_container_sas_url, prefix="subfolder")
                model = await poller.result()

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_build_model_continuation_token(self, client, formrecognizer_storage_container_sas_url):
        async with client:
            initial_poller = await client.begin_build_model(formrecognizer_storage_container_sas_url)
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_build_model(None, continuation_token=cont_token)
            result = await poller.result()
            assert result
            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_build_model_poller_metadata(self, client, formrecognizer_storage_container_sas_url):
        async with client:
            poller = await client.begin_build_model(formrecognizer_storage_container_sas_url)
            assert poller.operation_id
            assert poller.percent_completed is not None
            await poller.result()
            assert poller.operation_kind == "documentModelBuild"
            assert poller.percent_completed == 100
            assert poller.resource_location_url
            assert poller.created_on
            assert poller.last_updated_on

    # --------------------------------------- BACK COMPATABILITY TESTS ---------------------------------------

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    async def test_training_with_labels_v2(self, client, formrecognizer_storage_container_sas_url_v2):
        async with client:
            poller = await client.begin_training(training_files_url=formrecognizer_storage_container_sas_url_v2, use_training_labels=True)
            model = await poller.result()

        model_dict = model.to_dict()
        model = CustomFormModel.from_dict(model_dict)

        assert model.model_id
        assert model.training_started_on
        assert model.training_completed_on
        assert model.errors == []
        assert model.status == "ready"
        for doc in model.training_documents:
            assert doc.name
            assert doc.page_count
            assert doc.status
            assert doc.errors == []
        for sub in model.submodels:
            assert sub.form_type
            assert sub.accuracy is not None
            for key, field in sub.fields.items():
                assert field.accuracy is not None
                assert field.name

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    async def test_training_multipage_with_labels_v2(self, client, formrecognizer_multipage_storage_container_sas_url_v2):
        async with client:
            poller = await client.begin_training(formrecognizer_multipage_storage_container_sas_url_v2, use_training_labels=True)
            model = await poller.result()

        assert model.model_id
        assert model.training_started_on
        assert model.training_completed_on
        assert model.errors == []
        assert model.status == "ready"
        for doc in model.training_documents:
            assert doc.name
            assert doc.page_count
            assert doc.status
            assert doc.errors == []
        for sub in model.submodels:
            assert sub.form_type
            assert sub.accuracy is not None
            for key, field in sub.fields.items():
                assert field.accuracy is not None
                assert field.name


    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    async def test_training_without_labels_v2(self, client, formrecognizer_storage_container_sas_url_v2):
        async with client:
            poller = await client.begin_training(training_files_url=formrecognizer_storage_container_sas_url_v2, use_training_labels=True)
            model = await poller.result()

        model_dict = model.to_dict()
        model = CustomFormModel.from_dict(model_dict)

        assert model.model_id
        assert model.training_started_on
        assert model.training_completed_on
        assert model.errors == []
        assert model.status == "ready"
        for doc in model.training_documents:
            assert doc.name
            assert doc.page_count
            assert doc.status
            assert doc.errors == []
        for sub in model.submodels:
            assert sub.form_type
            assert sub.accuracy is not None
            for key, field in sub.fields.items():
                assert field.accuracy is not None
                assert field.name

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    async def test_training_multipage_without_labels_v2(self, client, formrecognizer_multipage_storage_container_sas_url_v2):
        async with client:
            poller = await client.begin_training(formrecognizer_multipage_storage_container_sas_url_v2, use_training_labels=True)
            model = await poller.result()

        assert model.model_id
        assert model.training_started_on
        assert model.training_completed_on
        assert model.errors == []
        assert model.status == "ready"
        for doc in model.training_documents:
            assert doc.name
            assert doc.page_count
            assert doc.status
            assert doc.errors == []
        for sub in model.submodels:
            assert sub.form_type
            assert sub.accuracy is not None
            for key, field in sub.fields.items():
                assert field.accuracy is not None
                assert field.name

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    async def test_training_with_files_filter_v2(self, client, formrecognizer_storage_container_sas_url_v2):
        async with client:
            poller = await client.begin_training(training_files_url=formrecognizer_storage_container_sas_url_v2, use_training_labels=False, include_subfolders=True)
            model = await poller.result()
            assert len(model.training_documents) == 6
            assert model.training_documents[-1].name == "subfolder/Form_6.jpg"  # we traversed subfolders

            poller = await client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False, prefix="subfolder", include_subfolders=True)
            model = await poller.result()
            assert len(model.training_documents) == 1
            assert model.training_documents[0].name == "subfolder/Form_6.jpg"  # we filtered for only subfolders

            with pytest.raises(HttpResponseError) as e:
                poller = await client.begin_training(training_files_url=formrecognizer_storage_container_sas_url_v2, use_training_labels=False, prefix="xxx")
                model = await poller.result()
            assert e.value.error.code
            assert e.value.error.message

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    async def test_training_with_labels_v21(self, client, formrecognizer_storage_container_sas_url_v2):
        async with client:
            poller = await client.begin_training(training_files_url=formrecognizer_storage_container_sas_url_v2, use_training_labels=True, model_name="my labeled model")
            model = await poller.result()

        model_dict = model.to_dict()
        model = CustomFormModel.from_dict(model_dict)

        assert model.model_id
        assert model.model_name == "my labeled model"
        assert model.training_started_on
        assert model.training_completed_on
        assert model.errors == []
        assert model.status == "ready"
        for doc in model.training_documents:
            assert doc.name
            assert doc.page_count
            assert doc.status
            assert doc.errors == []
        for sub in model.submodels:
            assert sub.form_type
            assert sub.accuracy is not None
            for key, field in sub.fields.items():
                assert field.accuracy is not None
                assert field.name

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    async def test_training_multipage_with_labels_v21(self, client, formrecognizer_multipage_storage_container_sas_url_v2):
        async with client:
            poller = await client.begin_training(formrecognizer_multipage_storage_container_sas_url_v2, use_training_labels=True)
            model = await poller.result()

        assert model.model_id
        assert model.training_started_on
        assert model.training_completed_on
        assert model.errors == []
        assert model.status == "ready"
        for doc in model.training_documents:
            assert doc.name
            assert doc.page_count
            assert doc.status
            assert doc.errors == []
        for sub in model.submodels:
            assert sub.form_type
            assert sub.accuracy is not None
            for key, field in sub.fields.items():
                assert field.accuracy is not None
                assert field.name

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    async def test_training_without_labels_v21(self, client, formrecognizer_storage_container_sas_url_v2):
        async with client:
            poller = await client.begin_training(training_files_url=formrecognizer_storage_container_sas_url_v2, use_training_labels=True, model_name="my labeled model")
            model = await poller.result()

        model_dict = model.to_dict()
        model = CustomFormModel.from_dict(model_dict)

        assert model.model_id
        assert model.model_name == "my labeled model"
        assert model.training_started_on
        assert model.training_completed_on
        assert model.errors == []
        assert model.status == "ready"
        for doc in model.training_documents:
            assert doc.name
            assert doc.page_count
            assert doc.status
            assert doc.errors == []
        for sub in model.submodels:
            assert sub.form_type
            assert sub.accuracy is not None
            for key, field in sub.fields.items():
                assert field.accuracy is not None
                assert field.name

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    async def test_training_multipage_without_labels_v21(self, client, formrecognizer_multipage_storage_container_sas_url_v2):
        async with client:
            poller = await client.begin_training(formrecognizer_multipage_storage_container_sas_url_v2, use_training_labels=True)
            model = await poller.result()

        assert model.model_id
        assert model.training_started_on
        assert model.training_completed_on
        assert model.errors == []
        assert model.status == "ready"
        for doc in model.training_documents:
            assert doc.name
            assert doc.page_count
            assert doc.status
            assert doc.errors == []
        for sub in model.submodels:
            assert sub.form_type
            assert sub.accuracy is not None
            for key, field in sub.fields.items():
                assert field.accuracy is not None
                assert field.name

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    async def test_training_with_files_filter_v21(self, client, formrecognizer_storage_container_sas_url_v2):
        async with client:
            poller = await client.begin_training(training_files_url=formrecognizer_storage_container_sas_url_v2, use_training_labels=False, include_subfolders=True)
            model = await poller.result()
            assert len(model.training_documents) == 6
            assert model.training_documents[-1].name == "subfolder/Form_6.jpg"  # we traversed subfolders

            poller = await client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False, prefix="subfolder", include_subfolders=True)
            model = await poller.result()
            assert len(model.training_documents) == 1
            assert model.training_documents[0].name == "subfolder/Form_6.jpg"  # we filtered for only subfolders

            with pytest.raises(HttpResponseError) as e:
                poller = await client.begin_training(training_files_url=formrecognizer_storage_container_sas_url_v2, use_training_labels=False, prefix="xxx")
                model = await poller.result()
            assert e.value.error.code
            assert e.value.error.message

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.0"})
    async def test_training_with_model_name_bad_api_version(self, client):
        with pytest.raises(ValueError) as excinfo:
            async with client:
                poller = await client.begin_training(training_files_url="url", use_training_labels=True, model_name="not supported in v2.0")
                result = await poller.result()
        assert "'model_name' is only available for API version V2_1 and up" in str(excinfo.value)
