# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormContentType, _models
from azure.ai.formrecognizer.aio import FormRecognizerClient, FormTrainingClient, DocumentAnalysisClient, DocumentModelAdministrationClient
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._generated.v2021_09_30_preview.models import AnalyzeResultOperation
from azure.ai.formrecognizer import AnalyzeResult
from azure.ai.formrecognizer._response_handlers import prepare_form_result
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer

DocumentModelAdministrationClientPreparer = functools.partial(_GlobalClientPreparer, DocumentModelAdministrationClient)
FormTrainingClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)


class TestCustomFormsAsync(AsyncFormRecognizerTest):

    @FormRecognizerPreparer()
    async def test_analyze_document_none_model_id(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = DocumentAnalysisClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key))
        with self.assertRaises(ValueError):
            async with client:
                await client.begin_analyze_document(model=None, document=b"xx")

    @FormRecognizerPreparer()
    async def test_analyze_document_empty_model_id(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = DocumentAnalysisClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key))
        with self.assertRaises(ValueError):
            async with client:
                await client.begin_analyze_document(model="", document=b"xx")

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    async def test_custom_form_unlabeled(self, client, formrecognizer_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        async with client:
            training_poller = await client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
            model = await training_poller.result()

            async with fr_client:
                poller = await fr_client.begin_recognize_custom_forms(model.model_id, myfile, content_type=FormContentType.IMAGE_JPEG)
                form = await poller.result()
        self.assertEqual(form[0].form_type, "form-0")
        self.assertUnlabeledRecognizedFormHasValues(form[0], model)

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    async def test_custom_form_multipage_unlabeled(self, client, formrecognizer_multipage_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()
        with open(self.multipage_invoice_pdf, "rb") as fd:
            myfile = fd.read()

        async with client:
            training_poller = await client.begin_training(formrecognizer_multipage_storage_container_sas_url, use_training_labels=False)
            model = await training_poller.result()

            async with fr_client:
                poller = await fr_client.begin_recognize_custom_forms(
                    model.model_id,
                    myfile,
                    content_type=FormContentType.APPLICATION_PDF
                )
                forms = await poller.result()

        for form in forms:
            if form.form_type is None:
                continue  # blank page
            self.assertEqual(form.form_type, "form-0")
            self.assertUnlabeledRecognizedFormHasValues(form, model)

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    async def test_custom_form_multipage_labeled(self, client, formrecognizer_multipage_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()
        with open(self.multipage_invoice_pdf, "rb") as fd:
            myfile = fd.read()

        async with client:
            training_poller = await client.begin_training(
                formrecognizer_multipage_storage_container_sas_url,
                use_training_labels=True
            )
            model = await training_poller.result()

            async with fr_client:
                poller = await fr_client.begin_recognize_custom_forms(
                    model.model_id,
                    myfile,
                    content_type=FormContentType.APPLICATION_PDF
                )
                forms = await poller.result()

        for form in forms:
            self.assertEqual(form.form_type, "custom:"+model.model_id)
            self.assertLabeledRecognizedFormHasValues(form, model)

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    async def test_custom_forms_multipage_unlabeled_transform(self, client, formrecognizer_multipage_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.multipage_invoice_pdf, "rb") as fd:
            myfile = fd.read()

        async with client:
            training_poller = await client.begin_training(formrecognizer_multipage_storage_container_sas_url, use_training_labels=False)
            model = await training_poller.result()

            async with fr_client:
                poller = await fr_client.begin_recognize_custom_forms(
                    model.model_id,
                    myfile,
                    include_field_elements=True,
                    cls=callback
                )
                form = await poller.result()
        actual = responses[0]
        recognized_form = responses[1]
        read_results = actual.analyze_result.read_results
        page_results = actual.analyze_result.page_results

        self.assertFormPagesTransformCorrect(recognized_form, read_results, page_results)

        for form, actual in zip(recognized_form, page_results):
            self.assertEqual(form.page_range.first_page_number, actual.page)
            self.assertEqual(form.page_range.last_page_number, actual.page)
            self.assertIsNone(form.form_type_confidence)
            self.assertEqual(form.model_id, model.model_id)
            self.assertUnlabeledFormFieldDictTransformCorrect(form.fields, actual.key_value_pairs, read_results)


    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_custom_document_transform(self, client, formrecognizer_storage_container_sas_url):
        fr_client = client.get_document_analysis_client()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeResultOperation, raw_response)
            document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(document)

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        async with client:
            build_polling = await client.begin_build_model(formrecognizer_storage_container_sas_url)
            model = await build_polling.result()

            async with fr_client:
                poller = await fr_client.begin_analyze_document(
                    model.model_id,
                    myfile,
                    cls=callback
                )
                document = await poller.result()

        raw_analyze_result = responses[0].analyze_result
        returned_model = responses[1]

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content

        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(returned_model.key_value_pairs, raw_analyze_result.key_value_pairs)
        self.assertDocumentEntitiesTransformCorrect(returned_model.entities, raw_analyze_result.entities)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_custom_document_multipage_transform(self, client, formrecognizer_multipage_storage_container_sas_url):
        fr_client = client.get_document_analysis_client()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeResultOperation, raw_response)
            document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(document)

        with open(self.multipage_invoice_pdf, "rb") as fd:
            myfile = fd.read()

        async with client:
            build_poller = await client.begin_build_model(formrecognizer_multipage_storage_container_sas_url)
            model = await build_poller.result()

            async with fr_client:
                poller = await fr_client.begin_analyze_document(
                    model.model_id,
                    myfile,
                    cls=callback
                )
                document = await poller.result()

        raw_analyze_result = responses[0].analyze_result
        returned_model = responses[1]

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content

        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(returned_model.key_value_pairs, raw_analyze_result.key_value_pairs)
        self.assertDocumentEntitiesTransformCorrect(returned_model.entities, raw_analyze_result.entities)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    @pytest.mark.live_test_only
    async def test_custom_form_continuation_token(self, client, formrecognizer_storage_container_sas_url):
        fr_client = client.get_form_recognizer_client()
        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        async with client:
            poller = await client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
            model = await poller.result()

            async with fr_client:
                initial_poller = await fr_client.begin_recognize_custom_forms(
                    model.model_id,
                    myfile
                )

                cont_token = initial_poller.continuation_token()
                poller = await fr_client.begin_recognize_custom_forms(
                    model.model_id,
                    None,
                    continuation_token=cont_token
                )
                result = await poller.result()
                self.assertIsNotNone(result)
                await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    async def test_custom_form_multipage_vendor_set_unlabeled_transform(self, client, formrecognizer_multipage_storage_container_sas_url_2):
        fr_client = client.get_form_recognizer_client()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.multipage_vendor_pdf, "rb") as fd:
            myfile = fd.read()

        async with client:
            poller = await client.begin_training(formrecognizer_multipage_storage_container_sas_url_2, use_training_labels=False)
            model = await poller.result()

            async with fr_client:
                poller = await fr_client.begin_recognize_custom_forms(
                    model.model_id,
                    myfile,
                    include_field_elements=True,
                    cls=callback
                )
                form = await poller.result()
        actual = responses[0]
        recognized_form = responses[1]
        read_results = actual.analyze_result.read_results
        page_results = actual.analyze_result.page_results

        self.assertFormPagesTransformCorrect(recognized_form, read_results, page_results)
        for form, actual in zip(recognized_form, page_results):
            self.assertEqual(form.page_range.first_page_number, actual.page)
            self.assertEqual(form.page_range.last_page_number, actual.page)
            self.assertIsNone(form.form_type_confidence)
            self.assertEqual(form.model_id, model.model_id)
            self.assertUnlabeledFormFieldDictTransformCorrect(form.fields, actual.key_value_pairs, read_results)

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    async def test_custom_form_multipage_vendor_set_labeled_transform(self, client, formrecognizer_multipage_storage_container_sas_url_2):
        fr_client = client.get_form_recognizer_client()

        responses = []

        with open(self.multipage_vendor_pdf, "rb") as fd:
            myfile = fd.read()

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        async with client:
            poller = await client.begin_training(formrecognizer_multipage_storage_container_sas_url_2, use_training_labels=True)
            model = await poller.result()

            async with fr_client:
                poller = await fr_client.begin_recognize_custom_forms(
                    model.model_id,
                    myfile,
                    include_field_elements=True,
                    cls=callback
                )
                form = await poller.result()
        actual = responses[0]
        recognized_form = responses[1]
        read_results = actual.analyze_result.read_results
        page_results = actual.analyze_result.page_results
        document_results = actual.analyze_result.document_results

        self.assertFormPagesTransformCorrect(recognized_form, read_results, page_results)
        for form, actual in zip(recognized_form, document_results):
            self.assertEqual(form.page_range.first_page_number, actual.page_range[0])
            self.assertEqual(form.page_range.last_page_number, actual.page_range[1])
            self.assertEqual(form.form_type, "custom:"+model.model_id)
            self.assertIsNotNone(form.form_type_confidence)
            self.assertEqual(form.model_id, model.model_id)
            self.assertFormFieldsTransformCorrect(form.fields, actual.fields, read_results)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_custom_document_selection_mark(self, client, formrecognizer_selection_mark_storage_container_sas_url):
        fr_client = client.get_document_analysis_client()
        with open(self.selection_form_pdf, "rb") as fd:
            myfile = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeResultOperation, raw_response)
            document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(document)

        async with client:
            poller = await client.begin_build_model(formrecognizer_selection_mark_storage_container_sas_url)
            model = await poller.result()

            poller = await fr_client.begin_analyze_document(
                model.model_id,
                myfile,
                cls=callback
            )
            document = await poller.result()

        raw_analyze_result = responses[0].analyze_result
        returned_model = responses[1]

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content

        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(returned_model.key_value_pairs, raw_analyze_result.key_value_pairs)
        self.assertDocumentEntitiesTransformCorrect(returned_model.entities, raw_analyze_result.entities)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    async def test_pages_kwarg_specified(self, client, formrecognizer_storage_container_sas_url):
        fr_client = client.get_document_analysis_client()

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        async with client:
            build_poller = await client.begin_build_model(formrecognizer_storage_container_sas_url)
            model = await build_poller.result()

            async with fr_client:
                poller = await fr_client.begin_analyze_document(model.model_id, myfile, pages="1")
                assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
                result = await poller.result()
                assert result
