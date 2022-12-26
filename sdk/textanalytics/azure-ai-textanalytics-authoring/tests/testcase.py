# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
import functools
from azure.core.credentials import AccessToken, AzureKeyCredential
from devtools_testutils import (
    AzureMgmtPreparer,
)

from devtools_testutils import PowerShellPreparer, AzureRecordedTestCase


def is_public_cloud():
    return (".microsoftonline.com" in os.getenv('AZURE_AUTHORITY_HOST', ''))


TextAnalyticsPreparer = functools.partial(
    PowerShellPreparer,
    'textanalytics',
    textanalytics_test_endpoint="https://fakeendpoint.cognitiveservices.azure.com",
    textanalytics_test_api_key="fakeZmFrZV9hY29jdW50X2tleQ==",
)


class TextAnalyticsClientPreparer(AzureMgmtPreparer):
    def __init__(self, client_cls, client_kwargs={}, **kwargs):
        super().__init__(
            name_prefix='',
            random_name_length=42
        )
        self.client_kwargs = client_kwargs
        self.client_cls = client_cls

    def create_resource(self, name, **kwargs):
        textanalytics_test_endpoint = kwargs.get("textanalytics_test_endpoint")
        textanalytics_test_api_key = kwargs.get("textanalytics_test_api_key")

        if "textanalytics_test_api_key" in self.client_kwargs:
            textanalytics_test_api_key = self.client_kwargs.pop("textanalytics_test_api_key")

        client = self.client_cls(
            textanalytics_test_endpoint,
            AzureKeyCredential(textanalytics_test_api_key),
            **self.client_kwargs
        )
        kwargs.update({"client": client})
        return kwargs


class TextAnalyticsTest(AzureRecordedTestCase):
    pass