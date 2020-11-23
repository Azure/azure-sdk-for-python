# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ServiceRequestError, ClientAuthenticationError, HttpResponseError
from azure.ai.formrecognizer import FormContentType
from azure.ai.formrecognizer.aio import FormRecognizerClient, FormTrainingClient
from azure.ai.formrecognizer._generated.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_form_result
from testcase import GlobalFormRecognizerAccountPreparer
from asynctestcase import AsyncFormRecognizerTest
from testcase import GlobalClientPreparer as _GlobalClientPreparer


GlobalClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)


class TestCustomFormsAsync(AsyncFormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    async def test_custom_form_none_model_id(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with self.assertRaises(ValueError):
            async with client:
                await client.begin_recognize_custom_forms(model_id=None, form=b"xx")

    @GlobalFormRecognizerAccountPreparer()
    async def test_custom_form_empty_model_id(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with self.assertRaises(ValueError):
            async with client:
                await client.begin_recognize_custom_forms(model_id="", form=b"xx")

    @GlobalFormRecognizerAccountPreparer()
    async def test_custom_form_bad_endpoint(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(form_recognizer_account_key))
            async with client:
                poller = await client.begin_recognize_custom_forms(model_id="xx", form=myfile)
                result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    async def test_authentication_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                poller = await client.begin_recognize_custom_forms(model_id="xx", form=b"xx", content_type="image/jpeg")
                result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    async def test_passing_unsupported_url_content_type(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with self.assertRaises(TypeError):
            async with client:
                poller = await client.begin_recognize_custom_forms(model_id="xx", form="https://badurl.jpg", content_type="application/json")
                result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    async def test_auto_detect_unsupported_stream_content(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with open(self.unsupported_content_py, "rb") as fd:
            myfile = fd.read()

        with self.assertRaises(ValueError):
            async with client:
                poller = await client.begin_recognize_custom_forms(
                    model_id="xxx",
                    form=myfile,
                )
                result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    async def test_custom_form_damaged_file(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()
        async with client:
            training_poller = await client.begin_training(container_sas_url, use_training_labels=False)
            model = await training_poller.result()

            with self.assertRaises(HttpResponseError):
                async with fr_client:
                    poller = await fr_client.begin_recognize_custom_forms(
                        model.model_id,
                        b"\x25\x50\x44\x46\x55\x55\x55",
                    )
                    result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    async def test_custom_form_unlabeled_blank_page(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()
        with open(self.blank_pdf, "rb") as fd:
            blank = fd.read()

        async with client:
            poller = await client.begin_training(container_sas_url, use_training_labels=False)
            model = await poller.result()

            async with fr_client:
                poller = await fr_client.begin_recognize_custom_forms(
                    model.model_id,
                    blank
                )
                form = await poller.result()

        self.assertEqual(len(form), 1)
        self.assertEqual(form[0].page_range.first_page_number, 1)
        self.assertEqual(form[0].page_range.last_page_number, 1)
        self.assertIsNotNone(form[0].pages)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    async def test_custom_form_labeled_blank_page(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()
        with open(self.blank_pdf, "rb") as fd:
            blank = fd.read()

        async with client:
            poller = await client.begin_training(container_sas_url, use_training_labels=True)
            model = await poller.result()

            async with fr_client:
                poller = await fr_client.begin_recognize_custom_forms(
                    model.model_id,
                    blank
                )
                form = await poller.result()

        self.assertEqual(len(form), 1)
        self.assertEqual(form[0].page_range.first_page_number, 1)
        self.assertEqual(form[0].page_range.last_page_number, 1)
        self.assertIsNotNone(form[0].pages)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    async def test_custom_form_unlabeled(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        async with client:
            training_poller = await client.begin_training(container_sas_url, use_training_labels=False)
            model = await training_poller.result()

            async with fr_client:
                poller = await fr_client.begin_recognize_custom_forms(model.model_id, myfile, content_type=FormContentType.IMAGE_JPEG)
                form = await poller.result()
        self.assertEqual(form[0].form_type, "form-0")
        self.assertUnlabeledRecognizedFormHasValues(form[0], model)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, multipage=True)
    async def test_custom_form_multipage_unlabeled(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()
        with open(self.multipage_invoice_pdf, "rb") as fd:
            myfile = fd.read()

        async with client:
            training_poller = await client.begin_training(container_sas_url, use_training_labels=False)
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

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    async def test_custom_form_labeled(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        async with client:
            training_poller = await client.begin_training(container_sas_url, use_training_labels=True, model_name="labeled")
            model = await training_poller.result()

            async with fr_client:
                poller = await fr_client.begin_recognize_custom_forms(model.model_id, myfile, content_type=FormContentType.IMAGE_JPEG)
                form = await poller.result()

        self.assertEqual(form[0].form_type, "custom:labeled")
        self.assertLabeledRecognizedFormHasValues(form[0], model)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, multipage=True)
    async def test_custom_form_multipage_labeled(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()
        with open(self.multipage_invoice_pdf, "rb") as fd:
            myfile = fd.read()

        async with client:
            training_poller = await client.begin_training(
                container_sas_url,
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

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    async def test_form_unlabeled_transform(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        async with client:
            training_poller = await client.begin_training(container_sas_url, use_training_labels=False)
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
        actual_fields = actual.analyze_result.page_results[0].key_value_pairs

        self.assertFormPagesTransformCorrect(recognized_form[0].pages, read_results, page_results)
        self.assertEqual(recognized_form[0].page_range.first_page_number, page_results[0].page)
        self.assertEqual(recognized_form[0].page_range.last_page_number, page_results[0].page)
        self.assertIsNone(recognized_form[0].form_type_confidence)
        self.assertIsNotNone(recognized_form[0].model_id)
        self.assertUnlabeledFormFieldDictTransformCorrect(recognized_form[0].fields, actual_fields, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, multipage=True)
    async def test_custom_forms_multipage_unlabeled_transform(self, client, container_sas_url):
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
            training_poller = await client.begin_training(container_sas_url, use_training_labels=False)
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


    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    async def test_form_labeled_transform(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        async with client:
            training_polling = await client.begin_training(container_sas_url, use_training_labels=True)
            model = await training_polling.result()

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
        actual_fields = actual.analyze_result.document_results[0].fields

        self.assertFormPagesTransformCorrect(recognized_form[0].pages, read_results, page_results)
        self.assertEqual(recognized_form[0].page_range.first_page_number, page_results[0].page)
        self.assertEqual(recognized_form[0].page_range.last_page_number, page_results[0].page)
        self.assertEqual(recognized_form[0].form_type_confidence, 1.0)
        self.assertIsNotNone(recognized_form[0].model_id)
        self.assertFormFieldsTransformCorrect(recognized_form[0].fields, actual_fields, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, multipage=True)
    async def test_custom_forms_multipage_labeled_transform(self, client, container_sas_url):
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
            training_poller = await client.begin_training(container_sas_url, use_training_labels=True)
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
        document_results = actual.analyze_result.document_results

        self.assertFormPagesTransformCorrect(recognized_form, read_results, page_results)
        for form, actual in zip(recognized_form, document_results):
            self.assertEqual(form.page_range.first_page_number, actual.page_range[0])
            self.assertEqual(form.page_range.last_page_number, actual.page_range[1])
            self.assertEqual(form.form_type, "custom:"+model.model_id)
            self.assertEqual(form.form_type_confidence, 1.0)
            self.assertEqual(form.model_id, model.model_id)
            self.assertFormFieldsTransformCorrect(form.fields, actual.fields, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True)
    @pytest.mark.live_test_only
    async def test_custom_form_continuation_token(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()
        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        async with client:
            poller = await client.begin_training(container_sas_url, use_training_labels=False)
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

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, multipage2=True)
    async def test_custom_form_multipage_vendor_set_unlabeled_transform(self, client, container_sas_url):
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
            poller = await client.begin_training(container_sas_url, use_training_labels=False)
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

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, multipage2=True)
    async def test_custom_form_multipage_vendor_set_labeled_transform(self, client, container_sas_url):
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
            poller = await client.begin_training(container_sas_url, use_training_labels=True)
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
            self.assertEqual(form.form_type_confidence, 1.0)
            self.assertEqual(form.model_id, model.model_id)
            self.assertFormFieldsTransformCorrect(form.fields, actual.fields, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(training=True, selection_marks=True)
    async def test_custom_form_selection_mark(self, client, container_sas_url):
        fr_client = client.get_form_recognizer_client()
        with open(self.selection_form_pdf, "rb") as fd:
            myfile = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        async with client:
            poller = await client.begin_training(container_sas_url, use_training_labels=True)
            model = await poller.result()

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
        actual_fields = actual.analyze_result.document_results[0].fields

        self.assertFormPagesTransformCorrect(recognized_form[0].pages, read_results, page_results)
