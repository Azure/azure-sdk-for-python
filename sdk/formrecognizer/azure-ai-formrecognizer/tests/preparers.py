
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import functools
from devtools_testutils import PowerShellPreparer, AzureMgmtPreparer
from azure.core.credentials import AzureKeyCredential

ENABLE_LOGGER = os.getenv('ENABLE_LOGGER', "False")
REGION = os.getenv('FORMRECOGNIZER_LOCATION', None)


FormRecognizerPreparer = functools.partial(
    PowerShellPreparer,
    'formrecognizer',
    formrecognizer_test_endpoint="https://region.api.cognitive.microsoft.com/",
    formrecognizer_test_api_key="fakeZmFrZV9hY29jdW50X2tleQ==",
    formrecognizer_storage_container_sas_url="container_sas_url",
    formrecognizer_testing_data_container_sas_url="container_sas_url",
    formrecognizer_multipage_storage_container_sas_url="container_sas_url",
    formrecognizer_multipage_storage_container_sas_url_2="container_sas_url",
    formrecognizer_selection_mark_storage_container_sas_url="container_sas_url",
    formrecognizer_resource_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rgname/providers/Microsoft.CognitiveServices/accounts/frname",
    formrecognizer_region="region"
)


class GlobalClientPreparer(AzureMgmtPreparer):
    def __init__(self, client_cls, client_kwargs={}, **kwargs):
        super(GlobalClientPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )
        self.client_kwargs = client_kwargs
        self.client_cls = client_cls

    def create_resource(self, name, **kwargs):
        if self.is_live:
            form_recognizer_account = os.environ["FORMRECOGNIZER_TEST_ENDPOINT"]
            form_recognizer_account_key = os.environ["FORMRECOGNIZER_TEST_API_KEY"]
            polling_interval = 5
        else:
            form_recognizer_account = "https://region.api.cognitive.microsoft.com/"
            form_recognizer_account_key = "fakeZmFrZV9hY29jdW50X2tleQ=="
            polling_interval = 0

        client = self.client_cls(
            form_recognizer_account,
            AzureKeyCredential(form_recognizer_account_key),
            polling_interval=polling_interval,
            logging_enable=True if ENABLE_LOGGER == "True" else False,
            **self.client_kwargs
        )
        kwargs.update({"client": client})
        return kwargs
