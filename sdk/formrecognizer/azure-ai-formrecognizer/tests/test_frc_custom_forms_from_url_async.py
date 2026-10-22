# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.formrecognizer.aio import FormTrainingClient
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_form_result
from preparers import FormRecognizerPreparer, get_async_client
from asynctestcase import AsyncFormRecognizerTest
from testcase import _get_blob_url
from conftest import skip_flaky_test
get_ft_client = functools.partial(get_async_client, FormTrainingClient)


class TestCustomFormsFromUrlAsync(AsyncFormRecognizerTest):

    @pytest.mark.skip("Test is flaky and hangs")
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_custom_form_multipage_unlabeled(self, formrecognizer_multipage_storage_container_sas_url_v2, **kwargs):
        client = get_ft_client()
        fr_client = client.get_form_recognizer_client()
        blob_sas_url = _get_blob_url(formrecognizer_multipage_storage_container_sas_url_v2, "multipage-training-data", "multipage_invoice1.pdf")
        async with client:
            training_poller = await client.begin_training(formrecognizer_multipage_storage_container_sas_url_v2, use_training_labels=False)
            model = await training_poller.result()

            async with fr_client:
                poller = await fr_client.begin_recognize_custom_forms_from_url(
                    model.model_id,
                    blob_sas_url,
                )
                forms = await poller.result()

        for form in forms:
            if form.form_type is None:
                continue  # blank page
            assert form.form_type == "form-0"
            self.assertUnlabeledRecognizedFormHasValues(form, model)

    @pytest.mark.skip("Test is flaky and hangs")
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_form_multipage_labeled(self, formrecognizer_multipage_storage_container_sas_url_v2, **kwargs):
        client = get_ft_client()
        fr_client = client.get_form_recognizer_client()
        blob_sas_url = _get_blob_url(formrecognizer_multipage_storage_container_sas_url_v2, "multipage-training-data", "multipage_invoice1.pdf")
        async with client:
            training_poller = await client.begin_training(
                formrecognizer_multipage_storage_container_sas_url_v2,
                use_training_labels=True
            )
            model = await training_poller.result()

            async with fr_client:
                poller = await fr_client.begin_recognize_custom_forms_from_url(
                    model.model_id,
                    blob_sas_url
                )
                forms = await poller.result()

        for form in forms:
            assert form.form_type ==  "custom:"+model.model_id
            self.assertLabeledRecognizedFormHasValues(form, model)

    @pytest.mark.skip("Test is flaky and hangs")
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_multipage_unlabeled_transform(self, formrecognizer_multipage_storage_container_sas_url_v2, **kwargs):
        client = get_ft_client()
        fr_client = client.get_form_recognizer_client()
        blob_sas_url = _get_blob_url(formrecognizer_multipage_storage_container_sas_url_v2, "multipage-training-data", "multipage_invoice1.pdf")
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        async with client:
            training_poller = await client.begin_training(formrecognizer_multipage_storage_container_sas_url_v2, use_training_labels=False)
            model = await training_poller.result()

            async with fr_client:
                poller = await fr_client.begin_recognize_custom_forms_from_url(
                    model.model_id,
                    blob_sas_url,
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
            assert form.page_range.first_page_number ==  actual.page
            assert form.page_range.last_page_number ==  actual.page
            assert form.form_type_confidence is None
            assert form.model_id ==  model.model_id
            self.assertUnlabeledFormFieldDictTransformCorrect(form.fields, actual.key_value_pairs, read_results)

    @pytest.mark.skip("Test is flaky and hangs")
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_multipage_labeled_transform(self, formrecognizer_multipage_storage_container_sas_url_v2, **kwargs):
        client = get_ft_client()
        fr_client = client.get_form_recognizer_client()
        blob_sas_url = _get_blob_url(formrecognizer_multipage_storage_container_sas_url_v2, "multipage-training-data", "multipage_invoice1.pdf")
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        async with client:
            training_poller = await client.begin_training(formrecognizer_multipage_storage_container_sas_url_v2, use_training_labels=True)
            model = await training_poller.result()

            async with fr_client:
                poller = await fr_client.begin_recognize_custom_forms_from_url(
                    model.model_id,
                    blob_sas_url,
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
            assert form.page_range.first_page_number ==  actual.page_range[0]
            assert form.page_range.last_page_number ==  actual.page_range[1]
            assert form.form_type ==  "custom:"+model.model_id
            assert form.form_type_confidence is not None
            assert form.model_id ==  model.model_id
            self.assertFormFieldsTransformCorrect(form.fields, actual.fields, read_results)

    @pytest.mark.skip("Test is flaky and hangs")
    @skip_flaky_test
    @FormRecognizerPreparer()
    async def test_custom_form_continuation_token(self, **kwargs):
        client = get_ft_client()
        formrecognizer_storage_container_sas_url = kwargs.pop("formrecognizer_storage_container_sas_url")
        fr_client = client.get_form_recognizer_client()

        async with client:
            poller = await client.begin_training(formrecognizer_storage_container_sas_url, use_training_labels=False)
            model = await poller.result()

            async with fr_client:
                initial_poller = await fr_client.begin_recognize_custom_forms_from_url(
                    model.model_id,
                    self.form_url_jpg
                )
                cont_token = initial_poller.continuation_token()
                poller = await fr_client.begin_recognize_custom_forms_from_url(
                    model.model_id,
                    None,
                    continuation_token=cont_token
                )
                result = await poller.result()
                assert result is not None
                await initial_poller.wait()  # necessary so devtools_testutils doesn't throw assertion error

    @pytest.mark.skip("Test is flaky and hangs")
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_custom_form_multipage_vendor_set_unlabeled_transform(self, formrecognizer_multipage_storage_container_sas_url_2_v2, **kwargs):
        client = get_ft_client()
        fr_client = client.get_form_recognizer_client()
        blob_sas_url = _get_blob_url(formrecognizer_multipage_storage_container_sas_url_2_v2, "multipage-vendor-forms", "multi1.pdf")
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        async with client:
            poller = await client.begin_training(formrecognizer_multipage_storage_container_sas_url_2_v2, use_training_labels=False)
            model = await poller.result()

            async with fr_client:
                poller = await fr_client.begin_recognize_custom_forms_from_url(
                    model.model_id,
                    blob_sas_url,
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
            assert form.page_range.first_page_number ==  actual.page
            assert form.page_range.last_page_number ==  actual.page
            assert form.form_type_confidence is None
            assert form.model_id ==  model.model_id
            self.assertUnlabeledFormFieldDictTransformCorrect(form.fields, actual.key_value_pairs, read_results)

    @pytest.mark.skip("Test is flaky and hangs")
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_custom_form_multipage_vendor_set_labeled_transform(self, formrecognizer_multipage_storage_container_sas_url_2_v2, **kwargs):
        client = get_ft_client()
        fr_client = client.get_form_recognizer_client()
        blob_sas_url = _get_blob_url(formrecognizer_multipage_storage_container_sas_url_2_v2, "multipage-vendor-forms", "multi1.pdf")
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        async with client:
            poller = await client.begin_training(formrecognizer_multipage_storage_container_sas_url_2_v2, use_training_labels=True)
            model = await poller.result()

            async with fr_client:
                poller = await fr_client.begin_recognize_custom_forms_from_url(
                    model.model_id,
                    blob_sas_url,
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
            assert form.page_range.first_page_number ==  actual.page_range[0]
            assert form.page_range.last_page_number ==  actual.page_range[1]
            assert form.form_type ==  "custom:"+model.model_id
            assert form.form_type_confidence is not None
            assert form.model_id ==  model.model_id
            self.assertFormFieldsTransformCorrect(form.fields, actual.fields, read_results)

    @pytest.mark.skip("Test is flaky and hangs")
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_pages_kwarg_specified(self, formrecognizer_testing_data_container_sas_url, **kwargs):
        client = get_ft_client()
        fr_client = client.get_form_recognizer_client()
        blob_sas_url = _get_blob_url(formrecognizer_testing_data_container_sas_url, "testingdata", "multi1.pdf")

        async with fr_client:
            training_poller = await client.begin_training(formrecognizer_testing_data_container_sas_url, use_training_labels=False)
            model = await training_poller.result()

            poller = await fr_client.begin_recognize_custom_forms_from_url(
                model.model_id, 
                blob_sas_url, 
                pages=["1"])
            
            assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
            result = await poller.result()
            assert result
