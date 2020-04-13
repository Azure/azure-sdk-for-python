# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from azure.ai.formrecognizer import FormRecognizerClient
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer, GlobalFormAndStorageAccountPreparer
from testcase import GlobalTrainingAccountPreparer as _GlobalTrainingAccountPreparer


GlobalTrainingAccountPreparer = functools.partial(_GlobalTrainingAccountPreparer, FormRecognizerClient)


class TestCustomForms(FormRecognizerTest):

    @GlobalFormAndStorageAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_custom_form_unlabeled(self, client, container_sas_url):
        training_client = client.get_form_training_client()

        poller = training_client.begin_training(container_sas_url)
        model = poller.result()

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        poller = client.begin_recognize_custom_forms(model.model_id, myfile)
        form = poller.result()

        self.assertEqual(form[0].form_type, "form-0")
        self.assertFormPagesHasValues(form[0].pages)
        for label, field in form[0].fields.items():
            self.assertIsNotNone(field.confidence)
            self.assertIsNotNone(field.name)
            self.assertIsNotNone(field.page_number)
            self.assertIsNotNone(field.value)
            self.assertIsNotNone(field.value_data.text)
            self.assertIsNotNone(field.label_data.text)

    @GlobalFormAndStorageAccountPreparer()
    @GlobalTrainingAccountPreparer()
    def test_custom_form_labeled(self, client, container_sas_url):
        training_client = client.get_form_training_client()

        poller = training_client.begin_training(container_sas_url, use_labels=True)
        model = poller.result()

        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()

        poller = client.begin_recognize_custom_forms(model.model_id, myfile)
        form = poller.result()

        self.assertEqual(form[0].form_type, "form-"+model.model_id)
        self.assertFormPagesHasValues(form[0].pages)
        for label, field in form[0].fields.items():
            self.assertIsNotNone(field.confidence)
            self.assertIsNotNone(field.name)
            self.assertIsNotNone(field.page_number)
            self.assertIsNotNone(field.value_data.text)
            self.assertIsNotNone(field.value_data.bounding_box)
