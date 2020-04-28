# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from datetime import date, time
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError, HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_us_receipt
from azure.ai.formrecognizer import FormRecognizerClient, FormContentType
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer, LogCaptured


class TestLogging(FormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    def test_logging_receipt(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with LogCaptured(self) as log_captured:
            poller = client.begin_recognize_receipts_from_url(self.receipt_url_jpg, include_text_content=True, logging_enable=True)
            log_as_str = log_captured.getvalue()
            result = poller.result()
            log_as_str = log_captured.getvalue()
