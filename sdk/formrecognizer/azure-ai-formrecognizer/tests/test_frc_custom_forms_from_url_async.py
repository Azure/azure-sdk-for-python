# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_custom_default_matcher
from azure.ai.formrecognizer.aio import FormTrainingClient
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_form_result
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from testcase import _get_blob_url
from preparers import GlobalClientPreparer as _GlobalClientPreparer

FormTrainingClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)


class TestCustomFormsFromUrlAsync(AsyncFormRecognizerTest):

    def teardown(self):
        self.sleep(4)

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    @recorded_by_proxy_async
    async def test_custom_form_multipage_unlabeled(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_multipage_storage_container_sas_url_v2 = kwargs.pop("formrecognizer_multipage_storage_container_sas_url_v2")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
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

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    @recorded_by_proxy_async
    async def test_form_multipage_labeled(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_multipage_storage_container_sas_url_v2 = kwargs.pop("formrecognizer_multipage_storage_container_sas_url_v2")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
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

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    @recorded_by_proxy_async
    async def test_multipage_unlabeled_transform(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_multipage_storage_container_sas_url_v2 = kwargs.pop("formrecognizer_multipage_storage_container_sas_url_v2")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
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

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    @recorded_by_proxy_async
    async def test_multipage_labeled_transform(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_multipage_storage_container_sas_url_v2 = kwargs.pop("formrecognizer_multipage_storage_container_sas_url_v2")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
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

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    async def test_custom_form_continuation_token(self, **kwargs):
        client = kwargs.pop("client")
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
                await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    @recorded_by_proxy_async
    async def test_custom_form_multipage_vendor_set_unlabeled_transform(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_multipage_storage_container_sas_url_2_v2 = kwargs.pop("formrecognizer_multipage_storage_container_sas_url_2_v2")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
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

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    @recorded_by_proxy_async
    async def test_custom_form_multipage_vendor_set_labeled_transform(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_multipage_storage_container_sas_url_2_v2 = kwargs.pop("formrecognizer_multipage_storage_container_sas_url_2_v2")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
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

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    @recorded_by_proxy_async
    async def test_pages_kwarg_specified(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_testing_data_container_sas_url = kwargs.pop("formrecognizer_testing_data_container_sas_url")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
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
