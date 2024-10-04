
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import functools
from devtools_testutils import PowerShellPreparer, AzureMgmtPreparer, is_live, get_credential
from azure.core.credentials import AzureKeyCredential

ENABLE_LOGGER = os.getenv('ENABLE_LOGGER', "False")
REGION = os.getenv('FORMRECOGNIZER_LOCATION', None)


FormRecognizerPreparer = functools.partial(
    PowerShellPreparer,
    'formrecognizer',
    formrecognizer_test_endpoint="https://fakeendpoint.cognitiveservices.azure.com",
    formrecognizer_storage_container_sas_url="https://blob_sas_url",
    formrecognizer_testing_data_container_sas_url="https://blob_sas_url",
    formrecognizer_multipage_storage_container_sas_url="https://blob_sas_url",
    formrecognizer_multipage_storage_container_sas_url_2="https://blob_sas_url",
    formrecognizer_selection_mark_storage_container_sas_url="https://blob_sas_url",
    formrecognizer_table_variable_rows_container_sas_url="https://blob_sas_url",
    formrecognizer_table_fixed_rows_container_sas_url="https://blob_sas_url",
    formrecognizer_storage_container_sas_url_v2="https://blob_sas_url",
    formrecognizer_multipage_storage_container_sas_url_v2="https://blob_sas_url",
    formrecognizer_multipage_storage_container_sas_url_2_v2="https://blob_sas_url",
    formrecognizer_selection_mark_storage_container_sas_url_v2="https://blob_sas_url",
    formrecognizer_table_variable_rows_container_sas_url_v2="https://blob_sas_url",
    formrecognizer_table_fixed_rows_container_sas_url_v2="https://blob_sas_url",
    formrecognizer_training_data_classifier="https://blob_sas_url",
    formrecognizer_resource_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rgname/providers/Microsoft.CognitiveServices/accounts/formrecognizername",
    formrecognizer_region="region"
)

def get_sync_client(client_cls, **kwargs):
    ENABLE_LOGGER = os.getenv('ENABLE_LOGGER', "False")
    polling_interval = kwargs.pop("polling_interval", None)
    if is_live():
        form_recognizer_account = os.environ["FORMRECOGNIZER_TEST_ENDPOINT"]
        if not polling_interval:
            polling_interval = 1
    else:
        form_recognizer_account = "https://fakeendpoint.cognitiveservices.azure.com"
        if not polling_interval:
            polling_interval = 0
    if "api_key" in kwargs:
        api_key = kwargs.pop("api_key")
        return client_cls(
            form_recognizer_account,
            AzureKeyCredential(api_key),
            polling_interval=polling_interval,
            logging_enable=True if ENABLE_LOGGER == "True" else False,
            **kwargs
        )
    return client_cls(
        form_recognizer_account,
        get_credential(),
        polling_interval=polling_interval,
        logging_enable=True if ENABLE_LOGGER == "True" else False,
        **kwargs
    )

def get_async_client(client_cls, **kwargs):
    ENABLE_LOGGER = os.getenv('ENABLE_LOGGER', "False")
    polling_interval = kwargs.pop("polling_interval", None)
    if is_live():
        form_recognizer_account = os.environ["FORMRECOGNIZER_TEST_ENDPOINT"]
        if not polling_interval:
            polling_interval = 1
    else:
        form_recognizer_account = "https://fakeendpoint.cognitiveservices.azure.com"
        if not polling_interval:
            polling_interval = 0
    if "api_key" in kwargs:
        api_key = kwargs.pop("api_key")
        return client_cls(
            form_recognizer_account,
            AzureKeyCredential(api_key),
            polling_interval=polling_interval,
            logging_enable=True if ENABLE_LOGGER == "True" else False,
            **kwargs
        )
    return client_cls(
        form_recognizer_account,
        get_credential(is_async=True),
        polling_interval=polling_interval,
        logging_enable=True if ENABLE_LOGGER == "True" else False,
        **kwargs
    )
