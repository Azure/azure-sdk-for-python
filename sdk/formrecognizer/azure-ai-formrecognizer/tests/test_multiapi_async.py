
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from testcase import GlobalFormRecognizerAccountPreparer
from testcase import GlobalClientPreparer as _GlobalClientPreparer
from asynctestcase import AsyncFormRecognizerTest
from azure.ai.formrecognizer.aio import FormRecognizerClient, FormTrainingClient
from azure.ai.formrecognizer import FormRecognizerApiVersion

FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)
FormTrainingClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)

class TestMultiapi(AsyncFormRecognizerTest):
    @GlobalFormRecognizerAccountPreparer()
    @FormRecognizerClientPreparer()
    def test_default_api_version_form_recognizer_client(self, client):
        assert "v2.1-preview.1" in client._client._client._base_url

    @GlobalFormRecognizerAccountPreparer()
    @FormTrainingClientPreparer()
    def test_default_api_version_form_training_client(self, client):
        assert "v2.1-preview.1" in client._client._client._base_url

    @GlobalFormRecognizerAccountPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_v2_0_form_recognizer_client(self, client):
        assert "v2.0" in client._client._client._base_url

    @GlobalFormRecognizerAccountPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_v2_0_form_training_client(self, client):
        assert "v2.0" in client._client._client._base_url

    @GlobalFormRecognizerAccountPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_1_PREVIEW_1})
    def test_v2_1_preview_1_form_recognizer_client(self, client):
        assert "v2.1-preview.1" in client._client._client._base_url

    @GlobalFormRecognizerAccountPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_1_PREVIEW_1})
    def test_v2_1_preview_1_form_training_client(self, client):
        assert "v2.1-preview.1" in client._client._client._base_url
