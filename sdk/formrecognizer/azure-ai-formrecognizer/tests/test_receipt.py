# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer


class TestReceipt(FormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    def test_receipt(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        response = client.begin_recognize_receipts_from_url(
            url="https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/contoso-allinone.jpg",
            include_text_content=True
        )

        result = response.result()
        self.assertIsNotNone(result)
