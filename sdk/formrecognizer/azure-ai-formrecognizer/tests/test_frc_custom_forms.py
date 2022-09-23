# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils import recorded_by_proxy
from azure.ai.formrecognizer import FormContentType, FormTrainingClient, _models
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_form_result
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer

FormTrainingClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)


class TestCustomForms(FormRecognizerTest):

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    @recorded_by_proxy
    def test_custom_form_unlabeled(self, client, formrecognizer_storage_container_sas_url_v2, **kwargs):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False)
        model = poller.result()

        with open(self.form_jpg, "rb") as stream:
            poller = fr_client.begin_recognize_custom_forms(
                model.model_id,
                stream,
                content_type=FormContentType.IMAGE_JPEG
            )
        form = poller.result()

        assert form[0].form_type ==  "form-0"
        self.assertUnlabeledRecognizedFormHasValues(form[0], model)

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    @recorded_by_proxy
    def test_custom_form_multipage_unlabeled(self, client, formrecognizer_multipage_storage_container_sas_url_v2, **kwargs):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_multipage_storage_container_sas_url_v2, use_training_labels=False)
        model = poller.result()

        with open(self.multipage_invoice_pdf, "rb") as stream:
            poller = fr_client.begin_recognize_custom_forms(
                model.model_id,
                stream,
                content_type=FormContentType.APPLICATION_PDF
            )
        forms = poller.result()

        for form in forms:
            if form.form_type is None:
                continue  # blank page
            assert form.form_type == "form-0"
            self.assertUnlabeledRecognizedFormHasValues(form, model)

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    @recorded_by_proxy
    def test_custom_form_labeled(self, client, formrecognizer_storage_container_sas_url_v2, **kwargs):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(
            formrecognizer_storage_container_sas_url_v2,
            use_training_labels=True,
            model_name="labeled"
        )
        model = poller.result()

        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()

        poller = fr_client.begin_recognize_custom_forms(model.model_id, my_file, content_type=FormContentType.IMAGE_JPEG)
        form = poller.result()

        assert form[0].form_type ==  "custom:labeled"
        self.assertLabeledRecognizedFormHasValues(form[0], model)

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    @recorded_by_proxy
    def test_custom_form_multipage_labeled(self, client, formrecognizer_multipage_storage_container_sas_url_v2, **kwargs):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(
            formrecognizer_multipage_storage_container_sas_url_v2,
            use_training_labels=True
        )
        model = poller.result()

        with open(self.multipage_invoice_pdf, "rb") as fd:
            my_file = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            my_file,
            content_type=FormContentType.APPLICATION_PDF
        )
        forms = poller.result()

        for form in forms:
            assert form.form_type ==  "custom:"+model.model_id
            self.assertLabeledRecognizedFormHasValues(form, model)

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    @recorded_by_proxy
    def test_custom_form_unlabeled_transform(self, client, formrecognizer_storage_container_sas_url_v2, **kwargs):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            my_file,
            include_field_elements=True,
            cls=callback
        )
        form = poller.result()
        actual = responses[0]
        recognized_form = responses[1]
        read_results = actual.analyze_result.read_results
        page_results = actual.analyze_result.page_results
        actual_fields = actual.analyze_result.page_results[0].key_value_pairs

        self.assertFormPagesTransformCorrect(recognized_form[0].pages, read_results, page_results)
        assert recognized_form[0].page_range.first_page_number ==  page_results[0].page
        assert recognized_form[0].page_range.last_page_number ==  page_results[0].page
        assert recognized_form[0].form_type_confidence is None
        assert recognized_form[0].model_id is not None
        self.assertUnlabeledFormFieldDictTransformCorrect(recognized_form[0].fields, actual_fields, read_results)

        recognized_form_dict = [v.to_dict() for v in recognized_form]
        assert recognized_form_dict[0].get("form_type_confidence") is None
        assert recognized_form_dict[0].get("model_id") is not None
        assert recognized_form_dict[0].get("form_type") ==  "form-0"

        recognized_form = _models.RecognizedForm.from_dict(recognized_form_dict[0])

        self.assertFormPagesTransformCorrect(recognized_form.pages, read_results, page_results)
        assert recognized_form.page_range.first_page_number ==  page_results[0].page
        assert recognized_form.page_range.last_page_number ==  page_results[0].page
        assert recognized_form.form_type_confidence is None
        assert recognized_form.model_id is not None
        self.assertUnlabeledFormFieldDictTransformCorrect(recognized_form.fields, actual_fields, read_results)

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    @recorded_by_proxy
    def test_custom_form_multipage_unlabeled_transform(self, client, formrecognizer_multipage_storage_container_sas_url_v2, **kwargs):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_multipage_storage_container_sas_url_v2, use_training_labels=False)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.multipage_invoice_pdf, "rb") as fd:
            my_file = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            my_file,
            include_field_elements=True,
            cls=callback
        )
        form = poller.result()
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

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    def test_custom_form_continuation_token(self, **kwargs):
        client = kwargs.pop("client")
        formrecognizer_storage_container_sas_url_v2 = kwargs.pop("formrecognizer_storage_container_sas_url_v2")
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False)
        model = poller.result()

        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()
        initial_poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            my_file
        )
        cont_token = initial_poller.continuation_token()
        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            None,
            continuation_token=cont_token
        )
        result = poller.result()
        assert result is not None
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    @recorded_by_proxy
    def test_custom_form_multipage_vendor_set_unlabeled_transform(self, client, formrecognizer_multipage_storage_container_sas_url_2_v2, **kwargs):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_multipage_storage_container_sas_url_2_v2, use_training_labels=False)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.multipage_vendor_pdf, "rb") as fd:
            my_file = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            my_file,
            include_field_elements=True,
            cls=callback
        )
        form = poller.result()
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

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    @recorded_by_proxy
    def test_custom_form_multipage_vendor_set_labeled_transform(self, client, formrecognizer_multipage_storage_container_sas_url_2_v2, **kwargs):
        fr_client = client.get_form_recognizer_client()

        poller = client.begin_training(formrecognizer_multipage_storage_container_sas_url_2_v2, use_training_labels=True)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = fr_client._deserialize(AnalyzeOperationResult, raw_response)
            form = prepare_form_result(analyze_result, model.model_id)
            responses.append(analyze_result)
            responses.append(form)

        with open(self.multipage_vendor_pdf, "rb") as fd:
            my_file = fd.read()

        poller = fr_client.begin_recognize_custom_forms(
            model.model_id,
            my_file,
            include_field_elements=True,
            cls=callback
        )
        form = poller.result()
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
