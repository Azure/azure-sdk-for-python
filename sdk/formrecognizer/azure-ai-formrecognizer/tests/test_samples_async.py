# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
USAGE:
    python test_samples.py

    Set the environment variables with your own values before running the samples.
    See independent sample files to check what env variables must be set.
"""


import subprocess
import functools
import sys
import os
import pytest
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer.aio import FormTrainingClient
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer

def run(cmd, my_env):
    os.environ['PYTHONUNBUFFERED'] = "1"
    proc = subprocess.Popen(cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
        env = my_env
    )
    stdout, stderr = proc.communicate()
 
    return proc.returncode, stdout, stderr

def _test_file(file_name, account, key):
    os.environ['AZURE_FORM_RECOGNIZER_ENDPOINT'] = account
    os.environ['AZURE_FORM_RECOGNIZER_KEY'] = key
    path_to_sample = os.path.abspath(
        os.path.join(os.path.abspath(__file__), "..", "..", "./samples/async_samples/" + file_name))
    code, out, err = run([sys.executable, path_to_sample], my_env=dict(os.environ))
    try:
        assert code == 0
        assert err is None
    except AssertionError as e:
        e.args += (out, )
        raise AssertionError(e)


class TestSamplesAsync(FormRecognizerTest):
    # Async sample tests
    @pytest.mark.live_test_only
    @GlobalFormRecognizerAccountPreparer()
    def test_sample_authentication_async(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        _test_file('sample_authentication_async.py', form_recognizer_account, form_recognizer_account_key)

    @pytest.mark.live_test_only
    @GlobalFormRecognizerAccountPreparer()
    async def test_sample_get_bounding_boxes_async(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        os.environ['CONTAINER_SAS_URL'] = self.get_settings_value("FORM_RECOGNIZER_STORAGE_CONTAINER_SAS_URL")
        ftc = FormTrainingClient(form_recognizer_account,  AzureKeyCredential(form_recognizer_account_key))
        container_sas_url = os.environ['CONTAINER_SAS_URL']
        async with ftc:
            poller = await ftc.begin_training(container_sas_url, use_training_labels=False)
            model = await poller.result()
        os.environ['CUSTOM_TRAINED_MODEL_ID'] = model.model_id
        _test_file('sample_get_bounding_boxes_async.py', form_recognizer_account, form_recognizer_account_key)

    @pytest.mark.live_test_only
    @GlobalFormRecognizerAccountPreparer()
    def test_sample_manage_custom_models_async(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        _test_file('sample_manage_custom_models_async.py', form_recognizer_account, form_recognizer_account_key)

    @pytest.mark.live_test_only
    @GlobalFormRecognizerAccountPreparer()
    def test_sample_recognize_content_async(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        _test_file('sample_recognize_content_async.py', form_recognizer_account, form_recognizer_account_key)

    @pytest.mark.live_test_only
    @GlobalFormRecognizerAccountPreparer()
    async def test_sample_recognize_custom_forms_async(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        os.environ['CONTAINER_SAS_URL'] = self.get_settings_value("FORM_RECOGNIZER_STORAGE_CONTAINER_SAS_URL")
        ftc = FormTrainingClient(form_recognizer_account,  AzureKeyCredential(form_recognizer_account_key))
        container_sas_url = os.environ['CONTAINER_SAS_URL']
        async with ftc:
            poller = await ftc.begin_training(container_sas_url, use_training_labels=False)
            model = await poller.result()
        os.environ['CUSTOM_TRAINED_MODEL_ID'] = model.model_id
        _test_file('sample_recognize_custom_forms_async.py', form_recognizer_account, form_recognizer_account_key)

    @pytest.mark.live_test_only
    @GlobalFormRecognizerAccountPreparer()
    def test_sample_recognize_receipts_from_url_async(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        _test_file('sample_recognize_receipts_from_url_async.py', form_recognizer_account, form_recognizer_account_key)

    @pytest.mark.live_test_only
    @GlobalFormRecognizerAccountPreparer()
    def test_sample_recognize_receipts_async(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        _test_file('sample_recognize_receipts_async.py', form_recognizer_account, form_recognizer_account_key)

    @pytest.mark.live_test_only
    @GlobalFormRecognizerAccountPreparer()
    def test_sample_train_model_with_labels_async(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        os.environ['CONTAINER_SAS_URL'] = self.get_settings_value("FORM_RECOGNIZER_STORAGE_CONTAINER_SAS_URL")
        _test_file('sample_train_model_with_labels_async.py', form_recognizer_account, form_recognizer_account_key)

    @pytest.mark.live_test_only
    @GlobalFormRecognizerAccountPreparer()
    def test_sample_train_model_without_labels_async(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        os.environ['CONTAINER_SAS_URL'] = self.get_settings_value("FORM_RECOGNIZER_STORAGE_CONTAINER_SAS_URL")
        _test_file('sample_train_model_without_labels_async.py', form_recognizer_account, form_recognizer_account_key)

    @pytest.mark.live_test_only
    @GlobalFormRecognizerAccountPreparer()
    def test_sample_strongly_typing_recognized_form_async(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        _test_file('sample_strongly_typing_recognized_form_async.py', form_recognizer_account, form_recognizer_account_key)

    @pytest.mark.live_test_only
    @GlobalFormRecognizerAccountPreparer()
    async def test_sample_copy_model_async(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        os.environ['CONTAINER_SAS_URL'] = self.get_settings_value("FORM_RECOGNIZER_STORAGE_CONTAINER_SAS_URL")
        ftc = FormTrainingClient(form_recognizer_account,  AzureKeyCredential(form_recognizer_account_key))
        container_sas_url = os.environ['CONTAINER_SAS_URL']
        async with ftc:
            poller = await ftc.begin_training(container_sas_url, use_training_labels=False)
            model = await poller.result()
        os.environ['AZURE_SOURCE_MODEL_ID'] = model.model_id
        os.environ["AZURE_FORM_RECOGNIZER_TARGET_ENDPOINT"] = form_recognizer_account
        os.environ["AZURE_FORM_RECOGNIZER_TARGET_KEY"] = form_recognizer_account_key
        os.environ["AZURE_FORM_RECOGNIZER_TARGET_REGION"] = location
        os.environ["AZURE_FORM_RECOGNIZER_TARGET_RESOURCE_ID"] = \
            "/subscriptions/" + self.get_settings_value("SUBSCRIPTION_ID") + "/resourceGroups/" + \
            resource_group.name + "/providers/Microsoft.CognitiveServices/accounts/" + \
            FormRecognizerTest._FORM_RECOGNIZER_NAME
        _test_file('sample_copy_model_async.py', form_recognizer_account, form_recognizer_account_key)

    @pytest.mark.live_test_only
    @GlobalFormRecognizerAccountPreparer()
    async def test_sample_differentiate_output_models_trained_with_and_without_labels_async(
            self, resource_group, location, form_recognizer_account, form_recognizer_account_key
    ):
        os.environ['CONTAINER_SAS_URL'] = self.get_settings_value("FORM_RECOGNIZER_STORAGE_CONTAINER_SAS_URL")
        ftc = FormTrainingClient(form_recognizer_account,  AzureKeyCredential(form_recognizer_account_key))
        container_sas_url = os.environ['CONTAINER_SAS_URL']
        async with ftc:
            poller = await ftc.begin_training(container_sas_url, use_training_labels=False)
            unlabeled_model = await poller.result()
            poller = await ftc.begin_training(container_sas_url, use_training_labels=True)
            labeled_model = await poller.result()
        os.environ["ID_OF_MODEL_TRAINED_WITH_LABELS"] = labeled_model.model_id
        os.environ["ID_OF_MODEL_TRAINED_WITHOUT_LABELS"] = unlabeled_model.model_id
        _test_file('sample_differentiate_output_models_trained_with_and_without_labels_async.py',
                   form_recognizer_account,
                   form_recognizer_account_key
                   )
